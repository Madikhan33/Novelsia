<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click="$emit('cancel')">
      <div class="modal-container" @click.stop>
        <div class="modal-content">
          <div class="modal-header">
            <h3 class="modal-title">{{ title }}</h3>
            <button @click="$emit('cancel')" class="close-btn">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>
          
          <div class="modal-body">
            <p class="modal-message">{{ message }}</p>
          </div>
          
          <div class="modal-footer">
            <button @click="$emit('cancel')" class="btn btn-secondary">
              Отмена
            </button>
            <button @click="$emit('confirm')" class="btn btn-primary">
              Продолжить
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'ConfirmModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Подтверждение'
    },
    message: {
      type: String,
      default: 'Вы уверены?'
    }
  },
  emits: ['confirm', 'cancel'],
  mounted() {
    document.addEventListener('keydown', this.handleKeydown)
  },
  unmounted() {
    document.removeEventListener('keydown', this.handleKeydown)
  },
  methods: {
    handleKeydown(event) {
      if (this.isOpen && event.key === 'Escape') {
        this.$emit('cancel')
      }
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
}

.modal-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  max-width: 400px;
  width: 90%;
  margin: 1rem;
  animation: slideUp 0.3s ease-out;
}

.modal-content {
  padding: 0;
}

.modal-header {
  padding: 1.5rem 1.5rem 0 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  line-height: 1.3;
}

.close-btn {
  background: none;
  border: none;
  padding: 0.25rem;
  cursor: pointer;
  color: #6b7280;
  transition: all 0.2s ease;
  border-radius: 0.25rem;
  margin: -0.25rem -0.25rem 0 0;
}

.close-btn:hover {
  color: #374151;
  background: #f3f4f6;
}

.modal-body {
  padding: 1rem 1.5rem;
}

.modal-message {
  color: #374151;
  margin: 0;
  line-height: 1.5;
  font-size: 0.95rem;
}

.modal-footer {
  padding: 0 1.5rem 1.5rem 1.5rem;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid;
  min-width: 80px;
  text-align: center;
}

.btn-secondary {
  background: white;
  color: #374151;
  border-color: #d1d5db;
}

.btn-secondary:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  background: #111827;
  color: white;
  border-color: #111827;
}

.btn-primary:hover {
  background: #1f2937;
  border-color: #1f2937;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@media (max-width: 480px) {
  .modal-footer {
    flex-direction: column-reverse;
  }
  
  .btn {
    width: 100%;
  }
}
</style> 