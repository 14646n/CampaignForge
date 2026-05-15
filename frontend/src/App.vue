<template>
  <div id="app">
    <nav style="padding: 1rem; background: #333; color: white;">
      <router-link to="/" style="color: white; margin-right: 1rem;">Home</router-link>
      <router-link to="/campaigns" style="color: white;">Campaigns</router-link>
    </nav>
    <main style="padding: 1rem;">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
</script>

<style>
body { margin: 0; font-family: sans-serif; }
</style>
