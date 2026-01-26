<template>
  <Teleport to="body">
    <Transition
      enter-active-class="tw-transition-all tw-duration-300 tw-ease-out"
      enter-from-class="tw-opacity-0"
      enter-to-class="tw-opacity-100"
      leave-active-class="tw-transition-all tw-duration-200 tw-ease-in"
      leave-from-class="tw-opacity-100"
      leave-to-class="tw-opacity-0"
    >
      <div
        v-if="modelValue"
        class="tw-fixed tw-inset-0 tw-z-[9999] tw-flex tw-items-center tw-justify-center tw-p-4 tw-bg-black/50 tw-backdrop-blur-sm"
        @click="handleBackdropClick"
      >
        <Transition
          enter-active-class="tw-transition-all tw-duration-300 tw-ease-out"
          enter-from-class="tw-opacity-0 tw-scale-95 tw--translate-y-4"
          enter-to-class="tw-opacity-100 tw-scale-100 tw-translate-y-0"
          leave-active-class="tw-transition-all tw-duration-200 tw-ease-in"
          leave-from-class="tw-opacity-100 tw-scale-100 tw-translate-y-0"
          leave-to-class="tw-opacity-0 tw-scale-95 tw--translate-y-4"
        >
          <div
            v-if="modelValue"
            class="tw-relative tw-w-full tw-max-w-[600px] tw-bg-white dark:tw-bg-slate-800 tw-rounded-3xl tw-shadow-2xl tw-border tw-border-white/80 dark:tw-border-gray-700/50 tw-overflow-hidden"
            @click.stop
          >
            <!-- Close Button -->
            <button
              class="tw-absolute tw-top-6 tw-right-6 tw-z-20 tw-p-2 tw-rounded-full tw-text-gray-400 hover:tw-text-gray-600 hover:tw-bg-gray-100 dark:tw-text-gray-500 dark:hover:tw-text-gray-300 dark:hover:tw-bg-gray-700 tw-transition-all focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-primary-500/20"
              @click="handleClose"
              aria-label="Close dialog"
            >
              <span class="material-symbols-outlined tw-text-xl tw-leading-none">close</span>
            </button>

            <!-- Modal Content -->
            <div class="tw-px-6 sm:tw-px-8 tw-pt-6 sm:tw-pt-8 tw-pb-4 tw-flex tw-flex-col tw-items-start tw-w-full">
              <!-- Header -->
              <div class="tw-flex tw-items-center tw-gap-3 sm:tw-gap-4 tw-flex-wrap">
                <div class="tw-flex tw-items-center tw-justify-center tw-w-10 tw-h-10 tw-rounded-full tw-bg-gray-50 dark:tw-bg-gray-800/80 tw-text-gray-700 dark:tw-text-gray-300 tw-ring-1 tw-ring-gray-100 dark:tw-ring-gray-700 tw-shrink-0">
                  <span class="material-symbols-outlined tw-text-xl">sync_alt</span>
                </div>
                <div class="tw-flex tw-items-center tw-gap-3 tw-flex-wrap">
                  <h2 class="tw-font-display tw-text-xl sm:tw-text-2xl tw-font-semibold tw-text-gray-900 dark:tw-text-white tw-tracking-tight tw-leading-snug">
                    Transition Order Status
                  </h2>
                  <span class="tw-px-2.5 tw-py-1 tw-rounded-md tw-bg-gray-50 dark:tw-bg-gray-800/80 tw-text-[10px] tw-text-gray-500 dark:tw-text-gray-400 tw-font-bold tw-tracking-[0.1em] tw-uppercase tw-border tw-border-gray-100 dark:tw-border-gray-700">
                    {{ itemCount > 1 ? 'Bulk Action' : 'Single Action' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Transition Visual -->
            <div class="tw-w-full tw-px-6 sm:tw-px-8 tw-py-6 sm:tw-py-8 tw-flex tw-items-center tw-justify-center">
              <div class="tw-flex tw-flex-col sm:tw-flex-row tw-items-center tw-justify-center tw-w-full tw-gap-6 sm:tw-gap-12">
                <!-- Current Stage -->
                <div class="tw-flex tw-flex-col tw-items-center tw-space-y-2 tw-opacity-60 tw-grayscale tw-transition-all tw-duration-500 tw-min-w-[120px]">
                  <span class="tw-text-[10px] tw-uppercase tw-tracking-widest tw-text-gray-500 tw-font-sans tw-font-semibold">Current</span>
                  <span class="tw-text-xl sm:tw-text-2xl tw-font-display tw-text-gray-500 dark:tw-text-gray-400 tw-line-through tw-decoration-gray-300/50 tw-text-center">{{ fromStage }}</span>
                </div>

                <!-- Arrow -->
                <div class="tw-flex tw-items-center tw-justify-center tw-text-gray-300 dark:tw-text-gray-600 tw-rotate-90 sm:tw-rotate-0">
                  <span class="material-symbols-outlined tw-text-4xl tw-font-light">arrow_right_alt</span>
                </div>

                <!-- Target Stage -->
                <div class="tw-flex tw-flex-col tw-items-center tw-space-y-2 tw-relative tw-min-w-[120px]">
                  <span class="tw-text-[10px] tw-uppercase tw-tracking-widest tw-text-primary-600 dark:tw-text-blue-400 tw-font-sans tw-font-bold">Target</span>
                  <span class="tw-text-2xl sm:tw-text-3xl tw-font-display tw-text-gray-900 dark:tw-text-white tw-font-medium tw-text-center">{{ toStage }}</span>
                  <div class="tw-absolute tw-left-1/2 tw-top-1/2 tw--translate-x-1/2 tw--translate-y-1/2 tw-w-20 tw-h-20 tw-bg-primary-500/5 dark:tw-bg-white/5 tw-rounded-full tw-blur-xl tw--z-10"></div>
                </div>
              </div>
            </div>

            <!-- Info Box (for bulk actions) -->
            <div v-if="itemCount > 1" class="tw-mx-6 sm:tw-mx-8 tw-mb-6 tw-p-3 sm:tw-p-4 tw-bg-blue-50 dark:tw-bg-blue-900/20 tw-border tw-border-blue-200 dark:tw-border-blue-700/50 tw-rounded-lg tw-flex tw-items-start tw-gap-3">
              <span class="material-symbols-outlined tw-text-blue-600 dark:tw-text-blue-400 tw-text-base sm:tw-text-lg tw-shrink-0 tw-mt-0.5">info</span>
              <span class="tw-text-xs sm:tw-text-sm tw-text-blue-900 dark:tw-text-blue-100 tw-font-medium">
                {{ itemCount }} items will be moved to "{{ toStage }}"
              </span>
            </div>

            <!-- Actions -->
            <div class="tw-flex tw-flex-col-reverse sm:tw-flex-row tw-items-stretch sm:tw-items-center tw-justify-end tw-w-full tw-gap-3 tw-px-6 sm:tw-px-8 tw-pb-6 sm:tw-pb-8 tw-pt-2">
              <button
                class="tw-px-6 tw-py-2.5 tw-rounded-xl tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-text-gray-600 dark:tw-text-gray-300 tw-font-medium tw-text-sm hover:tw-text-gray-900 dark:hover:tw-text-white hover:tw-border-gray-300 dark:hover:tw-border-gray-500 hover:tw-bg-gray-50 dark:hover:tw-bg-gray-700 tw-transition-all tw-duration-200 focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-gray-200 dark:focus:tw-ring-gray-600"
                @click="handleClose"
              >
                Cancel
              </button>
              <button
                class="tw-px-6 tw-py-2.5 tw-rounded-xl tw-bg-primary-600 tw-text-white tw-font-medium tw-text-sm tw-shadow-lg tw-shadow-primary-200/50 dark:tw-shadow-none hover:tw-bg-primary-500 dark:hover:tw-bg-primary-500 tw-transition-all tw-duration-200 focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-offset-2 focus:tw-ring-primary-600/15 dark:tw-ring-offset-gray-900 tw-transform active:tw-scale-[0.98]"
                @click="handleConfirm"
              >
                Confirm Transition
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
// defineProps and defineEmits are compiler macros - no import needed in <script setup>

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  fromStage: {
    type: String,
    required: true
  },
  toStage: {
    type: String,
    required: true
  },
  itemCount: {
    type: Number,
    default: 1
  }
});

const emit = defineEmits(['update:modelValue', 'confirm', 'cancel']);

const handleClose = () => {
  emit('update:modelValue', false);
  emit('cancel');
};

const handleBackdropClick = () => {
  handleClose();
};

const handleConfirm = () => {
  emit('confirm');
  emit('update:modelValue', false);
};
</script>

<style scoped>
/* Ensure smooth animations */
* {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Backdrop blur support */
@supports (backdrop-filter: blur(8px)) {
  .tw-backdrop-blur-sm {
    backdrop-filter: blur(8px);
  }
}

/* Mobile optimizations */
@media (max-width: 640px) {
  .material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 20;
  }
}
</style>
