<template>
  <div class="bg-base-200 p-6 rounded-lg">
    <h2 class="text-2xl font-bold mb-4">Skills Showcase</h2>

    <div class="form-control mb-4">
      <label class="label">
        <span class="label-text">Add a skill</span>
      </label>
      <div class="flex gap-2">
        <input
          v-model="newSkill"
          @keyup.enter="addSkill"
          type="text"
          placeholder="e.g., React, Python, Node.js"
          class="input input-bordered flex-1"
        />
        <button @click="addSkill" class="btn btn-primary" :disabled="!newSkill.trim()">
          Add
        </button>
      </div>
    </div>

    <div v-if="skills.length > 0" class="mb-4">
      <h3 class="text-lg font-semibold mb-2">Your Skills:</h3>
      <div class="flex flex-wrap gap-2">
        <div
          v-for="(skill, index) in skills"
          :key="index"
          class="badge badge-primary cursor-pointer"
          @click="removeSkill(index)"
        >
          {{ skill }}
          <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </div>
      </div>
    </div>

    <div class="stats stats-vertical lg:stats-horizontal shadow">
      <div class="stat">
        <div class="stat-title">Skills Added</div>
        <div class="stat-value">{{ skills.length }}</div>
        <div class="stat-desc">Click badges to remove</div>
      </div>

      <div class="stat">
        <div class="stat-title">Vue.js Status</div>
        <div class="stat-value text-success">Active</div>
        <div class="stat-desc">Component working</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const skills = ref<string[]>(['JavaScript', 'Vue.js', 'TypeScript'])
const newSkill = ref('')

const addSkill = () => {
  if (newSkill.value.trim() && !skills.value.includes(newSkill.value.trim())) {
    skills.value.push(newSkill.value.trim())
    newSkill.value = ''
  }
}

const removeSkill = (index: number) => {
  skills.value.splice(index, 1)
}
</script>