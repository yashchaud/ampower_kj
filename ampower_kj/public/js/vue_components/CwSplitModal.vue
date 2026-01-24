<template>
  <Teleport to="body">
    <Transition
      enter-active-class="tw-transition-all tw-duration-200 tw-ease-out"
      enter-from-class="tw-opacity-0"
      enter-to-class="tw-opacity-100"
      leave-active-class="tw-transition-all tw-duration-150 tw-ease-in"
      leave-from-class="tw-opacity-100"
      leave-to-class="tw-opacity-0"
    >
      <div
        v-if="modelValue"
        class="tw-fixed tw-inset-0 tw-z-[9999] tw-flex tw-items-center tw-justify-center tw-bg-black/50 tw-p-4"
        @click.self="close"
      >
        <Transition
          enter-active-class="tw-transition-all tw-duration-200 tw-ease-out"
          enter-from-class="tw-opacity-0 tw-scale-95"
          enter-to-class="tw-opacity-100 tw-scale-100"
          leave-active-class="tw-transition-all tw-duration-150 tw-ease-in"
          leave-from-class="tw-opacity-100 tw-scale-100"
          leave-to-class="tw-opacity-0 tw-scale-95"
        >
          <div
            v-if="modelValue"
            class="tw-w-full tw-max-w-4xl tw-bg-white tw-rounded-2xl tw-shadow-2xl tw-overflow-hidden tw-max-h-[90vh] tw-flex tw-flex-col"
          >
            <!-- Header -->
            <div class="tw-px-6 tw-py-4 tw-border-b tw-bg-slate-50 tw-flex tw-items-center tw-justify-between">
              <div>
                <h2 class="tw-text-lg tw-font-bold tw-text-slate-800">
                  Edit Item Values
                  <span class="tw-text-sm tw-font-normal tw-text-slate-500">
                    ({{ selectedOrders.length }} {{ selectedOrders.length === 1 ? 'Item' : 'Items' }} Selected)
                  </span>
                </h2>
                <p class="tw-text-sm tw-text-slate-500 tw-mt-1">Select an item to edit its quantity</p>
              </div>
              <button
                class="tw-text-slate-400 hover:tw-text-slate-600 tw-transition-colors"
                @click="close"
              >
                <span class="material-symbols-outlined tw-text-2xl">close</span>
              </button>
            </div>

            <!-- Content -->
            <div class="tw-flex tw-flex-1 tw-overflow-hidden">
              <!-- Left Panel: Item List -->
              <div class="tw-w-1/3 tw-border-r tw-bg-slate-50 tw-overflow-y-auto">
                <div
                  v-for="(order, idx) in selectedOrders"
                  :key="order.id"
                  class="tw-px-4 tw-py-3 tw-border-b tw-cursor-pointer tw-transition-all"
                  :class="{
                    'tw-bg-primary-50 tw-border-l-4 tw-border-l-primary-500': selectedIndex === idx,
                    'hover:tw-bg-slate-100': selectedIndex !== idx
                  }"
                  @click="selectedIndex = idx"
                >
                  <div class="tw-text-sm tw-font-semibold tw-text-slate-800 tw-mb-1">
                    {{ order.id }}
                  </div>
                  <div class="tw-text-xs tw-text-slate-500">
                    {{ order.customer }}
                  </div>
                  <div class="tw-text-xs tw-text-slate-600 tw-mt-1">
                    Qty: <span class="tw-font-medium">{{ order.qty }}</span>
                  </div>
                </div>

                <div v-if="selectedOrders.length === 0" class="tw-px-4 tw-py-8 tw-text-center tw-text-slate-400">
                  <span class="material-symbols-outlined tw-text-4xl tw-mb-2">inbox</span>
                  <p class="tw-text-sm">No items selected</p>
                </div>
              </div>

              <!-- Right Panel: Details & Split Input -->
              <div class="tw-w-2/3 tw-p-6 tw-overflow-y-auto">
                <template v-if="currentOrder">
                  <!-- Order Info Card -->
                  <div class="tw-bg-blue-50 tw-rounded-xl tw-p-4 tw-mb-6">
                    <div class="tw-grid tw-grid-cols-2 tw-gap-4">
                      <div>
                        <span class="tw-text-xs tw-text-slate-500 tw-block tw-mb-1">Customer</span>
                        <span class="tw-text-sm tw-font-medium tw-text-slate-800">
                          {{ currentOrder.customer || 'N/A' }}
                        </span>
                      </div>
                      <div>
                        <span class="tw-text-xs tw-text-slate-500 tw-block tw-mb-1">Karigar</span>
                        <span class="tw-text-sm tw-font-medium tw-text-slate-800">
                          {{ currentOrder.karigar?.name || 'N/A' }}
                        </span>
                      </div>
                      <div>
                        <span class="tw-text-xs tw-text-slate-500 tw-block tw-mb-1">Item Code</span>
                        <span class="tw-text-sm tw-font-medium tw-text-slate-800">
                          {{ currentOrder.item_code || 'N/A' }}
                        </span>
                      </div>
                      <div>
                        <span class="tw-text-xs tw-text-slate-500 tw-block tw-mb-1">Item Details</span>
                        <span class="tw-text-sm tw-font-medium tw-text-slate-800">
                          {{ currentOrder.item_details || 'N/A' }}
                        </span>
                      </div>
                      <div class="tw-col-span-2">
                        <span class="tw-text-xs tw-text-slate-500 tw-block tw-mb-1">Total Quantity</span>
                        <span class="tw-text-xl tw-font-bold tw-text-primary-600">
                          {{ currentOrder.qty }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Split Quantity Section -->
                  <div class="tw-mb-6">
                    <label class="tw-block tw-text-sm tw-font-semibold tw-text-slate-700 tw-mb-2">
                      Split Quantity *
                    </label>
                    <input
                      v-model.number="splitQty"
                      type="number"
                      min="1"
                      :max="currentOrder.qty - 1"
                      class="tw-w-full tw-px-4 tw-py-3 tw-border tw-border-slate-300 tw-rounded-lg tw-text-sm focus:tw-border-primary-500 focus:tw-ring-2 focus:tw-ring-primary-100 tw-outline-none tw-transition-all"
                      :class="{
                        'tw-border-red-300 focus:tw-border-red-500 focus:tw-ring-red-100': !isValidSplit && splitQty !== null
                      }"
                      placeholder="Enter quantity to keep in original"
                    />
                    <p class="tw-text-xs tw-text-slate-500 tw-mt-2">
                      Enter the quantity to keep in the original entry. The remaining quantity will be moved to a new entry.
                    </p>

                    <!-- Validation Messages -->
                    <div v-if="splitQty !== null && !isValidSplit" class="tw-mt-2">
                      <p v-if="splitQty <= 0" class="tw-text-xs tw-text-red-600">
                        Split quantity must be greater than 0
                      </p>
                      <p v-if="splitQty >= currentOrder.qty" class="tw-text-xs tw-text-red-600">
                        Split quantity must be less than total quantity ({{ currentOrder.qty }})
                      </p>
                    </div>

                    <!-- Remaining Quantity Display -->
                    <div v-if="isValidSplit" class="tw-mt-3 tw-p-3 tw-bg-emerald-50 tw-rounded-lg tw-border tw-border-emerald-200">
                      <div class="tw-flex tw-items-center tw-justify-between tw-text-sm">
                        <span class="tw-text-slate-600">Remaining quantity for new entry:</span>
                        <span class="tw-font-bold tw-text-emerald-700 tw-text-lg">
                          {{ currentOrder.qty - splitQty }}
                        </span>
                      </div>
                    </div>
                  </div>

                  <!-- Warning Message -->
                  <div class="tw-bg-amber-50 tw-border tw-border-amber-200 tw-rounded-lg tw-p-3 tw-mb-6">
                    <div class="tw-flex tw-items-start tw-gap-2">
                      <span class="material-symbols-outlined tw-text-amber-600 tw-text-xl">warning</span>
                      <div class="tw-text-xs tw-text-amber-800">
                        <p class="tw-font-semibold tw-mb-1">Splitting will:</p>
                        <ul class="tw-list-disc tw-list-inside tw-space-y-1">
                          <li>Keep {{ splitQty || 0 }} qty in the original entry</li>
                          <li>Create a new entry with {{ splitQty ? currentOrder.qty - splitQty : 0 }} qty</li>
                          <li>Both entries will maintain all other attributes</li>
                        </ul>
                      </div>
                    </div>
                  </div>

                  <!-- Save Button -->
                  <button
                    class="tw-w-full tw-py-3 tw-px-4 tw-rounded-lg tw-font-semibold tw-text-white tw-transition-all tw-duration-200"
                    :class="{
                      'tw-bg-primary-500 hover:tw-bg-primary-600 tw-shadow-md hover:tw-shadow-lg': isValidSplit,
                      'tw-bg-slate-300 tw-cursor-not-allowed': !isValidSplit
                    }"
                    :disabled="!isValidSplit"
                    @click="handleSplit"
                  >
                    <span class="material-symbols-outlined tw-align-middle tw-mr-2">call_split</span>
                    Split Item
                  </button>
                </template>

                <!-- Empty State -->
                <div v-else class="tw-flex tw-flex-col tw-items-center tw-justify-center tw-h-full tw-text-slate-400">
                  <span class="material-symbols-outlined tw-text-6xl tw-mb-4">arrow_back</span>
                  <p class="tw-text-sm">Select an item from the left panel to split</p>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="tw-px-6 tw-py-4 tw-border-t tw-bg-slate-50 tw-flex tw-items-center tw-justify-between">
              <div class="tw-text-xs tw-text-slate-500">
                Item {{ selectedIndex + 1 }} of {{ selectedOrders.length }}
              </div>
              <div class="tw-flex tw-gap-3">
                <button
                  class="tw-px-4 tw-py-2 tw-border tw-border-slate-300 tw-rounded-lg tw-text-sm tw-font-medium tw-text-slate-700 hover:tw-bg-slate-100 tw-transition-colors"
                  @click="close"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </Transition>
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
    `• Original entry: <strong>${splitQty.value} qty</strong><br>` +
    `• New entry: <strong>${remainingQty} qty</strong><br><br>` +
    `Do you want to continue?`,
    () => {
      emit('split-complete', {
        itemName: currentOrder.value.id,
        splitQty: splitQty.value,
        remainingQty: remainingQty
      });
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
.tw-overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.tw-overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

.tw-overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

.tw-overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
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
