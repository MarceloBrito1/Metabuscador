<template>
  <nav class="navbar">
    <RouterLink to="/" class="brand">🔍 Metabuscador</RouterLink>
    <div class="links">
      <template v-if="auth.user">
        <span class="username">{{ auth.user.username }}</span>
        <button @click="auth.logout()" class="logout-btn">Sair</button>
      </template>
      <template v-else>
        <RouterLink to="/login">Entrar</RouterLink>
        <RouterLink to="/register">Cadastrar</RouterLink>
      </template>
    </div>
  </nav>
</template>

<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
onMounted(() => auth.fetchUser())
</script>

<style scoped>
.navbar { display: flex; justify-content: space-between; align-items: center; padding: 1rem 2rem; background: #2563eb; color: white; }
.brand { color: white; text-decoration: none; font-size: 1.3rem; font-weight: bold; }
.links { display: flex; gap: 1rem; align-items: center; }
.links a { color: white; text-decoration: none; }
.links a:hover { text-decoration: underline; }
.username { font-weight: bold; }
.logout-btn { background: transparent; border: 1px solid white; color: white; padding: 0.3rem 0.8rem; border-radius: 4px; cursor: pointer; }
</style>
