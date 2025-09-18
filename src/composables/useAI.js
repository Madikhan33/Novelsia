/**
 * Композабл для работы с AI подсказками (Сюжетный помощник)
 * Предназначен для развития сюжета, персонажей, диалогов и творческих идей
 * Для инлайн подсказок (завершение текста) используйте useInlineAI
 */
import { ref, computed } from 'vue'
import { apiClient } from '../services/api.js'

export function useAI() {
  const isLoading = ref(false)
  const suggestions = ref([])
  const error = ref('')
  const showSuggestions = ref(false)
  const currentContext = ref('')
  
  // Настройки AI
  const aiSettings = ref({
    style: 'neutral',
    maxLength: 150,
    autoGenerate: true,
    contextLength: 300
  })

  // Дебаунс для автоматической генерации
  let debounceTimer = null
  const debounceDelay = 1500 // 1.5 секунды

  // Проверяем, достаточно ли контекста для генерации
  const hasEnoughContext = computed(() => {
    return currentContext.value && currentContext.value.length >= 30
  })

  // Автоматическая генерация подсказок (как в курсоре)
  const triggerAutoGeneration = (context, chapterId = null, novelId = null) => {
    if (!aiSettings.value.autoGenerate) return

    currentContext.value = context
    
    // Очищаем предыдущий таймер
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    // Устанавливаем новый таймер
    debounceTimer = setTimeout(() => {
      if (hasEnoughContext.value && !isLoading.value) {
        generateSuggestions(context, chapterId, novelId, true)
      }
    }, debounceDelay)
  }

  // Генерация подсказок
  const generateSuggestions = async (context, chapterId = null, novelId = null, isAuto = false) => {
    if (!context || context.length < 20) {
      if (!isAuto) {
        error.value = 'Недостаточно контекста для генерации подсказок'
      }
      return
    }

    isLoading.value = true
    error.value = ''
    
    try {
      // Берем нужную длину контекста
      const trimmedContext = context.slice(-aiSettings.value.contextLength)
      
      if (isAuto) {
        // Для автоматической генерации - один быстрый запрос
        const result = await apiClient.testGenerateAISuggestion({
          suggestion_type: 'continuation',
          context: trimmedContext,
          chapter_id: chapterId,
          novel_id: novelId,
          max_length: aiSettings.value.maxLength,
          style: aiSettings.value.style
        })

        if (result && result.content) {
          suggestions.value = [result.content]
          showSuggestions.value = true
        }
      } else {
        // Для ручной генерации - несколько вариантов
        await generateMultipleSuggestions(trimmedContext, chapterId, novelId)
      }
    } catch (err) {
      error.value = err.message || 'Ошибка при генерации подсказок'
      console.error('Error generating suggestions:', err)
    } finally {
      isLoading.value = false
    }
  }

  // Генерация нескольких вариантов подсказок с разными типами
  const generateMultipleSuggestions = async (context, chapterId = null, novelId = null) => {
    try {
      const promises = []
      
      // Разные типы сюжетных подсказок для творческого развития
      const suggestionTypes = [
        { type: 'plot_development', description: 'развитие сюжета' },
        { type: 'character_development', description: 'развитие персонажа' },
        { type: 'dialogue', description: 'диалог' },
        { type: 'scene_description', description: 'описание сцены' },
        { type: 'conflict', description: 'конфликт' },
        { type: 'emotion', description: 'эмоциональное развитие' },
        { type: 'world_building', description: 'создание мира' },
        { type: 'plot_twist', description: 'поворот сюжета' }
      ]
      
      // Выбираем 3 случайных типа для разнообразия
      const selectedTypes = suggestionTypes
        .sort(() => 0.5 - Math.random())
        .slice(0, 3)
      
      for (const { type } of selectedTypes) {
        promises.push(
          apiClient.testGenerateAISuggestion({
            suggestion_type: type,
            context: context,
            chapter_id: chapterId,
            novel_id: novelId,
            max_length: aiSettings.value.maxLength,
            style: aiSettings.value.style
          })
        )
      }

      const results = await Promise.allSettled(promises)
      const newSuggestions = results
        .filter(result => result.status === 'fulfilled' && result.value?.content)
        .map(result => result.value.content)
        .filter(content => content.length > 10)

      if (newSuggestions.length > 0) {
        suggestions.value = newSuggestions
        showSuggestions.value = true
      } else {
        error.value = 'Не удалось сгенерировать подсказки'
      }
    } catch (err) {
      error.value = 'Ошибка при генерации множественных подсказок'
      console.error('Error generating multiple suggestions:', err)
    }
  }

  // Применение подсказки
  const applySuggestion = (suggestion, callback) => {
    if (callback && typeof callback === 'function') {
      callback(suggestion)
    }
    hideSuggestions()
  }

  // Скрытие подсказок
  const hideSuggestions = () => {
    showSuggestions.value = false
    suggestions.value = []
    error.value = ''
  }

  // Показать подсказки вручную
  const showSuggestionsPanel = (context, chapterId = null, novelId = null) => {
    currentContext.value = context
    generateSuggestions(context, chapterId, novelId, false)
  }

  // Обновление настроек AI
  const updateAISettings = (newSettings) => {
    aiSettings.value = { ...aiSettings.value, ...newSettings }
    
    // Сохраняем настройки в localStorage
    localStorage.setItem('ai_settings', JSON.stringify(aiSettings.value))
  }

  // Загрузка настроек из localStorage
  const loadAISettings = () => {
    try {
      const saved = localStorage.getItem('ai_settings')
      if (saved) {
        aiSettings.value = { ...aiSettings.value, ...JSON.parse(saved) }
      }
    } catch (err) {
      console.warn('Could not load AI settings:', err)
    }
  }

  // Проверка здоровья AI сервиса
  const checkAIHealth = async () => {
    try {
      const health = await apiClient.request('/ai/health')
      console.log('AI Service Health:', health)
      return health
    } catch (err) {
      console.error('AI Health check failed:', err)
      return { status: 'error', error: err.message }
    }
  }

  // Инициализация
  loadAISettings()

  return {
    // Состояние
    isLoading,
    suggestions,
    error,
    showSuggestions,
    aiSettings,
    hasEnoughContext,
    
    // Методы
    triggerAutoGeneration,
    generateSuggestions,
    applySuggestion,
    hideSuggestions,
    showSuggestionsPanel,
    updateAISettings,
    checkAIHealth
  }
}