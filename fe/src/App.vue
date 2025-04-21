<script setup lang="ts">
import { ref, computed } from 'vue'
import TileViewer from './components/TileViewer.vue'

const radius = ref(6)   // change this to increase/decrease board radius
const tileWidth = 32    // should match your TileViewer rhombus width

// build a 2D array of tiles in a pointy‐topped hexagon layout
const rows = computed<number[][]>(() => {
  const R = radius.value
  const result: number[][] = []
  for (let r = -R; r <= R; r++) {
    const row: number[] = []
    const startQ = Math.max(-R, -r - R)
    const endQ   = Math.min(R, -r + R)
    for (let q = startQ; q <= endQ; q++) {
      row.push(4)  // placeholder spriteIndex or data
    }
    result.push(row)
  }
  return result
})

// longest row in a hexagon is always 2*R + 1
const maxRowLength = computed(() => 2 * radius.value + 1)

// compute horizontal offset so each row is centered
// (difference in tile count * half tile width)
const rowOffset = (row: number[]) => {
  return (maxRowLength.value - row.length) * (tileWidth / 2)
}
</script>

<template>
  <div id="app">
    <div class="board">
      <div
        class="board-row"
        v-for="(row, rowIndex) in rows"
        :key="rowIndex"
        :style="{ marginLeft: rowOffset(rowIndex) + 'px' }"
      >
        <TileViewer
          v-for="(tile, colIndex) in row"
          :key="`${rowIndex}-${colIndex}`"
          spriteSheet="/Tileset1.png"
          :spriteIndex="3"
        />
      </div>
    </div>
  </div>
</template>

<style>
#app {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}
.board {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.board-row {
  display: flex;
  margin-top: -12px; /* half the tile height */
}
</style>