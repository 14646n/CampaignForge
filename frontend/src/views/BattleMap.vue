<template>
  <div class="map-container">
    <div class="main-area">
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

    <div class="sidebar">
      <ChatInterface />
    </div>

    <!-- Модальное окно с результатом AI -->
    <div v-if="showAIModal" class="modal-overlay" @click="closeAIModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>🎲 Результат AI</h3>
          <button @click="closeAIModal" class="close-btn">×</button>
        </div>
        <div class="modal-body">
          <pre>{{ lastAIResult }}</pre>
        </div>
        <div class="modal-footer">
          <button @click="closeAIModal" class="ok-btn">Понятно</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from "vue";
import { useRoute } from "vue-router";
import { useCampaignStore } from "../stores/campaign";
import ChatInterface from "../components/ChatInterface.vue";

const route = useRoute();
const store = useCampaignStore();

const stageConfig = reactive({
  width: window.innerWidth - 400,
  height: window.innerHeight,
});

const gridConfig = {
  width: 2000,
  height: 2000,
  stroke: "#ccc",
  strokeWidth: 1,
};

const showAIModal = ref(false);
const lastAIResult = ref('');

// Подписка на новые сообщения AI
const unsubscribe = store.$onAction(({ name, args }) => {
  if (name === 'addAIMessage') {
    const message = args[0];
    if (message && message.content) {
      lastAIResult.value = message.content;
      showAIModal.value = true;
    }
  }
});

onMounted(() => {
  store.fetchSession(route.params.id as string);
  
  // Обновляем размер сцены при изменении размера окна
  window.addEventListener('resize', () => {
    stageConfig.width = window.innerWidth - 400;
    stageConfig.height = window.innerHeight;
  });
});

onUnmounted(() => {
  unsubscribe();
});

const onDragEnd = (e: any, char: any) => {
  const node = e.target;
  const snap = 50; // Размер клетки
  const x = Math.round(node.x() / snap) * snap;
  const y = Math.round(node.y() / snap) * snap;

  node.x(x);
  node.y(y);

  store.moveToken(char.id, x, y);
};

const closeAIModal = () => {
  showAIModal.value = false;
};
</script>

<style scoped>
.map-container {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

.main-area {
  flex: 1;
  background: #1a1a2e;
  overflow: hidden;
}

.sidebar {
  width: 400px;
  padding: 16px;
  background: #0f0f1a;
  border-left: 1px solid #16213e;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 12px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
}

.modal-header h3 {
  margin: 0;
  color: #e94560;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  color: #888;
  font-size: 28px;
  cursor: pointer;
  line-height: 1;
  transition: color 0.2s;
}

.close-btn:hover {
  color: #e94560;
}

.modal-body {
  padding: 20px;
  max-height: 60vh;
  overflow-y: auto;
}

.modal-body pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.6;
  color: #eee;
  margin: 0;
}

.modal-footer {
  padding: 16px 20px;
  background: #16213e;
  border-top: 1px solid #0f3460;
  display: flex;
  justify-content: flex-end;
}

.ok-btn {
  padding: 10px 24px;
  background: #e94560;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.ok-btn:hover {
  background: #ff6b6b;
}
</style>
