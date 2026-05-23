<template>
  <div class="chat-input-bar">
    <el-input
      v-model="inputText"
      type="textarea"
      :rows="2"
      :disabled="disabled"
      :placeholder="disabled ? '面试已结束' : '输入你的回答或向面试官提问...'"
      resize="none"
      @keydown.enter.exact.prevent="handleSend"
    />
    <div class="input-actions">
      <span class="input-hint">Enter 发送 · Shift+Enter 换行</span>
      <div class="action-btns">
        <el-button type="primary" :disabled="disabled || !inputText.trim() || loading" @click="handleSend">
          发送
        </el-button>
        <el-button :disabled="disabled || loading" @click="$emit('next')">
          下一题
        </el-button>
        <el-button type="danger" :disabled="disabled || loading" @click="$emit('end')">
          结束面试
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['send', 'next', 'end'])

const inputText = ref('')

function handleSend() {
  const text = inputText.value.trim()
  if (!text || props.disabled || props.loading) return
  emit('send', text)
  inputText.value = ''
}
</script>

<style scoped>
.chat-input-bar {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.input-hint {
  font-size: 12px;
  color: #94a3b8;
}

.action-btns {
  display: flex;
  gap: 8px;
}
</style>
