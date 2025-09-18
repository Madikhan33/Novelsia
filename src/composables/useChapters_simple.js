import { ref, reactive, computed, watch, nextTick } from 'vue'

// Упрощенное управление главами без книг
export function useChapters() {
  // Реактивное состояние
  const chapters = ref([])
  const currentChapter = reactive({
    id: null,
    title: '',
    content: '',
    created: null,
    lastModified: null,
    chapterNumber: null
  })
  
  const isDirty = ref(false)
  const isLoading = ref(false)
  const searchQuery = ref('')
  
  // Автосохранение
  let autoSaveInterval = null
  
  // Вычисляемые свойства
  const sortedChapters = computed(() => {
    return [...chapters.value].sort((a, b) => 
      new Date(b.lastModified) - new Date(a.lastModified)
    )
  })
  
  // Главы с правильной нумерацией
  const orderedChapters = computed(() => {
    return [...chapters.value].sort((a, b) => {
      if (a.chapterNumber !== b.chapterNumber) {
        return a.chapterNumber - b.chapterNumber
      }
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
    return `${prefix}${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }
  
  // Генерация номера главы
  const generateChapterNumber = () => {
    if (chapters.value.length === 0) return 1
    const maxNumber = Math.max(...chapters.value.map(c => c.chapterNumber || 0))
    return maxNumber + 1
  }
  
  // Отметка о изменениях
  const markDirty = () => {
    isDirty.value = true
  }
  
  const markClean = () => {
    isDirty.value = false
  }
  
  // Сохранение в localStorage
  const saveToStorage = () => {
    try {
      localStorage.setItem('novelsia_chapters', JSON.stringify(chapters.value))
      localStorage.setItem('novelsia_current_chapter', JSON.stringify(currentChapter))
      console.log('Данные сохранены в localStorage')
    } catch (error) {
      console.error('Ошибка сохранения в localStorage:', error)
    }
  }
  
  // Загрузка из localStorage
  const loadFromStorage = () => {
    try {
      const savedChapters = localStorage.getItem('novelsia_chapters')
      const savedCurrentChapter = localStorage.getItem('novelsia_current_chapter')
      
      if (savedChapters) {
        chapters.value = JSON.parse(savedChapters)
      }
      
      if (savedCurrentChapter) {
        const saved = JSON.parse(savedCurrentChapter)
        Object.assign(currentChapter, saved)
      }
      
      // Если нет текущей главы, создаем первую
      if (!currentChapter.id && chapters.value.length === 0) {
        createNewChapter()
      } else if (!currentChapter.id && chapters.value.length > 0) {
        loadChapter(chapters.value[0])
      }
      
      console.log('Данные загружены из localStorage')
    } catch (error) {
      console.error('Ошибка загрузки из localStorage:', error)
      createNewChapter() // Создаем новую главу при ошибке
    }
  }
  
  // Загрузка глав (заглушка для API)
  const loadChapters = async () => {
    isLoading.value = true
    try {
      // Пока используем localStorage вместо API
      loadFromStorage()
    } catch (error) {
      console.error('Ошибка загрузки глав:', error)
    } finally {
      isLoading.value = false
    }
  }
  
  // Сохранение текущей главы
  const saveCurrentChapter = () => {
    if (!currentChapter.title.trim()) {
      currentChapter.title = `Глава ${currentChapter.chapterNumber || generateChapterNumber()}`
    }
    
    const now = new Date().toISOString()
    currentChapter.lastModified = now
    currentChapter.words = wordCount.value
    
    // Обновляем или добавляем главу в массив
    const existingIndex = chapters.value.findIndex(c => c.id === currentChapter.id)
    if (existingIndex !== -1) {
      chapters.value[existingIndex] = { ...currentChapter }
    } else {
      chapters.value.push({ ...currentChapter })
    }
    
    saveToStorage()
    markClean()
    
    return { ...currentChapter }
  }
  
  // Загрузка главы
  const loadChapter = (chapter) => {
    if (isDirty.value) {
      saveCurrentChapter()
    }
    
    Object.assign(currentChapter, chapter)
    markClean()
  }
  
  // Создание новой главы
  const createNewChapter = () => {
    if (isDirty.value) {
      saveCurrentChapter()
    }
    
    const newChapter = {
      id: generateId('chapter_'),
      title: '',
      content: '',
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      chapterNumber: generateChapterNumber(),
      words: 0
    }
    
    Object.assign(currentChapter, newChapter)
    markDirty() // Помечаем как измененную, чтобы она сохранилась
    
    return newChapter
  }
  
  // Удаление главы
  const deleteChapter = (chapterId) => {
    const index = chapters.value.findIndex(c => c.id === chapterId)
    if (index === -1) return false
    
    chapters.value.splice(index, 1)
    
    // Если удалили текущую главу, загружаем другую
    if (currentChapter.id === chapterId) {
      if (chapters.value.length > 0) {
        loadChapter(chapters.value[0])
      } else {
        createNewChapter()
      }
    }
    
    saveToStorage()
    return true
  }
  
  // Дублирование главы
  const duplicateChapter = (chapterId) => {
    const chapter = chapters.value.find(c => c.id === chapterId)
    if (!chapter) return null
    
    const newChapter = {
      ...chapter,
      id: generateId('chapter_'),
      title: `${chapter.title} (копия)`,
      created: new Date().toISOString(),
      lastModified: new Date().toISOString(),
      chapterNumber: generateChapterNumber()
    }
    
    chapters.value.push(newChapter)
    saveToStorage()
    
    return newChapter
  }
  
  // Обновление названия главы
  const updateChapterTitle = (chapterId, newTitle) => {
    const chapter = chapters.value.find(c => c.id === chapterId)
    if (!chapter) return false
    
    chapter.title = newTitle
    chapter.lastModified = new Date().toISOString()
    
    if (currentChapter.id === chapterId) {
      currentChapter.title = newTitle
      markDirty()
    }
    
    saveToStorage()
    return true
  }
  
  // Экспорт глав
  const exportChapters = (format = 'json') => {
    if (format === 'json') {
      return JSON.stringify(chapters.value, null, 2)
    } else if (format === 'txt') {
      return chapters.value
        .sort((a, b) => a.chapterNumber - b.chapterNumber)
        .map(chapter => `# ${chapter.title}\n\n${chapter.content}`)
        .join('\n\n---\n\n')
    }
  }
  
  // Импорт глав
  const importChapters = (data, replace = false) => {
    try {
      let importedChapters = []
      
      if (typeof data === 'string') {
        if (data.trim().startsWith('{') || data.trim().startsWith('[')) {
          importedChapters = JSON.parse(data)
        } else {
          // Импорт из текстового формата
          const parts = data.split('\n\n---\n\n')
          importedChapters = parts.map((part, index) => {
            const lines = part.trim().split('\n')
            const title = lines[0].replace(/^#\s*/, '') || `Импортированная глава ${index + 1}`
            const content = lines.slice(2).join('\n')
            
            return {
              id: generateId('imported_'),
              title,
              content,
              created: new Date().toISOString(),
              lastModified: new Date().toISOString(),
              chapterNumber: index + 1,
              words: content.trim() ? content.trim().split(/\s+/).length : 0
            }
          })
        }
      }
      
      if (!Array.isArray(importedChapters)) {
        importedChapters = [importedChapters]
      }
      
      if (replace) {
        chapters.value = importedChapters
      } else {
        chapters.value.push(...importedChapters)
      }
      
      saveToStorage()
      return importedChapters.length
    } catch (error) {
      console.error('Ошибка импорта:', error)
      throw new Error('Неверный формат данных для импорта')
    }
  }
  
  // Поиск по главам
  const searchChapters = (query) => {
    searchQuery.value = query
  }
  
  // Автосохранение
  const startAutoSave = (interval = 30000) => {
    stopAutoSave()
    autoSaveInterval = setInterval(() => {
      if (isDirty.value) {
        saveCurrentChapter()
        console.log('Автосохранение выполнено')
      }
    }, interval)
  }
  
  const stopAutoSave = () => {
    if (autoSaveInterval) {
      clearInterval(autoSaveInterval)
      autoSaveInterval = null
    }
  }
  
  // Наблюдатель для отслеживания изменений
  watch([() => currentChapter.title, () => currentChapter.content], () => {
    markDirty()
  }, { deep: true })
  
  return {
    // Состояние
    chapters,
    currentChapter,
    isDirty,
    isLoading,
    searchQuery,
    
    // Вычисляемые свойства
    sortedChapters,
    orderedChapters,
    filteredChapters,
    wordCount,
    totalWords,
    chaptersStats,
    
    // Методы
    loadChapters,
    saveCurrentChapter,
    loadChapter,
    createNewChapter,
    deleteChapter,
    duplicateChapter,
    updateChapterTitle,
    exportChapters,
    importChapters,
    searchChapters,
    markDirty,
    markClean,
    startAutoSave,
    stopAutoSave
  }
}
