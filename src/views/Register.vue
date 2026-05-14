<template>
  <div class="auth-page">
    <section class="auth-brand">
      <div class="auth-logo">
        <img :src="viteIcon" alt="OfferPilot" />
        <span>OfferPilot</span>
      </div>
      <div class="auth-copy">
        <h1>创建你的求职准备档案</h1>
        <p>注册后会为你保存个人目标、题目状态、投递记录和面试复盘。当前版本使用本地存储，适合前端功能演示。</p>
        <div class="auth-highlights">
          <span>个人目标配置</span>
          <span>复习状态保存</span>
          <span>投递流程追踪</span>
          <span>报告持续沉淀</span>
        </div>
      </div>
    </section>

    <section class="auth-panel">
      <el-card class="auth-card" shadow="never">
        <h2>注册</h2>
        <p class="hint">填写基础信息，进入 OfferPilot 工作台。</p>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
          <el-form-item label="昵称" prop="name">
            <el-input v-model="form.name" placeholder="例如：前端实习生" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="name@example.com" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input v-model="form.confirmPassword" type="password" show-password placeholder="再次输入密码" />
          </el-form-item>
          <el-button class="auth-submit" type="primary" size="large" :loading="loading" @click="submit">
            创建账号
          </el-button>
        </el-form>
        <div class="auth-switch">
          已有账号？
          <el-link type="primary" @click="router.push('/login')">去登录</el-link>
        </div>
      </el-card>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import viteIcon from '@/assets/vite.svg'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const auth = useAuthStore()
const formRef = ref()
const loading = ref(false)
const form = reactive({
  name: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const rules = {
  name: [{ required: true, message: '请输入昵称', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value !== form.password) callback(new Error('两次密码不一致'))
        else callback()
      },
      trigger: 'blur'
    }
  ]
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.register(form)
    ElMessage.success('注册成功')
    router.push('/back/dashboard')
  } catch (error) {
    ElMessage.error(error.message || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style src="./auth.css"></style>
