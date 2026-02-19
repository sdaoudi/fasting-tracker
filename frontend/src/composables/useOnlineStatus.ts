import { ref, onMounted, onUnmounted } from 'vue'

const isOnline = ref(navigator.onLine)

function update() {
  isOnline.value = navigator.onLine
}

export function useOnlineStatus() {
  onMounted(() => {
    window.addEventListener('online', update)
    window.addEventListener('offline', update)
  })

  onUnmounted(() => {
    window.removeEventListener('online', update)
    window.removeEventListener('offline', update)
  })

  return { isOnline }
}
