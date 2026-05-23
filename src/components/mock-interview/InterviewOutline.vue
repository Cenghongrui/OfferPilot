<template>
  <div class="interview-outline">
    <div class="outline-header">
      <strong>面试大纲</strong>
      <span class="op-tag">{{ questions.length }} 题</span>
    </div>
    <div class="outline-list" v-if="questions.length">
      <button
        v-for="q in questions"
        :key="q.number"
        :class="{ active: q.number === activeQuestion }"
        @click="$emit('detail', q.number)"
        :title="`查看第 ${q.number} 题对话详情`"
      >
        <span class="q-num">第{{ q.number }}题</span>
        <span class="q-label">{{ q.label }}</span>
      </button>
    </div>
    <el-empty v-else description="暂无题目" :image-size="40" />
  </div>
</template>

<script setup>
defineProps({
  questions: { type: Array, default: () => [] },
  activeQuestion: { type: Number, default: 0 }
})

defineEmits(['detail'])
</script>

<style scoped>
.interview-outline {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.outline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid #e5e7eb;
}

.outline-header strong {
  font-size: 14px;
  color: #172033;
}

.outline-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.outline-list button {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  padding: 10px 12px;
  margin-bottom: 4px;
  border: 1px solid transparent;
  border-radius: 6px;
  text-align: left;
  background: #fff;
  cursor: pointer;
  transition: background 0.15s;
}

.outline-list button:hover {
  background: #f1f5f9;
}

.outline-list button.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.q-num {
  font-size: 14px;
  font-weight: 600;
  color: #172033;
}

.q-label {
  font-size: 12px;
  color: #667085;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
