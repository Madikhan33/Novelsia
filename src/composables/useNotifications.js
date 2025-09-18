import { ref, reactive, nextTick } from 'vue'

export function useNotifications() {
  const notifications = ref([])
  const maxNotifications = 5
  
  let notificationId = 0
  
  const addNotification = (message, type = 'success', duration = 4000) => {
    const id = ++notificationId
    
    const notification = {
      id,
      message,
      type,
      timestamp: Date.now(),
      isVisible: false
    }
    
    // Добавляем уведомление
    notifications.value.push(notification)
    
    // Ограничиваем количество уведомлений
    if (notifications.value.length > maxNotifications) {
      notifications.value.shift()
    }
    
    // Показываем с анимацией
    nextTick(() => {
      const notif = notifications.value.find(n => n.id === id)
      if (notif) notif.isVisible = true
    })
    
    // Автоудаление
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, duration)
    }
    
    return id
  }
  
  const removeNotification = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index !== -1) {
      notifications.value[index].isVisible = false
      
      // Удаляем после анимации
      setTimeout(() => {
        const currentIndex = notifications.value.findIndex(n => n.id === id)
        if (currentIndex !== -1) {
          notifications.value.splice(currentIndex, 1)
        }
      }, 300)
    }
  }
  
  const clearAll = () => {
    notifications.value.forEach(n => n.isVisible = false)
    setTimeout(() => {
      notifications.value.length = 0
    }, 300)
  }
  
  // Быстрые методы для разных типов
  const success = (message, duration) => addNotification(message, 'success', duration)
  const error = (message, duration) => addNotification(message, 'error', duration)
  const info = (message, duration) => addNotification(message, 'info', duration)
  const warning = (message, duration) => addNotification(message, 'warning', duration)
  
  return {
    notifications,
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    info,
    warning
  }
} 