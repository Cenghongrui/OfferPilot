<template>
  <div class="interview-history">
    <div class="history-header">
      <strong>历史面试</strong>
      <el-button size="small" type="primary" @click="$emit('start')">开始面试</el-button>
    </div>
    <div class="history-list" v-loading="loading">
      <template v-if="sessions.length">
        <button
          v-for="s in sessions"
          :key="s.id"
          :class="['history-item', { active: s.id === currentSessionId }]"
          @click="$emit('select', s.id)"
        >
          <div class="item-top">
            <span class="item-position">{{ s.position || '未设置' }}</span>
            <span class="op-tag" :class="s.status === 'running' ? 'green' : ''">
              {{ s.status === 'running' ? '进行中' : '已完成' }}
            </span>
          </div>
          <div class="item-meta">
            <span>{{ s.interviewType || '技术面试' }}</span>
            <span v-if="s.questionCount">{{ s.questionCount }} 题</span>
            <span v-if="s.report?.total" class="item-score">{{ s.report.total }}分</span>
          </div>
          <div class="item-time">{{ formatDate(s.createdAt) }}</div>
        </button>
      </template>
      <el-empty v-else description="暂无历史面试记录" :image-size="40" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  sessions: { type: Array, default: () => [] },
  currentSessionId: { type: String, default: '' },
  loading: { type: Boolean, default: false }
})

defineEmits(['select', 'start'])

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
</script>

<style scoped>
.interview-history {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.history-header strong {
  font-size: 15px;
  color: #172033;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  text-align: left;
  color: #172033;
  background: #fff;
  cursor: pointer;
  transition: border-color 0.15s, background 0.15s;
}

.history-item:hover {
  border-color: #93c5fd;
  background: #f8fafc;
}

.history-item.active {
  border-color: #2563eb;
  background: #eff6ff;
}

.item-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.item-position {
  font-weight: 600;
  font-size: 14px;
}

.item-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #667085;
}

.item-score {
  color: #2563eb;
  font-weight: 600;
}

.item-time {
  font-size: 12px;
  color: #94a3b8;
}
</style>
