<template>
  <!-- Overlay для затемнения фона -->
  <div 
    v-if="isOpen" 
    class="sidebar-overlay" 
    @click="$emit('close')"
  ></div>
  
  <!-- Сайдбар -->
  <div 
    class="sidebar-container"
    :class="{ 'sidebar-open': isOpen }"
  >
    <!-- Заголовок -->
    <div class="sidebar-header">
      <div class="header-content">
        <h2 class="sidebar-title">
          Главы
          <span class="chapters-count">{{ chapters.length }}</span>
        </h2>
        <p class="sidebar-subtitle">Управление главами вашего романа</p>
      </div>
      <button 
        @click="$emit('close')" 
        class="close-button"
        title="Закрыть панель"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>
    
    <!-- Содержимое -->
    <div class="sidebar-content">
      <!-- Статистика -->
      <div class="stats-section">
        <div class="stat-item">
          <div class="stat-info">
            <div class="stat-value">{{ chapters.length }}</div>
            <div class="stat-label">Всего глав</div>
          </div>
        </div>
        <div class="stat-item">
          <div class="stat-info">
            <div class="stat-value">{{ totalWords }}</div>
            <div class="stat-label">Всего слов</div>
          </div>
        </div>
      </div>
      
      <!-- Список глав -->
      <div class="chapters-section">
        <h3 class="section-title">Список глав</h3>
        
        <div v-if="chapters.length === 0" class="empty-state">
          <h4>Пока нет глав</h4>
          <p>Создайте первую главу, чтобы начать писать свой роман!</p>
          <button class="create-chapter-btn" @click="$emit('new-chapter')">
            <span>+</span>
            Создать главу
          </button>
        </div>
        
        <div v-else class="chapters-list">
          <div 
            v-for="(chapter, index) in chapters" 
            :key="chapter.id"
            class="chapter-card"
            :class="{ 
              'chapter-active': chapter.id === currentChapterId,
              'chapter-hover': true
            }"
          >
            <div class="chapter-number">{{ chapter.chapterNumber || index + 1 }}</div>
                         <div class="chapter-info">
               <div class="chapter-title-section">
                 <input
                   v-if="editingChapterId === chapter.id"
                   v-model="editingTitle"
                   @blur="saveChapterTitle(chapter.id)"
                   @keyup.enter="saveChapterTitle(chapter.id)"
                   @keyup.esc="cancelEdit"
                   class="chapter-title-input"
                   ref="titleInput"
                   placeholder="Название главы"
                 />
                 <h4 
                   v-else
                   @click="startEditTitle(chapter.id, chapter.title)"
                   class="chapter-title"
                 >
                   {{ chapter.title }}
                 </h4>
               </div>
               <div class="chapter-meta">
                 <span class="meta-item">
                   {{ formatDate(chapter.lastModified) }}
                 </span>
               </div>
             </div>
            <div class="chapter-actions">
              <button 
                @click.stop="$emit('load-chapter', chapter)"
                class="action-btn load-btn"
                title="Открыть главу"
              >
                Открыть
              </button>
              <button 
                @click.stop="$emit('duplicate-chapter', chapter.id)"
                class="action-btn duplicate-btn"
                title="Создать копию"
              >
                Копия
              </button>
              <button 
                @click.stop="deleteChapter(chapter)"
                class="action-btn delete-btn"
                title="Удалить главу"
              >
                Удалить
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, nextTick } from 'vue'

export default {
  name: 'ChaptersSidebar',
  props: {
    chapters: {
      type: Array,
      default: () => []
    },
    isOpen: {
      type: Boolean,
      default: false
    },
    currentChapterId: {
      type: String,
      default: null
    },
    isLoading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'load-chapter', 'delete-chapter', 'duplicate-chapter', 'new-chapter', 'update-chapter-title'],
  setup(props, { emit }) {
    console.log('ChaptersSidebar setup, props.isOpen:', props.isOpen)
    
    const editingChapterId = ref(null)
    const editingTitle = ref('')
    const titleInput = ref(null)
    
    const totalWords = computed(() => {
      return props.chapters.reduce((total, chapter) => total + (chapter.words || 0), 0)
    })
    
    const getChapterPreview = (content) => {
      if (!content) return 'Пустая глава'
      const cleaned = content.replace(/\s+/g, ' ').trim()
      return cleaned.length > 80 ? cleaned.substring(0, 80) + '...' : cleaned
    }
    
    const formatDate = (dateString) => {
      if (!dateString) return 'Недавно'
      const date = new Date(dateString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 1) return 'Сегодня'
      if (diffDays === 2) return 'Вчера'
      if (diffDays <= 7) return `${diffDays - 1} дн. назад`
      if (diffDays <= 30) return `${Math.floor(diffDays / 7)} нед. назад`
      
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit'
      })
    }
    
    const startEditTitle = (chapterId, currentTitle) => {
      editingChapterId.value = chapterId
      editingTitle.value = currentTitle || ''
      nextTick(() => {
        if (titleInput.value) {
          titleInput.value.focus()
          titleInput.value.select()
        }
      })
    }
    
    const saveChapterTitle = (chapterId) => {
      if (editingTitle.value.trim()) {
        emit('update-chapter-title', chapterId, editingTitle.value.trim())
      }
      editingChapterId.value = null
      editingTitle.value = ''
    }
    
    const cancelEdit = () => {
      editingChapterId.value = null
      editingTitle.value = ''
    }
    
    const deleteChapter = (chapter) => {
      if (confirm(`Вы уверены, что хотите удалить главу "${chapter.title || 'Без названия'}"?`)) {
        emit('delete-chapter', chapter.id)
      }
    }
    
    return {
      totalWords,
      getChapterPreview,
      formatDate,
      editingChapterId,
      editingTitle,
      titleInput,
      startEditTitle,
      saveChapterTitle,
      cancelEdit,
      deleteChapter
    }
  }
}
</script>

<style scoped>
.sidebar-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  backdrop-filter: blur(2px);
  animation: fadeIn 0.3s ease;
}

.sidebar-container {
  position: fixed;
  top: 0;
  right: -400px;
  width: 400px;
  height: 100vh;
  background: #ffffff;
  z-index: 1001;
  transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: -4px 0 20px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-left: 1px solid #e5e7eb;
}

.sidebar-container.sidebar-open {
  right: 0;
}

.sidebar-header {
  padding: 24px;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  position: relative;
}

.header-content {
  flex: 1;
}

.sidebar-title {
  margin: 0 0 8px 0;
  color: #111827;
  font-size: 24px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 12px;
}

.chapters-count {
  background: #111827;
  color: white;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.sidebar-subtitle {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
  font-weight: 400;
}

.close-button {
  position: absolute;
  top: 20px;
  right: 20px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  color: #374151;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-button:hover {
  background: #e5e7eb;
  color: #111827;
}

.sidebar-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background: #ffffff;
}

.stats-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 32px;
}

.stat-item {
  background: #f9fafb;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  transition: all 0.2s ease;
}

.stat-item:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.stat-info {
  flex: 1;
  text-align: center;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #111827;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 2px;
}

.chapters-section {
  flex: 1;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #111827;
  display: flex;
  align-items: center;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.empty-state h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.empty-state p {
  margin: 0 0 24px 0;
  font-size: 14px;
  line-height: 1.5;
}

.create-chapter-btn {
  background: #111827;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.create-chapter-btn:hover {
  background: #374151;
  transform: translateY(-1px);
}

.create-chapter-btn span {
  font-size: 18px;
  font-weight: 700;
}

.chapters-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chapter-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s ease;
  border: 1px solid #e5e7eb;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 16px;
  position: relative;
}

.chapter-card:hover {
  border-color: #d1d5db;
  background: #f9fafb;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chapter-active {
  border-color: #111827;
  background: #f3f4f6;
}

.chapter-number {
  background: #111827;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 14px;
  flex-shrink: 0;
}

.chapter-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  justify-content: center;
}

.chapter-title-section {
  margin-bottom: 0;
}

.chapter-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  line-height: 1.3;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  cursor: pointer;
  padding: 4px 0;
  border-radius: 4px;
  transition: background 0.2s ease;
  max-width: 100%;

}

.chapter-title:hover {
  background: #f3f4f6;
}

.chapter-title-input {
  width: 100%;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
  background: #ffffff;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  outline: none;
  font-family: inherit;
  box-sizing: border-box;
  background: #f3f4f6;
}



.chapter-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  font-size: 11px;
  color: #9ca3af;
  font-weight: 500;
}

.chapter-actions {
  display: flex;
  justify-self: end;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
  flex-shrink: 0;
  margin-left: 8px;
}

.chapter-card:hover .chapter-actions {
  opacity: 1;
}

.action-btn {
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  padding: 6px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 12px;
  font-weight: 500;
}

.action-btn:hover {
  background: #111827;
  color: white;
  border-color: #111827;
}

.delete-btn:hover {
  background: #dc2626;
  color: white;
  border-color: #dc2626;
}

/* Кастомные скроллбары */
.sidebar-content::-webkit-scrollbar {
  width: 6px;
}

.sidebar-content::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 3px;
}

.sidebar-content::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
  transition: background 0.2s ease;
}

.sidebar-content::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

/* Анимации */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .sidebar-container {
    width: 100%;
    right: -100%;
  }
  
  .stats-section {
    grid-template-columns: 1fr;
  }
  
  .sidebar-header {
    padding: 20px;
  }
  
  .sidebar-content {
    padding: 20px;
  }
}
</style> 