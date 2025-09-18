<template>
  <Teleport to="body">
    <div class="notification-container">
      <TransitionGroup 
        name="notification" 
        tag="div" 
        class="notifications-list"
        @enter="onEnter"
        @leave="onLeave"
      >
        <div
          v-for="notification in visibleNotifications"
          :key="notification.id"
          class="notification"
          :class="[
            `notification-${notification.type}`,
            { 'notification-visible': notification.isVisible }
          ]"
          @click="() => $emit('remove', notification.id)"
        >
          <div class="notification-icon">
            <CheckIcon v-if="notification.type === 'success'" />
            <AlertCircleIcon v-else-if="notification.type === 'error'" />
            <InfoIcon v-else-if="notification.type === 'info'" />
            <AlertTriangleIcon v-else-if="notification.type === 'warning'" />
          </div>
          
          <div class="notification-content">
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
          </div>
          
          <button 
            @click.stop="() => $emit('remove', notification.id)"
            class="notification-close"
            aria-label="Закрыть уведомление"
          >
            <XIcon />
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script>
import { computed } from 'vue'

// Иконки
const CheckIcon = { template: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20,6 9,17 4,12"></polyline></svg>' }
const AlertCircleIcon = { template: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>' }
const InfoIcon = { template: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>' }
const AlertTriangleIcon = { template: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>' }
const XIcon = { template: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>' }

export default {
  name: 'NotificationContainer',
  components: {
    CheckIcon,
    AlertCircleIcon,
    InfoIcon,
    AlertTriangleIcon,
    XIcon
  },
  props: {
    notifications: {
      type: Array,
      default: () => []
    }
  },
  emits: ['remove'],
  setup(props) {
    const visibleNotifications = computed(() => {
      return props.notifications.slice(0, 5) // Показываем максимум 5 уведомлений
    })
    
    const formatTime = (timestamp) => {
      const now = Date.now()
      const diff = now - timestamp
      
      if (diff < 60000) return 'только что'
      if (diff < 3600000) return `${Math.floor(diff / 60000)} мин назад`
      return new Date(timestamp).toLocaleTimeString('ru-RU', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    const onEnter = (el) => {
      // Анимация входа
      el.style.height = '0px'
      el.style.opacity = '0'
      
      requestAnimationFrame(() => {
        el.style.height = el.scrollHeight + 'px'
        el.style.opacity = '1'
      })
    }
    
    const onLeave = (el) => {
      // Анимация выхода
      el.style.height = el.scrollHeight + 'px'
      
      requestAnimationFrame(() => {
        el.style.height = '0px'
        el.style.opacity = '0'
      })
    }
    
    return {
      visibleNotifications,
      formatTime,
      onEnter,
      onLeave
    }
  }
}
</script>

<style scoped>
.notification-container {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1000;
  pointer-events: none;
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  max-width: 400px;
  width: auto;
  min-width: 320px;
}

.notification {
  background: var(--color-white);
  border-radius: var(--border-radius);
  box-shadow: var(--shadow-lg);
  border-left: 4px solid;
  padding: 1rem;
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  pointer-events: all;
  transition: var(--transition);
  transform: translateX(100%);
  opacity: 0;
  overflow: hidden;
}

.notification-visible {
  transform: translateX(0);
  opacity: 1;
}

.notification:hover {
  box-shadow: var(--shadow-lg);
  transform: translateX(-4px) translateY(-2px);
}

.notification-success {
  border-left-color: #10b981;
}

.notification-error {
  border-left-color: #ef4444;
}

.notification-warning {
  border-left-color: #f59e0b;
}

.notification-info {
  border-left-color: #3b82f6;
}

.notification-icon {
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.notification-success .notification-icon {
  color: #10b981;
}

.notification-error .notification-icon {
  color: #ef4444;
}

.notification-warning .notification-icon {
  color: #f59e0b;
}

.notification-info .notification-icon {
  color: #3b82f6;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-message {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-primary);
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.notification-time {
  font-size: 0.75rem;
  color: var(--color-secondary);
}

.notification-close {
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-gray-400);
  transition: var(--transition);
  padding: 0.25rem;
  border-radius: var(--border-radius);
  margin: -0.25rem -0.25rem 0 0;
}

.notification-close:hover {
  color: var(--color-primary);
  background: var(--color-gray-50);
}

/* Анимации */
.notification-enter-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
  height: 0;
  margin: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.95);
  height: 0;
  margin: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.notification-move {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Адаптивность */
@media (max-width: 480px) {
  .notification-container {
    left: 1rem;
    right: 1rem;
    top: 1rem;
  }
  
  .notifications-list {
    min-width: auto;
    max-width: none;
  }
  
  .notification {
    padding: 0.75rem;
  }
  
  .notification-message {
    font-size: 0.8125rem;
  }
  
  .notification:hover {
    transform: translateY(-2px);
  }
}

/* Темная тема (если нужно) */
@media (prefers-color-scheme: dark) {
  .notification {
    background: var(--color-gray-800);
    color: var(--color-gray-100);
  }
  
  .notification-message {
    color: var(--color-gray-100);
  }
  
  .notification-time {
    color: var(--color-gray-400);
  }
  
  .notification-close {
    color: var(--color-gray-500);
  }
  
  .notification-close:hover {
    color: var(--color-gray-200);
    background: var(--color-gray-700);
  }
}
</style> 