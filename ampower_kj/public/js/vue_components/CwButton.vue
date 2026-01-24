<template>
  <button
    :type="type"
    class="tw-inline-flex tw-items-center tw-justify-center tw-gap-2 tw-font-medium tw-rounded-lg tw-transition-all tw-duration-200 tw-cursor-pointer disabled:tw-opacity-50 disabled:tw-cursor-not-allowed"
    :class="[sizeClasses[size], variantClasses[variant], fullWidth ? 'tw-w-full' : '']"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span v-if="loading" class="material-symbols-outlined tw-animate-spin tw-text-lg">progress_activity</span>
    <span v-else-if="icon" class="material-symbols-outlined tw-text-lg">{{ icon }}</span>
    <slot></slot>
    <span v-if="iconRight" class="material-symbols-outlined tw-text-lg">{{ iconRight }}</span>
  </button>
</template>

<script setup>
const props = defineProps({
  variant: {
    type: String,
    default: 'secondary',
    validator: (v) => ['primary', 'secondary', 'ghost', 'danger', 'success'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  type: {
    type: String,
    default: 'button'
  },
  icon: {
    type: String,
    default: ''
  },
  iconRight: {
    type: String,
    default: ''
  },
  loading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['click']);

const handleClick = (e) => {
  if (!props.disabled && !props.loading) {
    emit('click', e);
  }
};

const sizeClasses = {
  sm: 'tw-px-3 tw-py-1.5 tw-text-xs',
  md: 'tw-px-4 tw-py-2 tw-text-sm',
  lg: 'tw-px-5 tw-py-2.5 tw-text-base'
};

const variantClasses = {
  primary: 'tw-bg-primary-700 tw-text-white hover:tw-bg-primary-800 tw-shadow-sm active:tw-scale-[0.98]',
  secondary: 'tw-bg-white tw-text-slate-700 tw-border tw-border-slate-300 hover:tw-bg-slate-50 hover:tw-border-slate-400',
  ghost: 'tw-text-slate-600 hover:tw-bg-slate-100',
  danger: 'tw-bg-red-600 tw-text-white hover:tw-bg-red-700 tw-shadow-sm',
  success: 'tw-bg-green-600 tw-text-white hover:tw-bg-green-700 tw-shadow-sm'
};
</script>
