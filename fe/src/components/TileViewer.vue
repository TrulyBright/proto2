<script setup lang="ts">
import { ref, computed } from 'vue'

defineProps<{
    spriteSheet: string
    spriteIndex: number
}>()

const spriteWidth = 32
const spriteHeight = 32
const isHovered = ref(false)

const currentSpriteIndex = computed(() => {
    return isHovered.value ? 4 : 3 // Toggle between sprite indices 3 and 4
})
</script>

<template>
    <div 
        class="sprite-container" 
        :style="{
            backgroundImage: `url(${spriteSheet})`,
            backgroundPosition: `0px -${currentSpriteIndex * spriteHeight}px`,
            width: `${spriteWidth}px`,
            height: `${spriteHeight}px`,
        }"
        @mouseover="isHovered = true"
        @mouseleave="isHovered = false"
    ></div>
</template>

<style scoped>
.sprite-container {
    background-repeat: no-repeat;
    overflow: hidden;
    width: 32px;
    height: 32px;
    cursor: pointer;
}
</style>