<template>
  <div class="tw-relative tw-inline-block" ref="dropdownRef">
    <!-- Trigger button -->
    <div @click="toggle">
      <slot name="trigger">
        <CwButton
          :variant="buttonVariant"
          :icon="icon"
          :icon-right="isOpen ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
        >
          {{ label }}
        </CwButton>
      </slot>
    </div>

    <!-- Backdrop -->
    <Teleport to="body">
      <div v-if="isOpen" class="tw-fixed tw-inset-0 tw-z-40" @click="close"></div>
    </Teleport>

    <!-- Dropdown menu -->
    <Transition
      enter-active-class="tw-transition tw-ease-out tw-duration-200"
      enter-from-class="tw-opacity-0 tw-scale-95"
      enter-to-class="tw-opacity-100 tw-scale-100"
      leave-active-class="tw-transition tw-ease-in tw-duration-150"
      leave-from-class="tw-opacity-100 tw-scale-100"
      leave-to-class="tw-opacity-0 tw-scale-95"
    >
      <div
        v-if="isOpen"
        class="tw-absolute tw-z-50 tw-mt-2 tw-bg-white tw-rounded-xl tw-shadow-dropdown tw-border tw-border-slate-200 tw-py-2 tw-min-w-[200px]"
        :class="[alignClass, widthClass]"
      >
        <!-- Header -->
        <div v-if="title" class="tw-px-4 tw-py-2 tw-border-b tw-border-slate-100">
          <p class="tw-text-xs tw-font-semibold tw-text-slate-500 tw-uppercase tw-tracking-wider">
            {{ title }}
          </p>
        </div>

        <!-- Items -->
        <slot>
          <template v-for="(item, index) in items" :key="item.value || index">
            <div v-if="item.divider" class="tw-my-2 tw-border-t tw-border-slate-100"></div>
            <button
              v-else
              class="tw-w-full tw-flex tw-items-center tw-gap-3 tw-px-4 tw-py-2.5 tw-text-sm tw-text-left tw-transition-colors"
              :class="[
                item.danger ? 'tw-text-red-600 hover:tw-bg-red-50' : 'tw-text-slate-700 hover:tw-bg-slate-50',
                item.disabled ? 'tw-opacity-50 tw-cursor-not-allowed' : ''
              ]"
              :disabled="item.disabled"
              @click="selectItem(item)"
            >
              <div
                v-if="item.icon"
                class="tw-w-8 tw-h-8 tw-rounded-lg tw-flex tw-items-center tw-justify-center"
                :class="item.iconBg || 'tw-bg-slate-100'"
              >
                <span
                  class="material-symbols-outlined tw-text-lg"
                  :class="item.iconClass || 'tw-text-slate-600'"
                >
                  {{ item.icon }}
                </span>
              </div>
              <div class="tw-flex-1">
                <p class="tw-font-medium">{{ item.label }}</p>
                <p v-if="item.description" class="tw-text-xs tw-text-slate-500">{{ item.description }}</p>
              </div>
              <span v-if="item.shortcut" class="tw-text-xs tw-text-slate-400 tw-font-mono">{{ item.shortcut }}</span>
            </button>
          </template>
        </slot>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import CwButton from './CwButton.vue';

const props = defineProps({
  label: {
    type: String,
    default: ''
  },
  icon: {
    type: String,
    default: ''
  },
  title: {
    type: String,
    default: ''
  },
  items: {
    type: Array,
    default: () => []
    // Each item: { label: string, value?: any, icon?: string, iconBg?: string, iconClass?: string, description?: string, shortcut?: string, divider?: boolean, danger?: boolean, disabled?: boolean }
  },
  buttonVariant: {
    type: String,
    default: 'secondary'
  },
  align: {
    type: String,
    default: 'right',
    validator: (v) => ['left', 'right'].includes(v)
  },
  width: {
    type: String,
    default: 'auto',
    validator: (v) => ['auto', 'full', 'trigger'].includes(v)
  }
});

const emit = defineEmits(['select']);

const isOpen = ref(false);
const dropdownRef = ref(null);

const toggle = () => {
  isOpen.value = !isOpen.value;
};

const close = () => {
  isOpen.value = false;
};

const selectItem = (item) => {
  if (item.disabled) return;
  emit('select', item);
  close();
};

const alignClass = computed(() => props.align === 'left' ? 'tw-left-0' : 'tw-right-0');

const widthClass = computed(() =>
  props.width === 'full' ? 'tw-w-full' :
  props.width === 'trigger' ? 'tw-min-w-full' : ''
);
</script>
