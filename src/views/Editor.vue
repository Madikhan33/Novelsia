<template>
  <div class="editor-app">
    <!-- Навигационная панель -->
    <NavBar 
      :current-chapter="currentChapter"
      :word-count="wordCount"
      :is-dirty="isDirty"
      :chapters-count="chaptersStats.total"
      :total-words="chaptersStats.totalWords"
      :book-title="bookTitle"
      :is-authenticated="isAuthenticated"
      :user="user"
      @save="handleSave"
      @new-chapter="handleNewChapter"
      @toggle-sidebar="toggleSidebar"
      @export="handleExport"
      @import="handleImport"
      @search="handleSearch"
      @title-change="handleTitleChange"
      @book-title-change="handleBookTitleChange"
      @toggle-books-modal="handleToggleBooksModal"
      @show-auth="authModalOpen = true"
      @logout="handleLogout"
    />

    <!-- Основной редактор -->
    <EditorMain
      ref="editorRef"
      :current-chapter="currentChapter"
      :is-loading="isLoading"
      @content-change="handleContentChange"
      @keydown="handleKeydown"
    />

    <!-- Боковая панель с главами -->
    <ChaptersSidebar 
      :chapters="filteredChapters"
      :is-open="sidebarOpen"
      :current-chapter-id="currentChapter.id"
      :is-loading="isLoading"
      @close="closeSidebar"
      @load-chapter="handleLoadChapter"
      @delete-chapter="handleDeleteChapter"
      @duplicate-chapter="handleDuplicateChapter"
      @new-chapter="handleNewChapter"
      @update-chapter-title="updateChapterTitle"
    />

    <!-- Модальные окна -->
    <ConfirmModal
      :is-open="showConfirmModal"
      :title="confirmModal.title"
      :message="confirmModal.message"
      @confirm="confirmModal.onConfirm"
      @cancel="closeConfirmModal"
    />

    <!-- Система уведомлений -->
    <NotificationContainer :notifications="notifications" @remove="removeNotification" />

    <!-- Модальное окно для книг -->
    <BooksModal
      :is-open="booksModalOpen"
      :books="books"
      @close="booksModalOpen = false"
      @upload-book="handleBookUpload"
      @load-book="handleLoadBook"
    />

    <!-- AI Подсказки (встроенная панель) -->
    <AISuggestions
      :context="currentChapter.content"
      :chapter-id="currentChapter.id"
      :novel-id="currentNovelId"
      @apply-suggestion="handleApplySuggestion"
    />

    <!-- Загрузочный индикатор -->
    <LoadingOverlay v-if="isLoading" />
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, nextTick, defineAsyncComponent } from 'vue'
import { useRouter } from 'vue-router'
import { useChapters } from '../composables/useChapters'
import { useNotifications } from '../composables/useNotifications'
import { useAuth } from '../composables/useAuth'

// Ленивая загрузка компонентов для оптимизации
const NavBar = defineAsyncComponent(() => import('../components/NavBar.vue'))
const EditorMain = defineAsyncComponent(() => import('../components/EditorMain.vue'))
const ChaptersSidebar = defineAsyncComponent(() => import('../components/ChaptersSidebar.vue'))
const ConfirmModal = defineAsyncComponent(() => import('../components/ConfirmModal.vue'))
const NotificationContainer = defineAsyncComponent(() => import('../components/NotificationContainer.vue'))
const LoadingOverlay = defineAsyncComponent(() => import('../components/LoadingOverlay.vue'))
const BooksModal = defineAsyncComponent(() => import('../components/BooksModal.vue'))
const AISuggestions = defineAsyncComponent(() => import('../components/AISuggestions.vue'))

export default {
  name: 'Editor',
  components: {
    NavBar,
    EditorMain,
    ChaptersSidebar,
    ConfirmModal,
    NotificationContainer,
    LoadingOverlay,
    BooksModal,
    AISuggestions
  },
  setup() {
    const router = useRouter()
    
    // Композабли
    const {
      chapters,
      currentChapter,
      isDirty,
      isLoading,
      searchQuery,
      filteredChapters,
      wordCount,
      chaptersStats,
      loadChapters,
      saveCurrentChapter,
      loadChapter,
      createNewChapter,
      deleteChapter,
      duplicateChapter,
      exportChapters,
      importChapters,
      searchChapters,
      markDirty,
      startAutoSave,
      stopAutoSave,
      updateChapterTitle,
      books,
      currentBookId,
      uploadBook,
      loadBook: switchBook,
      fetchBooks
    } = useChapters()

    const {
      notifications,
      removeNotification,
      success,
      error,
      info,
      warning
    } = useNotifications()

    const {
      isAuthenticated,
      user,
      checkAuth,
      logout: authLogout
    } = useAuth()

    // Локальное состояние
    const sidebarOpen = ref(false)
    const booksModalOpen = ref(false)
    const showConfirmModal = ref(false)
    const confirmModal = ref({
      title: '',
      message: '',
      onConfirm: () => {}
    })
    const editorRef = ref(null)
    const bookTitle = ref('')
    const currentNovelId = ref(1)

    // Обработчики событий
    const handleSave = async () => {
      try {
        const saved = saveCurrentChapter()
        success(`Глава "${saved.title}" сохранена!`)
      } catch (err) {
        error(err.message)
      }
    }

    const handleNewChapter = () => {
      if (isDirty.value) {
        confirmModal.value = {
          title: 'Новая глава',
          message: 'Есть несохраненные изменения. Продолжить без сохранения?',
          onConfirm: () => {
            createNewChapter()
            closeConfirmModal()
            success('Новая глава создана')
            focusEditor()
          }
        }
        showConfirmModal.value = true
      } else {
        createNewChapter()
        success('Новая глава создана')
        focusEditor()
      }
    }

    const handleToggleBooksModal = () => {
      booksModalOpen.value = !booksModalOpen.value
    }

    const handleLogout = async () => {
      try {
        await authLogout()
        success('Вы успешно вышли из системы')
        router.push('/')
      } catch (error) {
        error('Ошибка при выходе из системы')
      }
    }

    const handleBookUpload = async (file) => {
      try {
        await uploadBook(file)
        success('Книга успешно загружена!')
        booksModalOpen.value = false
      } catch (err) {
        error(`Ошибка загрузки книги: ${err.message}`)
      }
    }

    const handleLoadBook = async (bookId) => {
      try {
        await switchBook(bookId)
        success('Книга успешно загружена!')
        booksModalOpen.value = false
      } catch (err) {
        error(`Ошибка загрузки книги: ${err.message}`)
      }
    }

    const handleLoadChapter = (chapter) => {
      if (isDirty.value) {
        try {
          saveCurrentChapter()
          info('Предыдущая глава автоматически сохранена')
        } catch (err) {
          warning('Не удалось автосохранить предыдущую главу')
        }
      }

      loadChapter(chapter)
      closeSidebar()
      success(`Загружена глава: ${chapter.title}`)
      focusEditor()
    }

    const handleDeleteChapter = (chapterId) => {
      const chapter = chapters.value.find(c => c.id === chapterId)
      if (!chapter) return

      confirmModal.value = {
        title: 'Удаление главы',
        message: `Вы уверены, что хотите удалить главу "${chapter.title}"? Это действие нельзя отменить.`,
        onConfirm: () => {
          const deleted = deleteChapter(chapterId)
          if (deleted) {
            success('Глава удалена')
          } else {
            error('Не удалось удалить главу')
          }
          closeConfirmModal()
        }
      }
      showConfirmModal.value = true
    }

    const handleDuplicateChapter = (chapterId) => {
      try {
        const duplicated = duplicateChapter(chapterId)
        if (duplicated) {
          success(`Создана копия главы: ${duplicated.title}`)
        }
      } catch (err) {
        error('Не удалось создать копию главы')
      }
    }

    const handleExport = (format = 'json') => {
      try {
        const data = exportChapters(format)
        const blob = new Blob([data], { 
          type: format === 'json' ? 'application/json' : 'text/plain' 
        })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = `novelsia_export_${new Date().toISOString().split('T')[0]}.${format}`
        link.click()
        URL.revokeObjectURL(url)
        success(`Данные экспортированы в формате ${format.toUpperCase()}`)
      } catch (err) {
        error('Ошибка экспорта данных')
      }
    }

    const handleImport = async (file) => {
      try {
        const text = await file.text()
        const count = importChapters(text, true)
        success(`Импортировано ${count} глав`)
      } catch (err) {
        error('Ошибка импорта данных: ' + err.message)
      }
    }

    const handleSearch = (query) => {
      searchChapters(query)
    }

    const handleTitleChange = (title) => {
      currentChapter.title = title
      markDirty()
    }

    const handleUpdateChapterTitle = (chapterId, newTitle) => {
      const updated = updateChapterTitle(chapterId, newTitle)
      if (updated) {
        success(`Название главы обновлено: ${newTitle}`)
      } else {
        error('Не удалось обновить название главы')
      }
    }

    const handleBookTitleChange = (newTitle) => {
      bookTitle.value = newTitle
      success(`Название книги обновлено: ${newTitle}`)
    }

    const handleContentChange = (content) => {
      currentChapter.content = content
      markDirty()
    }

    const handleApplySuggestion = (suggestion) => {
      if (editorRef.value && editorRef.value.textareaRef) {
        const textarea = editorRef.value.textareaRef
        const start = textarea.selectionStart
        const end = textarea.selectionEnd
        const currentContent = currentChapter.content
        
        const beforeCursor = currentContent.substring(0, start)
        const afterCursor = currentContent.substring(end)
        
        const needsSpace = beforeCursor.length > 0 && !beforeCursor.endsWith(' ')
        const suggestionToInsert = needsSpace ? ` ${suggestion}` : suggestion
        
        currentChapter.content = beforeCursor + suggestionToInsert + afterCursor
        markDirty()
        
        nextTick(() => {
          const newPosition = start + suggestionToInsert.length
          textarea.setSelectionRange(newPosition, newPosition)
          textarea.focus()
        })
        
        success('AI подсказка применена!')
      }
    }

    const handleKeydown = (event) => {
      if (event.ctrlKey || event.metaKey) {
        switch (event.key) {
          case 's':
            event.preventDefault()
            handleSave()
            break
          case 'n':
            event.preventDefault()
            handleNewChapter()
            break
          case 'f':
            if (event.shiftKey) {
              event.preventDefault()
              toggleSidebar()
            }
            break
          case 'e':
            if (event.shiftKey) {
              event.preventDefault()
              handleExport()
            }
            break
        }
      }

      if (event.key === 'Escape') {
        closeSidebar()
        closeConfirmModal()
      }
    }

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value
    }

    const closeSidebar = () => {
      sidebarOpen.value = false
    }

    const closeConfirmModal = () => {
      showConfirmModal.value = false
    }

    const focusEditor = () => {
      nextTick(() => {
        if (editorRef.value) {
          editorRef.value.focus()
        }
      })
    }

    // Предупреждение при закрытии
    const handleBeforeUnload = (event) => {
      if (isDirty.value) {
        event.preventDefault()
        event.returnValue = 'У вас есть несохраненные изменения. Вы уверены, что хотите покинуть страницу?'
        return event.returnValue
      }
    }

    // Инициализация
    onMounted(async () => {
      try {
        await checkAuth()
        
        if (!isAuthenticated.value) {
          router.push('/')
          return
        }

        await loadChapters()
        await fetchBooks()
        startAutoSave(30000)
        focusEditor()
        
        window.addEventListener('beforeunload', handleBeforeUnload)
      } catch (err) {
        error('Ошибка при загрузке редактора')
        router.push('/')
      }
    })

    onUnmounted(() => {
      stopAutoSave()
      window.removeEventListener('beforeunload', handleBeforeUnload)
    })

    return {
      // Состояние
      currentChapter,
      isDirty,
      isLoading,
      searchQuery,
      filteredChapters,
      wordCount,
      chaptersStats,
      sidebarOpen,
      showConfirmModal,
      confirmModal,
      notifications,
      editorRef,
      bookTitle,
      chapters,
      booksModalOpen,
      books,
      isAuthenticated,
      user,
      currentNovelId,
      
      // Methods
      handleSave,
      handleNewChapter,
      handleLoadChapter,
      handleDeleteChapter,
      handleDuplicateChapter,
      handleExport,
      handleImport,
      handleSearch,
      handleTitleChange,
      handleUpdateChapterTitle,
      handleBookTitleChange,
      handleContentChange,
      handleKeydown,
      toggleSidebar,
      closeSidebar,
      closeConfirmModal,
      removeNotification,
      focusEditor,
      handleBookUpload,
      handleLoadBook,
      handleApplySuggestion,
      handleLogout,
      handleToggleBooksModal,
      updateChapterTitle
    }
  }
}
</script>

<style scoped>
.editor-app {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>