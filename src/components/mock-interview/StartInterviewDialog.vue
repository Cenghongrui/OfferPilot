<template>
  <el-dialog v-model="localVisible" title="开始模拟面试" width="520px" @close="$emit('cancel')">
    <el-form label-width="96px">
      <el-form-item label="面试岗位" required>
        <el-input v-model="form.position" placeholder="例如：前端开发实习生" />
      </el-form-item>
      <el-form-item label="技术栈" required>
        <el-input v-model="form.techStack" type="textarea" :rows="4" placeholder="例如：Vue3、JavaScript、CSS、HTTP、FastAPI、SQLite" />
      </el-form-item>
      <el-form-item label="面试类型">
        <el-select v-model="form.interviewType" style="width: 100%">
          <el-option v-for="mode in modes" :key="mode.name" :label="mode.name" :value="mode.name" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleConfirm">开始计时并抽题</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  visible: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
  modes: { type: Array, default: () => [] }
})

const emit = defineEmits(['confirm', 'cancel'])

const form = reactive({
  position: '前端开发实习生',
  techStack: 'Vue3、JavaScript、CSS、HTTP、FastAPI、SQLite',
  interviewType: 'Vue 专项面'
})

const localVisible = computed({
  get: () => props.visible,
  set: (val) => { if (!val) emit('cancel') }
})

watch(() => props.modes, (list) => {
  if (list.length && !list.some(m => m.name === form.interviewType)) {
    form.interviewType = list[0].name
  }
}, { immediate: true })

function handleConfirm() {
  if (!form.position.trim() || !form.techStack.trim()) {
    ElMessage.warning('请填写面试岗位和技术栈')
    return
  }
  emit('confirm', { ...form })
}
</script>
