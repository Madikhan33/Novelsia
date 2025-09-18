<template>
  <div 
    class="chapter-card"
    :class="{ 
      'chapter-active': isActive,
      'chapter-highlighted': isHighlighted 
    }"
    @click="$emit('load')"
  >
    <div class="chapter-content">
      <!-- Заголовок главы -->
      <div class="chapter-header">
        <h4 class="chapter-title" v-html="highlightedTitle"></h4>
        <div class="chapter-actions" @click.stop>
          <button 
            @click="$emit('load')"
            class="action-btn action-load"
            title="Открыть главу"
          >
            <EditIcon />
          </button>
          <button 
            @click="$emit('duplicate')"
            class="action-btn action-duplicate"
            title="Создать копию"
          >
            <CopyIcon />
          </button>
          <button 
            @click="handleDelete"
            class="action-btn action-delete"
            title="Удалить главу"
          >
            <TrashIcon />
          </button>
        </div>
      </div>
      
      <!-- Метаданные -->
      <div class="chapter-meta">
        <div class="meta-item">
          <WordCountIcon class="meta-icon" />
          <span class="meta-text">{{ formatWordCount(chapter.words) }} слов</span>
        </div>
        <div class="meta-item">
          <ClockIcon class="meta-icon" />
          <span class="meta-text">{{ formatDate(chapter.lastModified) }}</span>
        </div>
        <div v-if="readingTime" class="meta-item">
          <BookOpenIcon class="meta-icon" />
          <span class="meta-text">{{ readingTime }} мин</span>
        </div>
      </div>
      
      <!-- Предпросмотр содержимого -->
      <div v-if="chapter.content" class="chapter-preview">
        <div class="preview-text" v-html="highlightedPreview"></div>
        <div v-if="chapter.content.length > previewLength" class="preview-more">
          <span class="preview-more-text">+{{ chapter.content.length - previewLength }} символов</span>
        </div>
      </div>
      
      <!-- Индикатор состояния -->
      <div v-if="isActive" class="active-indicator">
        <div class="active-pulse"></div>
        <span class="active-text">Редактируется</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

// Иконки
const EditIcon = { template: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="m18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>' }
const CopyIcon = { template: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"></rect><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"></path></svg>' }
const TrashIcon = { template: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3,6 5,6 21,6"></polyline><path d="m19,6v14a2,2 0,0 1,-2,2H7a2,2 0,0 1,-2,-2V6m3,0V4a2,2 0,0 1,2,-2h4a2,2 0,0 1,2,2v2"></path></svg>' }
const WordCountIcon = { template: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14,2 14,8 20,8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>' }
const ClockIcon = { template: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12,6 12,12 16,14"></polyline></svg>' }
const BookOpenIcon = { template: '<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>' }

export default {
  name: 'ChapterCard',
  components: {
    EditIcon,
    CopyIcon,
    TrashIcon,
    WordCountIcon,
    ClockIcon,
    BookOpenIcon
  },
  props: {
    chapter: {
      type: Object,
      required: true
    },
    isActive: {
      type: Boolean,
      default: false
    },
    searchQuery: {
      type: String,
      default: ''
    }
  },
  emits: ['load', 'delete', 'duplicate'],
  setup(props, { emit }) {
    const previewLength = 120
    
    // Вычисляемые свойства
    const isHighlighted = computed(() => {
      return props.searchQuery && props.searchQuery.trim().length > 0
    })
    
    const readingTime = computed(() => {
      // Расчет времени чтения (200 слов в минуту)
      if (!props.chapter.words || props.chapter.words < 50) return null
      return Math.ceil(props.chapter.words / 200)
    })
    
    const highlightedTitle = computed(() => {
      if (!props.searchQuery.trim()) return props.chapter.title
      
      const query = props.searchQuery.trim()
      const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi')
      return props.chapter.title.replace(regex, '<mark>$1</mark>')
    })
    
    const highlightedPreview = computed(() => {
      const preview = getPreview(props.chapter.content)
      if (!props.searchQuery.trim()) return preview
      
      const query = props.searchQuery.trim()
      const regex = new RegExp(`(${escapeRegExp(query)})`, 'gi')
      return preview.replace(regex, '<mark>$1</mark>')
    })
    
    // Методы
    const escapeRegExp = (string) => {
      return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    }
    
    const getPreview = (content) => {
      if (!content) return ''
      const cleaned = content.replace(/\s+/g, ' ').trim()
      return cleaned.length > previewLength 
        ? cleaned.substring(0, previewLength) + '...'
        : cleaned
    }
    
    const formatWordCount = (count) => {
      if (!count) return '0'
      if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'K'
      }
      return count.toString()
    }
    
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) {
        return 'Сегодня'
      } else if (diffDays === 2) {
        return 'Вчера'
      } else if (diffDays <= 7) {
        return `${diffDays - 1} дн. назад`
      } else if (diffDays <= 30) {
        return `${Math.floor(diffDays / 7)} нед. назад`
      } else {
        return date.toLocaleDateString('ru-RU', {
          day: '2-digit',
          month: '2-digit',
          year: '2-digit'
        })
      }
    }
    
    const handleDelete = () => {
      if (confirm(`Вы уверены, что хотите удалить главу "${props.chapter.title}"?`)) {
        emit('delete')
      }
    }
    
    return {
      previewLength,
      isHighlighted,
      readingTime,
      highlightedTitle,
      highlightedPreview,
      formatWordCount,
      formatDate,
      handleDelete
    }
  }
}
</script>

<style scoped>
.chapter-card {
  background: var(--color-white);
  border: 1px solid var(--color-border);
  border-radius: var(--border-radius);
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: var(--transition);
  position: relative;
  overflow: hidden;
}

.chapter-card:hover {
  border-color: var(--color-gray-300);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.chapter-active {
  border-color: var(--color-primary);
  background: var(--color-gray-50);
  box-shadow: var(--shadow-sm);
}

.chapter-highlighted {
  border-color: var(--color-primary);
}

.chapter-content {
  padding: 1rem;
}

.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 0.75rem;
}

.chapter-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-primary);
  line-height: 1.4;
  flex: 1;
  word-break: break-word;
}

.chapter-title :deep(mark) {
  background: #fef3c7;
  color: #92400e;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  font-weight: 600;
}

.chapter-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: var(--transition);
  flex-shrink: 0;
}

.chapter-card:hover .chapter-actions {
  opacity: 1;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  background: none;
  border: 1px solid transparent;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
  color: var(--color-gray-500);
}

.action-load:hover {
  background: #dbeafe;
  color: #2563eb;
  border-color: #93c5fd;
}

.action-duplicate:hover {
  background: #f3e8ff;
  color: #7c3aed;
  border-color: #c4b5fd;
}

.action-delete:hover {
  background: #fee2e2;
  color: #dc2626;
  border-color: #fca5a5;
}

.chapter-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--color-secondary);
}

.meta-icon {
  flex-shrink: 0;
  opacity: 0.7;
}

.meta-text {
  font-weight: 500;
}

.chapter-preview {
  position: relative;
}

.preview-text {
  font-size: 0.875rem;
  color: var(--color-gray-600);
  line-height: 1.5;
  font-family: var(--font-content);
}

.preview-text :deep(mark) {
  background: #fef3c7;
  color: #92400e;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
}

.preview-more {
  margin-top: 0.5rem;
}

.preview-more-text {
  font-size: 0.75rem;
  color: var(--color-gray-400);
  font-style: italic;
}

.active-indicator {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: var(--color-primary);
  color: var(--color-white);
  padding: 0.25rem 0.5rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.active-pulse {
  width: 0.5rem;
  height: 0.5rem;
  background: #10b981;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

.active-text {
  white-space: nowrap;
}

/* Адаптивность */
@media (max-width: 768px) {
  .chapter-content {
    padding: 0.75rem;
  }
  
  .chapter-header {
    margin-bottom: 0.5rem;
  }
  
  .chapter-title {
    font-size: 0.9375rem;
  }
  
  .chapter-actions {
    opacity: 1; /* Всегда показываем на мобильных */
  }
  
  .action-btn {
    width: 2rem;
    height: 2rem;
  }
  
  .chapter-meta {
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }
  
  .active-indicator {
    position: static;
    margin-top: 0.5rem;
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .chapter-header {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
  
  .chapter-actions {
    justify-content: flex-end;
  }
  
  .chapter-meta {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .meta-item {
    justify-content: space-between;
  }
}
</style> 