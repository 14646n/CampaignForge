import { createRouter, createWebHistory } from 'vue-router';
import BattleMap from '../views/BattleMap.vue';
import CampaignView from '../views/CampaignView.vue';
import HomeView from '../views/HomeView.vue';

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/campaigns', name: 'campaigns', component: CampaignView },
  { path: '/campaign/:id', name: 'campaign', component: CampaignView },
  { path: '/map/:id', name: 'map', component: BattleMap },
];

export default createRouter({ history: createWebHistory(), routes });