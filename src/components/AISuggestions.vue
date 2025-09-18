<template>
  <div class="ai-suggestions-panel" :class="{ 'collapsed': !isExpanded }">
    <div class="suggestions-container">
      <div class="suggestions-header">
        <h3>AI Помощник</h3>
        <button 
          @click="togglePanel" 
          class="toggle-btn"
          :title="isExpanded ? 'Свернуть' : 'Развернуть'"
        >
          <ChevronIcon :direction="isExpanded ? 'left' : 'right'" />
        </button>
      </div>
      
      <div class="suggestions-content" v-show="isExpanded">
        <!-- Ввод промпта -->
        <div class="prompt-input">
          <textarea
            v-model="userPrompt"
            class="prompt-textarea"
            placeholder="Опишите, что дальше писать... (Ctrl+Enter чтобы сгенерировать)"
            @keydown.ctrl.enter.prevent="submitPrompt"
          ></textarea>
          <div class="prompt-actions">
            <button class="generate-btn" @click="submitPrompt" :disabled="isLoading || !userPrompt.trim()">
              Сгенерировать
            </button>
          </div>
        </div>
        <!-- Загрузка -->
        <div v-if="isLoading" class="loading-state">
          <div class="spinner"></div>
          <span>Генерация подсказок...</span>
        </div>
        
        <!-- Список подсказок -->
        <div v-else-if="suggestions.length > 0" class="suggestions-list">
          <div
            v-for="(item, index) in suggestions"
            :key="index"
            class="suggestion-item"
            @click="applySuggestion(item.text)"
          >
            <div class="suggestion-text">{{ item.text }}</div>
            <div class="suggestion-meta">
              <div class="score-bar">
                <div class="score-fill" :style="{ width: item.score + '%' }"></div>
              </div>
              <span class="score-label" :style="{ color: scoreColor(item.score) }">{{ Math.round(item.score) }}%</span>
            </div>
            <div class="suggestion-actions">
              <button class="apply-btn" @click.stop="applySuggestion(item.text)">Применить</button>
              <button class="regenerate-btn" @click.stop="regenerateSuggestion(index)">↻</button>
            </div>
          </div>
        </div>
        
        <!-- Пустое состояние -->
        <div v-else class="empty-state">
          <p>Напишите промпт слева и нажмите «Сгенерировать» или Ctrl+Enter, чтобы получить 3 варианта продолжения с оценкой релевантности.</p>
        </div>
        
        <!-- Ошибка -->
        <div v-if="error" class="error-state">
          <p>{{ error }}</p>
          <button @click="retry" class="retry-btn">Попробовать снова</button>
        </div>
      </div>
      
      <div class="suggestions-footer">
        <div class="settings">
          <select v-model="suggestionStyle" @change="onStyleChange">
            <option value="descriptive">Описательный</option>
            <option value="detailed">Детальный</option>
            <option value="dynamic">Динамичный</option>
          </select>
        </div>
        <div class="footer-actions">
          <button class="clear-btn" @click="clearAll" :disabled="isLoading">Очистить</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'

// Иконка шеврона
const ChevronIcon = {
  props: ['direction'],
  template: `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
    <polyline :points="direction === 'left' ? '15,18 9,12 15,6' : '9,18 15,12 9,6'"></polyline>
  </svg>`
}
import { apiClient } from '../services/api.js'

export default {
  name: 'AISuggestions',
  components: {
    ChevronIcon
  },
  props: {
    context: {
      type: String,
      default: ''
    },
    chapterId: {
      type: Number,
      default: null
    },
    novelId: {
      type: Number,
      default: null
    }
  },
  emits: ['apply-suggestion'],
  setup(props, { emit }) {
    // [{ text: string, score: number }]
    const suggestions = ref([])
    const isLoading = ref(false)
    const error = ref('')
    const suggestionStyle = ref('neutral')
    const isExpanded = ref(true)
    const userPrompt = ref('')
    const abortController = ref(null)

    // Автогенерация отключена по требованию
    // Генерация только по пользовательскому промпту

    const computeRelevanceScore = (context, prompt, text) => {
      const normalize = (s) => (s || '')
        .toLowerCase()
        .replace(/[^a-zа-яё0-9\s]/gi, ' ')
        .split(/\s+/)
        .filter(Boolean)
      const ctxWords = new Set(normalize(context))
      const prmWords = new Set(normalize(prompt))
      const txtWords = normalize(text)
      if (txtWords.length === 0) return 0
      let overlap = 0
      for (const w of txtWords) {
        if (ctxWords.has(w) || prmWords.has(w)) overlap++
      }
      const ratio = overlap / txtWords.length
      return Math.max(0, Math.min(100, Math.round((ratio * 100))))
    }

    const scoreColor = () => '#6b7280' // монохромный серый для всех состояний

    const submitPrompt = async () => {
      const prompt = userPrompt.value.trim()
      if (!prompt) return
      isLoading.value = true
      error.value = ''
      suggestions.value = []
      try {
        // Контекст из редактора (последние 400 символов)
        const context = (props.context || '').slice(-400)
        const payload = {
          suggestion_type: 'text_completion',
          context: `${context}\n\nИнструкция: ${prompt}`,
          chapter_id: props.chapterId,
          novel_id: props.novelId,
          max_length: 120,
          style: suggestionStyle.value || 'continuation'
        }
        // Генерируем 3 варианта (с возможностью отмены)
        abortController.value?.abort()
        abortController.value = new AbortController()
        const requests = [0,1,2].map(() =>
          apiClient.testGenerateAISuggestion(payload, { signal: abortController.value.signal })
        )
        const results = await Promise.allSettled(requests)
        const variants = results
          .filter(r => r.status === 'fulfilled' && r.value && r.value.content)
          .map(r => String(r.value.content).trim())
          .filter(Boolean)
          .map(text => ({
            text,
            score: computeRelevanceScore(context, prompt, text)
          }))

        if (variants.length === 0) {
          error.value = 'Не удалось сгенерировать варианты по промпту'
        } else {
          // Сортируем по релевантности по убыванию
          variants.sort((a, b) => b.score - a.score)
          suggestions.value = variants
        }
      } catch (err) {
        error.value = err.message || 'Ошибка при генерации'
        console.error('Prompt generation failed:', err)
      } finally {
        isLoading.value = false
      }
    }

    const applySuggestion = (suggestion) => {
      emit('apply-suggestion', suggestion)
    }

    const regenerateSuggestion = async (index) => {
      if (isLoading.value) return

      try {
        isLoading.value = true
        const context = (props.context || '').slice(-400)
        const prompt = userPrompt.value.trim()
        const result = await apiClient.testGenerateAISuggestion({
          suggestion_type: 'text_completion',
          context: `${context}\n\nИнструкция: ${prompt}`,
          chapter_id: props.chapterId,
          novel_id: props.novelId,
          max_length: 120,
          style: suggestionStyle.value || 'continuation'
        })

        if (result && result.content) {
          const text = String(result.content).trim()
          suggestions.value[index] = {
            text,
            score: computeRelevanceScore(context, prompt, text)
          }
        }
      } catch (err) {
        console.error('Error regenerating suggestion:', err)
      } finally {
        isLoading.value = false
      }
    }

    const retry = () => {
      error.value = ''
      submitPrompt()
    }

    const clearAll = () => {
      // Отменяем активные запросы
      abortController.value?.abort()
      abortController.value = null
      // Чистим состояние
      suggestions.value = []
      userPrompt.value = ''
      error.value = ''
      isLoading.value = false
    }

    const togglePanel = () => {
      isExpanded.value = !isExpanded.value
      // Добавляем/убираем класс для body
      if (isExpanded.value) {
        document.body.classList.add('ai-panel-expanded')
      } else {
        document.body.classList.remove('ai-panel-expanded')
      }
    }

    const onStyleChange = () => {
      if (suggestions.value.length > 0) {
        generateSuggestions()
      }
    }
    
    // Lifecycle hooks
    onMounted(() => {
      // Устанавливаем начальное состояние класса
      if (isExpanded.value) {
        document.body.classList.add('ai-panel-expanded')
      }
    })
    
    onUnmounted(() => {
      // Очищаем класс при размонтировании
      document.body.classList.remove('ai-panel-expanded')
      abortController.value?.abort()
    })

    return {
      suggestions,
      isLoading,
      error,
      suggestionStyle,
      submitPrompt,
      applySuggestion,
      regenerateSuggestion,
      retry,
      togglePanel,
      onStyleChange,
      isExpanded,
      userPrompt,
      scoreColor,
      clearAll
    }
  }
}
</script>

<style scoped>
.ai-suggestions-panel {
  position: fixed;
  top: 0;
  left: 0px; /* Прикрепляем к левому краю */
  width: 320px;
  height: 100vh;
  background: var(--color-surface); /* Монохромный фон */
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow-md); /* Приглушенная тень */
  z-index: 100;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  transform: translateX(0);
  max-width: calc(100vw - 4rem);
}

.ai-suggestions-panel.collapsed {
  transform: translateX(-280px);
}

/* Адаптивность для AI панели */
@media (max-width: 768px) {
  .ai-suggestions-panel {
    width: 280px;
    left: 1rem;
    max-width: calc(100vw - 2rem);
  }
  
  .ai-suggestions-panel.collapsed {
    transform: translateX(-250px);
  }
}

@media (max-width: 480px) {
  .ai-suggestions-panel {
    width: 260px;
    left: 0.5rem;
    max-width: calc(100vw - 1rem);
    top: 0;
    height: 100vh;
  }
  
  .ai-suggestions-panel.collapsed {
    transform: translateX(-230px);
  }
}

.suggestions-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.suggestions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border); /* Монохромная граница */
  background: var(--color-gray-50); /* Светлый фон */
  margin-top: 30px; /* Выравниваем с navbar */
}

.suggestions-header h3 {
  margin: auto;
  font-size: 17px;
  font-weight: 700;
  font-style: normal;
  color: var(--color-primary); /* Основной цвет текста */
}

.toggle-btn {
  background: none;
  border: none;
  color: var(--color-secondary); /* Монохромный цвет иконки */
  cursor: pointer;
  padding: 4px;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.toggle-btn:hover {
  background: var(--color-gray-100); /* Светлый фон при наведении */
  color: var(--color-primary); /* Основной цвет текста при наведении */
}

.suggestions-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}

.prompt-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.prompt-textarea {
  width: 100%;
  min-height: 80px;
  resize: vertical;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-white);
  color: var(--color-primary);
  font-size: 14px;
}

.prompt-actions {
  display: flex;
  justify-content: flex-end;
}

.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 0;
  color: #6c757d;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e9ecef;
  border-top: 2px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-item {
  border: 1px solid var(--color-border); /* Монохромная граница */
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: var(--color-white); /* Светлый фон элемента */
}

.suggestion-item:hover {
  border-color: var(--color-gray-400); /* Затемненная граница при наведении */
  box-shadow: var(--shadow-sm); /* Приглушенная тень при наведении */
}

.suggestion-text {
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-primary); /* Основной цвет текста */
  margin-bottom: 8px;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.score-bar {
  flex: 1;
  height: 6px;
  background: var(--color-gray-100);
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  width: 0%;
  background: var(--color-gray-500);
  transition: width 0.3s ease;
}

.score-label {
  font-size: 12px;
  font-weight: 600;
}

.suggestion-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.apply-btn, .regenerate-btn {
  padding: 4px 12px;
  border: 1px solid var(--color-border); /* Монохромная граница */
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.apply-btn {
  background: var(--color-gray-900);
  color: var(--color-white);
  border-color: var(--color-gray-900);
}

.apply-btn:hover {
  background: var(--color-black);
  border-color: var(--color-black);
}

.regenerate-btn {
  background: var(--color-white); /* Белый фон */
  color: var(--color-secondary); /* Серый текст */
}

.regenerate-btn:hover {
  background: var(--color-gray-100); /* Светлый фон при наведении */
  color: var(--color-gray-900); /* Монохромный темный */
}

.empty-state, .error-state {
  text-align: center;
  padding: 30px 0;
  color: var(--color-gray-50);
}

.retry-btn {
  margin-top: 12px;
  padding: 8px 16px;
  background: var(--color-gray-900);
  color: var(--color-white);
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.retry-btn:hover {
  background: var(--color-black);
}

.suggestions-footer {
  padding: 16px 20px;
  border-top: 1px solid var(--color-border); /* Монохромная граница */
  background: var(--color-gray-50); /* Светлый фон */
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestions-footer select {
  background: var(--color-white);
  color: var(--color-primary);
  border: 1px solid var(--color-border);
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 12px;
}

.footer-actions { display: flex; gap: 8px; }
.clear-btn {
  padding: 6px 10px;
  background: var(--color-white);
  color: var(--color-secondary);
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
}
.clear-btn:hover { background: var(--color-gray-100); color: var(--color-gray-900); }

.generate-btn {
  padding: 8px 16px;
  background: var(--color-gray-800); /* Темно-серый фон */
  color: var(--color-white); /* Белый текст */
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
  font-size: 14px;
}

.generate-btn:hover:not(:disabled) {
  background: var(--color-black); /* Еще темнее при наведении */
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.settings select {
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  font-size: 12px;
  background: var(--color-white);
  color: var(--color-primary);
}

/* Темная тема для AI панели */
:global(.dark-mode) .ai-suggestions-panel {
  background: #252526;
  border-color: #3e3e42;
}

:global(.dark-mode) .suggestions-header {
  background: #2d2d30;
  border-color: #3e3e42;
}

:global(.dark-mode) .suggestions-header h3 {
  color: #e8e8ed;
}

:global(.dark-mode) .toggle-btn {
  color: #b8b8bd;
}

:global(.dark-mode) .toggle-btn:hover {
  background: #3e3e42;
  color: #e8e8ed;
}

:global(.dark-mode) .prompt-textarea {
  background: #1e1e1e;
  color: #cccccc;
  border-color: #3e3e42;
}

:global(.dark-mode) .prompt-textarea:focus {
  border-color: #007acc;
}

:global(.dark-mode) .generate-btn {
  background: #007acc;
  color: #ffffff;
}

:global(.dark-mode) .generate-btn:hover:not(:disabled) {
  background: #005a9e;
}

:global(.dark-mode) .suggestion-item {
  background: #1e1e1e;
  border-color: #3e3e42;
  color: #cccccc;
}

:global(.dark-mode) .suggestion-item:hover {
  border-color: #007acc;
}

:global(.dark-mode) .apply-btn {
  background: #007acc;
  color: #ffffff;
  border-color: #007acc;
}

:global(.dark-mode) .apply-btn:hover {
  background: #005a9e;
  border-color: #005a9e;
}

:global(.dark-mode) .regenerate-btn {
  background: #2d2d30;
  color: #b8b8bd;
  border-color: #3e3e42;
}

:global(.dark-mode) .regenerate-btn:hover {
  background: #3e3e42;
  color: #e8e8ed;
}

:global(.dark-mode) .suggestions-footer {
  background: #2d2d30;
  border-color: #3e3e42;
}

:global(.dark-mode) .settings select,
:global(.dark-mode) .suggestions-footer .settings select,
:global(.dark-mode) .suggestions-footer select {
  background: #1e1e1e !important;
  color: #cccccc !important;
  border-color: #3e3e42 !important;
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

:global(.dark-mode) .settings select option,
:global(.dark-mode) .suggestions-footer .settings select option,
:global(.dark-mode) .suggestions-footer select option {
  background: #1e1e1e !important;
  color: #cccccc !important;
}

:global(.dark-mode) .clear-btn {
  background: #2d2d30;
  color: #b8b8bd;
  border-color: #3e3e42;
}

:global(.dark-mode) .clear-btn:hover {
  background: #3e3e42;
  color: #e8e8ed;
}

:global(.dark-mode) .settings select {
  background: #1e1e1e;
  color: #cccccc;
  border-color: #3e3e42;
}

:global(.dark-mode) .settings select option {
  background: #1e1e1e;
  color: #cccccc;
}
</style>