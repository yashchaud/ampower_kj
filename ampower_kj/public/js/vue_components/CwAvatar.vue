<template>
  <div
    class="tw-inline-flex tw-items-center tw-justify-center tw-rounded-full tw-font-semibold tw-text-white tw-overflow-hidden tw-flex-shrink-0"
    :class="sizeClasses[size]"
    :style="{ backgroundColor: backgroundColor }"
  >
    <img v-if="src" :src="src" :alt="name" class="tw-w-full tw-h-full tw-object-cover" />
    <span v-else>{{ initials }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  name: {
    type: String,
    default: ''
  },
  src: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(v)
  },
  color: {
    type: String,
    default: ''
  }
});

const initials = computed(() => {
  if (!props.name) return '?';
  const parts = props.name.trim().split(' ');
  if (parts.length === 1) {
    return parts[0].charAt(0).toUpperCase();
  }
  return (parts[0].charAt(0) + parts[parts.length - 1].charAt(0)).toUpperCase();
});

const sizeClasses = {
  xs: 'tw-w-5 tw-h-5 tw-text-[10px]',
  sm: 'tw-w-6 tw-h-6 tw-text-xs',
  md: 'tw-w-8 tw-h-8 tw-text-sm',
  lg: 'tw-w-10 tw-h-10 tw-text-base',
  xl: 'tw-w-12 tw-h-12 tw-text-lg'
};

const backgroundColor = computed(() => {
  if (props.color) {
    return props.color;
  }
  // Generate a consistent color from name
  const colors = [
    '#6366f1', // indigo
    '#8b5cf6', // violet
    '#a855f7', // purple
    '#ec4899', // pink
    '#ef4444', // red
    '#f97316', // orange
    '#eab308', // yellow
    '#22c55e', // green
    '#14b8a6', // teal
    '#06b6d4', // cyan
    '#3b82f6', // blue
  ];
  const hash = props.name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  return colors[hash % colors.length];
});
</script>
