<template>
  <div class="home">
    <header class="header">
      <div class="container">
        <h1 class="logo">Novelsia</h1>
        <nav class="nav">
          <div v-if="isAuthenticated" class="user-menu">
            <span>Привет, {{ user?.username }}!</span>
            <button @click="handleLogout" class="btn-secondary">Выйти</button>
          </div>
          <div v-else class="auth-buttons">
            <button @click="openAuthModal" class="btn-primary">Войти</button>
          </div>
        </nav>
      </div>
    </header>

    <main class="main">
      <div class="container">
        <div class="hero">
          <h2>Добро пожаловать в Novelsia</h2>
          <p>Современное рабочее пространство для писателей</p>
          
          <div class="cta">
            <button v-if="!isAuthenticated" @click="openAuthModal" class="btn-primary btn-large">
              Начать писать
            </button>
            <button v-else @click="goToEditor" class="btn-primary btn-large">
              Открыть редактор
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- Auth Modal -->
    <AuthModal 
      :isOpen="showAuthModal" 
      @close="closeAuthModal"
      @authenticated="handleAuthenticated"
    />
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import AuthModal from '../components/AuthModal.vue'

export default {
  name: 'Home',
  components: {
    AuthModal
  },
  setup() {
    const router = useRouter()
    const { isAuthenticated, user, logout } = useAuth()
    const showAuthModal = ref(false)

    const openAuthModal = () => {
      showAuthModal.value = true
    }

    const closeAuthModal = () => {
      showAuthModal.value = false
    }

    const handleAuthenticated = () => {
      showAuthModal.value = false
      // Redirect to editor after authentication
      router.push('/editor')
    }

    const handleLogout = async () => {
      await logout()
    }

    const goToEditor = () => {
      router.push('/editor')
    }

    return {
      isAuthenticated,
      user,
      showAuthModal,
      openAuthModal,
      closeAuthModal,
      handleAuthenticated,
      handleLogout,
      goToEditor
    }
  }
}
</script>

<style scoped>
.header {
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  padding: 1rem 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary);
  margin: 0;
}

.nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.auth-buttons {
  display: flex;
  gap: 0.5rem;
}

.main {
  flex: 1;
  display: flex;
  align-items: center;
  min-height: calc(100vh - 80px);
}

.hero {
  text-align: center;
  max-width: 600px;
  margin: 0 auto;
}

.hero h2 {
  font-size: 3rem;
  font-weight: 700;
  color: var(--color-primary);
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.25rem;
  color: var(--color-secondary);
  margin-bottom: 2rem;
}

.cta {
  margin-top: 2rem;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  font-weight: 500;
  transition: var(--transition);
}

.btn-primary:hover {
  background: var(--color-gray-800);
}

.btn-large {
  padding: 1rem 2rem;
  font-size: 1.125rem;
}

.btn-secondary {
  background: transparent;
  color: var(--color-secondary);
  border: 1px solid var(--color-border);
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
}

.btn-secondary:hover {
  background: var(--color-gray-50);
  color: var(--color-primary);
}
</style>