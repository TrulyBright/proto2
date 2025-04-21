<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import TileViewer from './components/TileViewer.vue'
import SpriteViewer from './components/SpriteViewer.vue'

interface PlayerData {
  spriteIndex: number
  // …other player fields
}

// width of one tile in px
const tileWidth = 32

// reactive board state from SSE
const board = ref<(PlayerData | null)[][]>([])

board.value = [
  [null, null, null, null, null, null],
  [null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null, null],
  [null, null, null, null, null, null, null],
  [null, null, null, null, null, null],
]

onMounted(() => {
  const source = new EventSource('localhost:8000/watch')
  source.onmessage = (e) => {
    // server sends a JSON‑encoded 2D array of PlayerData|null
    board.value = JSON.parse(e.data)
  }
})

// rows is simply our 2D array
const rows = computed(() => board.value)

// find the longest row for centering
const maxRowLength = computed(() =>
  rows.value.reduce((m, r) => Math.max(m, r.length), 0)
)

// horizontal offset so each row is centered
const rowOffset = (row: (PlayerData | null)[]) =>
  (maxRowLength.value - row.length) * (tileWidth / 2)
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
        <div
          v-for="(tile, colIndex) in row"
          :key="`${rowIndex}-${colIndex}`"
          style="position: relative;"
        >
          <TileViewer
            spriteSheet="/Tileset1.png"
            :spriteIndex="3"
            style="z-index: -1;"
          />
          <SpriteViewer
            spriteSheet="/Idle.png"
            :spriteIndex="0"
            :spriteWidth="48"
            :spriteHeight="48"
            :frameCount="8"
            :duration="1000"
            :loop="true"
            :onAnimationStart="() => {}"
            :onAnimationEnd="() => {}"
            style="position: absolute; top: -30px; left: -8px; z-index: 100;"
          />
        </div>
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