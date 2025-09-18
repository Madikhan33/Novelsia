/**
 * Утилита для тестирования аутентификации
 */

export function testAuthFlow() {
  console.log('=== Тест потока аутентификации ===')
  
  // Проверяем localStorage
  const token = localStorage.getItem('access_token')
  const userData = localStorage.getItem('user_data')
  
  console.log('Токен в localStorage:', token ? 'Есть' : 'Нет')
  console.log('Данные пользователя в localStorage:', userData ? 'Есть' : 'Нет')
  
  // Проверяем API клиент
  import('../services/api.js').then(({ apiClient }) => {
    console.log('Токен в API клиенте:', apiClient.token ? 'Есть' : 'Нет')
    console.log('Токены совпадают:', apiClient.token === token)
  })
  
  // Проверяем useAuth
  import('../composables/useAuth.js').then(({ useAuth }) => {
    const { isAuthenticated, user, token: authToken } = useAuth()
    console.log('isAuthenticated:', isAuthenticated.value)
    console.log('Пользователь в useAuth:', user.value ? 'Есть' : 'Нет')
    console.log('Токен в useAuth:', authToken.value ? 'Есть' : 'Нет')
  })
}

// Экспортируем для использования в консоли браузера
if (typeof window !== 'undefined') {
  window.testAuthFlow = testAuthFlow
}