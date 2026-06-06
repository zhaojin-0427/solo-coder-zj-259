<template>
  <el-container class="layout">
    <el-header class="header">
      <div class="title">
        <el-icon :size="28" color="#c69c6d"><StarFilled /></el-icon>
        <span>传统酿酒作坊发酵监控与陈酿管理系统</span>
      </div>
      <div class="subtitle">古法酿造 · 匠心传承</div>
    </el-header>
    <el-container>
      <el-aside width="200px" class="aside">
        <el-menu
          :default-active="route.path"
          router
          background-color="#5a3a2a"
          text-color="#e8d5b7"
          active-text-color="#f4c06a"
        >
          <el-menu-item index="/cellar-pools">
            <el-icon><OfficeBuilding /></el-icon>
            <span>窖池管理</span>
          </el-menu-item>
          <el-menu-item index="/fermentation">
            <el-icon><DataAnalysis /></el-icon>
            <span>发酵监控</span>
          </el-menu-item>
          <el-menu-item index="/wine-quality">
            <el-icon><Medal /></el-icon>
            <span>酒质登记</span>
          </el-menu-item>
          <el-menu-item index="/aging-storage">
            <el-icon><Collection /></el-icon>
            <span>陈酿库位</span>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><TrendCharts /></el-icon>
            <span>统计分析</span>
          </el-menu-item>
        </el-menu>
      </el-aside>
      <el-main class="main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
const route = useRoute()
</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
  padding: 0;
}
.layout {
  height: 100vh;
}
.header {
  background: linear-gradient(135deg, #3d2817 0%, #5a3a2a 100%);
  color: #e8d5b7;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 30px;
  border-bottom: 3px solid #c69c6d;
}
.title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  font-weight: 600;
  letter-spacing: 2px;
}
.subtitle {
  font-size: 14px;
  color: #c69c6d;
  letter-spacing: 3px;
}
.aside {
  background: #5a3a2a;
}
.aside .el-menu {
  border-right: none;
}
.main {
  background: #f7f3ec;
  padding: 24px;
  overflow: auto;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
