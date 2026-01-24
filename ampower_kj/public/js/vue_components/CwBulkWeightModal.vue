<template>
  <Teleport to="body">
    <!-- Modal -->
    <Transition
      enter-active-class="tw-transition-all tw-duration-300"
      enter-from-class="tw-opacity-0 tw-scale-95"
      enter-to-class="tw-opacity-100 tw-scale-100"
      leave-active-class="tw-transition-all tw-duration-200"
      leave-from-class="tw-opacity-100 tw-scale-100"
      leave-to-class="tw-opacity-0 tw-scale-95"
    >
      <div
        v-if="modelValue"
        class="tw-fixed tw-inset-0 tw-z-[100] tw-flex tw-items-center tw-justify-center tw-p-4 tw-bg-black/50 tw-backdrop-blur-sm"
        @click.self="closeModal"
      >
        <main
          class="tw-relative tw-w-full tw-max-w-[520px] tw-max-h-[90vh] tw-overflow-y-auto tw-bg-white dark:tw-bg-[#1E293B] tw-rounded-2xl sm:tw-rounded-3xl tw-shadow-2xl tw-border tw-border-white/80 dark:tw-border-gray-700/50 tw-transform tw-transition-all"
          @click.stop
        >
            <!-- Close Button -->
            <div class="tw-absolute tw-top-6 tw-right-6 tw-z-20">
              <button
                aria-label="Close dialog"
                class="tw-group tw-p-2 tw-rounded-full tw-text-gray-400 hover:tw-text-gray-600 hover:tw-bg-gray-100 dark:tw-text-gray-500 dark:hover:tw-text-gray-300 dark:hover:tw-bg-gray-800 tw-transition-all focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-[#1f2937]/20"
                @click="closeModal"
              >
                <span class="material-symbols-outlined tw-text-2xl tw-leading-none">close</span>
              </button>
            </div>

            <!-- Content -->
            <div class="tw-px-6 tw-py-8 sm:tw-px-10 sm:tw-py-12 md:tw-px-14 md:tw-py-14 tw-flex tw-flex-col tw-items-center tw-text-center">
              <!-- Header -->
              <div class="tw-mb-8 sm:tw-mb-10 tw-w-full tw-flex tw-flex-col tw-items-center">
                <div class="tw-mb-4 sm:tw-mb-6 tw-p-2.5 sm:tw-p-3 tw-rounded-full tw-bg-gray-50 dark:tw-bg-gray-800/80 tw-text-gray-700 dark:tw-text-gray-300 tw-ring-1 tw-ring-gray-100 dark:tw-ring-gray-700">
                  <span class="material-symbols-outlined tw-text-2xl sm:tw-text-3xl">scale</span>
                </div>
                <h2 class="tw-font-display tw-text-2xl sm:tw-text-3xl md:tw-text-4xl tw-font-semibold tw-text-gray-900 dark:tw-text-white tw-tracking-tight tw-px-4">
                  Enter Total Weight
                </h2>
                <p class="tw-mt-2 tw-text-xs sm:tw-text-sm tw-text-gray-500 dark:tw-text-gray-400 tw-font-medium tw-tracking-wide tw-uppercase">
                  Bulk Distribution
                </p>
              </div>

              <!-- Weight Input -->
              <div class="tw-w-full tw-relative tw-group tw-mb-8 sm:tw-mb-10">
                <div class="tw-relative tw-mx-auto tw-max-w-[280px]">
                  <input
                    v-model="totalWeight"
                    class="tw-block tw-w-full tw-text-center tw-bg-transparent tw-border-0 tw-border-b tw-border-gray-200 dark:tw-border-gray-700 focus:tw-border-primary-600 dark:focus:tw-border-white focus:tw-ring-0 tw-text-[3rem] sm:tw-text-[4rem] tw-leading-none tw-font-display tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-200 dark:placeholder:tw-text-gray-700 tw-pb-2 tw-pt-4 tw-transition-colors tw-duration-300"
                    inputmode="decimal"
                    placeholder="0.00"
                    type="text"
                    @input="handleWeightInput"
                  />
                  <div class="tw-absolute tw-right-0 sm:tw-right-auto sm:tw-translate-x-8 tw-bottom-4 sm:tw-bottom-5 tw-pointer-events-none tw-select-none tw-text-lg sm:tw-text-xl tw-font-sans tw-font-medium tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1">
                    g
                  </div>
                </div>
              </div>

              <!-- Info Box -->
              <div class="tw-w-full tw-flex tw-items-start tw-gap-3 sm:tw-gap-4 tw-bg-blue-50 dark:tw-bg-blue-900/10 tw-p-4 sm:tw-p-5 tw-rounded-xl sm:tw-rounded-2xl tw-border tw-border-blue-100 dark:tw-border-blue-800/30 tw-mb-8 sm:tw-mb-10 tw-text-left">
                <span class="material-symbols-outlined tw-text-blue-500 dark:tw-text-blue-400 tw-text-lg sm:tw-text-xl tw-mt-0.5 tw-shrink-0">info</span>
                <div class="tw-space-y-1">
                  <p class="tw-text-xs sm:tw-text-sm tw-text-blue-900 dark:tw-text-blue-100 tw-font-medium">
                    Distribution Logic applied
                  </p>
                  <p class="tw-text-[11px] sm:tw-text-xs tw-text-blue-700/80 dark:tw-text-blue-300/70 tw-leading-relaxed">
                    This total weight will be distributed proportionally across <span class="tw-font-semibold">{{ selectedCount }} selected order{{ selectedCount !== 1 ? 's' : '' }}</span> based on their quantities (total: {{ totalQuantity }} units). Any previous manual inputs for these orders will be overwritten.
                  </p>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="tw-flex tw-flex-col-reverse sm:tw-flex-row tw-items-center tw-gap-3 sm:tw-gap-4 tw-w-full">
                <button
                  class="tw-w-full sm:tw-w-1/2 tw-py-3 sm:tw-py-4 tw-px-4 sm:tw-px-6 tw-rounded-lg sm:tw-rounded-xl tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-text-gray-600 dark:tw-text-gray-300 tw-font-medium tw-text-sm hover:tw-text-gray-900 dark:hover:tw-text-white hover:tw-border-gray-300 dark:hover:tw-border-gray-500 hover:tw-bg-gray-50 dark:hover:tw-bg-gray-800 tw-transition-all tw-duration-200 focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-gray-200 dark:focus:tw-ring-gray-700"
                  @click="closeModal"
                >
                  Discard
                </button>
                <button
                  class="tw-w-full sm:tw-w-1/2 tw-py-3 sm:tw-py-4 tw-px-4 sm:tw-px-6 tw-rounded-lg sm:tw-rounded-xl tw-bg-primary-600 tw-text-white tw-font-medium tw-text-sm tw-shadow-lg tw-shadow-gray-200/50 dark:tw-shadow-none hover:tw-bg-primary-500 dark:hover:tw-bg-primary-500 tw-transition-all tw-duration-200 focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-offset-2 focus:tw-ring-primary-600/15 dark:tw-ring-offset-gray-900 tw-transform active:tw-scale-[0.98] disabled:tw-opacity-50 disabled:tw-cursor-not-allowed"
                  :disabled="!isValid"
                  @click="applyWeight"
                >
                  Apply Weight
                </button>
              </div>
            </div>
          </main>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  selectedCount: {
    type: Number,
    required: true
  },
  selectedOrders: {
    type: Array,
    required: true
  },
  frappe: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'apply']);

// State
const totalWeight = ref('');

// Computed
const isValid = computed(() => {
  const weight = parseFloat(totalWeight.value);
  return !isNaN(weight) && weight > 0;
});

const totalQuantity = computed(() => {
  return props.selectedOrders.reduce((sum, order) => {
    return sum + (parseFloat(order.qty) || 0);
  }, 0);
});

// Methods
const handleWeightInput = (event) => {
  // Allow only numbers and decimal point
  let value = event.target.value;
  // Remove any non-numeric characters except decimal point
  value = value.replace(/[^\d.]/g, '');
  // Ensure only one decimal point
  const parts = value.split('.');
  if (parts.length > 2) {
    value = parts[0] + '.' + parts.slice(1).join('');
  }
  totalWeight.value = value;
};

const closeModal = () => {
  emit('update:modelValue', false);
};

const applyWeight = () => {
  if (!isValid.value) return;

  const weightInGrams = parseFloat(totalWeight.value); // Already in grams, no conversion needed

  // Calculate total quantity from all selected orders
  const totalQty = props.selectedOrders.reduce((sum, order) => {
    return sum + (parseFloat(order.qty) || 0);
  }, 0);

  // Calculate weight per unit (per single quantity)
  const weightPerUnit = totalQty > 0 ? weightInGrams / totalQty : 0;

  emit('apply', {
    totalWeight: parseFloat(totalWeight.value),
    totalWeightGrams: weightInGrams,
    totalQty: totalQty,
    weightPerUnit: weightPerUnit
  });

  // Reset and close
  totalWeight.value = '';
  closeModal();
};

// Reset form when modal closes
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    totalWeight.value = '';
  }
});
</script>
