<script setup>
import { RouterLink, RouterView } from 'vue-router'
import HelloWorld from './components/HelloWorld.vue'
</script>

<template>
  <header>
    <img alt="Golden Gate Bridge" class="logo" src="@/assets/bridge.jpg" width="308" height="210" />

    <div class="wrapper">
      <HelloWorld />

    </div>
  </header>

  <RouterView />
  
</template>

<style scoped>

</style>