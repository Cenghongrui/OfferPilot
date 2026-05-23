<template>
  <div class="interview-chat" ref="chatContainer">
    <div class="messages-wrapper">
      <div
        v-for="(msg, idx) in messages"
        :key="idx"
      >
        <div
          v-if="msg.questionNumber"
          :id="`question-${msg.questionNumber}`"
          class="question-divider"
        >
          <span>第 {{ msg.questionNumber }} 题</span>
        </div>
        <div :class="['message-bubble', msg.role === 'user' ? 'user' : 'assistant']">
          <div class="bubble-avatar">
            {{ msg.role === 'user' ? '我' : 'AI' }}
          </div>
          <div class="bubble-content">
            <div class="bubble-role">{{ msg.role === 'user' ? '候选人' : '面试官' }}</div>
            <div class="bubble-text">{{ msg.content }}</div>
          </div>
        </div>
      </div>

      <div v-if="streamingContent" class="message-bubble assistant">
        <div class="bubble-avatar">AI</div>
        <div class="bubble-content">
          <div class="bubble-role">面试官</div>
          <div class="bubble-text">
            {{ streamingContent }}<span class="typing-cursor">|</span>
          </div>
        </div>
      </div>

      <el-empty v-if="!messages.length && !streamingContent" description="点击「开始面试」与 AI 面试官对话" :image-size="80" />
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  messages: { type: Array, default: () => [] },
  streamingContent: { type: String, default: '' },
  currentQuestionNumber: { type: Number, default: 0 }
})

const chatContainer = ref(null)

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

watch(() => props.messages.length, scrollToBottom)
watch(() => props.streamingContent, scrollToBottom, { deep: false })

defineExpose({ scrollToBottom })
</script>

<style scoped>
.interview-chat {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.messages-wrapper {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.question-divider {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 16px 0 12px;
}

.question-divider span {
  padding: 4px 16px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  color: #2563eb;
  background: #eff6ff;
}

.message-bubble {
  display: flex;
  gap: 10px;
  padding: 8px 0;
  max-width: 85%;
}

.message-bubble.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-bubble.assistant {
  align-self: flex-start;
}

.bubble-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.message-bubble.assistant .bubble-avatar {
  color: #fff;
  background: #2563eb;
}

.message-bubble.user .bubble-avatar {
  color: #fff;
  background: #16a34a;
}

.bubble-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.bubble-role {
  font-size: 12px;
  color: #94a3b8;
}

.message-bubble.user .bubble-role {
  text-align: right;
}

.bubble-text {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.message-bubble.assistant .bubble-text {
  color: #172033;
  background: #f1f5f9;
  border-top-left-radius: 2px;
}

.message-bubble.user .bubble-text {
  color: #fff;
  background: #2563eb;
  border-top-right-radius: 2px;
}

.typing-cursor {
  display: inline;
  animation: blink 1s step-end infinite;
  color: #2563eb;
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
