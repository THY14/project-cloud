<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'

interface Keyword {
  keyword: string
  weight: number
}

const route = useRoute()
const userId = Number(route.params.userId)

// Explicitly type the ref
const topKeywords = ref<Keyword[]>([])

onMounted(async () => {
  try {
    const response = await fetch(`/api/user/${userId}/top-keywords?top_n=10`)
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
    const data = await response.json()
    topKeywords.value = data.top_keywords
  } catch (err) {
    console.error("Failed to fetch top keywords:", err)
  }
})
</script>

<template>
<section class="max-w-4xl mx-auto py-8">
  <h2 class="text-2xl font-bold mb-4">Top Keywords for You</h2>
  <div class="flex flex-wrap gap-3">
    <span v-for="item in topKeywords" :key="item.keyword" class="px-3 py-1 bg-red-600 text-white rounded">
      {{ item.keyword }} ({{ item.weight.toFixed(2) }})
    </span>
  </div>
</section>
</template>