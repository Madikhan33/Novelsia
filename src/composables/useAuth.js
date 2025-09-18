/**
 * Композабл для управления аутентификацией
 */
import { ref, computed, reactive } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api' // Your FastAPI backend URL

// Глобальное состояние аутентификации
const authState = reactive({
  user: null,
  token: null,
  isLoading: false,
  isAuthenticated: false
})

// Helper для API вызовов
async function authApiCall(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json'
  }

  if (authState.token) {
    headers['Authorization'] = `Bearer ${authState.token}`
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null
  })

  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail || 'Ошибка запроса')
  }

  return data
}

export function useAuth() {
  // Инициализация состояния из localStorage
  const initAuth = async () => {
    console.log('useAuth: initAuth вызвана')
    const savedToken = localStorage.getItem('access_token')
    const savedUser = localStorage.getItem('user_data')
    
    console.log('useAuth: savedToken из localStorage:', savedToken)
    console.log('useAuth: savedUser из localStorage:', savedUser)

    if (savedToken && savedUser) {
      try {
        authState.token = savedToken
        authState.user = JSON.parse(savedUser)
        authState.isAuthenticated = true
        
        // Синхронизируем токен с API клиентом
        try {
          const { apiClient } = await import('../services/api.js')
          apiClient.setToken(savedToken)
          console.log('useAuth: Токен синхронизирован с API клиентом')
        } catch (error) {
          console.warn('useAuth: Не удалось синхронизировать токен с API клиентом:', error)
        }
        
        console.log('useAuth: Состояние авторизации восстановлено')
        console.log('useAuth: authState.isAuthenticated:', authState.isAuthenticated)
      } catch (error) {
        console.warn('useAuth: Ошибка при восстановлении данных пользователя:', error)
        await clearAuth()
      }
    } else {
      console.log('useAuth: Нет сохраненных данных авторизации')
    }
  }

  // Очистка состояния аутентификации
  const clearAuth = async () => {
    authState.user = null
    authState.token = null
    authState.isAuthenticated = false
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_data')
    
    // Очищаем токен из API клиента
    try {
      const { apiClient } = await import('../services/api.js')
      apiClient.setToken(null)
    } catch (error) {
      console.warn('Не удалось очистить токен из API клиента:', error)
    }
  }

  // Сохранение данных аутентификации
  const saveAuth = async (token, user) => {
    authState.token = token
    authState.user = user
    authState.isAuthenticated = true
    localStorage.setItem('access_token', token)
    localStorage.setItem('user_data', JSON.stringify(user))
    
    // Синхронизируем токен с API клиентом
    try {
      const { apiClient } = await import('../services/api.js')
      apiClient.setToken(token)
    } catch (error) {
      console.warn('Не удалось синхронизировать токен с API клиентом:', error)
    }
  }

  // Регистрация пользователя
  const register = async (userData) => {
    console.log('useAuth: register вызвана с данными:', userData)
    authState.isLoading = true
    try {
      const requestData = {
        username: userData.username || userData.email, // Используем email как username если username не указан
        email: userData.email,
        password: userData.password
      }
      console.log('useAuth: Отправляем данные регистрации:', requestData)
      const response = await authApiCall('/auth/register', 'POST', requestData)
      console.log('useAuth: Ответ регистрации:', response)

      // Регистрация успешна, но токен не возвращается
      // Нужно выполнить автоматический вход
      console.log('useAuth: Выполняем автоматический вход после регистрации')
      const loginResponse = await login(userData.email, userData.password)
      return loginResponse
    } catch (error) {
      console.error('Ошибка регистрации:', error)
      throw error
    } finally {
      authState.isLoading = false
    }
  }

  // Логин пользователя
  const login = async (email, password) => {
    authState.isLoading = true
    try {
      // FastAPI ожидает form data для OAuth2
      const formData = new FormData()
      formData.append('username', email) // OAuth2 использует 'username' для email
      formData.append('password', password)

      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        body: formData
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.detail || 'Ошибка входа')
      }

      if (data.access_token) {
        // Сначала сохраняем токен
        authState.token = data.access_token
        localStorage.setItem('access_token', data.access_token)
        
        // Теперь получаем данные пользователя с токеном
        const userResponse = await authApiCall('/users/me', 'GET')
        
        // Сохраняем данные и синхронизируем токен с API клиентом
        await saveAuth(data.access_token, userResponse)
        
        return data
      } else {
        throw new Error('Не получен токен доступа')
      }
    } catch (error) {
      console.error('Ошибка логина:', error)
      throw error
    } finally {
      authState.isLoading = false
    }
  }

  // Выход из системы
  const logout = async () => {
    authState.isLoading = true
    try {
      // Опционально: уведомить сервер о выходе
      if (authState.token) {
        await authApiCall('/auth/logout', 'POST')
      }
    } catch (error) {
      console.warn('Ошибка при выходе с сервера:', error)
    } finally {
      await clearAuth()
      authState.isLoading = false
    }
  }

  // OAuth2 авторизация через Google
  const googleAuth = async () => {
    authState.isLoading = true
    try {
      // Перенаправление на Google OAuth
      window.location.href = `${API_BASE_URL}/auth/google`
    } catch (error) {
      console.error('Ошибка Google авторизации:', error)
      authState.isLoading = false
      throw error
    }
  }

  // OAuth2 авторизация через GitHub
  const githubAuth = async () => {
    authState.isLoading = true
    try {
      // Перенаправление на GitHub OAuth
      window.location.href = `${API_BASE_URL}/auth/github`
    } catch (error) {
      console.error('Ошибка GitHub авторизации:', error)
      authState.isLoading = false
      throw error
    }
  }

  // Проверка текущего пользователя
  const checkAuth = async () => {
    console.log('useAuth: checkAuth вызвана')
    console.log('useAuth: authState.token:', authState.token)
    
    if (!authState.token) {
      console.log('useAuth: Токен отсутствует, возвращаем false')
      authState.isAuthenticated = false
      return false
    }

    authState.isLoading = true
    try {
      console.log('useAuth: Отправляем запрос на /users/me')
      const user = await authApiCall('/users/me')
      console.log('useAuth: Получен ответ от /users/me:', user)
      authState.user = user
      authState.isAuthenticated = true
      localStorage.setItem('user_data', JSON.stringify(user))
      return true
    } catch (error) {
      console.error('useAuth: Ошибка проверки авторизации:', error)
      // Если токен недействителен (401), очищаем авторизацию
      if (error.message.includes('401') || error.message.includes('credentials')) {
        console.log('useAuth: Токен недействителен, очищаем авторизацию')
        await clearAuth()
      }
      return false
    } finally {
      authState.isLoading = false
    }
  }

  // Обновление профиля пользователя
  const updateProfile = async (profileData) => {
    authState.isLoading = true
    try {
      const updatedUser = await authApiCall('/auth/profile', 'PUT', profileData)
      authState.user = updatedUser
      localStorage.setItem('user_data', JSON.stringify(updatedUser))
      return updatedUser
    } catch (error) {
      console.error('Ошибка обновления профиля:', error)
      throw error
    } finally {
      authState.isLoading = false
    }
  }

  // Смена пароля
  const changePassword = async (currentPassword, newPassword) => {
    authState.isLoading = true
    try {
      await authApiCall('/auth/change-password', 'POST', {
        current_password: currentPassword,
        new_password: newPassword
      })
      return true
    } catch (error) {
      console.error('Ошибка смены пароля:', error)
      throw error
    } finally {
      authState.isLoading = false
    }
  }

  // Вычисляемые свойства
  const isAuthenticated = computed(() => authState.isAuthenticated)
  const user = computed(() => authState.user)
  const isLoading = computed(() => authState.isLoading)
  const token = computed(() => authState.token)

  // Инициализация при создании
  initAuth().catch(error => {
    console.warn('useAuth: Ошибка при инициализации:', error)
  })

  return {
    // Состояние
    isAuthenticated,
    user,
    isLoading,
    token,

    // Методы
    register,
    login,
    logout,
    googleAuth,
    githubAuth,
    checkAuth,
    updateProfile,
    changePassword,
    initAuth,
    clearAuth,
    saveAuth
  }
}

// Глобальная функция для проверки авторизации при запуске приложения
export async function initializeAuth() {
  const { checkAuth } = useAuth()
  try {
    await checkAuth()
  } catch (error) {
    console.warn('Не удалось проверить авторизацию при запуске:', error)
  }
}