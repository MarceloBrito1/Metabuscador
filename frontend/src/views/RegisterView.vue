<template>
  <div class="auth-form">
    <h2>Criar Conta</h2>
    <form @submit.prevent="handleRegister">
      <div class="field">
        <label>Usuário</label>
        <input v-model="username" type="text" required />
      </div>
      <div class="field">
        <label>E-mail</label>
        <input v-model="email" type="email" required />
      </div>
      <div class="field">
        <label>Senha</label>
        <input v-model="password" type="password" required minlength="6" />
      </div>
      <div v-if="error" class="error">{{ error }}</div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Criando...' : 'Criar Conta' }}
      </button>
    </form>
    <p>Já tem conta? <RouterLink to="/login">Entrar</RouterLink></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const username = ref('')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleRegister() {
  loading.value = true
  error.value = ''
  try {
    await auth.register(username.value, email.value, password.value)
  } catch (err) {
    error.value = err.response?.data?.detail || 'Erro ao criar conta.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-form { max-width: 400px; margin: 3rem auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 2px 16px rgba(0,0,0,0.1); }
h2 { margin-bottom: 1.5rem; text-align: center; }
.field { margin-bottom: 1rem; }
label { display: block; margin-bottom: 0.3rem; font-size: 0.9rem; color: #555; }
input { width: 100%; padding: 0.6rem; border: 1px solid #ccc; border-radius: 6px; font-size: 1rem; }
button { width: 100%; padding: 0.75rem; background: #2563eb; color: white; border: none; border-radius: 6px; font-size: 1rem; cursor: pointer; margin-top: 0.5rem; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #c00; font-size: 0.9rem; margin-bottom: 0.5rem; }
p { text-align: center; margin-top: 1rem; font-size: 0.9rem; }
</style>
