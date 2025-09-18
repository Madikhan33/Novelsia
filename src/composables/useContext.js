import { ref } from 'vue'
import { apiClient } from '../services/api.js'

export function useContext() {
  const characters = ref([])
  const worldInfo = ref({})
  const stylePreferences = ref({
    tone: 'neutral',
    pov: 'third_person',
    tense: 'past',
    genre: 'general'
  })
  const currentScene = ref('')
  
  // Добавить персонажа
  const addCharacter = async (name, description, traits = []) => {
    try {
      await apiClient.request('/context/character', {
        method: 'POST',
        body: JSON.stringify({ name, description, traits })
      })
      
      characters.value.push({ name, description, traits })
      return true
    } catch (error) {
      console.error('Failed to add character:', error)
      return false
    }
  }
  
  // Обновить информацию о мире
  const updateWorldInfo = async (key, value) => {
    try {
      await apiClient.request('/context/world-info', {
        method: 'POST',
        body: JSON.stringify({ [key]: value })
      })
      
      worldInfo.value[key] = value
      return true
    } catch (error) {
      console.error('Failed to update world info:', error)
      return false
    }
  }
  
  // Установить стилевые предпочтения
  const setStylePreferences = async (preferences) => {
    try {
      await apiClient.request('/context/style', {
        method: 'POST',
        body: JSON.stringify(preferences)
      })
      
      stylePreferences.value = { ...stylePreferences.value, ...preferences }
      return true
    } catch (error) {
      console.error('Failed to set style preferences:', error)
      return false
    }
  }
  
  // Установить текущую сцену
  const setCurrentScene = async (sceneDescription) => {
    try {
      await apiClient.request('/context/scene', {
        method: 'POST',
        body: JSON.stringify({ scene_description: sceneDescription })
      })
      
      currentScene.value = sceneDescription
      return true
    } catch (error) {
      console.error('Failed to set scene:', error)
      return false
    }
  }
  
  // Добавить краткое содержание главы
  const addChapterSummary = async (chapterId, summary) => {
    try {
      await apiClient.request('/context/chapter-summary', {
        method: 'POST',
        body: JSON.stringify({ chapter_id: chapterId, summary })
      })
      
      return true
    } catch (error) {
      console.error('Failed to add chapter summary:', error)
      return false
    }
  }
  
  // Экспортировать контекст
  const exportContext = async () => {
    try {
      const response = await apiClient.request('/context/export')
      return response.context
    } catch (error) {
      console.error('Failed to export context:', error)
      return null
    }
  }
  
  // Импортировать контекст
  const importContext = async (contextData) => {
    try {
      await apiClient.request('/context/import', {
        method: 'POST',
        body: JSON.stringify(contextData)
      })
      
      // Обновляем локальное состояние
      if (contextData.characters) {
        characters.value = Object.entries(contextData.characters).map(([name, data]) => ({
          name,
          ...data
        }))
      }
      
      if (contextData.world_info) {
        worldInfo.value = contextData.world_info
      }
      
      if (contextData.style_preferences) {
        stylePreferences.value = contextData.style_preferences
      }
      
      if (contextData.current_scene) {
        currentScene.value = contextData.current_scene
      }
      
      return true
    } catch (error) {
      console.error('Failed to import context:', error)
      return false
    }
  }
  
  // Очистить контекст
  const clearContext = async () => {
    try {
      await apiClient.request('/context/clear', {
        method: 'DELETE'
      })
      
      characters.value = []
      worldInfo.value = {}
      stylePreferences.value = {
        tone: 'neutral',
        pov: 'third_person',
        tense: 'past',
        genre: 'general'
      }
      currentScene.value = ''
      
      return true
    } catch (error) {
      console.error('Failed to clear context:', error)
      return false
    }
  }
  
  return {
    characters,
    worldInfo,
    stylePreferences,
    currentScene,
    addCharacter,
    updateWorldInfo,
    setStylePreferences,
    setCurrentScene,
    addChapterSummary,
    exportContext,
    importContext,
    clearContext
  }
}