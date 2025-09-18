/**
 * Композабл для инлайн AI подсказок (мозг писателя)
 * Предназначен для завершения текста и предугадывания намерений писателя
 */
import { ref, computed } from 'vue'
import { apiClient } from '../services/api.js'

export function useInlineAI() {
  const isLoading = ref(false)
  const currentSuggestion = ref('')
  const error = ref('')
  const lastContext = ref('')
  
  // Настройки инлайн AI (более краткие и быстрые)
  const inlineSettings = ref({
    maxLength: 50, // Короче чем у сюжетного AI
    contextLength: 150, // Меньше контекста
    delay: 800, // Быстрее отклик
    minContextLength: 10 // Меньший минимум
  })

  let debounceTimer = null

  // Проверяем, достаточно ли контекста для генерации
  const hasEnoughContext = computed(() => {
    return lastContext.value && lastContext.value.length >= inlineSettings.value.minContextLength
  })

  // Автоматическая генерация инлайн подсказки
  const triggerInlineGeneration = (context, cursorPosition = null) => {
    if (!context || context === lastContext.value) return

    lastContext.value = context
    
    // Очищаем предыдущий таймер
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    // Если контекста недостаточно, очищаем подсказку
    if (context.length < inlineSettings.value.minContextLength) {
      currentSuggestion.value = ''
      error.value = ''
      return
    }

    // Устанавливаем новый таймер
    debounceTimer = setTimeout(() => {
      if (hasEnoughContext.value && !isLoading.value) {
        generateInlineSuggestion(context, cursorPosition)
      }
    }, inlineSettings.value.delay)
  }

  // Генерация инлайн подсказки
  const generateInlineSuggestion = async (context, cursorPosition = null) => {
    if (!context || context.length < inlineSettings.value.minContextLength) {
      currentSuggestion.value = ''
      return
    }

    isLoading.value = true
    error.value = ''
    
    try {
      // Берем нужную длину контекста (последние символы до курсора)
      const trimmedContext = cursorPosition 
        ? context.slice(Math.max(0, cursorPosition - inlineSettings.value.contextLength), cursorPosition)
        : context.slice(-inlineSettings.value.contextLength)
      
      const result = await apiClient.testGenerateAISuggestion({
        suggestion_type: 'text_completion', // Специальный тип для инлайн подсказок
        context: trimmedContext,
        max_length: inlineSettings.value.maxLength,
        style: 'continuation', // Всегда продолжение для инлайн
        inline_mode: true // Флаг для бэкенда что это инлайн режим
      })

      if (result && result.content) {
        currentSuggestion.value = result.content.trim()
      } else {
        currentSuggestion.value = ''
      }
    } catch (err) {
      error.value = err.message || 'Ошибка при генерации инлайн подсказки'
      currentSuggestion.value = ''
      console.error('Error generating inline suggestion:', err)
    } finally {
      isLoading.value = false
    }
  }

  // Принятие инлайн подсказки
  const acceptInlineSuggestion = () => {
    const suggestion = currentSuggestion.value
    currentSuggestion.value = ''
    error.value = ''
    return suggestion
  }

  // Отклонение инлайн подсказки
  const rejectInlineSuggestion = () => {
    currentSuggestion.value = ''
    error.value = ''
  }

  // Очистка подсказки
  const clearInlineSuggestion = () => {
    currentSuggestion.value = ''
    error.value = ''
    lastContext.value = ''
    if (debounceTimer) {
      clearTimeout(debounceTimer)
      debounceTimer = null
    }
  }

  // Обновление настроек
  const updateInlineSettings = (newSettings) => {
    inlineSettings.value = { ...inlineSettings.value, ...newSettings }
    
    // Сохраняем настройки в localStorage
    localStorage.setItem('inline_ai_settings', JSON.stringify(inlineSettings.value))
  }

  // Загрузка настроек из localStorage
  const loadInlineSettings = () => {
    try {
      const saved = localStorage.getItem('inline_ai_settings')
      if (saved) {
        inlineSettings.value = { ...inlineSettings.value, ...JSON.parse(saved) }
      }
    } catch (err) {
      console.warn('Could not load inline AI settings:', err)
    }
  }

  // Инициализация
  loadInlineSettings()

  return {
    // Состояние
    isLoading,
    currentSuggestion,
    error,
    inlineSettings,
    hasEnoughContext,
    
    // Методы
    triggerInlineGeneration,
    generateInlineSuggestion,
    acceptInlineSuggestion,
    rejectInlineSuggestion,
    clearInlineSuggestion,
    updateInlineSettings
  }
}