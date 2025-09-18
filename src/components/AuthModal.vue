<template>
  <div v-if="isOpen" class="auth-modal-overlay" @click.self="$emit('close')">
    <div class="auth-modal-container">
      <div class="auth-modal-header">
        <h2 class="auth-modal-title">
          {{ isLoginMode ? 'Вход в аккаунт' : 'Создание аккаунта' }}
        </h2>
        <button @click="$emit('close')" class="close-btn">
          &times;
        </button>
      </div>
      
      <div class="auth-modal-content">
        <!-- Форма логина/регистрации -->
        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label for="email" class="form-label">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              required
              class="form-input"
              :class="{ 'error': errors.email }"
              placeholder="example@email.com"
            />
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="password" class="form-label">Пароль</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              required
              class="form-input"
              :class="{ 'error': errors.password }"
              placeholder="••••••••"
            />
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>

          <div v-if="!isLoginMode" class="form-group">
            <label for="confirmPassword" class="form-label">Подтвердите пароль</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              required
              class="form-input"
              :class="{ 'error': errors.confirmPassword }"
              placeholder="••••••••"
            />
            <span v-if="errors.confirmPassword" class="error-message">{{ errors.confirmPassword }}</span>
          </div>

          <div v-if="!isLoginMode" class="form-group">
            <label for="name" class="form-label">Имя пользователя</label>
            <input
              id="name"
              v-model="form.name"
              type="text"
              required
              class="form-input"
              :class="{ 'error': errors.username }"
              placeholder="Ваше имя пользователя"
            />
            <span v-if="errors.username" class="error-message">{{ errors.username }}</span>
            <small class="form-hint">Только буквы, цифры, дефисы и подчеркивания</small>
          </div>

          <button 
            type="submit" 
            class="auth-submit-btn"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="loading-spinner"></span>
            {{ isLoading ? 'Загрузка...' : (isLoginMode ? 'Войти' : 'Зарегистрироваться') }}
          </button>

          <div v-if="errorMessage" class="auth-error">
            {{ errorMessage }}
          </div>
        </form>

        <!-- Переключатель между логином и регистрацией -->
        <div class="auth-toggle">
          <p>
            {{ isLoginMode ? 'Нет аккаунта?' : 'Уже есть аккаунт?' }}
            <button @click="toggleMode" class="toggle-btn">
              {{ isLoginMode ? 'Зарегистрироваться' : 'Войти' }}
            </button>
          </p>
        </div>

        <!-- Разделитель -->
        <div class="auth-divider">
          <span>или</span>
        </div>

        <!-- OAuth2 кнопки -->
        <div class="oauth-buttons">
          <button @click="handleGoogleAuth" class="oauth-btn google-btn" :disabled="isLoading">
            <svg width="20" height="20" viewBox="0 0 24 24">
              <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
              <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
              <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
              <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
            </svg>
            Продолжить с Google
          </button>

          <button @click="handleGitHubAuth" class="oauth-btn github-btn" :disabled="isLoading">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="#000">
              <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            Продолжить с GitHub
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useAuth } from '../composables/useAuth'

export default {
  name: 'AuthModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'authenticated'],
  setup(props, { emit }) {
    const { login, register, googleAuth, githubAuth } = useAuth()
    
    const isLoginMode = ref(true)
    const isLoading = ref(false)
    const errorMessage = ref('')
    
    const form = reactive({
      email: '',
      password: '',
      confirmPassword: '',
      name: ''
    })
    
    const errors = reactive({
      email: '',
      password: '',
      confirmPassword: '',
      username: ''
    })

    const validateForm = () => {
      // Очищаем предыдущие ошибки
      errors.email = ''
      errors.password = ''
      errors.confirmPassword = ''
      errors.username = ''

      let isValid = true

      // Базовая валидация email для UX
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!form.email.trim()) {
        errors.email = 'Email обязателен'
        isValid = false
      } else if (!emailRegex.test(form.email)) {
        errors.email = 'Введите корректный email'
        isValid = false
      }

      // Базовая валидация пароля для UX
      if (!form.password) {
        errors.password = 'Пароль обязателен'
        isValid = false
      } else if (form.password.length < 6) {
        errors.password = 'Пароль должен содержать минимум 6 символов'
        isValid = false
      }

      // Валидация имени пользователя для регистрации
      if (!isLoginMode.value) {
        if (!form.name.trim()) {
          errors.username = 'Имя пользователя обязательно'
          isValid = false
        } else if (form.name.length < 3) {
          errors.username = 'Имя пользователя должно содержать минимум 3 символа'
          isValid = false
        } else if (!/^[a-zA-Z0-9_-]+$/.test(form.name)) {
          errors.username = 'Только буквы, цифры, дефисы и подчеркивания'
          isValid = false
        }
        
        // Валидация подтверждения пароля
        if (form.password !== form.confirmPassword) {
          errors.confirmPassword = 'Пароли не совпадают'
          isValid = false
        }
      }

      return isValid
    }

    const handleSubmit = async () => {
      if (!validateForm()) return

      isLoading.value = true
      errorMessage.value = ''

      try {
        if (isLoginMode.value) {
          await login(form.email, form.password)
        } else {
          await register({
            email: form.email,
            password: form.password,
            username: form.name || form.email.split('@')[0] // Используем name или часть email до @
          })
        }
        
        emit('authenticated')
        emit('close')
      } catch (error) {
        // Обрабатываем ошибки валидации от бэкенда
        if (error.response?.status === 422) {
          const validationErrors = error.response.data.detail
          if (Array.isArray(validationErrors)) {
            validationErrors.forEach(err => {
              const field = err.loc[err.loc.length - 1]
              if (field === 'email') errors.email = err.msg
              if (field === 'password') errors.password = err.msg
              if (field === 'username') errors.username = err.msg
            })
          } else {
            errorMessage.value = 'Ошибка валидации данных'
          }
        } else {
          errorMessage.value = error.message || 'Произошла ошибка'
        }
      } finally {
        isLoading.value = false
      }
    }

    const handleGoogleAuth = async () => {
      isLoading.value = true
      errorMessage.value = ''
      
      try {
        await googleAuth()
        emit('authenticated')
        emit('close')
      } catch (error) {
        errorMessage.value = error.message || 'Ошибка авторизации через Google'
      } finally {
        isLoading.value = false
      }
    }

    const handleGitHubAuth = async () => {
      isLoading.value = true
      errorMessage.value = ''
      
      try {
        await githubAuth()
        emit('authenticated')
        emit('close')
      } catch (error) {
        errorMessage.value = error.message || 'Ошибка авторизации через GitHub'
      } finally {
        isLoading.value = false
      }
    }

    const toggleMode = () => {
      isLoginMode.value = !isLoginMode.value
      errorMessage.value = ''
      
      // Очищаем ошибки и форму
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })
      
      // Очищаем поля формы
      form.email = ''
      form.password = ''
      form.confirmPassword = ''
      form.name = ''
    }

    return {
      isLoginMode,
      isLoading,
      errorMessage,
      form,
      errors,
      handleSubmit,
      handleGoogleAuth,
      handleGitHubAuth,
      toggleMode
    }
  }
}
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6); /* Возвращено к затемненному фону */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px); /* Возвращено размытие фона */
  animation: fadeIn 0.3s ease-out;
}

.auth-modal-container {
  background: var(--color-white);
  border-radius: var(--border-radius-lg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideInFromTop 0.3s ease-out;
}

.auth-modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-gray-50);
  border-radius: var(--border-radius-lg) var(--border-radius-lg) 0 0;
}

.auth-modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: var(--color-secondary);
  cursor: pointer;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: var(--transition);
}

.close-btn:hover {
  background: var(--color-gray-200);
  color: var(--color-primary);
}

.auth-modal-content {
  padding: 2rem;
}

.auth-form {
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--color-primary);
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  font-size: 1rem;
  transition: var(--transition);
  background: var(--color-white);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(17, 24, 39, 0.1);
}

.form-input.error {
  border-color: #dc3545;
}

.error-message {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875rem;
  color: #dc3545;
}

.form-hint {
  color: var(--color-secondary);
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: block;
}

.auth-submit-btn {
  width: 100%;
  padding: 0.75rem;
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  border-radius: var(--border-radius);
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.auth-submit-btn:hover:not(:disabled) {
  background: var(--color-gray-800);
}

.auth-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.auth-error {
  margin-top: 0.75rem;
  padding: 0.75rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: var(--border-radius);
  color: #dc2626;
  font-size: 0.875rem;
}

.auth-toggle {
  text-align: center;
  margin: 1.5rem 0;
}

.toggle-btn {
  background: none;
  border: none;
  color: var(--color-primary);
  cursor: pointer;
  font-weight: 500;
  text-decoration: underline;
  transition: var(--transition);
}

.toggle-btn:hover {
  color: var(--color-gray-800);
}

.auth-divider {
  position: relative;
  text-align: center;
  margin: 1.5rem 0;
  color: var(--color-secondary);
}

.auth-divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background: var(--color-border);
}

.auth-divider span {
  background: var(--color-white);
  padding: 0 1rem;
  position: relative;
}

.oauth-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.oauth-btn {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  background: var(--color-white);
  color: var(--color-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.oauth-btn:hover:not(:disabled) {
  background: var(--color-gray-50);
  border-color: var(--color-gray-300);
}

.oauth-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInFromTop {
  from {
    opacity: 0;
    transform: translateY(-50px) scale(0.9);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>