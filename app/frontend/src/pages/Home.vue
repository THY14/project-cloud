<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useRouter } from 'vue-router'

const route = useRoute()

const router = useRouter()

const userId = ref<number | null>(null)
const movies = ref<any[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  userId.value = Number(route.params.userId) || null
  console.log('User ID from URL:', userId.value)

  if (!userId.value) {
    error.value = "Invalid user ID"
    loading.value = false
    return
  }

  try {
    const res = await fetch(
      `/api/user/${userId.value}/recommend?top_n=10`
    )

    if (!res.ok) {
      throw new Error("Failed to fetch recommendations")
    }

    const data = await res.json()

    movies.value = data.recommendations.map((movie: any) => ({
      id: movie.movie_id,
      name: movie.title,
      score: movie.score,
      poster: movie.poster_url
    }))

  } catch (err: any) {
    console.error(err)
    error.value = "Could not load recommendations"
  } finally {
    loading.value = false
  }
})

function goKeyword() {
  router.push(`/recommend/${userId.value}/keyword`)
}
</script>

<template>
  <div class="bg-gray-900 min-h-screen text-white">

    <!-- Navbar -->
    <nav class="flex items-center justify-between p-6 bg-black bg-opacity-80 fixed w-full z-10">
      <div class="text-3xl font-bold text-red-600">CADTFLIX</div>

      <div @click="goKeyword" class="text-xl text-gray-300 cursor-pointer">
        User {{ userId }}
      </div>
    </nav>

    <!-- Hero -->
    <header class="pt-32 text-center">
      <h1 class="text-5xl font-extrabold mb-4">
        Welcome to CADTFLIX
      </h1>

      <p class="text-xl text-gray-400">
        Personalized movie recommendations just for you
      </p>
    </header>

    <!-- Loading -->
    <div v-if="loading" class="text-center mt-20 text-xl">
      Loading recommendations...
    </div>

    <!-- Error -->
    <div v-if="error" class="text-center mt-20 text-red-500">
      {{ error }}
    </div>

    <!-- Movie grid -->
    <section v-if="!loading && !error" class="max-w-6xl mx-auto px-4 py-12">

      <h2 class="text-3xl font-bold mb-8">
        Recommended Movies
      </h2>

      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-6">

        <div
          v-for="movie in movies"
          :key="movie.id"
          class="rounded overflow-hidden shadow-lg hover:scale-105 transform transition duration-300 cursor-pointer"
        >

          <img
            :src="movie.poster"
            :alt="movie.name"
            class="w-full h-64 object-cover"
          />

          <div class="p-3 bg-gray-800 text-center">

            <div class="font-semibold">
              {{ movie.name }}
            </div>

            <div class="text-sm text-gray-400">
              Score: {{ movie.score.toFixed(3) }}
            </div>

          </div>

        </div>

      </div>

    </section>

  </div>
</template>