<template>
  <div class="inline-suggestion-container" v-if="visible && suggestion">
    <span class="suggestion-text">{{ suggestion }}</span>
    <span class="suggestion-hint">Tab для принятия</span>
  </div>
</template>

<script>
import { ref, watch, onMounted, onUnmounted } from 'vue'

export default {
  name: 'InlineSuggestion',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    suggestion: {
      type: String,
      default: ''
    },
    cursorPosition: {
      type: Object,
      default: () => ({ top: 0, left: 0 })
    }
  },
  emits: ['accept', 'dismiss'],
  setup(props, { emit }) {
    const handleKeydown = (event) => {
      if (!props.visible) return
      
      if (event.key === 'Tab') {
        event.preventDefault()
        emit('accept')
      } else if (event.key === 'Escape') {
        event.preventDefault()
        emit('dismiss')
      }
    }
    
    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
    })
    
    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
    })
    
    return {}
  }
}
</script>

<style scoped>
.inline-suggestion-container {
  position: absolute;
  z-index: 1000;
  pointer-events: none;
}

.suggestion-text {
  color: rgba(255, 255, 255, 0.5);
  font-family: inherit;
  font-size: inherit;
  line-height: inherit;
  white-space: pre;
}

.suggestion-hint {
  position: absolute;
  top: -20px;
  left: 0;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.3);
  background: rgba(0, 0, 0, 0.8);
  padding: 2px 6px;
  border-radius: 3px;
  white-space: nowrap;
}
</style>