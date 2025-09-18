<template>
  <Teleport to="body">
    <Transition name="toast" appear>
      <div v-if="notification" class="toast-container" :class="toastTypeClass">
        <div class="toast-content">
          <div class="toast-icon">
            <svg v-if="notification.type === 'success'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20,6 9,17 4,12"></polyline>
            </svg>
            <svg v-else-if="notification.type === 'error'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="15" y1="9" x2="9" y2="15"></line>
              <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <path d="m9,12 2,2 4,-4"></path>
            </svg>
          </div>
          
          <div class="toast-message">
            {{ notification.message }}
          </div>
          
          <button @click="$emit('close')" class="toast-close">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script>
export default {
  name: 'NotificationToast',
  props: {
    notification: {
      type: Object,
      default: null
    }
  },
  emits: ['close'],
  computed: {
    toastTypeClass() {
      if (!this.notification) return ''
      return `toast-${this.notification.type || 'success'}`
    }
  },
  watch: {
    notification: {
      handler(newNotification) {
        if (newNotification) {
          // Автоматически закрываем уведомление через 4 секунды
          setTimeout(() => {
            this.$emit('close')
          }, 4000)
        }
      },
      immediate: true
    }
  }
}
</script>

<style scoped>
.toast-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 200;
  max-width: 400px;
  width: auto;
  min-width: 300px;
  background: white;
  border-radius: 0.5rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  border-left: 4px solid;
}

.toast-success {
  border-left-color: #10b981;
}

.toast-error {
  border-left-color: #ef4444;
}

.toast-info {
  border-left-color: #3b82f6;
}

.toast-content {
  display: flex;
  align-items: flex-start;
  padding: 1rem;
  gap: 0.75rem;
}

.toast-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.toast-success .toast-icon {
  color: #10b981;
}

.toast-error .toast-icon {
  color: #ef4444;
}

.toast-info .toast-icon {
  color: #3b82f6;
}

.toast-message {
  flex: 1;
  font-size: 0.875rem;
  color: #374151;
  line-height: 1.4;
  font-weight: 500;
}

.toast-close {
  background: none;
  border: none;
  cursor: pointer;
  color: #9ca3af;
  transition: color 0.2s ease;
  padding: 0.125rem;
  border-radius: 0.25rem;
  margin: -0.125rem -0.125rem 0 0;
}

.toast-close:hover {
  color: #6b7280;
  background: #f3f4f6;
}

/* Анимации */
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
}

.toast-enter-to,
.toast-leave-from {
  opacity: 1;
  transform: translateX(0) scale(1);
}

@media (max-width: 480px) {
  .toast-container {
    left: 1rem;
    right: 1rem;
    min-width: auto;
    max-width: none;
  }
  
  .toast-enter-from,
  .toast-leave-to {
    transform: translateY(-100%) scale(0.95);
  }
}
</style> 