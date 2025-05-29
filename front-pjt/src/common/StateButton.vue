<script setup>
import { computed, useAttrs, defineProps } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  type: {
    type: String,
    default: "button"
  },
  size: {
    type: String,
    default: "md"
  },
  isActive: {
    type: Boolean,
    default: false
  },
  class: {
    type: String,
    default: ""
  },
  to: {
    type: String,
    default: ""
  }
});

const router = useRouter();

const attrs = useAttrs();

function handleClick() {
  if (props.to) {
    router.push(props.to);
  }
}
</script>

<template>
  <button
    :class="[
      'toggle-button',
      props.class,
      props.size,
      props.type,
      { active: props.isActive }
    ]"
    v-bind="attrs"
    @click="handleClick"
  >
    <slot></slot>
  </button>
</template>

<style scoped lang="scss">
.toggle-button {
  white-space: nowrap;
  padding: 10px 20px;
  font-size: 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background-color: white;
  color: #666;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;

  &.tag {
    background-color: #f5f5f5;
    cursor: default;
    border: none;
    font-weight: 600;
  }

  &.state {
    &:hover {
      background-color: #f5f5f5;
    }

    &.active {
      background-color: #272c97;
      color: white;
      border-color: #272c97;

      &:hover {
        background-color: #1f2370;
      }
    }
  }

  &.sm {
    padding: 4px 10px;
    font-size: 13px;
  }

  &.md {
    padding: 8px 12px;
    font-size: 15px;
  }

  &:disabled {
    pointer-events: none;
    opacity: 0.6;
  }
}
</style>
