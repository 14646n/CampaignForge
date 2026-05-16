import { defineStore } from 'pinia';
import axios from 'axios';

export interface Character {
  id: number;
  name: string;
  color: string;
  position_x: number;
  position_y: number;
  x?: number;
  y?: number;
}

export interface Session {
  id: number;
  name: string;
  campaign: number;
  characters: Character[];
}

export interface AIMessage {
  id: number;
  session: number;
  content: string;
  message_type: string;
  created_at: string;
}

interface WebSocketMessage {
  type: string;
  data: any;
}

interface MoveTokenPayload {
  character_id: number;
  x: number;
  y: number;
}

interface WebSocketActionMessage {
  action: string;
  payload: MoveTokenPayload;
}

const api = axios.create({ baseURL: 'http://localhost:8000/api/' });

export const useCampaignStore = defineStore('campaign', {
  state: () => ({
    currentSession: null as Session | null,
    characters: [] as Character[],
    socket: null as WebSocket | null,
    aiMessages: [] as AIMessage[],
  }),
  actions: {
    async fetchSession(id: string | number) {
      const res = await api.get(`sessions/${id}/`);
      this.currentSession = res.data;
      this.characters = res.data.characters || [];
      this.connectWebSocket(id);
    },
    connectWebSocket(sessionId: string | number) {
      this.socket = new WebSocket(`ws://localhost:8000/ws/session/${sessionId}/`);
      
      this.socket.onmessage = (event) => {
        const data = JSON.parse(event.data) as WebSocketMessage;
        if (data.type === 'token_moved') {
          this.updateCharacterPosition(data.data);
        } else if (data.type === 'init_state') {
          this.characters = data.data;
        } else if (data.type === 'ai_result') {
          this.addAIMessage(data.data);
        }
      };
    },
    moveToken(charId: number, x: number, y: number) {
      if (this.socket && this.socket.readyState === WebSocket.OPEN) {
        const message: WebSocketActionMessage = {
          action: 'move_token',
          payload: { character_id: charId, x, y }
        };
        this.socket.send(JSON.stringify(message));
        // Оптимистичное обновление
        const char = this.characters.find(c => c.id === charId);
        if (char) { 
          char.position_x = x; 
          char.position_y = y; 
        }
      }
    },
    updateCharacterPosition(data: { character_id: number; x: number; y: number }) {
      const char = this.characters.find(c => c.id === data.character_id);
      if (char) {
        char.position_x = data.x;
        char.position_y = data.y;
      }
    },
    async requestAI(prompt: string, type: string) {
      if (!this.currentSession) return;
      await api.post(`sessions/${this.currentSession.id}/generate_ai/`, {
        prompt, type
      });
    },
    addAIMessage(message: AIMessage) {
      this.aiMessages.push(message);
    },
    clearMessages() {
      this.aiMessages = [];
    }
  }
});
