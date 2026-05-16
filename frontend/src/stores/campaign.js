import { defineStore } from 'pinia';
import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000/api/' });

export const useCampaignStore = defineStore('campaign', {
  state: () => ({
    currentSession: null,
    characters: [],
    socket: null,
  }),
  actions: {
    async fetchSession(id) {
      const res = await api.get(`sessions/${id}/`);
      this.currentSession = res.data;
      this.characters = res.data.characters || [];
      this.connectWebSocket(id);
    },
    connectWebSocket(sessionId) {
      this.socket = new WebSocket(`ws://localhost:8000/ws/session/${sessionId}/`);
      
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'token_moved') {
          this.updateCharacterPosition(data.data);
        } else if (data.type === 'init_state') {
          this.characters = data.data;
        } else if (data.type === 'ai_result') {
          alert(`AI Generated: ${JSON.stringify(data.data.content)}`);
          // Здесь можно открыть модальное окно с результатом
          console.log("AI Result:", data.data);
        }
      };
    },
    moveToken(charId, x, y) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        this.socket.send(JSON.stringify({
          action: 'move_token',
          payload: { character_id: charId, x, y }
        }));
        // Оптимистичное обновление
        const char = this.characters.find(c => c.id === charId);
        if (char) { char.position_x = x; char.position_y = y; }
      }
    },
    updateCharacterPosition(data) {
      const char = this.characters.find(c => c.id === data.character_id);
      if (char) {
        char.position_x = data.x;
        char.position_y = data.y;
      }
    },
    async requestAI(prompt, type) {
      if (!this.currentSession) return;
      await api.post(`sessions/${this.currentSession.id}/generate_ai/`, {
        prompt, type
      });
    }
  }
});