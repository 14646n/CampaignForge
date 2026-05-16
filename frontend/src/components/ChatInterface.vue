<template>
  <div class="chat-interface">
    <div class="chat-header">
      <h3>AI Dungeon Master</h3>
      <button @click="clearChat" class="clear-btn" title="Очистить чат">🗑️</button>
    </div>
    
    <div class="chat-messages" ref="messagesContainer">
      <div 
        v-for="(msg, index) in messages" 
        :key="index" 
        class="message"
        :class="msg.role"
      >
        <div class="message-avatar">
          {{ msg.role === 'user' ? '🧙‍♂️' : '🤖' }}
        </div>
        <div class="message-content">
          <div class="message-text">{{ msg.text }}</div>
          <div class="message-time">{{ msg.time }}</div>
        </div>
      </div>
      
      <div v-if="isTyping" class="message ai typing">
        <div class="message-avatar">🤖</div>
        <div class="message-content">
          <div class="typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div class="quick-actions">
        <button @click="setPrompt('Создать NPC')" class="quick-btn">NPC</button>
        <button @click="setPrompt('Создать встречу')" class="quick-btn">Встреча</button>
        <button @click="setPrompt('Описать локацию')" class="quick-btn">Локация</button>
        <button @click="setPrompt('Сгенерировать лут')" class="quick-btn">Лут</button>
      </div>
      
      <textarea
        v-model="inputMessage"
        @keydown.enter.exact.prevent="sendMessage"
        placeholder="Опишите что должно произойти..."
        rows="3"
      ></textarea>
      
      <button 
        @click="sendMessage" 
        :disabled="!inputMessage.trim() || isTyping"
        class="send-btn"
      >
        Отправить
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { useCampaignStore } from '../stores/campaign';

const store = useCampaignStore();
const messagesContainer = ref<HTMLElement | null>(null);

const inputMessage = ref('');
const isTyping = ref(false);

const messages = computed(() => {
  return store.aiMessages.map(msg => ({
    role: msg.message_type === 'user_request' ? 'user' : 'ai',
    text: msg.content,
    time: new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }));
});

const setPrompt = (text: string) => {
  inputMessage.value = text + ': ';
};

const clearChat = () => {
  store.clearMessages();
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isTyping.value) return;
  
  const prompt = inputMessage.value.trim();
  inputMessage.value = '';
  isTyping.value = true;
  
  try {
    // Определяем тип запроса по ключевым словам
    let type = 'general';
    if (prompt.toLowerCase().includes('npc')) type = 'npc';
    else if (prompt.toLowerCase().includes('встреч') || prompt.toLowerCase().includes('encounter')) type = 'encounter';
    else if (prompt.toLowerCase().includes('локац') || prompt.toLowerCase().includes('location')) type = 'location';
    else if (prompt.toLowerCase().includes('лут') || prompt.toLowerCase().includes('loot')) type = 'loot';
    
    await store.requestAI(prompt, type);
    await scrollToBottom();
  } catch (e) {
    console.error('Error sending message:', e);
  } finally {
    isTyping.value = false;
  }
};
</script>

<style scoped>
.chat-interface {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #1a1a2e;
  color: #eee;
  border-radius: 8px;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #16213e;
  border-bottom: 1px solid #0f3460;
}

.chat-header h3 {
  margin: 0;
  font-size: 16px;
  color: #e94560;
}

.clear-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 18px;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.clear-btn:hover {
  opacity: 1;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  gap: 10px;
  max-width: 85%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message.ai {
  align-self: flex-start;
}

.message-avatar {
  font-size: 24px;
  flex-shrink: 0;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  background: #16213e;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.message.user .message-text {
  background: #0f3460;
  border-bottom-right-radius: 4px;
}

.message.ai .message-text {
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #888;
  padding: 0 4px;
}

.message.user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 10px 14px;
  background: #16213e;
  border-radius: 12px;
  border-bottom-left-radius: 4px;
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  background: #e94560;
  border-radius: 50%;
  animation: typing 1.4s infinite;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% {
    transform: translateY(0);
    opacity: 0.7;
  }
  30% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.chat-input-area {
  padding: 16px;
  background: #16213e;
  border-top: 1px solid #0f3460;
}

.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 6px 12px;
  background: #0f3460;
  border: 1px solid #e94560;
  color: #e94560;
  border-radius: 16px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #e94560;
  color: #fff;
}

textarea {
  width: 100%;
  padding: 12px;
  background: #1a1a2e;
  border: 1px solid #0f3460;
  border-radius: 8px;
  color: #eee;
  font-family: inherit;
  font-size: 14px;
  resize: none;
  box-sizing: border-box;
}

textarea:focus {
  outline: none;
  border-color: #e94560;
}

.send-btn {
  margin-top: 10px;
  width: 100%;
  padding: 12px;
  background: #e94560;
  border: none;
  border-radius: 8px;
  color: #fff;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.send-btn:hover:not(:disabled) {
  background: #ff6b6b;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
