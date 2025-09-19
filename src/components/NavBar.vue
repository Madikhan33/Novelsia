<template>
  <nav class="navbar">
    <div class="nav-container">
      <!-- Бренд -->
      <div class="nav-brand">
        <div class="brand-section">
          <h1 class="logo">Novelsia</h1>
        </div>
      </div>
      
      <!-- Центральная секция -->
      <div class="nav-center">
        <div class="chapter-info">
          <!-- Поле названия книги -->
          <div class="input-group">
            <input
              :value="bookTitle"
              @input="handleBookTitleInput"
              class="input-field book-title-input"
              placeholder="Название книги"
              type="text"
              maxlength="100"
            />
          </div>

          <!-- Поле названия главы -->
          <div class="input-group">
            <input 
              id="chapterTitle"
              :value="currentChapter.title"
              @input="handleTitleInput"
              @keydown.enter.prevent="$emit('save')"
              class="input-field chapter-title-input"
              placeholder="Название главы"
              type="text"
              maxlength="100"
            />
          </div>
          
          <!-- Статистика -->
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">Слов</span>
              <span class="stat-value" :class="{ 'stat-dirty': isDirty }">
                {{ formatNumber(wordCount) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Глав</span>
              <span class="stat-value">{{ formatNumber(chaptersCount) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Всего</span>
              <span class="stat-value">{{ formatNumber(totalWords) }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Действия -->
      <div class="nav-actions">
        <!-- Основные действия переносим влево -->
        <div class="primary-actions">
          <button 
            @click="$emit('save')" 
            class="btn btn-save"
            :class="{ 'btn-dirty': isDirty, 'btn-pulse': isDirty }"
            :title="saveTooltip"
          >
            <span class="btn-text">{{ saveText }}</span>
          </button>
          
          <button 
            @click="$emit('new-chapter')" 
            class="btn btn-outline"
            title="Создать новую главу (Ctrl+N)"
          >
            <span class="btn-text">Новая</span>
          </button>
          
          <button 
            @click="$emit('toggle-books-modal')" 
            class="btn btn-outline"
            title="Открыть список книг"
          >
            <span class="btn-text">Мои книги</span>
          </button>
          
          <button 
            @click="handleToggleSidebar" 
            class="btn btn-outline"
            :title="`Открыть список глав (${chaptersCount})`"
          >
            <span class="btn-text">Главы</span>
            <span class="badge" v-if="chaptersCount > 0">{{ chaptersCount }}</span>
          </button>

          <div class="secondary-actions">
            <div class="dropdown" ref="dropdownRef">
              <button 
                @click="toggleDropdown"
                class="btn btn-icon"
                title="Дополнительные действия"
              >
                Еще
              </button>
              
              <div class="dropdown-menu" v-show="dropdownOpen">
                <button @click="handleExport('json')" class="dropdown-item">
                  Экспорт JSON
                </button>
                <button @click="handleExport('txt')" class="dropdown-item">
                  Экспорт TXT
                </button>
                <label class="dropdown-item file-input-wrapper">
                  Импорт
                  <input 
                    type="file" 
                    accept=".json,.txt"
                    @change="handleImport"
                    class="file-input"
                  />
                </label>
                <div class="dropdown-divider"></div>
                <button @click="showStats" class="dropdown-item">
                  Статистика
                </button>
                <button @click="showSettings" class="dropdown-item">
                  Настройки
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Информация о пользователе справа -->
        <div class="user-section">
          <div v-if="isAuthenticated" class="user-info">
            <span class="user-greeting">{{ userGreeting }}</span>
            <button @click="handleLogout" class="btn btn-outline logout-btn" title="Выйти из аккаунта">
              Выход
            </button>
          </div>
          <div v-else class="auth-actions">
            <button @click="$emit('show-auth')" class="btn btn-primary">
              Войти
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Индикатор автосохранения -->
    <Transition name="autosave">
      <div v-if="showAutoSaveIndicator" class="autosave-indicator">
        <span>Автосохранено</span>
      </div>
    </Transition>
  </nav>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'



export default {
  name: 'NavBar',
  components: {
  },
  props: {
    currentChapter: {
      type: Object,
      required: true
    },
    wordCount: {
      type: Number,
      default: 0
    },
    chaptersCount: {
      type: Number,
      default: 0
    },
    totalWords: {
      type: Number,
      default: 0
    },
    isDirty: {
      type: Boolean,
      default: false
    },
    isAuthenticated: {
      type: Boolean,
      default: false
    },
    user: {
      type: Object,
      default: null
    },
    bookTitle: {
      type: String,
      default: ''
    }
  },
  emits: [
    'save',
    'new-chapter', 
    'toggle-sidebar',
    'export',
    'import',
    'title-change',
    'book-title-change',
    'toggle-books-modal',
    'show-auth',
    'logout'
  ],
  setup(props, { emit }) {
    const dropdownRef = ref(null)
    const dropdownOpen = ref(false)
    const showAutoSaveIndicator = ref(false)
    
    // Вычисляемые свойства
    const userGreeting = computed(() => {
      if (!props.user) return 'Гость'
      return `${props.user.username || props.user.email || 'Пользователь'}!`
    })
    
    // Вычисляемые свойства
    const subtitle = computed(() => {
      const parts = []
      if (props.chaptersCount > 0) {
        parts.push(`${props.chaptersCount} глав`)
      }
      if (props.totalWords > 0) {
        parts.push(`${formatNumber(props.totalWords)} слов`)
      }
      return parts.length > 0 ? parts.join(' • ') : 'Пространство для писателей'
    })
    
    const saveText = computed(() => {
      return props.isDirty ? 'Сохранить' : 'Сохранено'
    })
    
    const saveTooltip = computed(() => {
      return props.isDirty 
        ? 'Сохранить главу (Ctrl+S)' 
        : 'Глава сохранена'
    })
    
    // Методы
    const formatNumber = (num) => {
      if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M'
      }
      if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K'
      }
      return num.toString()
    }
    
    let titleInputTimeout = null
    const handleTitleInput = (event) => {
      clearTimeout(titleInputTimeout)
      titleInputTimeout = setTimeout(() => {
        emit('title-change', event.target.value)
      }, 300) // Дебаунс для производительности
    }

    let bookTitleInputTimeout = null
    const handleBookTitleInput = (event) => {
      clearTimeout(bookTitleInputTimeout)
      bookTitleInputTimeout = setTimeout(() => {
        emit('book-title-change', event.target.value)
      }, 500) // Уменьшен дебаунс для названия книги
    }
    
    const toggleDropdown = () => {
      dropdownOpen.value = !dropdownOpen.value
    }
    
    const closeDropdown = () => {
      dropdownOpen.value = false
    }
    
    const handleExport = (format) => {
      emit('export', format)
      closeDropdown()
    }
    
    const handleImport = (event) => {
      const file = event.target.files[0]
      if (file) {
        emit('import', file)
        event.target.value = '' // Сброс input
      }
      closeDropdown()
    }
    
    const showStats = () => {
      // TODO: Реализовать окно статистики
      console.log('Показать статистику')
      closeDropdown()
    }
    
    const showSettings = () => {
      // TODO: Реализовать окно настроек
      console.log('Показать настройки')
      closeDropdown()
    }
    
    const handleToggleSidebar = () => {
      console.log('NavBar: кнопка toggle-sidebar нажата')
      emit('toggle-sidebar')
    }
    
    const handleLogout = () => {
      emit('logout')
    }


    
    const handleClickOutside = (event) => {
      if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
        closeDropdown()
      }
    }
    
    // Показать индикатор автосохранения
    const showAutoSave = () => {
      showAutoSaveIndicator.value = true
      setTimeout(() => {
        showAutoSaveIndicator.value = false
      }, 2000)
    }
    
    // Наблюдатели
    watch(() => props.isDirty, (newVal, oldVal) => {
      // Показываем индикатор когда isDirty меняется с true на false (сохранение)
      if (oldVal === true && newVal === false) {
        showAutoSave()
      }
    })
    
    // Жизненный цикл
    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })
    
    onUnmounted(() => {
      document.removeEventListener('click', handleClickOutside)
      clearTimeout(titleInputTimeout)
      clearTimeout(bookTitleInputTimeout)
    })
    
                    return {
            dropdownRef,
            dropdownOpen,
            showAutoSaveIndicator,
            userGreeting,
            subtitle,
            saveText,
            saveTooltip,
            formatNumber,
            handleTitleInput,
            handleBookTitleInput,
            toggleDropdown,
            closeDropdown,
            handleExport,
            handleImport,
            showStats,
            showSettings,
            handleToggleSidebar,
            handleLogout
          }
  }
}
</script>

<style scoped>
.navbar {
  height: var(--navbar-height);
  background: var(--color-white);
  border-bottom: 1px solid var(--color-border);
  z-index: 30;
  position: relative;
  overflow: hidden;
  margin-top: 10px;
}

.nav-container {
  height: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 1.5rem;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 2rem;
}

/* Бренд */
.nav-brand {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  min-width: 0;
  
}

.brand-section {
  display: flex;
  align-items: center;
  gap: 1rem;
}



.logo {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.025em;
  color: var(--color-primary);
  margin: 0;
  white-space: nowrap;
}

.logo-subtitle {
  font-size: 0.75rem;
  color: var(--color-secondary);
  font-weight: 400;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Центральная секция */
.nav-center {
  min-width: 0;
  max-width: 600px;
  margin-right: 0;
}

.chapter-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  justify-content: flex-start;
  max-width: 100px;
  width: 100%;
}

.input-group {
  display: flex;
  align-items: center;
  position: relative;
}

.input-group:first-child {
  flex: 2;
}

.input-group:last-child {
  flex: 1;
}

.chapter-title-input,
.book-title-input {
  border: none;
  border-radius: var(--border-radius);
  padding: 0.75rem 1rem;
  font-family: var(--font-ui);
  font-size: 1rem;
  font-weight: 500;
  background: var(--color-white);
  color: var(--color-gray-900);
  transition: var(--transition);
  width: 100%;
}

.chapter-title-input:focus,
.book-title-input:focus {
  outline: none;
  background: var(--color-gray-50);
}

.book-title-input {
  width: 200px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-primary);
  background: linear-gradient(135deg, 
    rgba(59, 130, 246, 0.1), 
    rgba(147, 51, 234, 0.05)
  );
  border: 2px solid transparent;
  background-clip: padding-box;
}

.book-title-input:focus {
  background: var(--color-white);
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.chapter-title-input::placeholder {
  color: var(--color-gray-400);
}

.stats-grid {
  display: flex;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.2rem;
  text-align: center;
}

.stat-item {
  justify-content: space-around;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-black);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.3rem;
  font-weight: 600;
  color: var(--color-black);
  font-variant-numeric: tabular-nums;
  transition: var(--transition);
}

.stat-dirty {
  color: var(--color-black);
}

/* Действия */
.nav-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.primary-actions {
  display: flex;
  align-items: center;
  gap: 1.2rem;
  margin-right: 80px;
}

.user-section {
  margin-left: auto; /* Прижимаем к правому краю */
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-greeting {
  font-size: 0.875rem;
  color: var(--color-secondary);
  white-space: nowrap;
  margin-right: 0.5rem;
}

.auth-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-right: 1rem;
  border-right: 1px solid var(--color-border);
}

.logout-btn {
  font-size: 0.75rem;
  padding: 0.5rem 0.75rem;
}

.btn-primary {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
}

.btn-primary:hover {
  background: var(--color-gray-800);
  border-color: var(--color-gray-800);
}

.secondary-actions {
  position: relative;
}

/* Кнопки */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  font-family: var(--font-ui);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  text-decoration: none;
  border: 1px solid;
  white-space: nowrap;
  position: relative;
}

.btn-save {
  background: var(--color-primary);
  color: var(--color-white);
  border-color: var(--color-primary);
}

.btn-save:hover {
  background: var(--color-gray-800);
  border-color: var(--color-gray-800);
}

.btn-dirty {
  background: var(--color-black);
  border-color: var(--color-black);
}

.btn-pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.btn-outline {
  background: var(--color-white);
  color: var(--color-primary);
  border-color: var(--color-border);
}

.btn-outline:hover {
  background: var(--color-gray-50);
  border-color: var(--color-gray-300);
}

.btn-icon {
  padding: 0.5rem;
  background: transparent;
  border: 1px solid transparent;
  color: var(--color-secondary);
}

.btn-icon:hover {
  background: var(--color-gray-50);
  color: var(--color-primary);
}

.btn-text {
  display: block;
}

.badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: var(--color-primary);
  color: var(--color-white);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
  line-height: 1;
}

/* Dropdown */
.dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  min-width: 200px;
  z-index: 100; /* Increased z-index */
  padding: 0.5rem 0;
  opacity: 0;
  visibility: hidden;
  transition: opacity 0.2s ease-in-out, visibility 0.2s ease-in-out;
}

.dropdown-menu[v-show="true"] {
  opacity: 1;
  visibility: visible;
}

.dropdown-item {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 0.75rem 1rem;
  background: none;
  border: none;
  font-family: inherit;
  font-size: 0.875rem;
  color: var(--color-primary);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
}

.dropdown-item:hover {
  background: var(--color-gray-50);
}

.dropdown-divider {
  height: 1px;
  background: var(--color-border);
  margin: 0.5rem 0;
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
}

.file-input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

/* Индикатор автосохранения */
.autosave-indicator {
  position: absolute;
  top: 50%;
  right: 1rem;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--color-gray-900);
  color: var(--color-white);
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius);
  font-size: 0.75rem;
  font-weight: 500;
  z-index: 40;
}



/* Анимации автосохранения */
.autosave-enter-active,
.autosave-leave-active {
  transition: all 0.3s ease;
}

.autosave-enter-from {
  opacity: 0;
  transform: translateY(-50%) translateX(100%);
}

.autosave-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(100%);
}

/* Адаптивность */
@media (max-width: 1200px) {
  .nav-container {
    grid-template-columns: auto 1fr auto;
    gap: 1rem;
  }
  
  .chapter-info {
    gap: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .nav-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto auto;
    padding: 1rem;
    gap: 1rem;
  }
  
  .nav-brand {
    text-align: center;
  }
  
  .chapter-info {
    flex-direction: column;
    gap: 1rem;
  }
  
  .input-group {
    max-width: none;
  }
  
  .nav-actions {
    justify-content: center;
  }
  
  .btn-text {
    display: none;
  }
  
  .btn {
    padding: 0.75rem;
  }
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
    gap: 0.5rem;
  }
  
  .stat-value {
    font-size: 1rem;
  }
  
  .primary-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .btn {
    flex: 1;
    justify-content: center;
  }
}
</style>