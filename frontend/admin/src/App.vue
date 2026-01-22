<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow-sm px-6 py-4 flex items-center justify-between">
      <h1 class="text-lg font-semibold text-gray-800">农产品溯源后台管理</h1>
    </header>
    <main class="p-6">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts"></script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, -system-ui, sans-serif;
}
</style>
