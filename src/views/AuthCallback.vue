<template>
  <div class="auth-callback">
    <div class="callback-container">
      <div v-if="isLoading" class="loading">
        <div class="spinner"></div>
        <p>Завершение авторизации...</p>
      </div>
      
      <div v-else-if="error" class="error">
        <h2>Ошибка авторизации</h2>
        <p>{{ error }}</p>
        <button @click="goHome" class="btn-primary">
          Вернуться на главную
        </button>
      </div>
      
      <div v-else class="success">
        <h2>Авторизация успешна!</h2>
        <p>Перенаправление...</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from '../composables/useAuth'

export default {
  name: 'AuthCallback',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const { saveAuth } = useAuth()
    
    const isLoading = ref(true)
    const error = ref('')
    
    const goHome = () => {
      router.push('/')
    }
    
    onMounted(async () => {
      console.log('AuthCallback: Component mounted')
      console.log('AuthCallback: Route query:', route.query)
      
      try {
        const token = route.query.token
        const errorParam = route.query.error
        
        console.log('AuthCallback: Token:', token ? 'Present' : 'Missing')
        console.log('AuthCallback: Error:', errorParam)
        
        if (errorParam) {
          error.value = decodeURIComponent(errorParam)
          isLoading.value = false
          return
        }
        
        if (token) {
          console.log('AuthCallback: Fetching user data...')
          // Get user data with the token
          const response = await fetch('http://localhost:8000/api/users/me', {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          })
          
          console.log('AuthCallback: User data response status:', response.status)
          
          if (response.ok) {
            const userData = await response.json()
            console.log('AuthCallback: User data received:', userData)
            
            await saveAuth(token, userData)
            console.log('AuthCallback: Auth saved, redirecting...')
            
            // Redirect to home page
            setTimeout(() => {
              router.push('/')
            }, 1500)
          } else {
            const errorText = await response.text()
            console.error('AuthCallback: Failed to get user data:', errorText)
            error.value = `Не удалось получить данные пользователя: ${response.status}`
          }
        } else {
          error.value = 'Токен авторизации не получен'
        }
      } catch (err) {
        error.value = 'Произошла ошибка при обработке авторизации'
        console.error('Auth callback error:', err)
      } finally {
        isLoading.value = false
      }
    })
    
    return {
      isLoading,
      error,
      goHome
    }
  }
}
</script>

<style scoped>
.auth-callback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-gray-50);
}

.callback-container {
  background: var(--color-white);
  padding: 2rem;
  border-radius: var(--border-radius-lg);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-gray-200);
  border-top: 4px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.error h2 {
  color: #dc3545;
  margin-bottom: 1rem;
}

.success h2 {
  color: var(--color-primary);
  margin-bottom: 1rem;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 500;
  margin-top: 1rem;
  transition: var(--transition);
}

.btn-primary:hover {
  background: var(--color-gray-800);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>