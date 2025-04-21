<script setup lang="ts">
defineProps<{
    spriteSheet: string
    spriteIndex: number
}>()

const spriteWidth = 32
const spriteHeight = 32
</script>

<template>
    <div class="sprite-container" :style="{
        backgroundImage: `url(${spriteSheet})`,
        backgroundPosition: `0px -${spriteIndex * spriteHeight}px`,
        width: `${spriteWidth}px`,
        height: `${spriteHeight}px`,
    }"></div>
</template>

<style scoped>
.sprite-container {
    background-repeat: no-repeat;
    overflow: hidden;
    width: 32px;
    height: 32px;
}
</style>