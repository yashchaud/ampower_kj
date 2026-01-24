<template>
  <Teleport to="body">
    <!-- Backdrop -->
    <Transition
      enter-active-class="tw-transition-opacity tw-duration-300"
      enter-from-class="tw-opacity-0"
      enter-to-class="tw-opacity-100"
      leave-active-class="tw-transition-opacity tw-duration-200"
      leave-from-class="tw-opacity-100"
      leave-to-class="tw-opacity-0"
    >
      <div
        v-if="modelValue"
        class="tw-fixed tw-inset-0 tw-bg-gray-900/50 dark:tw-bg-black/70 tw-backdrop-blur-sm tw-z-[9998]"
      ></div>
    </Transition>

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
        class="tw-fixed tw-inset-0 md:tw-inset-4 tw-z-[9999] tw-w-full md:tw-w-auto md:tw-max-w-7xl tw-h-[100dvh] md:tw-h-[700px] tw-mx-auto tw-my-0 md:tw-my-auto tw-bg-white dark:tw-bg-gray-900 md:tw-rounded-xl tw-shadow-none md:tw-shadow-2xl tw-overflow-hidden tw-flex tw-flex-col md:tw-flex-row"
      >
        <!-- Desktop Sidebar - Order Queue -->
        <div class="tw-hidden md:tw-flex tw-w-64 tw-bg-gray-50 dark:tw-bg-gray-900 tw-border-r tw-border-gray-200 dark:tw-border-gray-700 tw-flex-col tw-h-full tw-flex-shrink-0">
          <div class="tw-p-6 tw-border-b tw-border-gray-200 dark:tw-border-gray-700 tw-bg-gray-50/50 dark:tw-bg-gray-900/50 tw-backdrop-blur-sm tw-sticky tw-top-0">
            <h2 class="tw-text-xs tw-font-bold tw-uppercase tw-tracking-wider tw-text-gray-500 dark:tw-text-gray-400 tw-mb-1">Order Queue</h2>
            <p class="tw-text-sm tw-font-medium tw-text-gray-900 dark:tw-text-white tw-flex tw-items-center tw-gap-2">
              <span class="material-symbols-outlined tw-text-base">format_list_bulleted</span>
              {{ selectedOrders.length }} Selected
            </p>
          </div>

          <div class="tw-flex-1 tw-overflow-y-auto custom-scrollbar tw-p-3 tw-space-y-2">
            <button
              v-for="(order, idx) in selectedOrders"
              :key="order.id"
              @click="selectedIndex = idx"
              class="tw-w-full tw-text-left tw-relative tw-group"
              :class="selectedIndex === idx ? 'tw-z-10' : 'tw-z-0'"
            >
              <div
                v-if="selectedIndex === idx"
                class="tw-absolute tw-inset-0 tw-bg-white dark:tw-bg-gray-800 tw-shadow-md tw-border-l-[3px] tw-border-primary-600 tw-rounded-r-lg tw-transform tw-scale-[1.02]"
              ></div>
              <div
                class="tw-relative tw-p-3 tw-flex tw-items-center tw-justify-between tw-rounded-lg tw-transition-all"
                :class="selectedIndex !== idx ? 'hover:tw-bg-white dark:hover:tw-bg-gray-800 tw-border tw-border-transparent hover:tw-border-gray-200 dark:hover:tw-border-gray-700' : 'tw-pl-4'"
              >
                <div>
                  <span
                    class="tw-flex tw-items-center tw-gap-2 tw-text-xs tw-font-bold"
                    :class="selectedIndex === idx ? 'tw-text-primary-600 dark:tw-text-blue-400' : 'tw-text-gray-500 dark:tw-text-gray-400 group-hover:tw-text-gray-800 dark:group-hover:tw-text-gray-200'"
                  >
                    {{ order.id }}
                    <span v-if="selectedIndex === idx" class="tw-w-1.5 tw-h-1.5 tw-rounded-full tw-bg-primary-600 tw-animate-pulse"></span>
                  </span>
                  <span
                    class="tw-block tw-text-sm tw-font-mono tw-mt-0.5"
                    :class="selectedIndex === idx ? 'tw-font-bold tw-text-gray-900 dark:tw-text-white' : 'tw-text-gray-500 dark:tw-text-gray-400'"
                  >
                    Qty: {{ order.qty }}
                  </span>
                </div>
                <span
                  v-if="selectedIndex === idx"
                  class="material-symbols-outlined tw-text-primary-600 tw-text-xl"
                >
                  arrow_right
                </span>
              </div>
            </button>
          </div>
        </div>

        <!-- Mobile Header -->
        <div class="md:tw-hidden tw-flex-none tw-bg-white dark:tw-bg-gray-900 tw-border-b tw-border-gray-200 dark:tw-border-gray-700 tw-shadow-sm tw-sticky tw-top-0 tw-z-50">
          <div class="tw-flex tw-items-center tw-justify-between tw-px-4 tw-py-3">
            <div class="tw-flex tw-items-center tw-gap-3">
              <button @click="close" class="tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-700 tw-transition-colors">
                <span class="material-symbols-outlined">arrow_back</span>
              </button>
              <div>
                <div class="tw-flex tw-items-center tw-gap-2">
                  <span class="tw-text-sm tw-font-bold tw-text-gray-900 dark:tw-text-white">{{ currentOrder?.id || 'Order' }}</span>
                  <span class="tw-inline-flex tw-items-center tw-px-2 tw-py-0.5 tw-rounded-full tw-text-[10px] tw-font-bold tw-bg-primary-600/10 tw-text-primary-600 dark:tw-bg-blue-900/30 dark:tw-text-blue-300">
                    {{ selectedIndex + 1 }} of {{ selectedOrders.length }}
                  </span>
                </div>
              </div>
            </div>
            <button @click="close" class="tw-text-gray-400 hover:tw-text-gray-600 dark:hover:tw-text-gray-300 tw-p-1 tw-rounded-full hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800 tw-transition-colors">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>

          <!-- Mobile Order Chips -->
          <div class="tw-flex tw-overflow-x-auto tw-gap-2 tw-px-4 tw-pb-3 no-scrollbar tw-items-center tw-bg-white dark:tw-bg-gray-900">
            <button
              v-for="(order, idx) in selectedOrders"
              :key="order.id"
              @click="selectedIndex = idx"
              class="tw-flex-shrink-0 tw-px-3 tw-py-1.5 tw-rounded-full tw-text-xs tw-font-bold tw-whitespace-nowrap tw-border tw-transition-all"
              :class="selectedIndex === idx
                ? 'tw-bg-primary-600 tw-text-white tw-shadow-md tw-shadow-blue-500/20 tw-border-primary-600'
                : 'tw-bg-gray-50 dark:tw-bg-gray-800 tw-text-gray-600 dark:tw-text-gray-300 tw-border-gray-200 dark:tw-border-gray-700'"
            >
              {{ order.id }} • {{ order.qty }}
            </button>
          </div>
        </div>

        <!-- Main Content -->
        <div class="tw-flex-1 tw-flex tw-flex-col md:tw-flex-row tw-h-full tw-overflow-y-auto md:tw-overflow-hidden custom-scrollbar">
          <!-- Left Panel - Order Info -->
          <div class="tw-w-full md:tw-w-80 tw-bg-gray-50 dark:tw-bg-gray-800/50 md:tw-border-r tw-border-gray-200 dark:tw-border-gray-700 tw-flex tw-flex-col md:tw-h-full tw-overflow-hidden tw-flex-shrink-0">
            <div class="tw-absolute tw-top-0 tw-left-0 tw-w-full tw-h-48 tw-bg-gradient-to-b tw-from-blue-50/50 tw-to-transparent dark:tw-from-blue-900/10 tw-pointer-events-none"></div>

            <div class="tw-p-4 md:tw-p-8 tw-flex tw-flex-col tw-h-full tw-relative">
              <div class="tw-bg-white dark:tw-bg-gray-800/50 md:tw-bg-transparent tw-rounded-xl tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700 md:tw-shadow-none md:tw-border-0 tw-p-5 md:tw-p-0 tw-flex tw-flex-col md:tw-h-full">

                <!-- Desktop Header -->
                <div class="tw-hidden md:tw-flex tw-justify-between tw-items-start tw-mb-8">
                  <div>
                    <h2 class="tw-text-xs tw-font-bold tw-uppercase tw-tracking-wider tw-text-gray-500 dark:tw-text-gray-400 tw-mb-1">Source Item</h2>
                    <p class="tw-text-base tw-font-bold tw-text-gray-900 dark:tw-text-white tw-flex tw-items-center tw-gap-2">{{ currentOrder?.id || 'Order' }}</p>
                  </div>
                  <div class="tw-flex tw-items-center tw-gap-1.5 tw-bg-white dark:tw-bg-gray-800 tw-px-3 tw-py-1.5 tw-rounded-full tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                    <span class="tw-relative tw-flex tw-h-2 tw-w-2">
                      <span class="tw-animate-ping tw-absolute tw-inline-flex tw-h-full tw-w-full tw-rounded-full tw-bg-primary-600 tw-opacity-75"></span>
                      <span class="tw-relative tw-inline-flex tw-rounded-full tw-h-2 tw-w-2 tw-bg-primary-600"></span>
                    </span>
                    <span class="tw-text-xs tw-font-bold tw-text-gray-700 dark:tw-text-gray-200">{{ selectedIndex + 1 }} of {{ selectedOrders.length }}</span>
                  </div>
                </div>

                <!-- Quantity Display -->
                <div class="tw-flex-1 tw-flex tw-flex-row md:tw-flex-col tw-justify-between md:tw-justify-center tw-items-center tw-text-center tw-space-x-6 md:tw-space-x-0 md:tw-space-y-6">
                  <div class="tw-relative tw-group tw-flex tw-flex-col tw-items-center">
                    <div class="tw-absolute tw-inset-0 tw-bg-primary-600/5 tw-blur-3xl tw-rounded-full tw-transform tw-scale-150 tw-opacity-100"></div>
                    <span class="material-symbols-outlined tw-text-4xl md:tw-text-5xl tw-text-gray-300 dark:tw-text-gray-600 tw-mb-2 md:tw-mb-4 tw-block">inventory_2</span>
                    <div class="tw-text-left md:tw-text-center">
                      <h3 class="tw-text-3xl md:tw-text-5xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white tw-tracking-tight">
                        {{ currentOrder?.qty || 0 }}<span class="tw-text-xl md:tw-text-2xl tw-text-gray-400 dark:tw-text-gray-500"> pcs</span>
                      </h3>
                      <p class="tw-text-[10px] md:tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-mt-1 tw-font-medium tw-uppercase tw-tracking-wide">Total Quantity</p>
                    </div>
                  </div>

                  <!-- Order Details Grid -->
                  <div v-if="currentOrder" class="tw-grid tw-grid-cols-1 md:tw-grid-cols-2 tw-gap-2 md:tw-gap-4 tw-w-32 md:tw-w-full md:tw-pt-8 md:tw-border-t tw-border-gray-200 dark:tw-border-gray-700">
                    <div class="tw-text-center tw-p-2 md:tw-p-3 tw-rounded-lg tw-bg-gray-50 md:tw-bg-white dark:tw-bg-gray-900 md:dark:tw-bg-gray-800 tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                      <span class="tw-block tw-text-sm md:tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white tw-truncate">{{ currentOrder.item_code || 'N/A' }}</span>
                      <span class="tw-text-[10px] md:tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-uppercase tw-tracking-wider">Item Code</span>
                    </div>
                    <div class="tw-text-center tw-p-2 md:tw-p-3 tw-rounded-lg tw-bg-gray-50 md:tw-bg-white dark:tw-bg-gray-900 md:dark:tw-bg-gray-800 tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                      <span class="tw-block tw-text-sm md:tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white tw-truncate">{{ currentOrder.texture || 'N/A' }}</span>
                      <span class="tw-text-[10px] md:tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-uppercase tw-tracking-wider">Texture</span>
                    </div>
                  </div>
                </div>

                <div class="tw-hidden md:tw-block tw-mt-auto tw-pt-6 tw-text-center">
                  <div class="tw-inline-flex tw-items-center tw-gap-2 tw-px-3 tw-py-1.5 tw-rounded-full tw-bg-blue-50 dark:tw-bg-blue-900/20 tw-text-blue-700 dark:tw-text-blue-300 tw-text-xs tw-font-semibold">
                    Ready to Split
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Right Panel - Split Form -->
          <div class="tw-flex-1 tw-flex tw-flex-col tw-relative md:tw-h-full tw-bg-white dark:tw-bg-gray-900 tw-w-full">
            <!-- Close Button (Desktop) -->
            <button
              @click="close"
              class="tw-absolute tw-top-6 tw-right-6 tw-z-50 tw-text-gray-400 hover:tw-text-gray-600 dark:hover:tw-text-gray-300 tw-transition-colors tw-p-2 tw-rounded-full hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800 tw-hidden md:tw-block"
            >
              <span class="material-symbols-outlined tw-text-2xl">close</span>
            </button>

            <div class="tw-px-4 tw-py-4 md:tw-px-12 md:tw-pt-10 md:tw-pb-4">
              <h1 class="tw-text-3xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white tw-mb-6 tw-hidden md:tw-block">
                Split {{ currentOrder?.id || 'Order' }}
              </h1>
            </div>

            <!-- Split Form -->
            <div class="tw-flex-1 tw-overflow-visible md:tw-overflow-y-auto custom-scrollbar tw-px-4 md:tw-px-12 tw-py-2 md:tw-py-6 tw-space-y-6 md:tw-space-y-8 tw-pb-24 md:tw-pb-6">

              <!-- Part A -->
              <div class="tw-group tw-flex tw-flex-col md:tw-flex-row tw-items-start md:tw-items-end tw-gap-2 md:tw-gap-6 tw-w-full tw-bg-gray-50 dark:tw-bg-gray-800/50 md:tw-bg-transparent tw-p-4 md:tw-p-0 tw-rounded-xl tw-border tw-border-gray-100 dark:tw-border-gray-800 md:tw-border-0">
                <div class="tw-hidden sm:tw-flex tw-items-center tw-justify-center tw-w-8 tw-h-12 tw-text-xl tw-font-bold tw-text-gray-300 dark:tw-text-gray-600 tw-select-none">A</div>
                <div class="sm:tw-hidden tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1">PART A (Keep)</div>

                <div class="tw-flex-1 tw-w-full">
                  <div class="tw-border-b-2 tw-border-gray-200 dark:tw-border-gray-700 group-focus-within:tw-border-primary-600 tw-transition-colors tw-pb-1">
                    <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1 tw-uppercase tw-tracking-wide">Quantity to Keep</label>
                    <div class="tw-flex tw-items-baseline">
                      <input
                        v-model.number="splitQty"
                        type="number"
                        min="1"
                        :max="currentOrder ? currentOrder.qty - 1 : 0"
                        class="tw-w-full tw-bg-transparent tw-border-none tw-p-0 tw-text-2xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-300 focus:tw-ring-0"
                        :class="{'tw-text-red-600': splitQty !== null && !isValidSplit}"
                        placeholder="0"
                      />
                      <span class="tw-text-base tw-text-gray-400 tw-font-medium tw-ml-2">pcs</span>
                    </div>
                  </div>
                  <p v-if="splitQty !== null && !isValidSplit" class="tw-text-xs tw-text-red-600 tw-mt-1">
                    Enter a value between 1 and {{ currentOrder ? currentOrder.qty - 1 : 0 }}
                  </p>
                </div>
              </div>

              <!-- Part B -->
              <div class="tw-group tw-flex tw-flex-col md:tw-flex-row tw-items-start md:tw-items-end tw-gap-2 md:tw-gap-6 tw-w-full tw-bg-gray-50 dark:tw-bg-gray-800/50 md:tw-bg-transparent tw-p-4 md:tw-p-0 tw-rounded-xl tw-border tw-border-gray-100 dark:tw-border-gray-800 md:tw-border-0">
                <div class="tw-hidden sm:tw-flex tw-items-center tw-justify-center tw-w-8 tw-h-12 tw-text-xl tw-font-bold tw-text-gray-300 dark:tw-text-gray-600 tw-select-none">B</div>
                <div class="sm:tw-hidden tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1">PART B (New Entry)</div>

                <div class="tw-flex-1 tw-w-full">
                  <div class="tw-border-b-2 tw-border-gray-200 dark:tw-border-gray-700 tw-pb-1">
                    <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1 tw-uppercase tw-tracking-wide">New Entry Quantity</label>
                    <div class="tw-flex tw-items-baseline">
                      <div class="tw-w-full tw-text-2xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white">
                        {{ isValidSplit && currentOrder ? currentOrder.qty - splitQty : 0 }}
                      </div>
                      <span class="tw-text-base tw-text-gray-400 tw-font-medium tw-ml-2">pcs</span>
                    </div>
                  </div>
                  <p class="tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-mt-1">Automatically calculated</p>
                </div>
              </div>

              <!-- Info Box -->
              <div v-if="isValidSplit" class="tw-bg-emerald-50 dark:tw-bg-emerald-900/20 tw-border tw-border-emerald-200 dark:tw-border-emerald-800/30 tw-rounded-lg tw-p-4">
                <div class="tw-flex tw-items-start tw-gap-3">
                  <span class="material-symbols-outlined tw-text-emerald-600 dark:tw-text-emerald-400 tw-text-xl">check_circle</span>
                  <div class="tw-text-xs tw-text-emerald-800 dark:tw-text-emerald-200">
                    <p class="tw-font-semibold tw-mb-2">Split Preview:</p>
                    <ul class="tw-space-y-1">
                      <li>• Original entry will keep <strong>{{ splitQty }} pcs</strong></li>
                      <li>• New entry will have <strong>{{ currentOrder.qty - splitQty }} pcs</strong></li>
                      <li>• Both entries will maintain all other attributes</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer Actions -->
            <div class="tw-sticky tw-bottom-0 tw-px-4 md:tw-px-12 tw-py-4 md:tw-py-6 tw-border-t tw-border-gray-200 dark:tw-border-gray-800 tw-bg-white dark:tw-bg-gray-900 md:tw-rounded-br-xl tw-shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] md:tw-shadow-none">
              <div class="tw-flex tw-flex-row md:tw-flex-row tw-justify-between tw-items-center tw-gap-4 md:tw-gap-6">
                <div class="tw-text-sm tw-flex tw-flex-col md:tw-flex-row md:tw-items-center tw-gap-1 md:tw-gap-3">
                  <div class="tw-flex tw-items-center tw-gap-2">
                    <span class="tw-text-gray-500 dark:tw-text-gray-400 tw-font-medium">Status:</span>
                    <span v-if="isValidSplit" class="tw-font-mono tw-font-bold tw-text-green-600 dark:tw-text-green-400 tw-text-base tw-flex tw-items-center tw-gap-1">
                      <span class="material-symbols-outlined tw-text-base">check_circle</span>
                      Valid
                    </span>
                    <span v-else class="tw-font-mono tw-font-bold tw-text-gray-400 dark:tw-text-gray-600 tw-text-base">Pending</span>
                  </div>
                </div>

                <div class="tw-flex tw-items-center tw-gap-3 md:tw-gap-4 tw-w-auto sm:tw-justify-end">
                  <button
                    @click="close"
                    class="tw-hidden md:tw-block tw-text-sm tw-font-medium tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-900 dark:hover:tw-text-white tw-transition-colors tw-px-3 tw-py-2 tw-rounded hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    @click="handleSplit"
                    :disabled="!isValidSplit"
                    class="tw-bg-primary-600 hover:tw-bg-primary-500 tw-text-white tw-text-sm tw-font-semibold tw-py-3 tw-px-6 md:tw-px-8 tw-rounded-lg tw-shadow-lg tw-shadow-blue-500/20 tw-transition-all tw-transform active:tw-scale-95 tw-flex tw-items-center tw-gap-2 tw-whitespace-nowrap disabled:tw-opacity-50 disabled:tw-cursor-not-allowed disabled:tw-transform-none"
                  >
                    <span class="material-symbols-outlined tw-text-lg">call_split</span>
                    Split Item
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  selectedOrders: {
    type: Array,
    default: () => []
  },
  frappe: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'split-complete']);

// State
const selectedIndex = ref(0);
const splitQty = ref(null);

// Current order being edited
const currentOrder = computed(() => {
  if (selectedIndex.value >= 0 && selectedIndex.value < props.selectedOrders.length) {
    return props.selectedOrders[selectedIndex.value];
  }
  return null;
});

// Validation
const isValidSplit = computed(() => {
  if (splitQty.value === null || !currentOrder.value) {
    return false;
  }
  return splitQty.value > 0 && splitQty.value < currentOrder.value.qty;
});

// Watch for modal open/close to reset state
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    selectedIndex.value = 0;
    splitQty.value = null;
  }
});

// Watch for selected index change to reset split qty
watch(selectedIndex, () => {
  splitQty.value = null;
});

// Handle split
function handleSplit() {
  if (!isValidSplit.value || !currentOrder.value) {
    return;
  }

  const remainingQty = currentOrder.value.qty - splitQty.value;

  props.frappe.confirm(
    `This will split the entry "${currentOrder.value.id}" into two:<br><br>` +
    `• Original entry: <strong>${splitQty.value} pcs</strong><br>` +
    `• New entry: <strong>${remainingQty} pcs</strong><br><br>` +
    `Do you want to continue?`,
    () => {
      emit('split-complete', {
        itemName: currentOrder.value.id,
        splitQty: splitQty.value,
        remainingQty: remainingQty
      });

      // Move to next item or close if this was the last one
      if (selectedIndex.value < props.selectedOrders.length - 1) {
        selectedIndex.value++;
      } else {
        close();
      }
    }
  );
}

// Close modal
function close() {
  emit('update:modelValue', false);
}
</script>

<style scoped>
/* Custom scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e1;
  border-radius: 20px;
}

.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #4b5563;
}

/* No scrollbar for horizontal scroll */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Number input remove arrows */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}
</style>
