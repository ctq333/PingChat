<script setup>
import { ref } from 'vue';
import { useRoute } from 'vue-router'

const route = useRoute()

</script>

<template>
  <div class="app-layout">
    <main class="main-content">
      <UApp>
        <router-view />
      </UApp>
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  height: 100vh; /* ensures the layout fills the viewport */
  /*overflow: hidden;  prevent unwanted scroll */
}

.main-content {
  flex: 1 1 0%;
  min-height: 0; /* very important for flex children to avoid overflow */
  /*overflow: hidden;  prevents main-content from scrolling */
  /*background: #fafbfc;*/
}
</style>
