<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const userId = ref<number | null>(null)
const router = useRouter()

function login() {
  if (!userId.value) return alert('Please enter your user ID.')
  router.push(`/recommend/${userId.value}`)
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-linear-to-r from-gray-900 via-gray-800 to-gray-900 px-4">
    <div class="bg-gray-800 rounded-2xl shadow-2xl p-10 w-full max-w-sm text-center">
      <h1 class="text-4xl font-extrabold text-red-600 mb-6">CADTFLIX</h1>
      <p class="text-gray-300 mb-6">Enter your user ID to get your personalized movie recommendations.</p>

      <input
        type="number"
        v-model.number="userId"
        placeholder="User ID"
        class="w-full px-4 py-3 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-red-600 text-white bg-gray-900 placeholder-gray-400 font-medium"
      />

      <button
        @click="login"
        class="w-full bg-red-600 hover:bg-red-700 transition-colors duration-300 text-white font-bold py-3 rounded-lg shadow-lg"
      >
        Login
      </button>
    </div>
  </div>
</template>