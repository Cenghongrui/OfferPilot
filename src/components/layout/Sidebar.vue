<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <div class="title">
        <img :src="viteIcon" style="width: 30px;">
        <div class="title-content">OfferPilot</div>
      </div>
      <el-icon class="collapse-icon" :size="20" color="#333">
        <Fold />
      </el-icon>
    </div>
    <div class="sidebar-list">
      <div
        class="sidebar-item"
        v-for="item in mainRoutes"
        :key="item.path"
        :class="{ active: route.path === `/back/${item.path}` }"
        @click="changeView(item)"
      >
        <el-icon><component :is="item.meta.icon" /></el-icon>
        <div style="margin-left: 20px;">{{ item.meta.title }}</div>
      </div>
    </div>
    <div class="sidebar-bottom">
      <div class="user-card">
        <div class="avatar">{{ userInitial }}</div>
        <div class="user-info">
          <strong>{{ auth.user?.name || '未登录' }}</strong>
          <span>{{ auth.user?.email || '请先登录' }}</span>
        </div>
      </div>
      <div
        class="sidebar-item"
        v-for="item in personalRoutes"
        :key="item.path"
        :class="{ active: route.path === `/back/${item.path}` }"
        @click="changeView(item)"
      >
        <el-icon><component :is="item.meta.icon" /></el-icon>
        <div style="margin-left: 20px;">{{ item.meta.title }}</div>
      </div>
      <div class="sidebar-item logout-item" @click="logout">
        <el-icon><SwitchButton /></el-icon>
        <div style="margin-left: 20px;">退出登录</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import viteIcon from '@/assets/vite.svg'
import { ElIcon, ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/authStore'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const childRoutes = router.options.routes.find((item) => item.path === '/back')?.children || []
const mainRoutes = childRoutes.filter((item) => item.meta?.group === 'main')
const personalRoutes = childRoutes.filter((item) => item.meta?.group === 'personal')

const userInitial = computed(() => {
  return auth.user?.name?.slice(0, 1).toUpperCase() || 'U'
})

const changeView = (item) => {
  router.push(`/back/${item.path}`)
}

const logout = async () => {
  await auth.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style lang=scss scoped>
.sidebar {
  position: sticky;
  top: 0;
  flex: 0 0 220px;
  width: 220px;
  height: 100vh;
  overflow-y: auto;
  background-color: #fff;
  border-right: 1px solid #e0e0e0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;

  .sidebar-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px;
    font-size: 18px;
    font-weight: bold;
    border-bottom: 1px solid #e0e0e0;
    height: 30px;

    .title {
      display: flex;
      align-items: center;
      gap: 10px;

      .title-content {
        color: #333;
      }
    }

    .collapse-icon {
      flex: 0 0 auto;
      cursor: pointer;
    }
  }

  .sidebar-list {
    display: flex;
    flex-direction: column;
    flex: 1;
    color: #333;

    .sidebar-item {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      padding: 15px 20px;
      cursor: pointer;
      transition: background-color 0.5s ease, color 0.3s ease;
      margin: 5px;
      border-radius: 8px;
      font-size: 16px;
      font-weight: bold;

      &:hover {
        background-color: #055ce4;
        color: #fff;
      }

      &.active {
        background-color: #055ce4;
        color: #fff;
      }
    }
  }

  .sidebar-bottom {
    padding: 8px 0 14px;
    border-top: 1px solid #e5e7eb;
    color: #333;

    .user-card {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 8px 10px 10px;
      padding: 12px 10px;
      border-radius: 8px;
      background: #f6f8fb;

      .avatar {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 8px;
        color: #fff;
        background: #055ce4;
        font-weight: 800;
      }

      .user-info {
        min-width: 0;
        display: flex;
        flex-direction: column;
        gap: 3px;

        strong,
        span {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }

        strong {
          color: #172033;
          font-size: 14px;
        }

        span {
          color: #667085;
          font-size: 12px;
        }
      }
    }

    .sidebar-item {
      display: flex;
      align-items: center;
      justify-content: flex-start;
      padding: 13px 20px;
      cursor: pointer;
      transition: background-color 0.5s ease, color 0.3s ease;
      margin: 5px;
      border-radius: 8px;
      font-size: 15px;
      font-weight: bold;

      &:hover,
      &.active {
        background-color: #055ce4;
        color: #fff;
      }
    }

    .logout-item:hover {
      background-color: #dc2626;
    }
  }
}
</style>
