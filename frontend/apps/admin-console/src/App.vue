<script setup lang="ts">
import { onMounted, onUnmounted } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

function handleUnauthorized(): void {
  void router.push("/login");
}

onMounted(() => window.addEventListener("auth:unauthorized", handleUnauthorized));
onUnmounted(() => window.removeEventListener("auth:unauthorized", handleUnauthorized));
</script>

<template>
  <router-view />
</template>