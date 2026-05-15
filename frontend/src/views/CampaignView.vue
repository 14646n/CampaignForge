<template>
  <div>
    <h1>Campaign Dashboard</h1>
    <p>AI Integration Ready (Ollama)</p>
    <div class="card">
      <h3>Generate NPC</h3>
      <input v-model="prompt" placeholder="Describe NPC..." style="width: 100%; padding: 8px;" />
      <button @click="generateNPC" :disabled="loading" style="margin-top: 10px; padding: 8px 16px;">
        {{ loading ? 'Generating...' : 'Generate with Ollama' }}
      </button>
      <pre v-if="result" style="background: #f4f4f4; padding: 10px; margin-top: 10px;">{{ result }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
// Mock function for now until API endpoints are fully wired in next steps
const prompt = ref('')
const loading = ref(false)
const result = ref(null)

const generateNPC = async () => {
  loading.value = true
  // In next step we will connect this to the actual DRF endpoint
  setTimeout(() => {
    result.value = { name: "Test NPC", race: "Human", note: "Backend logic coming in next file set!" }
    loading.value = false
  }, 1000)
}
</script>
