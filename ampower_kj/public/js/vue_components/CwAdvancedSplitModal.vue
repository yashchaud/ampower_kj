<template>
  <Teleport to="body">
    <!-- Modal -->
    <Transition
      enter-active-class="tw-transition-all tw-duration-300"
      enter-from-class="tw-opacity-0 tw-scale-95"
      enter-to-class="tw-opacity-100 tw-scale-100"
      leave-active-class="tw-transition-all tw-duration-300"
      leave-from-class="tw-opacity-100 tw-scale-100"
      leave-to-class="tw-opacity-0 tw-scale-95"
    >
      <div v-if="modelValue" class="tw-fixed tw-inset-0 tw-z-[100] tw-flex tw-items-center tw-justify-center tw-p-4 tw-pointer-events-none">
        <div class="tw-relative tw-w-full tw-max-w-7xl tw-h-[700px] tw-bg-white dark:tw-bg-[#1F2937] tw-rounded-xl tw-shadow-2xl tw-overflow-hidden tw-flex tw-flex-col md:tw-flex-row tw-pointer-events-auto">
          
          <!-- Order Queue Sidebar -->
          <div class="tw-hidden md:tw-flex tw-w-64 tw-bg-gray-50 dark:tw-bg-gray-900 tw-border-r tw-border-gray-200 dark:tw-border-gray-700 tw-flex-col tw-h-full tw-flex-shrink-0">
            <div class="tw-p-6 tw-border-b tw-border-gray-200 dark:tw-border-gray-700 tw-bg-gray-50/50 dark:tw-bg-gray-900/50">
              <h2 class="tw-text-xs tw-font-bold tw-uppercase tw-tracking-wider tw-text-gray-500 dark:tw-text-gray-400 tw-mb-1">Order Queue</h2>
              <p class="tw-text-sm tw-font-medium tw-text-gray-900 dark:tw-text-white tw-flex tw-items-center tw-gap-2">
                <span class="material-symbols-outlined tw-text-base">format_list_bulleted</span>
                {{ selectedOrders.length }} Selected
              </p>
            </div>
            <div class="tw-flex-1 tw-overflow-y-auto custom-scrollbar tw-p-3 tw-space-y-2">
              <div v-for="(order, index) in selectedOrders" :key="order.id">
                <!-- Completed -->
                <div v-if="index < currentOrderIndex" class="tw-flex tw-items-center tw-justify-between tw-p-3 tw-rounded-lg tw-opacity-50">
                  <div>
                    <span class="tw-block tw-text-xs tw-font-bold tw-text-gray-600 dark:tw-text-gray-400 tw-line-through">{{ order.id }}</span>
                    <span class="tw-block tw-text-sm tw-text-gray-500 tw-font-mono">{{ formatWeight(getOrderWeight(order)) }}g</span>
                  </div>
                  <span class="material-symbols-outlined tw-text-green-500 tw-text-lg">check_circle</span>
                </div>
                <!-- Current -->
                <div v-else-if="index === currentOrderIndex" class="tw-relative">
                  <div class="tw-absolute tw-inset-0 tw-bg-white dark:tw-bg-gray-800 tw-shadow-md tw-border-l-[3px] tw-border-[#0066b3] tw-rounded-r-lg tw-transform tw-scale-[1.02]"></div>
                  <div class="tw-relative tw-p-3 tw-pl-4 tw-flex tw-items-center tw-justify-between">
                    <div>
                      <span class="tw-flex tw-items-center tw-gap-2 tw-text-xs tw-font-bold tw-text-[#0066b3]">
                        {{ order.id }}
                        <span class="tw-w-1.5 tw-h-1.5 tw-rounded-full tw-bg-[#0066b3] tw-animate-pulse"></span>
                      </span>
                      <span class="tw-block tw-text-sm tw-font-bold tw-text-gray-900 dark:tw-text-white tw-font-mono">{{ formatWeight(getOrderWeight(order)) }}g</span>
                    </div>
                    <span class="material-symbols-outlined tw-text-[#0066b3] tw-text-xl">arrow_right</span>
                  </div>
                </div>
                <!-- Pending -->
                <button v-else class="tw-w-full tw-text-left tw-flex tw-items-center tw-justify-between tw-p-3 tw-pl-4 tw-rounded-lg hover:tw-bg-white dark:hover:tw-bg-gray-800 tw-border tw-border-transparent hover:tw-border-gray-200 dark:hover:tw-border-gray-700 tw-transition-all tw-group">
                  <div>
                    <span class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 group-hover:tw-text-gray-800 dark:group-hover:tw-text-gray-200">{{ order.id }}</span>
                    <span class="tw-block tw-text-sm tw-text-gray-500 tw-font-mono">{{ formatWeight(getOrderWeight(order)) }}g</span>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- Current Order Info Panel -->
          <div class="tw-w-full md:tw-w-80 tw-bg-[#F9FAFB] dark:tw-bg-[#161e2e] tw-border-r tw-border-gray-200 dark:tw-border-gray-700 tw-flex tw-flex-col tw-h-full tw-flex-shrink-0">
            <div class="tw-absolute tw-top-0 tw-left-0 tw-w-full tw-h-48 tw-bg-gradient-to-b tw-from-blue-50/50 tw-to-transparent dark:tw-from-blue-900/10 tw-pointer-events-none"></div>
            <div class="tw-p-8 tw-flex tw-flex-col tw-h-full tw-relative tw-z-10">
              <div class="tw-flex tw-justify-between tw-items-start tw-mb-8">
                <div>
                  <h2 class="tw-text-xs tw-font-bold tw-uppercase tw-tracking-wider tw-text-gray-500 dark:tw-text-gray-400 tw-mb-1">Source Batch</h2>
                  <p class="tw-text-base tw-font-bold tw-text-gray-900 dark:tw-text-white">Order {{ currentOrder.id }}</p>
                </div>
                <div class="tw-flex tw-items-center tw-gap-1.5 tw-bg-white dark:tw-bg-gray-800 tw-px-3 tw-py-1.5 tw-rounded-full tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                  <span class="tw-relative tw-flex tw-h-2 tw-w-2">
                    <span class="tw-animate-ping tw-absolute tw-inline-flex tw-h-full tw-w-full tw-rounded-full tw-bg-[#0066b3] tw-opacity-75"></span>
                    <span class="tw-relative tw-inline-flex tw-rounded-full tw-h-2 tw-w-2 tw-bg-[#0066b3]"></span>
                  </span>
                  <span class="tw-text-xs tw-font-bold tw-text-gray-700 dark:tw-text-gray-200">{{ currentOrderIndex + 1 }} of {{ selectedOrders.length }}</span>
                </div>
              </div>
              <div class="tw-flex-1 tw-flex tw-flex-col tw-justify-center tw-items-center tw-text-center tw-space-y-6">
                <div class="tw-relative tw-group">
                  <div class="tw-absolute tw-inset-0 tw-bg-[#0066b3]/5 tw-blur-3xl tw-rounded-full tw-transform tw-scale-150"></div>
                  <span class="material-symbols-outlined tw-text-5xl tw-text-gray-300 dark:tw-text-gray-600 tw-mb-4 tw-block">scale</span>
                  <h3 class="tw-text-5xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white tw-tracking-tight">
                    {{ formatWeight(getOrderWeight(currentOrder)) }}<span class="tw-text-2xl tw-text-gray-400">.00g</span>
                  </h3>
                  <p class="tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-mt-2 tw-font-medium tw-uppercase tw-tracking-wide">Current Order Weight</p>
                </div>
                <div class="tw-grid tw-grid-cols-2 tw-gap-4 tw-w-full tw-pt-8 tw-border-t tw-border-gray-200 dark:tw-border-gray-700">
                  <div class="tw-text-center tw-p-3 tw-rounded-lg tw-bg-white dark:tw-bg-gray-800 tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                    <span class="tw-block tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white">22K</span>
                    <span class="tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-uppercase tw-tracking-wider">Purity</span>
                  </div>
                  <div class="tw-text-center tw-p-3 tw-rounded-lg tw-bg-white dark:tw-bg-gray-800 tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                    <span class="tw-block tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white">{{ currentOrder.item_group || 'N/A' }}</span>
                    <span class="tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-uppercase tw-tracking-wider">Type</span>
                  </div>
                </div>
              </div>
              <div class="tw-mt-auto tw-pt-6 tw-text-center">
                <div class="tw-inline-flex tw-items-center tw-gap-2 tw-px-3 tw-py-1.5 tw-rounded-full tw-bg-blue-50 dark:tw-bg-blue-900/20 tw-text-blue-700 dark:tw-text-blue-300 tw-text-xs tw-font-semibold">
                  Ready to Split
                </div>
              </div>
            </div>
          </div>

          <!-- Split Builder Panel -->
          <div class="tw-flex-1 tw-flex tw-flex-col tw-relative tw-h-full tw-bg-white dark:tw-bg-[#1F2937] tw-w-full">
            <button class="tw-absolute tw-top-6 tw-right-6 tw-text-gray-400 hover:tw-text-gray-600 dark:hover:tw-text-gray-300 tw-transition-colors tw-z-30 tw-p-1 tw-rounded-full hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800" @click="closeModal">
              <span class="material-symbols-outlined tw-text-2xl">close</span>
            </button>
            <div class="tw-px-10 lg:tw-px-12 tw-pt-10 tw-pb-4">
              <div class="tw-flex tw-justify-between tw-items-start tw-mb-6">
                <h1 class="tw-text-3xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white">Split Order {{ currentOrder.id }}</h1>
                <button
                  @click="showFilters = !showFilters"
                  :class="showFilters ? 'tw-bg-[#0066b3] tw-text-white' : 'tw-bg-gray-100 dark:tw-bg-gray-800 tw-text-gray-700 dark:tw-text-gray-300'"
                  class="tw-px-4 tw-py-2 tw-rounded-lg tw-text-sm tw-font-medium tw-transition-all tw-flex tw-items-center tw-gap-2 hover:tw-shadow-md"
                >
                  <span class="material-symbols-outlined tw-text-lg">filter_list</span>
                  Filters
                </button>
              </div>
              <div class="tw-inline-flex tw-bg-gray-100 dark:tw-bg-gray-800 tw-p-1 tw-rounded-lg">
                <button :class="splitMode === 'equal' ? 'tw-bg-white dark:tw-bg-gray-700 tw-shadow-sm tw-text-gray-900 dark:tw-text-white' : 'tw-text-gray-500 dark:tw-text-gray-400'" class="tw-px-5 tw-py-2 tw-rounded-md tw-text-sm tw-font-semibold tw-transition-all" @click="splitMode = 'equal'">Equal Split</button>
                <button :class="splitMode === 'custom' ? 'tw-bg-white dark:tw-bg-gray-700 tw-shadow-sm tw-text-gray-900 dark:tw-text-white' : 'tw-text-gray-500 dark:tw-text-gray-400'" class="tw-px-5 tw-py-2 tw-rounded-md tw-text-sm tw-font-medium tw-transition-all" @click="splitMode = 'custom'">Custom Split</button>
              </div>
            </div>

            <!-- Filters Section -->
            <Transition
              enter-active-class="tw-transition-all tw-duration-300"
              enter-from-class="tw-opacity-0 tw--translate-y-4"
              enter-to-class="tw-opacity-100 tw-translate-y-0"
              leave-active-class="tw-transition-all tw-duration-300"
              leave-from-class="tw-opacity-100 tw-translate-y-0"
              leave-to-class="tw-opacity-0 tw--translate-y-4"
            >
              <div v-if="showFilters" class="tw-px-10 lg:tw-px-12 tw-pb-6 tw-border-b tw-border-gray-200 dark:tw-border-gray-700">
                <div class="tw-bg-gray-50 dark:tw-bg-gray-800/50 tw-rounded-lg tw-p-6 tw-space-y-4">
                  <div class="tw-grid tw-grid-cols-1 md:tw-grid-cols-3 tw-gap-4">
                    <!-- Customer Filter -->
                    <div>
                      <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 tw-mb-2 tw-uppercase tw-tracking-wide">Customer</label>
                      <input
                        v-model="filters.customer"
                        type="text"
                        placeholder="Filter by customer..."
                        class="tw-w-full tw-px-4 tw-py-2 tw-bg-white dark:tw-bg-gray-700 tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-rounded-lg tw-text-sm tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-400 focus:tw-ring-2 focus:tw-ring-[#0066b3] focus:tw-border-transparent tw-transition-all"
                      />
                    </div>

                    <!-- Karigar Filter -->
                    <div>
                      <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 tw-mb-2 tw-uppercase tw-tracking-wide">Karigar</label>
                      <input
                        v-model="filters.karigar"
                        type="text"
                        placeholder="Filter by karigar..."
                        class="tw-w-full tw-px-4 tw-py-2 tw-bg-white dark:tw-bg-gray-700 tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-rounded-lg tw-text-sm tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-400 focus:tw-ring-2 focus:tw-ring-[#0066b3] focus:tw-border-transparent tw-transition-all"
                      />
                    </div>

                    <!-- Item Name Filter -->
                    <div>
                      <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 tw-mb-2 tw-uppercase tw-tracking-wide">Item Name</label>
                      <input
                        v-model="filters.itemName"
                        type="text"
                        placeholder="Filter by item name..."
                        class="tw-w-full tw-px-4 tw-py-2 tw-bg-white dark:tw-bg-gray-700 tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-rounded-lg tw-text-sm tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-400 focus:tw-ring-2 focus:tw-ring-[#0066b3] focus:tw-border-transparent tw-transition-all"
                      />
                    </div>
                  </div>

                  <!-- Clear Filters Button -->
                  <div class="tw-flex tw-justify-end">
                    <button
                      @click="clearFilters"
                      class="tw-px-4 tw-py-2 tw-text-sm tw-font-medium tw-text-gray-600 dark:tw-text-gray-400 hover:tw-text-gray-900 dark:hover:tw-text-white tw-transition-colors tw-flex tw-items-center tw-gap-2"
                    >
                      <span class="material-symbols-outlined tw-text-lg">clear</span>
                      Clear Filters
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
            <div class="tw-flex-1 tw-overflow-y-auto custom-scrollbar tw-px-10 lg:tw-px-12 tw-py-6 tw-space-y-8">
              <div v-for="(part, index) in splitParts" :key="part.id" class="tw-group tw-flex tw-items-end tw-gap-6 tw-w-full tw-relative">
                <div class="tw-hidden sm:tw-flex tw-items-center tw-justify-center tw-w-8 tw-h-12 tw-text-xl tw-font-bold tw-text-gray-300 dark:tw-text-gray-600 tw-select-none">{{ getPartLabel(index) }}</div>
                <div class="tw-flex-1 tw-w-full tw-border-b-2 tw-border-gray-200 dark:tw-border-gray-700 group-focus-within:tw-border-[#0066b3] tw-transition-colors tw-pb-1">
                  <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1 tw-uppercase tw-tracking-wide">Quantity Allocation</label>
                  <div class="tw-flex tw-items-baseline">
                    <input
                      v-model="part.qty"
                      :disabled="splitMode === 'equal'"
                      :max="getOrderQty(currentOrder)"
                      class="tw-w-full tw-bg-transparent tw-border-none tw-p-0 tw-text-2xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-300 focus:tw-ring-0"
                      type="number"
                      step="1"
                      min="1"
                      placeholder="0"
                      @input="handleQtyInput(index, $event)"
                    />
                    <span class="tw-text-base tw-text-gray-400 tw-font-medium tw-ml-2">pcs</span>
                  </div>
                </div>
                <button v-if="splitParts.length > 2" class="tw-absolute tw--right-8 tw-bottom-3 tw-text-gray-300 hover:tw-text-red-500 tw-transition-colors tw-hidden lg:tw-block tw-p-1" @click="removePart(index)">
                  <span class="material-symbols-outlined tw-text-xl">close</span>
                </button>
              </div>
              <div class="tw-pl-0 sm:tw-pl-14 tw-pt-2">
                <button class="tw-text-[#0066b3] hover:tw-text-[#005291] tw-transition-colors tw-flex tw-items-center tw-gap-2 tw-text-sm tw-font-semibold tw-group tw-py-2" @click="addPart">
                  <span class="material-symbols-outlined tw-text-xl group-hover:tw-scale-110 tw-transition-transform">add_circle</span>
                  Add Split Part
                </button>
              </div>
            </div>
            <div class="tw-px-10 lg:tw-px-12 tw-py-6 tw-border-t tw-border-gray-100 dark:tw-border-gray-800 tw-bg-white dark:tw-bg-[#1F2937] tw-rounded-br-xl">
              <div class="tw-flex tw-flex-col xl:tw-flex-row tw-justify-between tw-items-center tw-gap-6">
                <div class="tw-text-sm tw-flex tw-items-center tw-gap-3">
                  <span class="tw-text-gray-500 dark:tw-text-gray-400 tw-font-medium">Remaining:</span>
                  <span :class="remainingQty === 0 ? 'tw-text-green-600 dark:tw-text-green-400' : 'tw-text-red-600 dark:tw-text-red-400'" class="tw-font-mono tw-font-bold tw-text-lg">{{ Math.abs(remainingQty) }} pcs</span>
                  <span class="tw-text-xs tw-text-gray-400 dark:tw-text-gray-600 tw-flex tw-items-center tw-gap-1">
                    <span v-if="remainingQty === 0" class="material-symbols-outlined tw-text-base">check_circle</span>
                    {{ remainingQty === 0 ? 'Balanced' : 'Unbalanced' }}
                  </span>
                </div>
                <div class="tw-flex tw-items-center tw-gap-4 tw-w-full sm:tw-w-auto tw-justify-center sm:tw-justify-end">
                  <button class="tw-text-sm tw-font-medium tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-900 dark:hover:tw-text-white tw-transition-colors tw-cursor-pointer tw-px-3 tw-py-2 tw-rounded hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800" @click="skipOrder">Skip</button>
                  <button :disabled="!isValidSplit" class="tw-bg-[#0066b3] hover:tw-bg-[#005291] tw-text-white tw-text-sm tw-font-semibold tw-py-3 tw-px-8 tw-rounded-lg tw-shadow-lg tw-shadow-blue-500/20 tw-transition-all tw-transform active:tw-scale-95 tw-flex tw-items-center tw-gap-2 disabled:tw-opacity-50 disabled:tw-cursor-not-allowed" @click="processSplit">
                    {{ currentOrderIndex < selectedOrders.length - 1 ? 'Next Order' : 'Complete' }}
                    <span class="material-symbols-outlined tw-text-lg">arrow_forward</span>
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
  modelValue: Boolean,
  selectedOrders: { type: Array, required: true },
  frappe: { type: Object, required: true }
});

const emit = defineEmits(['update:modelValue', 'refresh']);

const currentOrderIndex = ref(0);
const splitMode = ref('equal');
const splitParts = ref([{ id: 1, qty: '' }, { id: 2, qty: '' }]);
const completedSplits = ref([]);
const showFilters = ref(false);
const filters = ref({
  customer: '',
  karigar: '',
  itemName: ''
});
let nextPartId = 3;

const currentOrder = computed(() => props.selectedOrders[currentOrderIndex.value] || {});

const remainingQty = computed(() => {
  const allocated = splitParts.value.reduce((sum, p) => sum + (parseInt(p.qty) || 0), 0);
  return getOrderQty(currentOrder.value) - allocated;
});

const isValidSplit = computed(() => {
  return splitParts.value.length >= 2 &&
         splitParts.value.every(p => parseInt(p.qty) > 0) &&
         remainingQty.value === 0;
});

function getOrderQty(order) {
  return parseInt(order.qty || 0);
}

function getOrderWeight(order) {
  return parseFloat(order.karigar_received_weight || order.item_weight || 0);
}

function formatWeight(w) {
  return parseFloat(w || 0).toFixed(2);
}

function getPartLabel(i) {
  return String.fromCharCode(65 + i);
}

function handleQtyInput(index, e) {
  let v = e.target.value.replace(/[^\d]/g, '');
  const numValue = parseInt(v) || 0;
  const totalQty = getOrderQty(currentOrder.value);

  // Calculate total of other parts
  const otherPartsTotal = splitParts.value.reduce((sum, p, i) => {
    if (i !== index) {
      return sum + (parseInt(p.qty) || 0);
    }
    return sum;
  }, 0);

  // Maximum this part can have
  const maxForThisPart = totalQty - otherPartsTotal;

  // Don't allow exceeding the maximum
  if (numValue > maxForThisPart) {
    splitParts.value[index].qty = maxForThisPart;
    if (maxForThisPart >= 0) {
      props.frappe.show_alert({
        message: `Maximum quantity for this part is ${maxForThisPart}`,
        indicator: 'orange'
      });
    }
  } else {
    splitParts.value[index].qty = v;
  }
}

function addPart() {
  splitParts.value.push({ id: nextPartId++, qty: '' });
}

function removePart(i) {
  if (splitParts.value.length > 2) splitParts.value.splice(i, 1);
}

function calculateEqualSplit() {
  const perPart = Math.floor(getOrderQty(currentOrder.value) / splitParts.value.length);
  const remainder = getOrderQty(currentOrder.value) % splitParts.value.length;

  splitParts.value.forEach((p, i) => {
    p.qty = i === 0 ? perPart + remainder : perPart;
  });
}

function closeModal() {
  emit('update:modelValue', false);
}

function skipOrder() {
  if (currentOrderIndex.value < props.selectedOrders.length - 1) {
    currentOrderIndex.value++;
    resetSplitForm();
  } else {
    finishAllSplits();
  }
}

function processSplit() {
  if (!isValidSplit.value) {
    props.frappe.msgprint('Please ensure all split parts have valid quantities and the total matches the order quantity');
    return;
  }

  // Process splits sequentially using the existing split_order_item API
  const parts = splitParts.value.filter(p => parseInt(p.qty) > 0);

  // Confirm split action
  const splitSummary = parts.map((p, i) => `${getPartLabel(i)}: ${p.qty} pcs`).join(', ');
  props.frappe.confirm(
    `This will split order ${currentOrder.value.id} into ${parts.length} parts: ${splitSummary}. Continue?`,
    () => {
      // Process splits sequentially
      processSplitsSequentially(currentOrder.value.id, parts, 0);
    }
  );
}

function processSplitsSequentially(originalName, parts, index) {
  if (index >= parts.length - 1) {
    // All splits done
    props.frappe.show_alert({
      message: `Successfully split ${originalName} into ${parts.length} parts`,
      indicator: 'green'
    });

    completedSplits.value.push({
      original: originalName,
      parts: parts.map((p, i) => ({ label: getPartLabel(i), qty: parseInt(p.qty) }))
    });

    // Move to next order or finish
    if (currentOrderIndex.value < props.selectedOrders.length - 1) {
      currentOrderIndex.value++;
      resetSplitForm();
    } else {
      finishAllSplits();
    }
    return;
  }

  // Split the first quantity from the original
  const splitQty = parseInt(parts[index].qty);

  props.frappe.call({
    method: 'ampower_kj.ampower_keerti_pristine_jewels.doctype.order_ledger.order_ledger.split_order_item',
    args: {
      item_name: originalName,
      split_qty: splitQty
    },
    freeze: true,
    freeze_message: `Splitting part ${index + 1} of ${parts.length - 1}...`,
    callback: function(r) {
      if (r.message && r.message.success) {
        // Continue with next split on the remaining entry
        processSplitsSequentially(r.message.new_entry, parts, index + 1);
      } else {
        props.frappe.msgprint(`Error splitting order: ${r.message?.error || 'Unknown error'}`);
      }
    },
    error: function(err) {
      props.frappe.msgprint(`Error splitting order: ${err.message || 'Unknown error'}`);
    }
  });
}

function resetSplitForm() {
  splitMode.value = 'equal';
  splitParts.value = [{ id: 1, qty: '' }, { id: 2, qty: '' }];
  nextPartId = 3;
  calculateEqualSplit();
}

function finishAllSplits() {
  closeModal();
  // Emit refresh to reload the data
  emit('refresh');

  if (completedSplits.value.length > 0) {
    props.frappe.show_alert({
      message: `Completed ${completedSplits.value.length} split operations`,
      indicator: 'green'
    });
  }
}

function clearFilters() {
  filters.value = {
    customer: '',
    karigar: '',
    itemName: ''
  };
}

watch(splitMode, (newMode) => {
  if (newMode === 'equal') calculateEqualSplit();
});

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    currentOrderIndex.value = 0;
    completedSplits.value = [];
    resetSplitForm();
  }
});

watch(() => splitParts.value.length, () => {
  if (splitMode.value === 'equal') calculateEqualSplit();
});
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar { width: 4px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb { background-color: #cbd5e1; border-radius: 20px; }
.dark .custom-scrollbar::-webkit-scrollbar-thumb { background-color: #4b5563; }
</style>
