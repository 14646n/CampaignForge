<template>
  <h1>Welcome to CampaignForge AI</h1>
  <p>Your local D&D Assistant powered by Ollama.</p>
  <div v-if="status">{{ status }}</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
const status = ref('Checking backend connection...')

onMounted(async () => {
  try {
    const res = await fetch('http://localhost:8000/admin/')
    if(res.ok || res.status === 401) status.value = 'Backend Connected! (Check /admin)'
  } catch (e) {
    status.value = 'Backend offline. Start Docker.'
  }
})
</script>
