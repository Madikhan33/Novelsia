<template>
  <div class="loading-overlay">
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <div class="loading-text">{{ message }}</div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoadingOverlay',
  props: {
    message: {
      type: String,
      default: 'Загрузка...'
    }
  }
}
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  backdrop-filter: blur(2px);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem;
  background: var(--color-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-lg);
  min-width: 200px;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid var(--color-gray-200);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: var(--color-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  text-align: center;
}
</style> 