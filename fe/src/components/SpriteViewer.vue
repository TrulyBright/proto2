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

const endingPosition = computed(() => {
    return -props.spriteWidth * props.frameCount
})
</script>

<template>
    <div class="sprite-container" :style="{
        backgroundImage: `url(${spriteSheet})`,
        width: `${spriteWidth}px`,
        height: `${spriteHeight}px`,
        animation: `play ${duration}ms steps(${frameCount}) ${loop ? 'infinite' : 'forwards'}`,
    }"></div>
</template>

<style>
@keyframes play {
    from {
        background-position: 0 0;
    }
    to {
        background-position: 384px 0;
    }
}
</style>