<template>
  <div class="map-container">
    <div class="controls">
      <h3>AI Assistant</h3>
      <textarea
        v-model="prompt"
        placeholder="Describe an NPC or Encounter..."
      ></textarea>
      <select v-model="type">
        <option value="npc">NPC</option>
        <option value="encounter">Encounter</option>
      </select>
      <button @click="sendToAI" :disabled="loading">
        {{ loading ? "Thinking..." : "Generate" }}
      </button>
    </div>

    <v-stage :config="stageConfig">
      <v-layer>
        <!-- Сетка -->
        <v-rect :config="gridConfig" />
      </v-layer>
      <v-layer>
        <!-- Токены -->
        <v-group
          v-for="char in store.characters"
          :key="char.id"
          :config="{
            draggable: true,
            x: char.x || char.position_x,
            y: char.y || char.position_y,
          }"
          @dragend="onDragEnd($event, char)"
        >
          <v-circle :config="{ radius: 25, fill: char.color || '#3b82f6' }" />
          <v-text
            :config="{
              text: char.name,
              fontSize: 14,
              offsetY: 35,
              fill: 'white',
            }"
          />
        </v-group>
      </v-layer>
    </v-stage>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from "vue";
import { useRoute } from "vue-router";
import { useCampaignStore } from "../stores/campaign";

const route = useRoute();
const store = useCampaignStore();
const prompt = ref("");
const type = ref("npc");
const loading = ref(false);

const stageConfig = reactive({
  width: window.innerWidth - 300,
  height: window.innerHeight,
});

const gridConfig = {
  width: 2000,
  height: 2000,
  stroke: "#ccc",
  strokeWidth: 1,
};

onMounted(() => {
  store.fetchSession(route.params.id);
});

const onDragEnd = (e, char) => {
  const node = e.target;
  const snap = 50; // Размер клетки
  const x = Math.round(node.x() / snap) * snap;
  const y = Math.round(node.y() / snap) * snap;

  node.x(x);
  node.y(y);

  store.moveToken(char.id, x, y);
};

const sendToAI = async () => {
  loading.value = true;
  try {
    await store.requestAI(prompt.value, type.value);
    prompt.value = "";
  } catch (e) {
    console.error(e);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.map-container {
  display: flex;
}
.controls {
  width: 300px;
  padding: 20px;
  background: #f0f0f0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
textarea {
  height: 100px;
}
</style>
