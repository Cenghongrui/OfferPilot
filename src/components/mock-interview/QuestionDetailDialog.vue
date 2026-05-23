<template>
  <el-dialog
    v-model="localVisible"
    :title="`第 ${questionNumber} 题对话详情`"
    width="640px"
    top="5vh"
    :close-on-click-modal="true"
    @close="$emit('close')"
  >
    <div class="detail-messages" ref="detailContainer">
      <template v-if="filteredMessages.length">
        <div
          v-for="(msg, idx) in filteredMessages"
          :key="idx"
          :class="['detail-bubble', msg.role === 'user' ? 'user' : 'assistant']"
        >
          <div class="detail-role">{{ msg.role === 'user' ? '候选人' : '面试官' }}</div>
          <div class="detail-text">{{ msg.content }}</div>
        </div>
      </template>
      <el-empty v-else description="暂无对话记录" :image-size="60" />

      <div v-if="isCurrentQuestion && streamingContent" class="detail-bubble assistant">
        <div class="detail-role">面试官</div>
        <div class="detail-text">{{ streamingContent }}<span class="typing-cursor">|</span></div>
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { computed, ref, watch, nextTick } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  questionNumber: { type: Number, default: 0 },
  messages: { type: Array, default: () => [] },
  currentQuestionNumber: { type: Number, default: 0 },
  streamingContent: { type: String, default: '' }
})

const emit = defineEmits(['close'])

const detailContainer = ref(null)

const localVisible = computed({
  get: () => props.visible,
  set: (val) => { if (!val) emit('close') }
})

const isCurrentQuestion = computed(() => props.questionNumber === props.currentQuestionNumber)

const filteredMessages = computed(() => {
  if (!props.questionNumber) return []

  const msgs = props.messages
  let start = -1
  let end = msgs.length

  for (let i = 0; i < msgs.length; i++) {
    if (msgs[i].questionNumber === props.questionNumber) {
      start = i
      continue
    }
    if (start >= 0 && msgs[i].questionNumber && msgs[i].questionNumber !== props.questionNumber) {
      end = i
      break
    }
  }

  if (start < 0) return []
  return msgs.slice(start, end)
})

function scrollDetailToBottom() {
  nextTick(() => {
    if (detailContainer.value) {
      detailContainer.value.scrollTop = detailContainer.value.scrollHeight
    }
  })
}

watch(() => props.visible, (v) => { if (v) scrollDetailToBottom() })
watch(() => filteredMessages.value.length, scrollDetailToBottom)
watch(() => props.streamingContent, () => {
  if (isCurrentQuestion.value) scrollDetailToBottom()
})
</script>

<style scoped>
.detail-messages {
  max-height: 55vh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  max-width: 90%;
}

.detail-bubble.assistant {
  align-self: flex-start;
  background: #f1f5f9;
  color: #172033;
}

.detail-bubble.user {
  align-self: flex-end;
  background: #eff6ff;
  color: #172033;
}

.detail-role {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 4px;
}

.detail-bubble.user .detail-role {
  text-align: right;
}

.detail-text {
  font-size: 14px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
}

.typing-cursor {
  animation: blink 1s step-end infinite;
  color: #2563eb;
}

@keyframes blink {
  50% { opacity: 0; }
}
</style>
