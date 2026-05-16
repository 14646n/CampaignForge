import { createRouter, createWebHistory } from 'vue-router';
import BattleMap from '../views/BattleMap.vue';

const routes = [
  { path: '/map/:id', component: BattleMap },
  { path: '/', redirect: '/map/1' } // Редирект на первую сессию для теста
];

export default createRouter({ history: createWebHistory(), routes });