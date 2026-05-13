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
      <div class="sidebar-item" v-for="(item) in router.options.routes[1].children" :key="item">
        <el-icon><component :is="item.meta.icon" /></el-icon>
        <div style="margin-left: 20px;">{{ item.meta.title }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import viteIcon from '@/assets/vite.svg'
import { ElIcon } from 'element-plus';
import { useRouter } from 'vue-router';

const router = useRouter();

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
    }
  }
}
</style>
