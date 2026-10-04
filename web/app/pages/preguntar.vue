<script setup lang="ts">
import { t } from '~/utils/strings'
</script>

<template>
  <div class="page">
    <p class="lead">
      {{ t.voice.comingSoon }}
    </p>
    <div class="actions">
      <BigButton
        variant="secondary"
        to="/"
      >
        {{ t.common.back }}
      </BigButton>
    </div>
  </div>
</template>
