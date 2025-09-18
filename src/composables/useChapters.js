import { ref, reactive, computed, watch, nextTick } from 'vue'
import { onMounted } from 'vue'
import { apiClient } from '../services/api.js'

// Helper for API calls using the global API client
async function apiCall(endpoint, method = 'GET', body = null, isFile = false) {
  if (isFile) {
    return await apiClient.request(endpoint, {
      method,
      body: body,
      headers: {} // Remove Content-Type for FormData
    })
  }
  
  return await apiClient.request(endpoint, {
    method,
    body: body ? JSON.stringify(body) : undefined
  })
}

// Оптимизированное управление главами и книгами
export function useChapters() {
  // Реактивное состояние
  const chapters = ref([])
  const books = ref([]) // List of books
  const currentBookId = ref(null) // ID of the currently active book
  const currentChapter = reactive({
    id: null,
    title: '',
    content: '',
    created: null,
    lastModified: null,
    chapterNumber: null, // Link chapter to book
    bookId: null
  })
  
  const isDirty = ref(false)
  const isLoading = ref(false)
  const searchQuery = ref('')
  
  // Вычисляемые свойства с мемоизацией
  const sortedChapters = computed(() => {
    return [...chapters.value].sort((a, b) => 
      new Date(b.lastModified) - new Date(a.lastModified)
    )
  })
  
  // Новое вычисляемое свойство для глав с правильной нумерацией
  const orderedChapters = computed(() => {
    return [...chapters.value].sort((a, b) => {
      // Сначала сортируем по номеру главы
      if (a.chapterNumber !== b.chapterNumber) {
        return a.chapterNumber - b.chapterNumber
      }
      // Если номера одинаковые, сортируем по дате создания
      return new Date(a.created) - new Date(b.created)
    })
  })
  
  const filteredChapters = computed(() => {
    if (!searchQuery.value.trim()) return orderedChapters.value
    
    const query = searchQuery.value.toLowerCase()
    return orderedChapters.value.filter(chapter => 
      chapter.title.toLowerCase().includes(query) ||
      chapter.content.toLowerCase().includes(query)
    )
  })
  
  const wordCount = computed(() => {
    return currentChapter.content.trim() 
      ? currentChapter.content.trim().split(/\s+/).length 
      : 0
  })
  
  const totalWords = computed(() => {
    return chapters.value.reduce((sum, chapter) => sum + (chapter.words || 0), 0)
  })
  
  const chaptersStats = computed(() => ({
    total: chapters.value.length,
    totalWords: totalWords.value,
    avgWords: chapters.value.length 
      ? Math.round(totalWords.value / chapters.value.length) 
      : 0,
    lastModified: chapters.value.length 
      ? new Date(Math.max(...chapters.value.map(c => new Date(c.lastModified))))
      : null
  }))
  
  // Утилиты
  const generateId = (prefix = '') => {
    // Для локальных ID используем отрицательные числа, чтобы не конфликтовать с бэкендом
    return -(Date.now() + Math.floor(Math.random() * 1000))
  }
  
  // Генерация номера главы
  const generateChapterNumber = () => {
    if (chapters.value.length === 0) return 1
    const maxNumber = Math.max(...chapters.value.map(c => c.chapterNumber || 0))
    return maxNumber + 1
  }
  
  // Перенумерация глав
  const reorderChapters = () => {
    const sorted = [...chapters.value].sort((a, b) => {
      if (a.chapterNumber !== b.chapterNumber) {
        return a.chapterNumber - b.chapterNumber
      }
      return new Date(a.created) - new Date(b.created)
    })
    
    sorted.forEach((chapter, index) => {
      chapter.chapterNumber = index + 1
    })
    
    chapters.value = sorted
  }
  
  const debounce = (func, wait) => {
    let timeout
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout)
        func(...args)
      }
      clearTimeout(timeout)
      timeout = setTimeout(later, wait)
    }
  }
  
  // Локальное хранилище с оптимизацией
  const loadChapters = async (bookIdToLoad = currentBookId.value) => {
    if (!bookIdToLoad) {
      chapters.value = []
      currentChapter.id = null
      currentChapter.title = ''
      currentChapter.content = ''
      currentChapter.created = null
      currentChapter.lastModified = null
      currentChapter.chapterNumber = null
      currentChapter.bookId = null
      isDirty.value = false
      return
    }

    try {
      isLoading.value = true
      
      // Попробуем загрузить главы из API
      try {
        // Используем правильный эндпоинт для получения глав
        const response = await apiCall(`/chapters/?novel_id=${bookIdToLoad}`, 'GET')
        chapters.value = response.chapters || response || []
        
        // Преобразуем данные из бэкенда в формат фронтенда
        chapters.value = chapters.value.map(chapter => ({
          id: chapter.id,
          title: chapter.title,
          content: chapter.content,
          created: chapter.created_at,
          lastModified: chapter.updated_at,
          chapterNumber: chapter.chapter_number,
          bookId: chapter.novel_id,
          words: chapter.content ? chapter.content.trim().split(/\s+/).length : 0
        }))
      } catch (apiError) {
        console.warn('API недоступен, используем локальные данные:', apiError)
        // Fallback: загружаем из localStorage
        const saved = localStorage.getItem('novelsia_chapters')
        const allChapters = saved ? JSON.parse(saved) : []
        chapters.value = allChapters.filter(c => c.bookId === bookIdToLoad)
      }
      
      let hasUnnumberedChapters = false
      chapters.value.forEach((chapter, index) => {
        if (!chapter.chapterNumber) {
          chapter.chapterNumber = index + 1
          hasUnnumberedChapters = true
        }
      })
      
      if (hasUnnumberedChapters) {
        try {
          await saveChapters() // Save updated numbers back to backend
        } catch (saveError) {
          console.warn('Не удалось сохранить через API, сохраняем локально')
          const saved = localStorage.getItem('novelsia_chapters')
          const allChapters = saved ? JSON.parse(saved) : []
          const otherChapters = allChapters.filter(c => c.bookId !== bookIdToLoad)
          localStorage.setItem('novelsia_chapters', JSON.stringify([...otherChapters, ...chapters.value]))
        }
      }
      
      // Load first chapter if available, or create new if not
      if (chapters.value.length > 0) {
        loadChapter(chapters.value[0])
      } else {
        createNewChapter(bookIdToLoad)
      }

      await nextTick()
    } catch (error) {
      console.error('Ошибка загрузки глав:', error)
      chapters.value = []
    } finally {
      isLoading.value = false
    }
  }
  
  const saveChapters = debounce(async () => {
    try {
      if (!currentBookId.value) return
      
      // Попробуем сохранить через API
      try {
        // Fetch existing chapters from backend to compare
        const response = await apiCall(`/chapters/?novel_id=${currentBookId.value}`, 'GET')
        const existingBackendChapters = response.chapters || response || []
        const existingBackendChapterIds = new Set(existingBackendChapters.map(c => c.id))

        for (const chapter of chapters.value) {
          const chapterData = {
            title: chapter.title,
            content: chapter.content,
            chapter_number: chapter.chapterNumber,
            novel_id: chapter.bookId
          }

          // Если ID отрицательный, это новая глава
          if (chapter.id < 0 || !existingBackendChapterIds.has(chapter.id)) {
            const newChapter = await apiCall('/chapters/', 'POST', chapterData)
            // Обновляем ID главы на реальный ID из бэкенда
            chapter.id = newChapter.id
          } else {
            await apiCall(`/chapters/${chapter.id}`, 'PUT', chapterData)
          }
        }

        // Delete removed chapters
        const currentFrontendChapterIds = new Set(chapters.value.map(c => c.id))
        for (const backendChapter of existingBackendChapters) {
          if (!currentFrontendChapterIds.has(backendChapter.id)) {
            await apiCall(`/chapters/${backendChapter.id}`, 'DELETE')
          }
        }
      } catch (apiError) {
        console.warn('API недоступен, сохраняем локально:', apiError)
        // Fallback: сохраняем в localStorage
        const saved = localStorage.getItem('novelsia_chapters')
        const allChapters = saved ? JSON.parse(saved) : []
        const otherChapters = allChapters.filter(c => c.bookId !== currentBookId.value)
        localStorage.setItem('novelsia_chapters', JSON.stringify([...otherChapters, ...chapters.value]))
      }

      // Update book metadata
      const currentBook = books.value.find(b => b.id === currentBookId.value)
      if (currentBook) {
        currentBook.lastModified = new Date().toISOString()
        localStorage.setItem('novelsia_books', JSON.stringify(books.value))
      }

    } catch (error) {
      console.error('Ошибка сохранения глав:', error)
      // Даже при ошибке попробуем сохранить локально
      try {
        const saved = localStorage.getItem('novelsia_chapters')
        const allChapters = saved ? JSON.parse(saved) : []
        const otherChapters = allChapters.filter(c => c.bookId !== currentBookId.value)
        localStorage.setItem('novelsia_chapters', JSON.stringify([...otherChapters, ...chapters.value]))
      } catch (localError) {
        console.error('Ошибка локального сохранения:', localError)
      }
    }
  }, 300)

  // New: Save/Load book metadata
  const saveCurrentBook = debounce(() => {
    try {
      if (!currentBookId.value) return
      const bookIndex = books.value.findIndex(b => b.id === currentBookId.value)
      if (bookIndex !== -1) {
        const currentBook = books.value[bookIndex]
        // Update book title if needed from somewhere (e.g., NavBar input)
        // For now, let's assume bookTitle in App.vue is handled separately
        // TODO: Replace with actual API call to update book metadata
        localStorage.setItem('novelsia_books', JSON.stringify(books.value))
      }
    } catch (error) {
      console.error('Ошибка сохранения книги:', error)
      throw new Error('Не удалось сохранить данные книги')
    }
  }, 500)

  const fetchBooks = async () => {
    try {
      isLoading.value = true
      
      // Попробуем загрузить книги из API
      try {
        const response = await apiCall('/novels/', 'GET')
        books.value = response.novels || []
        
        // Преобразуем данные из бэкенда в формат фронтенда
        books.value = books.value.map(book => ({
          id: book.id,
          title: book.title,
          description: book.description,
          created_at: book.created_at,
          updated_at: book.updated_at,
          author_id: book.author_id,
          is_public: book.is_public,
          status: book.status
        }))
      } catch (apiError) {
        console.warn('API недоступен, используем локальные данные:', apiError)
        // Fallback: загружаем из localStorage
        const savedBooks = localStorage.getItem('novelsia_books')
        books.value = savedBooks ? JSON.parse(savedBooks) : []
      }

      if (books.value.length === 0) {
        // Создаем книгу по умолчанию через API
        try {
          const newBook = await apiCall('/novels/', 'POST', {
            title: 'Моя первая книга',
            description: 'Описание моей первой книги',
            is_public: false
          })
          books.value = [newBook]
          currentBookId.value = newBook.id
          localStorage.setItem('currentBookId', newBook.id.toString())
        } catch (createError) {
          console.warn('Не удалось создать книгу через API, используем локальную:', createError)
          // Fallback: создаем локально
          const defaultBook = {
            id: 1,
            title: 'Моя первая книга',
            created_at: new Date().toISOString()
          }
          books.value = [defaultBook]
          currentBookId.value = 1
          localStorage.setItem('novelsia_books', JSON.stringify(books.value))
          localStorage.setItem('currentBookId', '1')
        }
      } else if (!currentBookId.value) {
        // Попытаемся восстановить последнюю выбранную книгу
        const savedBookId = localStorage.getItem('currentBookId')
        if (savedBookId && books.value.find(book => book.id === parseInt(savedBookId))) {
          currentBookId.value = parseInt(savedBookId)
        } else {
          currentBookId.value = books.value[0].id
          localStorage.setItem('currentBookId', currentBookId.value.toString())
        }
      }

      await loadChapters(currentBookId.value)
    } catch (error) {
      console.error('Ошибка загрузки книг:', error)
      // Полный fallback - создаем базовую структуру
      const defaultBook = {
        id: 1,
        title: 'Моя первая книга',
        created_at: new Date().toISOString()
      }
      books.value = [defaultBook]
      currentBookId.value = 1
      localStorage.setItem('novelsia_books', JSON.stringify(books.value))
      localStorage.setItem('currentBookId', '1')
    } finally {
      isLoading.value = false
    }
  }

  const uploadBook = async (file) => {
    isLoading.value = true
    try {
      const formData = new FormData()
      formData.append('file', file)

      // Replace with actual API call to upload book file
      const newBook = await apiCall('/novels/upload', 'POST', formData, true)
      
      // After successful upload, refresh the books list and switch to the new book
      await fetchBooks() // This will also set currentBookId

    } catch (error) {
      console.error('Ошибка загрузки книги:', error)
      throw new Error(`Ошибка загрузки книги: ${error.message}`)
    } finally {
      isLoading.value = false
    }
  }



  const loadBook = async (bookId) => {
    if (currentBookId.value === bookId) return

    // Save current book's chapters before switching (will be handled by saveChapters API call)
    if (isDirty.value && currentBookId.value) {
      await saveChapters() // Ensure chapters of the current book are saved
    }

    currentBookId.value = bookId
    localStorage.setItem('currentBookId', bookId.toString())
    // loadChapters will be triggered by the watch effect on currentBookId

    // Update book title in Navbar (handled by App.vue which gets bookTitle from here)
  }

  // Управление главами
  const markDirty = () => {
    isDirty.value = true
    saveCurrentBook() // Mark book dirty when chapters change
  }
  
  const markClean = () => {
    isDirty.value = false
  }
  
  const saveCurrentChapter = () => {
    if (!currentChapter.content.trim() && !currentChapter.title.trim()) {
      throw new Error('Нечего сохранять')
    }
    if (!currentBookId.value) {
      throw new Error('Нет выбранной книги для сохранения главы')
    }
    
    const chapterData = {
      id: currentChapter.id || generateId(), // Генерируем временный ID для новых глав
      title: currentChapter.title.trim() || 'Без названия',
      content: currentChapter.content,
      words: wordCount.value,
      lastModified: new Date().toISOString(),
      created: currentChapter.created || new Date().toISOString(),
      chapterNumber: currentChapter.chapterNumber || generateChapterNumber(),
      bookId: currentBookId.value // Associate chapter with current book
    }
    
    const existingIndex = chapters.value.findIndex(c => c.id === chapterData.id)
    
    if (existingIndex !== -1) {
      const existingChapter = chapters.value[existingIndex]
      chapterData.chapterNumber = existingChapter.chapterNumber
      chapters.value[existingIndex] = chapterData
    } else {
      chapters.value.push(chapterData)
    }
    
    currentChapter.id = chapterData.id
    currentChapter.created = chapterData.created
    currentChapter.chapterNumber = chapterData.chapterNumber
    currentChapter.bookId = chapterData.bookId
    
    saveChapters()
    markClean()
    
    return chapterData
  }
  
  const loadChapter = (chapter) => {
    currentChapter.id = chapter.id
    currentChapter.title = chapter.title
    currentChapter.content = chapter.content
    currentChapter.created = chapter.created
    currentChapter.lastModified = chapter.lastModified
    currentChapter.chapterNumber = chapter.chapterNumber
    currentChapter.bookId = chapter.bookId // Load bookId with chapter
    markClean()
  }
  
  const createNewChapter = (bookIdToAssociate = currentBookId.value) => {
    currentChapter.id = null
    currentChapter.title = ''
    currentChapter.content = ''
    currentChapter.created = null
    currentChapter.lastModified = null
    currentChapter.chapterNumber = null
    currentChapter.bookId = bookIdToAssociate
    markClean()
  }
  
  const deleteChapter = (chapterId) => {
    const index = chapters.value.findIndex(c => c.id === chapterId && c.bookId === currentBookId.value)
    if (index === -1) return false
    
    chapters.value.splice(index, 1)
    
    if (currentChapter.id === chapterId) {
      createNewChapter(currentBookId.value)
    }
    
    reorderChapters()
    saveChapters()
    return true
  }
  
  const duplicateChapter = (chapterId) => {
    const chapter = chapters.value.find(c => c.id === chapterId && c.bookId === currentBookId.value)
    if (!chapter) return null
    
    const duplicated = {
      ...chapter,
      id: generateId(),
      title: `${chapter.title} (копия)`,
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      chapterNumber: generateChapterNumber(),
      bookId: currentBookId.value
    }
    
    chapters.value.push(duplicated)
    saveChapters()
    return duplicated
  }
  
  const updateChapterTitle = (chapterId, newTitle) => {
    const chapter = chapters.value.find(c => c.id === chapterId && c.bookId === currentBookId.value)
    if (!chapter) return false
    
    chapter.title = newTitle.trim() || 'Без названия'
    chapter.lastModified = new Date().toISOString()
    
    saveChapters()
    return true
  }
  
  const exportChapters = (format = 'json') => {
    // Filter chapters by current book ID for export
    const chaptersToExport = chapters.value.filter(c => c.bookId === currentBookId.value)
    const currentBook = books.value.find(b => b.id === currentBookId.value)
    const bookTitleForExport = currentBook ? currentBook.title : 'Безымянная книга'

    const data = {
      bookTitle: bookTitleForExport,
      chapters: chaptersToExport,
      exported: new Date().toISOString(),
      version: '2.0'
    }
    
    if (format === 'json') {
      return JSON.stringify(data, null, 2)
    }
    
    if (format === 'txt') {
      return chaptersToExport.map(chapter => 
        `# ${chapter.title}\n\n${chapter.content}\n\n---\n\n`
      ).join('')
    }
    
    return data
  }
  
  const importChapters = (data, merge = true) => {
    if (!currentBookId.value) {
      throw new Error('Выберите книгу для импорта глав')
    }

    try {
      let imported = []
      
      if (typeof data === 'string') {
        const parsed = JSON.parse(data)
        imported = parsed.chapters || parsed
      } else {
        imported = data.chapters || data
      }
      
      if (!Array.isArray(imported)) {
        throw new Error('Неверный формат данных')
      }
      
      const validChapters = imported.filter(chapter =>
        chapter &&
        typeof chapter.title === 'string' &&
        typeof chapter.content === 'string'
      ).map(chapter => ({
        ...chapter,
        id: generateId(),
        lastModified: chapter.lastModified || new Date().toISOString(),
        created: chapter.created || new Date().toISOString(),
        bookId: currentBookId.value // Associate imported chapters with current book
      }))
      
      if (merge) {
        // Only merge chapters for the current book
        const existingChaptersForCurrentBook = chapters.value.filter(c => c.bookId === currentBookId.value)
        chapters.value = [...chapters.value.filter(c => c.bookId !== currentBookId.value), ...validChapters]
      } else {
        // Replace chapters only for the current book
        chapters.value = [...chapters.value.filter(c => c.bookId !== currentBookId.value), ...validChapters]
      }
      
      saveChapters()
      return validChapters.length
    } catch (error) {
      console.error('Ошибка импорта:', error)
      throw new Error('Не удалось импортировать данные')
    }
  }
  
  const searchChapters = (query) => {
    searchQuery.value = query
  }
  
  let autoSaveInterval = null
  
  const startAutoSave = (intervalMs = 30000) => {
    if (autoSaveInterval) clearInterval(autoSaveInterval)
    
    autoSaveInterval = setInterval(() => {
      if (isDirty.value && (currentChapter.content.trim() || currentChapter.title.trim())) {
        try {
          saveCurrentChapter()
        } catch (error) {
          console.warn('Автосохранение пропущено:', error.message)
        }
      }
    }, intervalMs)
  }
  
  const stopAutoSave = () => {
    if (autoSaveInterval) {
      clearInterval(autoSaveInterval)
      autoSaveInterval = null
    }
  }
  
  watch([() => currentChapter.title, () => currentChapter.content], markDirty, { deep: true })
  
  // New: Watch currentBookId to trigger chapter loading
  watch(currentBookId, (newBookId, oldBookId) => {
    if (newBookId !== oldBookId && newBookId) {
      loadChapters(newBookId)
    }
  })

  // Наблюдаем за изменением текущей книги и загружаем главы
  watch(currentBookId, async (newBookId) => {
    if (newBookId) {
      await loadChapters(newBookId)
      // Если после загрузки глав нет, создаем новую
      if (chapters.value.length === 0) {
        createNewChapter(newBookId)
      } else {
        // Загружаем последнюю главу как текущую
        const lastChapter = sortedChapters.value[0]
        if (lastChapter) {
          loadChapter(lastChapter)
        }
      }
    }
  }, { immediate: true }) // Запускаем сразу при инициализации

  // Initial load: Try to load a book based on URL or first available
  onMounted(async () => {
    await fetchBooks()
  })

  return {
    chapters: chapters,
    currentChapter,
    isDirty,
    isLoading,
    searchQuery,
    books, // books state
    currentBookId, // currentBookId state
    
    sortedChapters,
    orderedChapters,
    filteredChapters,
    wordCount,
    totalWords,
    chaptersStats,
    
    loadChapters,
    saveChapters,
    saveCurrentChapter,
    loadChapter,
    createNewChapter,
    deleteChapter,
    duplicateChapter,
    exportChapters,
    importChapters,
    searchChapters,
    markDirty,
    markClean,
    startAutoSave,
    stopAutoSave,
    reorderChapters,
    generateChapterNumber,
    updateChapterTitle,
    fetchBooks, // fetchBooks method
    uploadBook, // uploadBook method
    loadBook // loadBook method
  }
} 