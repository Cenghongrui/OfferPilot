<template>
  <el-dialog
    v-model="localVisible"
    title="面试报告"
    width="680px"
    top="5vh"
    :close-on-click-modal="false"
    @close="$emit('close')"
  >
    <template v-if="report">
      <div class="report-total">
        <div class="total-ring">
          <span class="total-num">{{ report.total }}</span>
          <span class="total-label">综合评分</span>
        </div>
      </div>

      <div class="report-dimensions" v-if="report.dimensions?.length">
        <div class="dimension-row" v-for="d in report.dimensions" :key="d.name">
          <div class="dim-header">
            <span class="dim-name">{{ d.name }}</span>
            <span class="dim-score">{{ d.score }} / 5</span>
          </div>
          <div class="dim-bar">
            <div class="dim-fill" :style="{ width: (d.score / 5 * 100) + '%' }"></div>
          </div>
          <div class="dim-comment">{{ d.comment }}</div>
        </div>
      </div>

      <div class="report-summary">
        <strong>总体评价</strong>
        <p>{{ report.summary }}</p>
      </div>

      <div class="report-block">
        <strong>表现较好的点</strong>
        <p>{{ report.strengths }}</p>
      </div>

      <div class="report-block">
        <strong>需要改进</strong>
        <p>{{ report.weakness }}</p>
      </div>

      <div class="report-block">
        <strong>复习建议</strong>
        <p>{{ report.suggestion }}</p>
      </div>

      <div class="report-block" v-if="report.resources?.length">
        <strong>推荐学习资源</strong>
        <div class="resource-list">
          <div class="resource-item" v-for="r in report.resources" :key="r.title">
            <span class="op-tag orange">{{ r.type }}</span>
            <div>
              <strong>{{ r.title }}</strong>
              <p>{{ r.description }}</p>
            </div>
          </div>
        </div>
      </div>

      <div class="report-block" v-if="report.nextQuestions?.length">
        <strong>后续练习题</strong>
        <ul>
          <li v-for="q in report.nextQuestions" :key="q">{{ q }}</li>
        </ul>
      </div>

      <span class="op-tag green">{{ report.source === 'deepseek' ? 'DeepSeek 生成' : '本地兜底报告' }}</span>
    </template>
    <el-empty v-else description="暂无报告数据" />

    <template #footer>
      <el-button @click="$emit('close')">关闭</el-button>
      <el-button type="primary" @click="$emit('continue')">继续面试</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  report: { type: Object, default: null },
  sessionId: { type: String, default: '' }
})

const emit = defineEmits(['continue', 'close'])

const localVisible = computed({
  get: () => props.visible,
  set: (val) => { if (!val) emit('close') }
})
</script>

<style scoped>
.report-total {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.total-ring {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #1d4ed8);
}

.total-num {
  font-size: 38px;
  font-weight: 700;
  line-height: 1;
}

.total-label {
  font-size: 12px;
  margin-top: 4px;
  opacity: 0.85;
}

.report-dimensions {
  display: grid;
  gap: 12px;
  margin-bottom: 18px;
}

.dimension-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dim-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.dim-name {
  color: #172033;
  font-weight: 500;
}

.dim-score {
  color: #2563eb;
  font-weight: 600;
}

.dim-bar {
  height: 6px;
  border-radius: 3px;
  background: #e5e7eb;
}

.dim-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #2563eb, #60a5fa);
  transition: width 0.4s ease;
}

.dim-comment {
  font-size: 12px;
  color: #667085;
}

.report-summary {
  padding: 14px;
  margin-bottom: 12px;
  border-radius: 8px;
  background: #f8fafc;
}

.report-summary strong {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
}

.report-summary p {
  color: #475467;
  line-height: 1.7;
}

.report-block {
  padding: 14px 0;
  border-top: 1px solid #e5e7eb;
}

.report-block strong {
  display: block;
  margin-bottom: 8px;
}

.report-block p {
  color: #475467;
  line-height: 1.7;
}

.report-block ul {
  margin: 0;
  padding-left: 18px;
  line-height: 1.8;
  color: #475467;
}

.resource-list {
  display: grid;
  gap: 10px;
  margin-top: 8px;
}

.resource-item {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}

.resource-item strong {
  margin-bottom: 4px;
  font-size: 13px;
}

.resource-item p {
  font-size: 13px;
}
</style>
