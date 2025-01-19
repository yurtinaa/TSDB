<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <header class="head py-3 mb-3 border-bottom" v-if="$route.meta.isNotAuth">
    <div
      class="container-fluid d-grid gap-3 align-items-center"
      style="grid-template-columns: 1fr 2fr"
    >
      <a class="text-light dropdown-item fw-bold fs-4" href="/">Проекты</a>

      <div class="d-flex justify-content-end">
        <button
          class="btn btn-secondary dropdown-toggle"
          type="button"
          data-bs-toggle="dropdown"
          aria-expanded="false"
        >
          Настройки
        </button>
        <ul class="dropdown-menu text-small" aria-labelledby="dropdown" style="">
          <li>
            <a class="dropdown-item" href="/login" :onclick="() => this.$store.dispatch('logout')"
              >Выйти</a
            >
          </li>
        </ul>
      </div>
    </div>
  </header>

  <RouterView />
</template>

<style scoped>
.head {
  background-color: rgb(0, 0, 0);
}
</style>
