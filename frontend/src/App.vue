<template>
  <div id="app">
    <NavBar />
    <main class="container">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import NavBar from './components/NavBar.vue'
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; color: #333; }
.container { max-width: 900px; margin: 0 auto; padding: 2rem 1rem; }
</style>
