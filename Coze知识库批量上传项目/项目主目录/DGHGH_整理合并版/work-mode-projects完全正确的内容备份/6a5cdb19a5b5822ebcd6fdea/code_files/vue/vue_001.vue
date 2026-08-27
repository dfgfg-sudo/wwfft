<!-- packages/web-dashboard/src/App.vue -->
<template>
  <div id="app">
    <header class="app-header">
      <div class="container">
        <div class="header-content">
          <router-link to="/" class="logo">
            <span class="logo-icon">🤖</span>
            <h1>AutoCode Pro</h1>
          </router-link>
          
          <nav class="main-nav">
            <router-link to="/">首页</router-link>
            <router-link to="/projects">项目</router-link>
            <router-link to="/templates">模板</router-link>
            <router-link to="/docs">文档</router-link>
            <router-link to="/settings" v-if="userStore.isAuthenticated">
              设置
            </router-link>
          </nav>
          
          <div class="user-actions">
            <template v-if="userStore.isAuthenticated">
              <span class="welcome">欢迎, {{ userStore.user?.name }}</span>
              <button @click="logout" class="btn-logout">退出</button>
            </template>
            <template v-else>
              <router-link to="/login" class="btn-login">登录</router-link>
              <router-link to="/register" class="btn-register">注册</router-link>
            </template>
          </div>
        </div>
      </div>
    </header>
    
    <main class="app-main">
      <div class="container">
        <router-view />
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="container">
        <div class="footer-content">
          <div class="footer-section">
            <h3>AutoCode Pro</h3>
            <p>AI驱动的软件生成平台</p>
            <p>用自然语言描述需求，自动生成完整可运行的软件项目</p>
          </div>
          
          <div class="footer-section">
            <h4>产品</h4>
            <ul>
              <li><router-link to="/features">功能特性</router-link></li>
              <li><router-link to="/pricing">定价</router-link></li>
              <li><router-link to="/templates">模板库</router-link></li>
              <li><router-link to="/docs">文档</router-link></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>支持</h4>
            <ul>
              <li><router-link to="/help">帮助中心</router-link></li>
              <li><router-link to="/contact">联系我们</router-link></li>
              <li><router-link to="/status">系统状态</router-link></li>
              <li><a href="mailto:support@autocode.pro">技术支持</a></li>
            </ul>
          </div>
          
          <div class="footer-section">
            <h4>社区</h4>
            <ul>
              <li><a href="https://github.com/autocode-pro" target="_blank">GitHub</a></li>
              <li><a href="https://discord.gg/autocode" target="_blank">Discord</a></li>
              <li><a href="https://twitter.com/autocode_pro" target="_blank">Twitter</a></li>
              <li><a href="https://blog.autocode.pro" target="_blank">博客</a></li>
            </ul>
          </div>
        </div>
        
        <div class="footer-bottom">
          <p>&copy; 2024 AutoCode Pro. 保留所有权利。</p>
          <div class="legal-links">
            <router-link to="/privacy">隐私政策</router-link>
            <router-link to="/terms">服务条款</router-link>
            <router-link to="/cookies">Cookie政策</router-link>
          </div>
        </div>
      </div>
    </footer>
    
    <!-- 全局通知 -->
    <transition name="slide-down">
      <div v-if="notificationStore.notifications.length" class="notifications">
        <div 
          v-for="notification in notificationStore.notifications" 
          :key="notification.id"
          :class="['notification', `notification-${notification.type}`]"
        >
          <div class="notification-content">
            <span class="notification-icon">{{ getNotificationIcon(notification.type) }}</span>
            <div class="notification-text">
              <strong>{{ notification.title }}</strong>
              <p>{{ notification.message }}</p>
            </div>
          </div>
          <button @click="removeNotification(notification.id)" class="notification-close">
            &times;
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/userStore'
import { useNotificationStore } from './stores/notificationStore'

export default {
  name: 'App',
  
  setup() {
    const router = useRouter()
    const userStore = useUserStore()
    const notificationStore = useNotificationStore()
    
    // 检查登录状态
    onMounted(() => {
      userStore.checkAuthStatus()
    })
    
    // 登出
    const logout = async () => {
      await userStore.logout()
      router.push('/login')
      notificationStore.addNotification({
        type: 'success',
        title: '已登出',
        message: '您已成功退出账号'
      })
    }
    
    // 移除通知
    const removeNotification = (id) => {
      notificationStore.removeNotification(id)
    }
    
    // 获取通知图标
    const getNotificationIcon = (type) => {
      const icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
      }
      return icons[type] || '💬'
    }
    
    return {
      userStore,
      notificationStore,
      logout,
      removeNotification,
      getNotificationIcon
    }
  }
}
</script>

<style scoped>
#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* 头部样式 */
.app-header {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 0;
}

.logo {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #333;
}

.logo-icon {
  font-size: 2rem;
  margin-right: 0.5rem;
}

.logo h1 {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.main-nav {
  display: flex;
  gap: 2rem;
}

.main-nav a {
  text-decoration: none;
  color: #666;
  font-weight: 500;
  padding: 0.5rem 0;
  position: relative;
  transition: color 0.3s ease;
}

.main-nav a:hover {
  color: #667eea;
}

.main-nav a.router-link-active {
  color: #667eea;
}

.main-nav a.router-link-active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: #667eea;
  border-radius: 1px;
}

.user-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome {
  color: #666;
  font-size: 0.875rem;
}

.btn-login,
.btn-register,
.btn-logout {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
}

.btn-login {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
}

.btn-login:hover {
  background: #667eea;
  color: white;
}

.btn-register {
  background: #667eea;
  color: white;
}

.btn-register:hover {
  background: #5a67d8;
}

.btn-logout {
  background: #f56565;
  color: white;
}

.btn-logout:hover {
  background: #e53e3e;
}

/* 主要内容区 */
.app-main {
  flex: 1;
  padding: 2rem 0;
  background: #f7fafc;
}

/* 底部样式 */
.app-footer {
  background: #2d3748;
  color: #cbd5e0;
  padding: 3rem 0 1.5rem;
}

.footer-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.footer-section h3,
.footer-section h4 {
  color: white;
  margin-bottom: 1rem;
}

.footer-section h3 {
  font-size: 1.5rem;
}

.footer-section h4 {
  font-size: 1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.footer-section p {
  margin: 0.5rem 0;
  line-height: 1.5;
}

.footer-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-section li {
  margin-bottom: 0.5rem;
}

.footer-section a {
  color: #cbd5e0;
  text-decoration: none;
  transition: color 0.3s ease;
}

.footer-section a:hover {
  color: white;
}

.footer-bottom {
  border-top: 1px solid #4a5568;
  padding-top: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-bottom p {
  margin: 0;
  font-size: 0.875rem;
}

.legal-links {
  display: flex;
  gap: 1.5rem;
}

.legal-links a {
  color: #cbd5e0;
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.3s ease;
}

.legal-links a:hover {
  color: white;
}

/* 通知样式 */
.notifications {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 9999;
  max-width: 400px;
}

.notification {
  background: white;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  animation: slideIn 0.3s ease;
}

.notification-success {
  border-left: 4px solid #48bb78;
}

.notification-error {
  border-left: 4px solid #f56565;
}

.notification-warning {
  border-left: 4px solid #ed8936;
}

.notification-info {
  border-left: 4px solid #4299e1;
}

.notification-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  flex: 1;
}

.notification-icon {
  font-size: 1.25rem;
  margin-top: 0.125rem;
}

.notification-text {
  flex: 1;
}

.notification-text strong {
  display: block;
  margin-bottom: 0.25rem;
  color: #2d3748;
}

.notification-text p {
  margin: 0;
  color: #718096;
  font-size: 0.875rem;
  line-height: 1.4;
}

.notification-close {
  background: none;
  border: none;
  color: #a0aec0;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0;
  margin-left: 0.5rem;
  line-height: 1;
  transition: color 0.3s ease;
}

.notification-close:hover {
  color: #718096;
}

/* 动画 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 1rem;
  }
  
  .main-nav {
    order: 3;
    width: 100%;
    justify-content: center;
    gap: 1rem;
  }
  
  .user-actions {
    order: 2;
  }
  
  .footer-content {
    grid-template-columns: 1fr;
    text-align: center;
  }
  
  .footer-bottom {
    flex-direction: column;
    gap: 1rem;
    text-align: center;
  }
  
  .notifications {
    left: 1rem;
    right: 1rem;
    max-width: none;
  }
}
</style>