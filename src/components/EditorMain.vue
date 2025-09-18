<template>
  <main class="editor-main">
    <div class="editor-container">
      <div class="editor-wrapper" :class="{ 'editor-loading': isLoading }">
        <!-- Контейнер для textarea и inline подсказки -->
        <div class="editor-content-wrapper">
          <!-- Textarea с оптимизациями -->
          <textarea 
            ref="textareaRef"
            :value="currentChapter.content"
            @input="handleInput"
            @keydown="handleKeydown"
            @scroll="handleScroll"
            @focus="handleFocus"
            @blur="handleBlur"
            class="text-editor"
            :class="{
              'editor-focused': isFocused,
              'editor-zen-mode': zenMode
            }"
            placeholder="Начните писать вашу историю..."
            spellcheck="false"
            autocomplete="off"
            autocorrect="off"
            autocapitalize="off"
            :disabled="isLoading"
          ></textarea>
          
          <!-- Inline подсказка (как в Cursor) -->
          <div 
            v-if="inlineSuggestion && showInlineSuggestion" 
            class="inline-suggestion"
            :style="inlineSuggestionStyle"
          >
            <span class="suggestion-text">{{ inlineSuggestion }}</span>
            <span class="suggestion-hint">Tab</span>
          </div>
        </div>
        
        <!-- Индикатор загрузки -->
        <div v-if="isLoading" class="loading-overlay">
          <div class="loading-spinner"></div>
          <span class="loading-text">Загрузка...</span>
        </div>
        
        <!-- Вертикальная панель инструментов справа -->
        <Transition name="toolbar">
          <div v-if="showToolbar" class="vertical-toolbar">
            <div class="toolbar-header">
              <h4>Инструменты</h4>
            </div>
            
            <div class="toolbar-buttons">
              <button 
                @click="toggleZenMode"
                class="toolbar-btn"
                :class="{ 'toolbar-btn-active': zenMode }"
                title="Дзен режим (F11)"
              >
                <span class="btn-label">{{ zenMode ? 'Выйти из дзена' : 'Дзен режим' }}</span>
              </button>
              
              <button 
                @click="toggleDarkMode"
                class="toolbar-btn"
                :class="{ 'toolbar-btn-active': darkMode }"
                title="Темная тема"
              >
                <span class="btn-label">{{ darkMode ? 'Светлая тема' : 'Темная тема' }}</span>
              </button>
              
              <div class="font-size-controls">
                <label class="control-label">Размер шрифта</label>
                <div class="size-controls">
                  <button @click="decreaseFontSize" class="size-btn" title="Уменьшить">-</button>
                  <span class="font-size-display">{{ fontSize }}px</span>
                  <button @click="increaseFontSize" class="size-btn" title="Увеличить">+</button>
                </div>
              </div>
            </div>
            
            <div class="toolbar-info">
              <div class="info-item">
                <span class="info-label">Строка</span>
                <span class="info-value">{{ currentLine }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Символов</span>
                <span class="info-value">{{ characterCount }}</span>
              </div>
            </div>
          </div>
        </Transition>
        
        <!-- Панель поиска -->
        <Transition name="search">
          <div v-if="showSearch" class="search-panel">
            <div class="search-input-group">
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                @keydown.enter="findNext"
                @keydown.escape="closeSearch"
                class="search-input"
                placeholder="Поиск в тексте..."
                type="text"
              />
              <button @click="findPrevious" class="search-btn" title="Предыдущий">
                <ChevronUpIcon />
              </button>
              <button @click="findNext" class="search-btn" title="Следующий">
                <ChevronDownIcon />
              </button>
              <button @click="closeSearch" class="search-btn search-close" title="Закрыть">
                <XIcon />
              </button>
            </div>
            <div v-if="searchResults.length > 0" class="search-results">
              {{ searchResults.currentIndex + 1 }} из {{ searchResults.total }}
            </div>
          </div>
        </Transition>
      </div>
    </div>
  </main>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { apiClient } from '../services/api.js'

// Простые и понятные иконки
const EyeIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 9a3 3 0 100 6 3 3 0 000-6zm0 8a5 5 0 01-5-5c0-1.5.7-2.9 1.8-3.8C10.3 7.3 11.1 7 12 7s1.7.3 3.2 1.2A5 5 0 0117 12a5 5 0 01-5 5zm0-10C7 7 3 10 1 12c2 2 6 5 11 5s9-3 11-5c-2-2-6-5-11-5z"/></svg>' }
const EyeOffIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8M12 5c7 0 11 7 11 7a13.2 13.2 0 01-1.7 2.7M6.6 6.6A13.2 13.2 0 001 12s4 7 11 7c1.5 0 3-.3 4.4-.9"/></svg>' }
const WrapTextIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M4 7h16M4 12h12a2 2 0 012 2v0a2 2 0 01-2 2h-3m0 0l-2-2m2 2l2 2M4 17h7"/></svg>' }
const ZoomInIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><path d="M12 18v-6m-3 3h6"/></svg>' }
const ZoomOutIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6z"/><path d="M9 15h6"/></svg>' }
const ChevronUpIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 15l-6-6-6 6"/></svg>' }
const ChevronDownIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 9l6 6 6-6"/></svg>' }
const XIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M18 6L6 18M6 6l12 12"/></svg>' }

export default {
  name: 'EditorMain',
  components: {
    EyeIcon,
    EyeOffIcon,
    WrapTextIcon,
    ZoomInIcon,
    ZoomOutIcon,
    ChevronUpIcon,
    ChevronDownIcon,
    XIcon
  },
  props: {
    currentChapter: {
      type: Object,
      required: true
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['content-change', 'keydown'],
  setup(props, { emit }) {
    // Refs
    const textareaRef = ref(null)
    const searchInputRef = ref(null)
    
    // Состояние
    const isFocused = ref(false)
    const zenMode = ref(false)
    const fontSize = ref(16)
    const showToolbar = ref(true)
    const showSearch = ref(false)
    const darkMode = ref(false)
    const searchQuery = ref('')
    const searchResults = ref({
      total: 0,
      currentIndex: -1,
      positions: []
    })
    const currentLine = ref(1)
    const currentColumn = ref(1)
    
    // Состояние для inline подсказок
    const inlineSuggestion = ref('')
    const showInlineSuggestion = ref(false)
    const inlineSuggestionStyle = ref({})
    const suggestionTimeout = ref(null)
    const isGeneratingSuggestion = ref(false)
    
    // Вычисляемые свойства
    const characterCount = computed(() => {
      return props.currentChapter.content.length
    })
    
    // Дебаунсинг для производительности
    let inputTimeout = null
    const debouncedEmitChange = (content) => {
      clearTimeout(inputTimeout)
      inputTimeout = setTimeout(() => {
        emit('content-change', content)
      }, 100)
    }
    
    // Функции для inline подсказок
    const generateInlineSuggestion = async () => {
      if (isGeneratingSuggestion.value) return
      
      const textarea = textareaRef.value
      if (!textarea) return
      
      const content = textarea.value
      const cursorPos = textarea.selectionStart
      
      // Берем последние 200 символов до курсора как контекст
      const contextStart = Math.max(0, cursorPos - 200)
      const context = content.substring(contextStart, cursorPos)
      
      // Не генерируем, если курсор в середине слова
      const textAfterCursor = content.substring(cursorPos, cursorPos + 1)
      if (textAfterCursor && textAfterCursor.match(/[a-zA-Zа-яА-Я]/)) return
      
      isGeneratingSuggestion.value = true
      
      try {
        const response = await apiClient.request('/ai/inline-suggestion', {
          method: 'POST',
          body: JSON.stringify({
            context: context,
            suggestion_type: 'continuation',
            max_length: 50,
            chapter_id: props.currentChapter.id || null
          })
        })
        
        if (response.content && response.content.trim()) {
          // Легкая очистка для "ghost text": убираем начальные переводы строк/пробелы
          let ghost = String(response.content)
            .replace(/^\s+/g, '')
            .replace(/^\n+/g, '')
            .replace(/^[«"'–—\-\s]+/, '')

          // Убираем перекрытие по словам с уже введенным текстом
          const tail = (context || '').slice(-100)
          const maxOverlap = Math.min(50, ghost.length, tail.length)
          let overlap = 0
          const lt = tail.toLowerCase()
          const ls = ghost.toLowerCase()
          for (let k = maxOverlap; k > 0; k--) {
            if (lt.endsWith(ls.slice(0, k))) { overlap = k; break }
          }
          if (overlap) ghost = ghost.slice(overlap).replace(/^\s+/, '')
          // Показываем только первое слово подсказки серым (эффект "ghost")
          inlineSuggestion.value = getFirstWord(ghost)
          showInlineSuggestion.value = true
          // Обновляем позицию после установки текста подсказки
          nextTick(() => {
            updateInlineSuggestionPosition()
          })
        }
      } catch (error) {
        console.error('Failed to generate suggestion:', error)
      } finally {
        isGeneratingSuggestion.value = false
      }
    }
    
    // Извлекает подходящую часть подсказки для отображения
    const getFirstWord = (text) => {
      if (!text) return ''
      const cleaned = String(text).replace(/^\s+/, '')
      
      // Для коротких текстов показываем всё
      if (cleaned.length <= 20) {
        return cleaned
      }
      
      // Для длинных текстов ищем первое подходящее слово
      const match = cleaned.match(/^([A-Za-zА-Яа-яЁё0-9\-]+)(?:\s|$)/)
      if (match && match[1]) {
        const word = match[1]
        // Если слово очень длинное, обрезаем до разумной длины
        if (word.length > 15) {
          return word.slice(0, 15) + '…'
        }
        return word + ' '
      }
      
      // Fallback: берем до первого пробела или обрезаем
      const idx = cleaned.indexOf(' ')
      const result = idx === -1 ? cleaned : cleaned.slice(0, idx + 1)
      return result.length > 20 ? result.slice(0, 17) + '…' : result
    }
    
    const updateInlineSuggestionPosition = () => {
      const textarea = textareaRef.value
      if (!textarea) return
      
      // Получаем позицию курсора
      const cursorPos = textarea.selectionStart
      const textBeforeCursor = textarea.value.substring(0, cursorPos)
      const lines = textBeforeCursor.split('\n')
      const currentLineText = lines[lines.length - 1]

      // Вычисляем позицию для отображения подсказки с учетом отступов и прокрутки
      const cs = window.getComputedStyle(textarea)
      const lineHeight = parseFloat(cs.lineHeight)
      const paddingLeft = parseFloat(cs.paddingLeft)
      const paddingTop = parseFloat(cs.paddingTop)
      const font = `${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`
      const measureCanvas = document.createElement('canvas')
      const ctx = measureCanvas.getContext('2d')
      ctx.font = font
      
      // Измеряем ширину текста до курсора
      const textWidth = ctx.measureText(currentLineText).width
      
      // Вычисляем доступную ширину для подсказки на текущей строке
      const availableWidth = textarea.clientWidth - paddingLeft * 2 - textWidth - 8
      const suggestionWidth = inlineSuggestion.value ? ctx.measureText(inlineSuggestion.value).width : 0
      
      // Если подсказка не помещается на текущей строке, переносим на следующую
      let suggestionTop = paddingTop + (lines.length - 1) * lineHeight - textarea.scrollTop
      let suggestionLeft = paddingLeft + textWidth - textarea.scrollLeft
      let maxWidth = availableWidth
      
      if (suggestionWidth > availableWidth && availableWidth < 100) {
        // Переносим подсказку на следующую строку
        suggestionTop += lineHeight
        suggestionLeft = paddingLeft - textarea.scrollLeft
        maxWidth = textarea.clientWidth - paddingLeft * 2 - 8
      }

      inlineSuggestionStyle.value = {
        top: `${suggestionTop}px`,
        left: `${suggestionLeft}px`,
        maxWidth: `${Math.max(maxWidth, 150)}px` // минимальная ширина 150px
      }
    }
    
    const acceptInlineSuggestion = () => {
      if (!showInlineSuggestion.value || !inlineSuggestion.value) return
      
      const textarea = textareaRef.value
      if (!textarea) return
      
      const cursorPos = textarea.selectionStart
      const newContent = 
        textarea.value.substring(0, cursorPos) + 
        inlineSuggestion.value + 
        textarea.value.substring(cursorPos)
      
      // Обновляем содержимое
      textarea.value = newContent
      
      // Перемещаем курсор в конец вставленного текста
      const newCursorPos = cursorPos + inlineSuggestion.value.length
      textarea.setSelectionRange(newCursorPos, newCursorPos)
      
      // Очищаем подсказку
      inlineSuggestion.value = ''
      showInlineSuggestion.value = false
      
      // Эмитим изменение
      emit('content-change', newContent)
    }
    
    const dismissInlineSuggestion = () => {
      inlineSuggestion.value = ''
      showInlineSuggestion.value = false
    }
    
    // Обработчики событий
    const handleInput = (event) => {
      const content = event.target.value
      debouncedEmitChange(content)
      updateCursorPosition()
      
      // Скрываем подсказку при вводе
      dismissInlineSuggestion()
      
      // Планируем генерацию новой подсказки
      clearTimeout(suggestionTimeout.value)
      suggestionTimeout.value = setTimeout(() => {
        generateInlineSuggestion()
      }, 500) // Быстрее для эффекта как в Cursor

      // Автоматически растягиваем textarea по контенту
      autoResizeTextarea()
    }
    
    const handleKeydown = (event) => {
      // Обработка Tab для принятия подсказки
      if (event.key === 'Tab' && showInlineSuggestion.value) {
        event.preventDefault()
        acceptInlineSuggestion()
        return
      }
      
      // Пропускаем событие наверх
      emit('keydown', event)
      
      // Локальные горячие клавиши
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 'f':
            event.preventDefault()
            toggleSearch()
            break
          case '=':
          case '+':
            event.preventDefault()
            increaseFontSize()
            break
          case '-':
            event.preventDefault()
            decreaseFontSize()
            break
        }
      }
      
      if (event.key === 'F11') {
        event.preventDefault()
        toggleZenMode()
      }
      
      if (event.key === 'Escape') {
        if (showSearch.value) {
          closeSearch()
        } else if (zenMode.value) {
          toggleZenMode()
        }
      }
      
      // Обновляем позицию курсора при навигации
      if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Home', 'End', 'PageUp', 'PageDown'].includes(event.key)) {
        nextTick(updateCursorPosition)
      }
    }
    
    const handleScroll = () => {
      if (showInlineSuggestion.value) updateInlineSuggestionPosition()
    }
    
    const handleFocus = () => {
      isFocused.value = true
      updateCursorPosition()
      autoResizeTextarea()
    }
    
    const handleBlur = () => {
      isFocused.value = false
    }
    
    // Методы редактора
    const focus = () => {
      nextTick(() => {
        if (textareaRef.value) {
          textareaRef.value.focus()
          autoResizeTextarea()
        }
      })
    }

    // Авто‑рост textarea под контент (без внутреннего скролла)
    const autoResizeTextarea = () => {
      const el = textareaRef.value
      if (!el) return
      el.style.height = 'auto'
      el.style.overflow = 'hidden'
      el.style.height = `${el.scrollHeight}px`
    }
    
    const toggleZenMode = () => {
      zenMode.value = !zenMode.value
      if (zenMode.value) {
        document.documentElement.classList.add('zen-mode')
      } else {
        document.documentElement.classList.remove('zen-mode')
      }
    }
    



    
    const increaseFontSize = () => {
      if (fontSize.value < 24) {
        fontSize.value += 2
        updateFontSize()
      }
    }
    
    const decreaseFontSize = () => {
      if (fontSize.value > 12) {
        fontSize.value -= 2
        updateFontSize()
      }
    }
    
    const updateFontSize = () => {
      if (textareaRef.value) {
        textareaRef.value.style.fontSize = `${fontSize.value}px`
      }
    }
    
    const updateCursorPosition = () => {
      if (!textareaRef.value) return
      
      const textarea = textareaRef.value
      const cursorPos = textarea.selectionStart
      const textBeforeCursor = textarea.value.substring(0, cursorPos)
      const lines = textBeforeCursor.split('\n')
      
      currentLine.value = lines.length
      currentColumn.value = lines[lines.length - 1].length + 1
    }
    
    // Поиск
    const toggleSearch = () => {
      showSearch.value = !showSearch.value
      if (showSearch.value) {
        nextTick(() => {
          if (searchInputRef.value) {
            searchInputRef.value.focus()
          }
        })
      } else {
        clearSearchHighlights()
      }
    }
    
    const closeSearch = () => {
      showSearch.value = false
      searchQuery.value = ''
      clearSearchHighlights()
    }
    
    const performSearch = () => {
      if (!searchQuery.value.trim() || !textareaRef.value) {
        searchResults.value = { total: 0, currentIndex: -1, positions: [] }
        return
      }
      
      const content = props.currentChapter.content
      const query = searchQuery.value.toLowerCase()
      const positions = []
      
      let index = content.toLowerCase().indexOf(query)
      while (index !== -1) {
        positions.push({
          start: index,
          end: index + query.length
        })
        index = content.toLowerCase().indexOf(query, index + 1)
      }
      
      searchResults.value = {
        total: positions.length,
        currentIndex: positions.length > 0 ? 0 : -1,
        positions
      }
      
      if (positions.length > 0) {
        highlightSearchResult(0)
      }
    }
    
    const findNext = () => {
      if (searchResults.value.total === 0) return
      
      const nextIndex = (searchResults.value.currentIndex + 1) % searchResults.value.total
      searchResults.value.currentIndex = nextIndex
      highlightSearchResult(nextIndex)
    }
    
    const findPrevious = () => {
      if (searchResults.value.total === 0) return
      
      const prevIndex = searchResults.value.currentIndex === 0 
        ? searchResults.value.total - 1 
        : searchResults.value.currentIndex - 1
      searchResults.value.currentIndex = prevIndex
      highlightSearchResult(prevIndex)
    }
    
    const highlightSearchResult = (index) => {
      if (!textareaRef.value || !searchResults.value.positions[index]) return
      
      const position = searchResults.value.positions[index]
      textareaRef.value.setSelectionRange(position.start, position.end)
      textareaRef.value.focus()
    }
    
    const clearSearchHighlights = () => {
      if (textareaRef.value) {
        textareaRef.value.setSelectionRange(
          textareaRef.value.selectionStart,
          textareaRef.value.selectionStart
        )
      }
    }
    
    // Функция темной темы
    const toggleDarkMode = () => {
      darkMode.value = !darkMode.value
      if (darkMode.value) {
        document.documentElement.classList.add('dark-mode')
      } else {
        document.documentElement.classList.remove('dark-mode')
      }
    }
    
    // Наблюдатели
    watch(searchQuery, performSearch)
    
    watch(() => props.currentChapter.content, () => {
      if (showSearch.value) {
        performSearch()
      }
    })
    
    // Жизненный цикл
    onMounted(() => {
      focus()
      updateFontSize()
      autoResizeTextarea()
      window.addEventListener('resize', autoResizeTextarea)

      
      // Загружаем настройки из localStorage
      const savedSettings = localStorage.getItem('novelsia_editor_settings')
      if (savedSettings) {
        try {
          const settings = JSON.parse(savedSettings)
          zenMode.value = settings.zenMode || false
          fontSize.value = settings.fontSize || 16
          
          if (zenMode.value) {
            document.documentElement.classList.add('zen-mode')
          }
          updateFontSize()
        } catch (e) {
          console.warn('Не удалось загрузить настройки редактора')
        }
      }

    })
    
    onUnmounted(() => {
      // Сохраняем настройки
      const settings = {
        zenMode: zenMode.value,
        fontSize: fontSize.value
      }
      localStorage.setItem('novelsia_editor_settings', JSON.stringify(settings))
      
      // Очищаем таймауты
      clearTimeout(inputTimeout)
      clearTimeout(suggestionTimeout.value)
      
      // Убираем zen-mode класс
      document.documentElement.classList.remove('zen-mode')

      window.removeEventListener('resize', autoResizeTextarea)
    })
    
    // Expose методы для родительского компонента
    return {
      textareaRef,
      searchInputRef,
      isFocused,
      zenMode,
      fontSize,
      darkMode,
      showToolbar,
      showSearch,
      searchQuery,
      searchResults,
      currentLine,
      currentColumn,
      characterCount,
      inlineSuggestion,
      showInlineSuggestion,
      inlineSuggestionStyle,
      handleInput,
      handleKeydown,
      handleScroll,
      handleFocus,
      handleBlur,
      focus,
      toggleZenMode,
      toggleDarkMode,
      increaseFontSize,
      decreaseFontSize,
      toggleSearch,
      closeSearch,
      findNext,
      findPrevious
    }
  }
}
</script>

<style scoped>
.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
  margin-left: 40px; /* Отступ для свернутой AI панели */
  transition: margin-left 0.3s ease;
}

/* Адаптация когда AI панель развернута */
:global(.ai-panel-expanded) .editor-main {
  margin-left: 320px;
}

.editor-container {
  flex: 1;
  display: flex;
  justify-content: center;
  padding: 2rem;
  padding-top: calc(2rem + 25px); /* Добавляем 25px сверху для смещения вниз */
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.editor-wrapper {
  width: 100%;
  max-width: 800px;
  height: 100%;
  position: relative;
  transition: var(--transition);
}

.editor-loading {
  pointer-events: none;
  opacity: 0.7;
}

.text-editor {
  width: 100%;
  min-height: 60vh;
  border: none;
  outline: none;
  font-family: var(--font-content);
  font-size: 1.125rem;
  line-height: 1.8;
  padding: 2rem;
  background: var(--color-white);
  color: var(--color-primary);
  resize: none;
  border-radius: var(--border-radius-lg);
  border: 1px solid transparent;
  transition: var(--transition);
  box-shadow: var(--shadow-sm);
  white-space: pre-wrap;
  word-break: break-word;
  user-select: none;
/*  overflow: hidden; */ /* без внутреннего скролла */
}

.text-editor:focus {
  border-color: var(--color-border);
  box-shadow: var(--shadow-md);
}

.text-editor::placeholder {
  color: var(--color-gray-400);
  font-style: italic;
}

.editor-focused {
  box-shadow: var(--shadow-lg);
}

.editor-zen-mode {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  max-width: none !important;
  border-radius: 0 !important;
  z-index: 999 !important;
  padding: 4rem !important;
}

/* Загрузочный оверлей */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  border-radius: var(--border-radius-lg);
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--color-gray-200);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: var(--color-secondary);
  font-size: 0.875rem;
}

/* Вертикальная панель инструментов справа */
.vertical-toolbar {
  position: absolute;
  top: 2rem;
  right: -220px;
  width: 200px;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  z-index: 10;
  overflow: hidden;
}

.toolbar-header {
  padding: 1rem;
  background: var(--color-gray-50);
  border-bottom: 1px solid var(--color-border);
}

.toolbar-header h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-primary);
  text-align: center;
}

.toolbar-buttons {
  padding: 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem;
  background: transparent;
  border: 1px solid transparent;
  border-radius: var(--border-radius);
  color: var(--color-secondary);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
  font-size: 0.875rem;
}

.toolbar-btn:hover {
  background: var(--color-gray-50);
  color: var(--color-primary);
  border-color: var(--color-border);
}

.toolbar-btn-active {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
}

.btn-label {
  font-size: 0.875rem;
  font-weight: 500;
}

.toolbar-info {
  padding: 1rem;
  border-top: 1px solid var(--color-border);
  background: var(--color-gray-50);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-label {
  font-size: 0.75rem;
  color: var(--color-secondary);
  font-weight: 500;
}

.info-value {
  font-size: 0.75rem;
  color: var(--color-primary);
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

/* Элементы управления */
.font-size-controls {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background: var(--color-gray-50);
  margin: 0;
}

.control-label {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-secondary);
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.size-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: space-between;
}

.size-btn {
  width: 2rem;
  height: 2rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background: var(--color-white);
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
}

.size-btn:hover {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
}

.font-size-display {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-primary);
  min-width: 3rem;
  text-align: center;
}

/* Улучшенная темная тема */
:global(.dark-mode) {
  --color-white: #1e1e1e;
  --color-gray-50: #2d2d30;
  --color-gray-100: #3e3e42;
  --color-gray-200: #4a4a4f;
  --color-gray-300: #5a5a5f;
  --color-gray-400: #6f6f74;
  --color-gray-500: #8a8a8f;
  --color-gray-600: #a0a0a5;
  --color-gray-700: #b8b8bd;
  --color-gray-800: #d0d0d5;
  --color-gray-900: #e8e8ed;
  --color-primary: #e8e8ed;
  --color-secondary: #b8b8bd;
  --color-border: #3e3e42;
  --color-surface: #252526;
  --color-black: #ffffff;
}

:global(.dark-mode) .text-editor {
  background: #1e1e1e;
  color: #cccccc;
  border-color: #3e3e42;
}

:global(.dark-mode) .text-editor:focus {
  border-color: #007acc;
  box-shadow: 0 0 0 2px rgba(0, 122, 204, 0.2);
}

:global(.dark-mode) .text-editor::placeholder {
  color: #6f6f74;
}

:global(.dark-mode) .vertical-toolbar {
  background: #252526;
  border-color: #3e3e42;
}

:global(.dark-mode) .toolbar-header {
  background: #2d2d30;
  border-color: #3e3e42;
}

:global(.dark-mode) .toolbar-btn {
  color: #b8b8bd;
  border-color: transparent;
}

:global(.dark-mode) .toolbar-btn:hover {
  background: #3e3e42;
  color: #e8e8ed;
  border-color: #007acc;
}

:global(.dark-mode) .toolbar-btn-active {
  background: #007acc;
  color: #ffffff;
  border-color: #007acc;
}

:global(.dark-mode) .font-size-controls {
  background: #2d2d30;
  border-color: #3e3e42;
}

:global(.dark-mode) .size-btn {
  background: #1e1e1e;
  border-color: #3e3e42;
  color: #b8b8bd;
}

:global(.dark-mode) .size-btn:hover {
  background: #007acc;
  color: #ffffff;
  border-color: #007acc;
}

:global(.dark-mode) .toolbar-info {
  background: #2d2d30;
  border-color: #3e3e42;
}

:global(.dark-mode) .info-label {
  color: #8a8a8f;
}

:global(.dark-mode) .info-value {
  color: #e8e8ed;
}

/* Панель поиска */
.search-panel {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  padding: 0.75rem;
  z-index: 10;
  min-width: 300px;
}

.search-input-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.search-input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  padding: 0.5rem;
  font-size: 0.875rem;
  background: var(--color-white);
  color: var(--color-primary);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.search-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  color: var(--color-secondary);
  cursor: pointer;
  transition: var(--transition);
}

.search-btn:hover {
  background: var(--color-gray-50);
  color: var(--color-primary);
}

.search-close:hover {
  background: var(--color-gray-900);
  color: var(--color-white);
}

.search-results {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: var(--color-secondary);
  text-align: center;
}

/* Inline подсказки (как в Cursor) */
.editor-content-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.inline-suggestion {
  position: absolute;
  pointer-events: none;
  z-index: 5;
  color: rgba(139, 148, 158, 0.7);
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  white-space: nowrap; /* не переносим внутри элемента, перенос обрабатываем через позиционирование */
  overflow: hidden;
  text-overflow: ellipsis;
  hyphens: none;
  transition: opacity 0.2s ease;
}

.suggestion-text {
  opacity: 0.7;
  display: inline-block;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-hint {
  display: inline-block;
  margin-left: 8px;
  padding: 2px 6px;
  background: rgba(139, 148, 158, 0.2);
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.5px;
  vertical-align: middle;
}

/* Анимации */
.toolbar-enter-active,
.toolbar-leave-active {
  transition: all 0.3s ease;
}

.toolbar-enter-from,
.toolbar-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

.search-enter-active,
.search-leave-active {
  transition: all 0.3s ease;
}

.search-enter-from,
.search-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* Глобальные стили для zen-mode */
:global(.zen-mode) {
  overflow: hidden;
}

:global(.zen-mode .navbar),
:global(.zen-mode .sidebar) {
  display: none !important;
}

/* Адаптивность */
@media (max-width: 768px) {
  .editor-container {
    padding: 1rem;
  }
  
  .text-editor {
    padding: 1.5rem;
    font-size: 1rem;
  }
  
  .editor-zen-mode {
    padding: 2rem !important;
  }
  
  .vertical-toolbar {
    position: fixed;
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    top: auto;
    width: auto;
    max-height: 50vh;
    overflow-y: auto;
  }
  
  .toolbar-buttons {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
  }
  
  .btn-label {
    display: none;
  }
  
  .search-panel {
    position: fixed;
    top: 1rem;
    left: 1rem;
    right: 1rem;
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .text-editor {
    padding: 1rem;
    border-radius: var(--border-radius);
  }
  
  .toolbar-buttons {
    grid-template-columns: 1fr;
    gap: 0.25rem;
  }
  
  .toolbar-info {
    display: none;
  }
}
</style> 