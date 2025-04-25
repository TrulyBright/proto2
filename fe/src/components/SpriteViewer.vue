<script setup lang="ts">
import { computed } from 'vue'
const props = defineProps<{
    spriteSheet: string
    spriteIndex: number
    spriteWidth: number
    spriteHeight: number
    frameCount: number
    duration: number
    loop: boolean
    onAnimationStart: () => void
    onAnimationEnd: () => void
}>()

const startingY = computed(() => {
    return props.spriteHeight * props.spriteIndex
})

const endingX = computed(() => {
    return props.spriteWidth * (props.frameCount - 1)
})
</script>

<template>
    <div class="sprite-container" :style="{
        backgroundImage: `url(${spriteSheet})`,
        width: `${spriteWidth}px`,
        height: `${spriteHeight}px`,
        animation: `play ${duration}ms steps(${frameCount}) ${loop ? 'infinite' : 'forwards'}`,
    }">
    </div>
</template>

