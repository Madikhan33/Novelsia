/**
 * API клиент для подключения к бэкенду Novelsia
 */

const API_BASE_URL = 'http://localhost:8000/api'

class APIClient {
  constructor() {
    this.token = null // Токен будет установлен через setToken из useAuth
  }

  setToken(token) {
    this.token = token
    if (token) {
      localStorage.setItem('access_token', token)
    } else {
      localStorage.removeItem('access_token')
    }
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    if (this.token) {
      config.headers['Authorization'] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, config)
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Network error' }))
        throw new Error(error.detail || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API Request failed:', error)
      throw error
    }
  }

  // Auth endpoints
  async login(username, password) {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await this.request('/auth/login', {
      method: 'POST',
      body: formData,
      headers: {} // Remove Content-Type for FormData
    })
    
    if (response.access_token) {
      this.setToken(response.access_token)
    }
    
    return response
  }

  async register(userData) {
    return await this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  }

  async getCurrentUser() {
    return await this.request('/users/me')
  }

  // Novel endpoints
  async getNovels() {
    return await this.request('/novels/')
  }

  async createNovel(novelData) {
    return await this.request('/novels/', {
      method: 'POST',
      body: JSON.stringify(novelData)
    })
  }

  async getNovel(novelId) {
    return await this.request(`/novels/${novelId}`)
  }

  async updateNovel(novelId, novelData) {
    return await this.request(`/novels/${novelId}`, {
      method: 'PUT',
      body: JSON.stringify(novelData)
    })
  }

  async deleteNovel(novelId) {
    return await this.request(`/novels/${novelId}`, {
      method: 'DELETE'
    })
  }

  // Chapter endpoints
  async getChapters(novelId) {
    return await this.request(`/chapters/?novel_id=${novelId}`)
  }

  async createChapter(chapterData) {
    return await this.request('/chapters/', {
      method: 'POST',
      body: JSON.stringify(chapterData)
    })
  }

  async getChapter(chapterId) {
    return await this.request(`/chapters/${chapterId}`)
  }

  async updateChapter(chapterId, chapterData) {
    return await this.request(`/chapters/${chapterId}`, {
      method: 'PUT',
      body: JSON.stringify(chapterData)
    })
  }

  async deleteChapter(chapterId) {
    return await this.request(`/chapters/${chapterId}`, {
      method: 'DELETE'
    })
  }

  // AI Suggestions endpoints
  async generateAISuggestion(requestData) {
    return await this.request('/ai/generate', {
      method: 'POST',
      body: JSON.stringify(requestData)
    })
  }

  async getAISuggestions(filters = {}) {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, value)
      }
    })
    
    const queryString = params.toString()
    const endpoint = queryString ? `/ai/?${queryString}` : '/ai/'
    
    return await this.request(endpoint)
  }

  async updateAISuggestion(suggestionId, updateData) {
    return await this.request(`/ai/${suggestionId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData)
    })
  }

  async deleteAISuggestion(suggestionId) {
    return await this.request(`/ai/${suggestionId}`, {
      method: 'DELETE'
    })
  }

  // Quick AI continuation (похоже на курсор)
  async getQuickContinuation(context, chapterId = null, novelId = null) {
    return await this.generateAISuggestion({
      suggestion_type: 'continuation',
      context: context,
      chapter_id: chapterId,
      novel_id: novelId,
      max_length: 150
    })
  }

  // Тестовая генерация AI предложений без авторизации
  // Доп. опции (например, { signal }) можно передавать вторым аргументом
  async testGenerateAISuggestion(requestData, fetchOptions = {}) {
    return await this.request('/ai/test-generate', {
      method: 'POST',
      body: JSON.stringify(requestData),
      ...fetchOptions
    })
  }

  // Специализированный метод для inline подсказок
  async generateInlineSuggestion(context, chapterId = null, fetchOptions = {}) {
    return await this.request('/ai/inline-suggestion', {
      method: 'POST',
      body: JSON.stringify({
        context: context,
        chapter_id: chapterId
      }),
      ...fetchOptions
    })
  }
}

// Создаем глобальный экземпляр
export const apiClient = new APIClient()

// Экспортируем класс для тестирования
export default APIClient