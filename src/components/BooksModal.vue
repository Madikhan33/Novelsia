<template>
  <div v-if="isOpen" class="books-modal-overlay" @click.self="$emit('close')">
    <div class="books-modal-container">
      <div class="books-modal-header">
        <h3 class="books-modal-title">Мои книги</h3>
        <button @click="$emit('close')" class="close-btn">
          &times;
        </button>
      </div>
      <div class="books-modal-content">
        <div class="book-upload-section">
          <h4>Загрузить новую книгу</h4>
          <label class="btn btn-outline">
            Выбрать файл книги
            <input
              type="file"
              accept=".json"
              @change="handleBookUpload"
              class="file-input"
            />
          </label>
          <p class="upload-hint">Поддерживаются только файлы .json.</p>
        </div>

        <div class="book-list-section">
          <h4>Ваши книги</h4>
          <ul v-if="books.length > 0" class="book-list">
            <li v-for="book in books" :key="book.id" class="book-item">
              <span class="book-title">{{ book.title || 'Безымянная книга' }}</span>
              <button @click="$emit('load-book', book.id)" class="btn btn-sm btn-outline">Открыть</button>
            </li>
          </ul>
          <p v-else class="no-books-message">У вас пока нет загруженных книг.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  books: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'upload-book', 'load-book'])

const handleBookUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    emit('upload-book', file)
    event.target.value = '' // Clear the input after selection
  }
}
</script>

<style scoped>
.books-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(3px);
  animation: fadeIn 0.3s ease-out;
}

.books-modal-container {
  background: var(--color-white);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideInFromTop 0.3s ease-out;
}

.books-modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid var(--color-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-gray-50);
}

.books-modal-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--color-primary);
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--color-secondary);
  transition: var(--transition);
}

.close-btn:hover {
  color: var(--color-gray-700);
}

.books-modal-content {
  padding: 1.5rem;
  flex-grow: 1;
  overflow-y: auto;
  color: var(--color-text);
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.book-upload-section,
.book-list-section {
  background: var(--color-gray-50);
  border-radius: var(--border-radius);
  padding: 1.5rem;
  border: 1px solid var(--color-border);
}

h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: var(--color-primary);
}

.upload-hint {
  font-size: 0.875rem;
  color: var(--color-secondary);
  margin-top: 0.5rem;
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
  display: inline-block;
}

.file-input {
  position: absolute;
  left: 0;
  top: 0;
  opacity: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.book-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.book-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-border-light);
}

.book-item:last-child {
  border-bottom: none;
}

.book-title {
  font-weight: 500;
  color: var(--color-primary);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.no-books-message {
  color: var(--color-secondary);
  font-style: italic;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideInFromTop {
  from { transform: translateY(-50px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>