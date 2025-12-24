---
// Job search filter component using Vue.js Composition API
---

<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h3 class="card-title">Job Search Filters</h3>

      <div class="form-control">
        <label class="label">
          <span class="label-text">Search Jobs</span>
        </label>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Job title, company, or keywords..."
          class="input input-bordered"
        />
      </div>

      <div class="form-control">
        <label class="label">
          <span class="label-text">Skills</span>
        </label>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="skill in availableSkills"
            :key="skill"
            @click="toggleSkill(skill)"
            :class="[
              'btn btn-sm',
              selectedSkills.includes(skill) ? 'btn-primary' : 'btn-outline'
            ]"
          >
            {{ skill }}
          </button>
        </div>
      </div>

      <div class="form-control">
        <label class="label">
          <span class="label-text">Work Style</span>
        </label>
        <div class="flex gap-2">
          <label class="cursor-pointer label">
            <input
              v-model="remoteOnly"
              type="checkbox"
              class="checkbox checkbox-primary"
            />
            <span class="label-text ml-2">Remote Only</span>
          </label>
          <label class="cursor-pointer label">
            <input
              v-model="asyncOnly"
              type="checkbox"
              class="checkbox checkbox-secondary"
            />
            <span class="label-text ml-2">Async Only</span>
          </label>
        </div>
      </div>

      <div class="card-actions justify-end mt-4">
        <button @click="clearFilters" class="btn btn-ghost">Clear All</button>
        <button @click="applyFilters" class="btn btn-primary">Apply Filters</button>
      </div>

      <div class="alert alert-info mt-4" v-if="hasActiveFilters">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
        </svg>
        <span>{{ activeFiltersCount }} filter{{ activeFiltersCount === 1 ? '' : 's' }} active</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const searchQuery = ref('')
const selectedSkills = ref<string[]>([])
const remoteOnly = ref(false)
const asyncOnly = ref(false)

const availableSkills = [
  'JavaScript', 'TypeScript', 'Python', 'React', 'Vue.js',
  'Node.js', 'Django', 'PostgreSQL', 'MongoDB', 'AWS'
]

const hasActiveFilters = computed(() => {
  return searchQuery.value.trim() ||
         selectedSkills.value.length > 0 ||
         remoteOnly.value ||
         asyncOnly.value
})

const activeFiltersCount = computed(() => {
  let count = 0
  if (searchQuery.value.trim()) count++
  if (selectedSkills.value.length > 0) count++
  if (remoteOnly.value) count++
  if (asyncOnly.value) count++
  return count
})

const toggleSkill = (skill: string) => {
  const index = selectedSkills.value.indexOf(skill)
  if (index > -1) {
    selectedSkills.value.splice(index, 1)
  } else {
    selectedSkills.value.push(skill)
  }
}

const clearFilters = () => {
  searchQuery.value = ''
  selectedSkills.value = []
  remoteOnly.value = false
  asyncOnly.value = false
}

const applyFilters = () => {
  // In a real app, this would emit events or call API
  console.log('Applying filters:', {
    query: searchQuery.value,
    skills: selectedSkills.value,
    remote: remoteOnly.value,
    async: asyncOnly.value
  })

  alert(`Filters applied! Search: "${searchQuery.value}", Skills: ${selectedSkills.value.join(', ')}, Remote: ${remoteOnly.value}, Async: ${asyncOnly.value}`)
}

// Define emits for parent components
defineEmits<{
  filtersChanged: [filters: {
    query: string
    skills: string[]
    remote: boolean
    async: boolean
  }]
}>()
</script>