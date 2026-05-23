<template>
  <div class="op-page settings-page">
    <section class="op-hero">
      <div>
        <div class="op-eyebrow">账号设置</div>
        <h1 class="op-title">设置</h1>
        <p class="op-subtitle">维护账号昵称、学习目标和消息提醒偏好。</p>
      </div>
      <div class="op-actions">
        <el-button type="primary" :icon="Check" @click="saveSettings">保存设置</el-button>
      </div>
    </section>

    <el-card class="settings-card" shadow="never">
      <el-form label-width="96px">
        <el-form-item label="账号昵称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="登录邮箱">
          <el-input v-model="form.email" disabled />
        </el-form-item>
        <el-form-item label="消息提醒">
          <el-switch v-model="form.notifications" active-text="开启" inactive-text="关闭" />
        </el-form-item>
        <el-form-item label="学习目标">
          <el-input v-model="form.goal" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, watchEffect } from 'vue'
import { ElMessage } from 'element-plus'
import { Check } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/authStore'

const auth = useAuthStore()
const form = reactive({
  name: '',
  email: '',
  goal: '',
  notifications: true
})

watchEffect(() => {
  form.name = auth.user?.name || ''
  form.email = auth.user?.email || ''
  form.goal = auth.user?.goal || ''
  form.notifications = auth.user?.notifications ?? true
})

async function saveSettings() {
  await auth.updateProfile({
    name: form.name,
    goal: form.goal,
    notifications: form.notifications
  })
  ElMessage.success('设置已保存')
}
</script>

<style src="./workbench.css"></style>
<style scoped>
.settings-page {
  padding: 0;
}

.settings-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  max-width: 720px;
}
</style>
