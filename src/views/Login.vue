<template>
  <div class="auth-page">
    <section class="auth-brand">
      <div class="auth-logo">
        <img :src="viteIcon" alt="OfferPilot" />
        <span>OfferPilot</span>
      </div>
      <div class="auth-copy">
        <h1>回到你的实习求职训练工作台</h1>
        <p>继续管理题库、算法、面经、投递进度和模拟面试报告，把每天的准备沉淀成可复盘的记录。</p>
        <div class="auth-highlights">
          <span>题库筛选与收藏</span>
          <span>投递阶段看板</span>
          <span>模拟面试报告</span>
          <span>本地数据持久化</span>
        </div>
      </div>
    </section>

    <section class="auth-panel">
      <el-card class="auth-card" shadow="never">
        <h2>登录</h2>
        <p class="hint">使用注册邮箱进入工作台。</p>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @keyup.enter="submit">
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="name@example.com" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="请输入密码" />
          </el-form-item>
          <el-button class="auth-submit" type="primary" size="large" :loading="loading" @click="submit">
            登录
          </el-button>
        </el-form>
        <div class="auth-switch">
          还没有账号？
          <el-link type="primary" @click="router.push('/register')">去注册</el-link>
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
  email: '',
  password: ''
})

const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    router.push('/back/dashboard')
  } catch (error) {
    ElMessage.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style src="./auth.css"></style>
