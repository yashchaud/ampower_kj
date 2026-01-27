<template>
  <Teleport to="body">
    <!-- Modal Overlay -->
    <Transition
      enter-active-class="tw-transition-opacity tw-duration-200"
      enter-from-class="tw-opacity-0"
      enter-to-class="tw-opacity-100"
      leave-active-class="tw-transition-opacity tw-duration-200"
      leave-from-class="tw-opacity-100"
      leave-to-class="tw-opacity-0"
    >
      <div
        v-if="modelValue"
        class="tw-fixed tw-inset-0 tw-z-[9999] tw-flex tw-items-center tw-justify-center tw-bg-black/50 tw-backdrop-blur-sm tw-p-4 sm:tw-p-6"
        @click.self="closeModal"
      >
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
            class="tw-w-full tw-max-w-5xl tw-bg-white tw-rounded-2xl tw-shadow-2xl tw-flex tw-flex-col tw-max-h-[90vh] tw-overflow-hidden tw-ring-1 tw-ring-black/5"
            role="dialog"
            aria-modal="true"
            :aria-labelledby="titleId"
          >
            <!-- Header -->
            <div class="tw-flex tw-items-center tw-justify-between tw-px-6 tw-py-4 tw-border-b tw-border-gray-100 tw-bg-white tw-sticky tw-top-0 tw-z-20">
              <div>
                <h1 :id="titleId" class="tw-text-xl tw-font-bold tw-text-[#111418] tw-tracking-tight">Order Item Details</h1>
                <p class="tw-text-sm tw-text-gray-500 tw-mt-0.5">
                  Order #{{ orderData.sales_order }} <span class="tw-mx-1">•</span> <span class="tw-font-medium tw-text-gray-700">{{ orderData.item_details }}</span>
                </p>
              </div>
              <div class="tw-flex tw-items-center tw-gap-2">
                <button
                  class="tw-w-9 tw-h-9 tw-flex tw-items-center tw-justify-center tw-text-gray-400 hover:tw-text-[#111418] hover:tw-bg-gray-100 tw-rounded-full tw-transition-colors"
                  title="Go to Sales Order"
                  @click="openInNewTab"
                >
                  <span class="material-symbols-outlined tw-text-[20px]">open_in_new</span>
                </button>
                <button
                  class="tw-w-9 tw-h-9 tw-flex tw-items-center tw-justify-center tw-text-gray-400 hover:tw-text-red-600 hover:tw-bg-red-50 tw-rounded-full tw-transition-colors"
                  title="Close"
                  @click="closeModal"
                >
                  <span class="material-symbols-outlined tw-text-[24px]">close</span>
                </button>
              </div>
            </div>

            <!-- Body -->
            <div class="tw-flex-1 tw-overflow-y-auto tw-p-6 md:tw-p-8 tw-bg-white">
              <div class="tw-grid tw-grid-cols-1 lg:tw-grid-cols-12 tw-gap-8 tw-h-full">

                <!-- LEFT COLUMN: IMAGES -->
                <div class="lg:tw-col-span-5 tw-flex tw-flex-col tw-gap-5">
                  <div class="tw-relative tw-w-full tw-aspect-[4/3] tw-bg-gray-50 tw-rounded-xl tw-overflow-hidden tw-group tw-shadow-inner tw-border tw-border-gray-100">
                    <div class="tw-absolute tw-top-3 tw-right-3 tw-bg-black/70 tw-backdrop-blur-md tw-text-white tw-text-xs tw-font-bold tw-px-3 tw-py-1.5 tw-rounded-full tw-z-10 tw-shadow-sm tw-border tw-border-white/10">
                      {{ currentImageIndex + 1 }} / {{ images.length }}
                    </div>
                    <div
                      class="tw-w-full tw-h-full tw-bg-center tw-bg-contain tw-bg-no-repeat tw-transition-transform tw-duration-500 group-hover:tw-scale-105"
                      :style="{ backgroundImage: `url('${images[currentImageIndex]}')` }"
                    ></div>
                    <div class="tw-absolute tw-inset-x-0 tw-top-1/2 tw--translate-y-1/2 tw-flex tw-justify-between tw-px-3 tw-opacity-0 group-hover:tw-opacity-100 tw-transition-opacity tw-duration-300">
                      <button
                        class="tw-w-9 tw-h-9 tw-flex tw-items-center tw-justify-center tw-rounded-full tw-bg-white tw-text-gray-900 tw-shadow-md hover:tw-scale-110 active:tw-scale-95 tw-transition-all tw-border tw-border-gray-100"
                        @click="previousImage"
                      >
                        <span class="material-symbols-outlined tw-text-[20px]">chevron_left</span>
                      </button>
                      <button
                        class="tw-w-9 tw-h-9 tw-flex tw-items-center tw-justify-center tw-rounded-full tw-bg-white tw-text-gray-900 tw-shadow-md hover:tw-scale-110 active:tw-scale-95 tw-transition-all tw-border tw-border-gray-100"
                        @click="nextImage"
                      >
                        <span class="material-symbols-outlined tw-text-[20px]">chevron_right</span>
                      </button>
                    </div>
                  </div>

                  <!-- Thumbnail Grid -->
                  <div class="tw-grid tw-grid-cols-5 tw-gap-3">
                    <div
                      v-for="(image, index) in images"
                      :key="index"
                      class="tw-aspect-square tw-rounded-lg tw-cursor-pointer tw-relative tw-overflow-hidden tw-p-0.5"
                      :class="[
                        currentImageIndex === index
                          ? 'tw-border-2 tw-border-primary'
                          : 'tw-border tw-border-transparent hover:tw-border-gray-300 tw-opacity-70 hover:tw-opacity-100'
                      ]"
                      @click="currentImageIndex = index"
                    >
                      <div class="tw-w-full tw-h-full tw-rounded-md tw-bg-cover tw-bg-center" :style="{ backgroundImage: `url('${image}')` }"></div>
                    </div>
                  </div>
                </div>

                <!-- RIGHT COLUMN: DETAILS -->
                <div class="lg:tw-col-span-7 tw-flex tw-flex-col tw-gap-6">

                  <!-- SECTION 1: PRODUCTION ENTRY -->
                  <div class="tw-flex tw-flex-col tw-gap-5">
                    <div class="tw-flex tw-items-center tw-gap-2 tw-mb-1">
                      <span class="material-symbols-outlined tw-text-primary tw-text-[20px]">edit_note</span>
                      <h3 class="tw-text-sm tw-font-bold tw-text-gray-900 tw-uppercase tw-tracking-wide">Production Entry</h3>
                    </div>

                    <!-- Weight Input and Reference Grid -->
                    <div class="tw-grid tw-grid-cols-1 sm:tw-grid-cols-2 tw-gap-4">
                      <!-- Gross Weight Input -->
                      <div class="tw-space-y-1.5 tw-relative tw-group">
                        <label class="tw-text-xs tw-font-semibold tw-text-primary tw-uppercase tw-tracking-wide tw-flex tw-justify-between" for="gross-weight">
                          {{ transitionType === 'dispatch' ? 'Dispatch Weight (g)' : 'Received Weight (g)' }}
                          <span class="tw-text-[10px] tw-text-gray-400 tw-font-normal tw-normal-case">Required</span>
                        </label>
                        <div class="tw-relative">
                          <input
                            v-model="formData.grossWeight"
                            class="tw-block tw-w-full tw-rounded-xl tw-bg-white tw-py-3 tw-pl-3 tw-pr-8 tw-text-[#111418] tw-font-bold tw-text-lg placeholder:tw-text-gray-300 focus:tw-ring-primary tw-shadow-sm tw-transition-shadow"
                            :class="weightError ? 'tw-border-red-500 focus:tw-border-red-500' : 'tw-border-primary/50 focus:tw-border-primary'"
                            id="gross-weight"
                            name="gross-weight"
                            placeholder="0.00"
                            step="0.01"
                            min="0"
                            max="999999"
                            type="number"
                            @input="validateWeightInput"
                          />
                          <div class="tw-absolute tw-inset-y-0 tw-right-0 tw-flex tw-items-center tw-pr-3 tw-pointer-events-none">
                            <span class="tw-text-gray-400 tw-text-sm tw-font-bold">g</span>
                          </div>
                        </div>
                        <p v-if="weightError" class="tw-mt-1 tw-text-xs tw-text-red-600 tw-font-medium">{{ weightError }}</p>
                      </div>

                      <!-- Item Weight (Reference) -->
                      <div class="tw-bg-gray-50 tw-rounded-xl tw-p-3.5 tw-border tw-border-gray-100 tw-flex tw-flex-col tw-justify-center tw-h-full">
                        <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide tw-block tw-mb-1">Item Weight (g)</label>
                        <div class="tw-flex tw-items-baseline tw-gap-1.5">
                          <span class="tw-text-[#111418] tw-font-bold tw-text-lg">{{ formatWeight(orderData.item_weight) }}</span>
                          <span class="tw-text-gray-500 tw-font-medium tw-text-sm">g</span>
                        </div>
                      </div>
                    </div>

                    <!-- Karigar Received Weight (Reference) - Only for dispatch transition -->
                    <div v-if="transitionType === 'dispatch'" class="tw-bg-gray-50 tw-rounded-xl tw-p-3.5 tw-border tw-border-gray-100">
                      <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide tw-block tw-mb-1">Karigar Received Weight (g)</label>
                      <div class="tw-flex tw-items-baseline tw-gap-1.5">
                        <span class="tw-text-[#111418] tw-font-bold tw-text-lg">{{ formatWeight(orderData.karigar_received_weight) }}</span>
                        <span class="tw-text-gray-500 tw-font-medium tw-text-sm">g</span>
                      </div>
                    </div>

                    <!-- Remarks Input -->
                    <div class="tw-space-y-1.5">
                      <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide" for="remarks">Specific Remarks</label>
                      <textarea
                        v-model="formData.remarks"
                        class="tw-block tw-w-full tw-rounded-xl tw-border-gray-200 tw-bg-white tw-py-2.5 tw-px-3 tw-text-[#111418] placeholder:tw-text-gray-400 focus:tw-border-primary focus:tw-ring-primary sm:tw-text-sm tw-shadow-sm tw-transition-shadow tw-resize-none"
                        id="remarks"
                        name="remarks"
                        placeholder="Add notes about production quality, resizing, or specific adjustments..."
                        rows="2"
                      ></textarea>
                    </div>
                  </div>

                  <!-- Divider -->
                  <div class="tw-border-t tw-border-gray-100"></div>

                  <!-- SECTION 2: ORDER INFORMATION -->
                  <div class="tw-flex tw-flex-col tw-gap-6">
                    <h3 class="tw-text-xs tw-font-bold tw-text-gray-400 tw-uppercase tw-tracking-widest">Order Information</h3>

                    <!-- Static Info Grid -->
                    <div class="tw-grid tw-grid-cols-1 sm:tw-grid-cols-2 tw-gap-4">
                      <div class="tw-bg-gray-50 tw-rounded-xl tw-p-3.5 tw-border tw-border-gray-100 hover:tw-border-gray-200 tw-transition-colors">
                        <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide tw-block tw-mb-1">Customer</label>
                        <div class="tw-flex tw-items-center tw-gap-2">
                          <span class="tw-w-5 tw-h-5 tw-rounded-full tw-bg-purple-100 tw-text-purple-700 tw-text-[10px] tw-font-bold tw-flex tw-items-center tw-justify-center">
                            {{ getInitials(orderData.customer) }}
                          </span>
                          <span class="tw-text-[#111418] tw-font-semibold tw-text-sm">{{ orderData.customer }}</span>
                        </div>
                      </div>
                      <div class="tw-bg-gray-50 tw-rounded-xl tw-p-3.5 tw-border tw-border-gray-100 hover:tw-border-gray-200 tw-transition-colors tw-group">
                        <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide tw-block tw-mb-1">Item Code</label>
                        <div class="tw-flex tw-items-center tw-justify-between">
                          <span class="tw-text-[#111418] tw-font-semibold tw-text-sm">{{ orderData.item_code }}</span>
                          <button
                            class="tw-text-gray-400 hover:tw-text-primary tw-opacity-0 group-hover:tw-opacity-100 tw-transition-opacity"
                            @click="copyToClipboard(orderData.item_code)"
                          >
                            <span class="material-symbols-outlined tw-text-[16px]">content_copy</span>
                          </button>
                        </div>
                      </div>
                      <div class="tw-bg-gray-50 tw-rounded-xl tw-p-3.5 tw-border tw-border-gray-100 hover:tw-border-gray-200 tw-transition-colors">
                        <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide tw-block tw-mb-1">Quantity</label>
                        <span class="tw-text-[#111418] tw-font-semibold tw-text-sm">{{ orderData.qty ?? 'N/A' }}</span>
                      </div>
                      <div class="tw-bg-gray-50 tw-rounded-xl tw-p-3.5 tw-border tw-border-gray-100 hover:tw-border-gray-200 tw-transition-colors">
                        <label class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide tw-block tw-mb-1">Texture</label>
                        <div class="tw-flex tw-items-center tw-gap-1.5">
                          <span class="material-symbols-outlined tw-text-gray-400 tw-text-[18px]">texture</span>
                          <span class="tw-text-[#111418] tw-font-semibold tw-text-sm">{{ orderData.texture }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Karigar Card -->
                    <div
                      v-if="orderData.karigar"
                      class="tw-border tw-border-gray-200 tw-rounded-xl tw-p-4 tw-flex tw-items-center tw-justify-between hover:tw-border-primary/40 hover:tw-shadow-sm tw-transition-all tw-cursor-pointer tw-group tw-bg-white"
                    >
                      <div class="tw-flex tw-flex-col tw-gap-2">
                        <span class="tw-text-xs tw-font-semibold tw-text-gray-500 tw-uppercase tw-tracking-wide">Assigned Karigar</span>
                        <div class="tw-flex tw-items-center tw-gap-3">
                          <CwAvatar :name="orderData.karigar.name" size="md" :color="getKarigarColor(orderData.karigar.color)" />
                          <div>
                            <p class="tw-text-[#111418] tw-font-bold tw-text-sm tw-leading-tight group-hover:tw-text-primary tw-transition-colors">
                              {{ orderData.karigar.name }}
                            </p>
                            <p class="tw-text-gray-500 tw-text-xs tw-mt-0.5">Master Craftsman • ID: #KG-{{ orderData.id }}</p>
                          </div>
                        </div>
                      </div>
                      <span class="material-symbols-outlined tw-text-gray-300 group-hover:tw-text-primary tw-transition-colors">chevron_right</span>
                    </div>

                    <!-- Notes Card -->
                    <div
                      v-if="orderData.productionNotes"
                      class="tw-bg-yellow-50/60 tw-rounded-xl tw-p-4 tw-border tw-border-yellow-100/80 tw-flex tw-flex-col tw-gap-2"
                    >
                      <div class="tw-flex tw-items-center tw-justify-between tw-mb-1">
                        <span class="tw-text-xs tw-font-bold tw-text-yellow-700 tw-uppercase tw-tracking-wide tw-flex tw-items-center tw-gap-1.5">
                          <span class="material-symbols-outlined tw-text-[16px]">sticky_note_2</span>
                          Production Notes
                        </span>
                        <span class="tw-text-[10px] tw-text-yellow-600/70 tw-font-medium tw-bg-yellow-100/50 tw-px-1.5 tw-py-0.5 tw-rounded">Updated 2h ago</span>
                      </div>
                      <p class="tw-text-sm tw-text-gray-800 tw-leading-relaxed">
                        {{ orderData.productionNotes }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Footer -->
            <div class="tw-px-6 tw-py-4 tw-bg-gray-50 tw-border-t tw-border-gray-100 tw-flex tw-justify-end tw-items-end tw-text-sm tw-sticky tw-bottom-0 tw-z-20">
              <div class="tw-flex tw-gap-3">
                <button
                  class="tw-px-4 tw-py-2 tw-font-semibold tw-text-white tw-bg-[#111418] tw-border tw-border-[#111418] tw-rounded-lg hover:tw-bg-black tw-shadow-sm tw-transition-colors focus:tw-ring-2 focus:tw-ring-gray-500 focus:tw-outline-none"
                  :disabled="!isFormValid"
                  :class="{ 'tw-opacity-50 tw-cursor-not-allowed': !isFormValid }"
                  @click="saveChanges"
                >
                  Save Changes
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import CwAvatar from './CwAvatar.vue';
import { getKarigarColor } from '../utils/colors.js';

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  orderData: {
    type: Object,
    required: true
  },
  frappe: {
    type: Object,
    required: true
  },
  transitionType: {
    type: String,
    default: 'received',
    validator: (value) => ['received', 'dispatch'].includes(value)
  }
});

const emit = defineEmits(['update:modelValue', 'save']);

const titleId = `cw-order-item-title-${Math.random().toString(36).slice(2)}`;

// Image gallery state
const currentImageIndex = ref(0);
const placeholder = '/assets/frappe/images/ui-states/list-empty-state.svg';

// Computed property for images - use orderData.images or fallback to placeholder
const images = computed(() => {
  if (props.orderData?.images && props.orderData.images.length > 0) {
    return props.orderData.images;
  }
  return [placeholder];
});

// Form data
const formData = ref({
  grossWeight: '',
  remarks: ''
});

const weightError = ref('');

// Validate weight input
const validateWeightInput = () => {
  const weight = parseFloat(formData.value.grossWeight);

  if (formData.value.grossWeight === '') {
    weightError.value = '';
    return;
  }

  if (isNaN(weight)) {
    weightError.value = 'Please enter a valid number';
    return;
  }

  if (weight <= 0) {
    weightError.value = 'Weight must be greater than 0';
    return;
  }

  if (weight > 999999) {
    weightError.value = 'Weight cannot exceed 999,999g (999kg)';
    return;
  }

  weightError.value = '';
};

// Computed
const isFormValid = computed(() => {
  return formData.value.grossWeight &&
         parseFloat(formData.value.grossWeight) > 0 &&
         parseFloat(formData.value.grossWeight) <= 999999 &&
         !weightError.value;
});

// Watch for modal open/close to manage form state
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    // Modal opened - reset to first image
    currentImageIndex.value = 0;

    // Initialize form data if needed
    if (!formData.value.grossWeight) {
      formData.value = {
        grossWeight: '',
        remarks: ''
      };
      weightError.value = '';
    }
  } else {
    // Modal closed - reset form
    formData.value = {
      grossWeight: '',
      remarks: ''
    };
    weightError.value = '';
    currentImageIndex.value = 0;
  }
});

// Methods
const closeModal = () => {
  emit('update:modelValue', false);
};

const openInNewTab = () => {
  if (props.frappe && props.orderData.sales_order) {
    window.open(`/app/sales-order/${props.orderData.sales_order}`, '_blank');
  }
};

const nextImage = () => {
  currentImageIndex.value = (currentImageIndex.value + 1) % images.value.length;
};

const previousImage = () => {
  currentImageIndex.value = currentImageIndex.value === 0 ? images.value.length - 1 : currentImageIndex.value - 1;
};

const getInitials = (name) => {
  if (!name) return '??';
  const parts = name.split(' ');
  if (parts.length >= 2) {
    return parts[0][0] + parts[1][0];
  }
  return name.substring(0, 2).toUpperCase();
};

// getKarigarColor is now imported from utils/colors.js

const formatWeight = (weight) => {
  if (weight === null || weight === undefined) return '0';
  const num = parseFloat(weight);
  return isNaN(num) ? '0' : num.toFixed(2);
};


const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
    .then(() => {
      if (props.frappe) {
        props.frappe.show_alert({
          message: 'Copied to clipboard',
          indicator: 'green'
        });
      }
    })
    .catch(() => {
      if (props.frappe?.msgprint) {
        props.frappe.msgprint({
          title: 'Copy Failed',
          message: 'Could not copy to clipboard. Please copy manually.',
          indicator: 'red'
        });
      }
    });
};

const saveChanges = () => {
  if (!isFormValid.value) return;

  const data = {
    orderId: props.orderData.id,
    grossWeight: parseFloat(formData.value.grossWeight),
    remarks: formData.value.remarks,
    transitionType: props.transitionType
  };

  emit('save', data);
  closeModal();
};

// Keyboard navigation for image gallery
const handleImageKeyboard = (e) => {
  // Only handle keyboard events when modal is open
  if (!props.modelValue || images.value.length <= 1) return;

  switch (e.key) {
    case 'ArrowLeft':
      e.preventDefault();
      previousImage();
      break;

    case 'ArrowRight':
      e.preventDefault();
      nextImage();
      break;

    case 'Escape':
      e.preventDefault();
      closeModal();
      break;
  }
};

// Lifecycle hooks for keyboard navigation
onMounted(() => {
  document.addEventListener('keydown', handleImageKeyboard);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleImageKeyboard);
});
</script>
