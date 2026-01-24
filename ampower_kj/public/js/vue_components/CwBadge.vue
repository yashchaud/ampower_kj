<template>
  <span
    class="tw-inline-flex tw-items-center tw-font-medium tw-rounded-full"
    :class="[sizeClasses[size], variantClasses[variant]]"
  >
    <span
      v-if="showDot"
      class="tw-w-1.5 tw-h-1.5 tw-rounded-full tw-mr-1.5"
      :class="dotClasses[variant]"
    ></span>
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup>
const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (v) => ['default', 'unassigned', 'assigned', 'incoming', 'qa', 'ready', 'delivered', 'cancelled', 'primary', 'success', 'warning', 'danger'].includes(v)
  },
  size: {
    type: String,
    default: 'md',
    validator: (v) => ['sm', 'md', 'lg'].includes(v)
  },
  showDot: {
    type: Boolean,
    default: false
  }
});

const sizeClasses = {
  sm: 'tw-px-1.5 tw-py-0.5 tw-text-[10px]',
  md: 'tw-px-2 tw-py-0.5 tw-text-xs',
  lg: 'tw-px-2.5 tw-py-1 tw-text-sm'
};

const variantClasses = {
  default: 'tw-bg-slate-100 tw-text-slate-700',
  unassigned: 'tw-bg-amber-100 tw-text-amber-800',
  assigned: 'tw-bg-blue-100 tw-text-blue-800',
  incoming: 'tw-bg-violet-100 tw-text-violet-800',
  qa: 'tw-bg-cyan-100 tw-text-cyan-800',
  ready: 'tw-bg-emerald-100 tw-text-emerald-800',
  delivered: 'tw-bg-green-100 tw-text-green-800',
  cancelled: 'tw-bg-red-100 tw-text-red-800',
  primary: 'tw-bg-primary-100 tw-text-primary-800',
  success: 'tw-bg-green-100 tw-text-green-800',
  warning: 'tw-bg-amber-100 tw-text-amber-800',
  danger: 'tw-bg-red-100 tw-text-red-800'
};

const dotClasses = {
  default: 'tw-bg-slate-500',
  unassigned: 'tw-bg-amber-500',
  assigned: 'tw-bg-blue-500',
  incoming: 'tw-bg-violet-500',
  qa: 'tw-bg-cyan-500',
  ready: 'tw-bg-emerald-500',
  delivered: 'tw-bg-green-500',
  cancelled: 'tw-bg-red-500',
  primary: 'tw-bg-primary-500',
  success: 'tw-bg-green-500',
  warning: 'tw-bg-amber-500',
  danger: 'tw-bg-red-500'
};
</script>
