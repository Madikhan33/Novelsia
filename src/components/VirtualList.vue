<template>
  <div 
    ref="containerRef"
    class="virtual-list"
    :style="{ height: containerHeight + 'px' }"
    @scroll="handleScroll"
  >
    <div 
      class="virtual-list-spacer-before"
      :style="{ height: spacerBefore + 'px' }"
    ></div>
    
    <div class="virtual-list-items">
      <slot
        v-for="(item, index) in visibleItems"
        :key="getItemKey(item, startIndex + index)"
        :item="item"
        :index="startIndex + index"
      ></slot>
    </div>
    
    <div 
      class="virtual-list-spacer-after"
      :style="{ height: spacerAfter + 'px' }"
    ></div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

export default {
  name: 'VirtualList',
  props: {
    items: {
      type: Array,
      required: true
    },
    itemHeight: {
      type: Number,
      default: 50
    },
    containerHeight: {
      type: Number,
      default: 400
    },
    buffer: {
      type: Number,
      default: 5 // Количество элементов для предварительной загрузки
    },
    keyField: {
      type: String,
      default: 'id'
    }
  },
  setup(props) {
    const containerRef = ref(null)
    const scrollTop = ref(0)
    
    // Вычисляемые свойства
    const totalHeight = computed(() => props.items.length * props.itemHeight)
    
    const visibleCount = computed(() => Math.ceil(props.containerHeight / props.itemHeight))
    
    const startIndex = computed(() => {
      const index = Math.floor(scrollTop.value / props.itemHeight)
      return Math.max(0, index - props.buffer)
    })
    
    const endIndex = computed(() => {
      const index = startIndex.value + visibleCount.value + props.buffer * 2
      return Math.min(props.items.length - 1, index)
    })
    
    const visibleItems = computed(() => {
      return props.items.slice(startIndex.value, endIndex.value + 1)
    })
    
    const spacerBefore = computed(() => startIndex.value * props.itemHeight)
    
    const spacerAfter = computed(() => {
      const remainingItems = props.items.length - endIndex.value - 1
      return Math.max(0, remainingItems * props.itemHeight)
    })
    
    // Методы
    const handleScroll = () => {
      if (containerRef.value) {
        scrollTop.value = containerRef.value.scrollTop
      }
    }
    
    const getItemKey = (item, index) => {
      if (typeof item === 'object' && item !== null && props.keyField in item) {
        return item[props.keyField]
      }
      return index
    }
    
    const scrollToIndex = (index, behavior = 'smooth') => {
      if (!containerRef.value) return
      
      const targetScrollTop = index * props.itemHeight
      containerRef.value.scrollTo({
        top: targetScrollTop,
        behavior
      })
    }
    
    const scrollToTop = () => {
      scrollToIndex(0, 'auto')
    }
    
    const scrollToBottom = () => {
      scrollToIndex(props.items.length - 1, 'smooth')
    }
    
    // Наблюдатели
    watch(() => props.items.length, () => {
      // При изменении количества элементов корректируем скролл
      nextTick(() => {
        if (containerRef.value) {
          const maxScrollTop = Math.max(0, totalHeight.value - props.containerHeight)
          if (scrollTop.value > maxScrollTop) {
            containerRef.value.scrollTop = maxScrollTop
          }
        }
      })
    })
    
    // Жизненный цикл
    onMounted(() => {
      if (containerRef.value) {
        // Инициализируем начальную позицию скролла
        handleScroll()
      }
    })
    
    return {
      containerRef,
      scrollTop,
      visibleItems,
      startIndex,
      endIndex,
      spacerBefore,
      spacerAfter,
      totalHeight,
      handleScroll,
      getItemKey,
      scrollToIndex,
      scrollToTop,
      scrollToBottom
    }
  }
}
</script>

<style scoped>
.virtual-list {
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.virtual-list-items {
  position: relative;
}

.virtual-list-spacer-before,
.virtual-list-spacer-after {
  flex-shrink: 0;
}

/* Кастомные скроллбары */
.virtual-list::-webkit-scrollbar {
  width: 6px;
}

.virtual-list::-webkit-scrollbar-track {
  background: var(--color-gray-100);
  border-radius: 3px;
}

.virtual-list::-webkit-scrollbar-thumb {
  background: var(--color-gray-300);
  border-radius: 3px;
  transition: var(--transition);
}

.virtual-list::-webkit-scrollbar-thumb:hover {
  background: var(--color-gray-400);
}

/* Плавный скролл для поддерживаемых браузеров */
.virtual-list {
  scroll-behavior: smooth;
}

/* Стили для мобильных устройств */
@media (max-width: 768px) {
  .virtual-list::-webkit-scrollbar {
    width: 4px;
  }
}
</style> 