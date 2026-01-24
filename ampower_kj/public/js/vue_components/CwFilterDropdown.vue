<template>
  <div class="tw-relative" ref="filterRef">
    <!-- Input Field -->
    <div class="tw-relative">
      <input
        v-model="inputValue"
        type="text"
        :placeholder="placeholder"
        class="tw-w-full tw-px-3 tw-py-2.5 tw-text-sm tw-bg-slate-50 tw-border tw-border-slate-200 tw-rounded-lg focus:tw-bg-white focus:tw-border-primary-500 focus:tw-ring-2 focus:tw-ring-primary-100 tw-outline-none tw-transition-all tw-pr-8"
        @input="handleInput"
        @focus="handleFocus"
        @keydown="handleKeydown"
      />

      <!-- Clear Button -->
      <button
        v-if="inputValue"
        class="tw-absolute tw-right-2 tw-top-1/2 -tw-translate-y-1/2 tw-text-slate-400 hover:tw-text-slate-600 tw-transition-colors"
        @click="clearInput"
        type="button"
      >
        <span class="material-symbols-outlined tw-text-lg">close</span>
      </button>
    </div>

    <!-- Dropdown Options -->
    <Teleport to="body">
      <div
        v-if="showDropdown && filteredOptions.length > 0"
        class="tw-fixed tw-z-[9999] tw-bg-white tw-border tw-border-slate-200 tw-rounded-lg tw-shadow-dropdown tw-py-1 tw-max-h-64 tw-overflow-y-auto"
        :style="dropdownStyle"
      >
        <div
          v-for="(option, index) in visibleOptions"
          :key="option"
          class="tw-px-3 tw-py-2 tw-text-sm tw-cursor-pointer hover:tw-bg-slate-50 tw-transition-colors"
          :class="{ 'tw-bg-slate-100': index === activeIndex }"
          @click="selectOption(option)"
          @mouseenter="activeIndex = index"
        >
          {{ option }}
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Select...'
  },
  maxOptions: {
    type: Number,
    default: 10
  },
  debounceMs: {
    type: Number,
    default: 500
  }
});

const emit = defineEmits(['update:modelValue', 'search']);

// State
const filterRef = ref(null);
const inputValue = ref(props.modelValue || '');
const showDropdown = ref(false);
const activeIndex = ref(-1);
const dropdownStyle = ref({});
let debounceTimeout = null;

// Watch for external changes to modelValue
watch(() => props.modelValue, (newVal) => {
  if (newVal !== inputValue.value) {
    inputValue.value = newVal || '';
  }
});

// Filtered options based on input
const filteredOptions = computed(() => {
  if (!inputValue.value) {
    return props.options;
  }
  const query = inputValue.value.toLowerCase();
  return props.options.filter(opt =>
    opt && opt.toLowerCase().includes(query)
  );
});

// Visible options (limited by maxOptions)
const visibleOptions = computed(() => {
  return filteredOptions.value.slice(0, props.maxOptions);
});

// Handle input change with debouncing
function handleInput() {
  showDropdown.value = true;
  activeIndex.value = -1;

  // Debounce the search event
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }

  debounceTimeout = setTimeout(() => {
    emit('update:modelValue', inputValue.value);
    emit('search', inputValue.value);
  }, props.debounceMs);
}

// Handle input focus
function handleFocus() {
  if (inputValue.value && filteredOptions.value.length > 0) {
    showDropdown.value = true;
    updateDropdownPosition();
  }
}

// Handle keyboard navigation
function handleKeydown(e) {
  if (!showDropdown.value || visibleOptions.value.length === 0) {
    if (e.key === 'Enter') {
      emit('update:modelValue', inputValue.value);
      emit('search', inputValue.value);
    }
    return;
  }

  switch (e.key) {
    case 'ArrowDown':
      e.preventDefault();
      activeIndex.value = Math.min(activeIndex.value + 1, visibleOptions.value.length - 1);
      scrollToActiveOption();
      break;

    case 'ArrowUp':
      e.preventDefault();
      activeIndex.value = Math.max(activeIndex.value - 1, 0);
      scrollToActiveOption();
      break;

    case 'Enter':
      e.preventDefault();
      if (activeIndex.value >= 0 && activeIndex.value < visibleOptions.value.length) {
        selectOption(visibleOptions.value[activeIndex.value]);
      } else {
        emit('update:modelValue', inputValue.value);
        emit('search', inputValue.value);
        showDropdown.value = false;
      }
      break;

    case 'Escape':
      e.preventDefault();
      showDropdown.value = false;
      activeIndex.value = -1;
      break;
  }
}

// Select an option
function selectOption(option) {
  inputValue.value = option;
  emit('update:modelValue', option);
  emit('search', option);
  showDropdown.value = false;
  activeIndex.value = -1;

  // Clear any pending debounce
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
    debounceTimeout = null;
  }
}

// Clear input
function clearInput() {
  inputValue.value = '';
  emit('update:modelValue', '');
  emit('search', '');
  showDropdown.value = false;
  activeIndex.value = -1;

  // Clear any pending debounce
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
    debounceTimeout = null;
  }
}

// Update dropdown position
function updateDropdownPosition() {
  if (!filterRef.value) return;

  const rect = filterRef.value.getBoundingClientRect();
  const inputRect = filterRef.value.querySelector('input').getBoundingClientRect();

  dropdownStyle.value = {
    top: `${inputRect.bottom + window.scrollY + 4}px`,
    left: `${inputRect.left + window.scrollX}px`,
    width: `${inputRect.width}px`
  };
}

// Scroll to active option in dropdown
function scrollToActiveOption() {
  // Wait for next tick to ensure DOM is updated
  setTimeout(() => {
    const dropdown = document.querySelector('[style*="z-index"][style*="9999"]');
    if (!dropdown) return;

    const activeOption = dropdown.children[activeIndex.value];
    if (!activeOption) return;

    const dropdownRect = dropdown.getBoundingClientRect();
    const optionRect = activeOption.getBoundingClientRect();

    if (optionRect.bottom > dropdownRect.bottom) {
      activeOption.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    } else if (optionRect.top < dropdownRect.top) {
      activeOption.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, 0);
}

// Click outside to close
function handleClickOutside(e) {
  if (filterRef.value && !filterRef.value.contains(e.target)) {
    // Check if click is on dropdown
    const dropdown = document.querySelector('[style*="z-index"][style*="9999"]');
    if (!dropdown || !dropdown.contains(e.target)) {
      showDropdown.value = false;
      activeIndex.value = -1;
    }
  }
}

// Watch showDropdown to update position
watch(showDropdown, (newVal) => {
  if (newVal) {
    updateDropdownPosition();
  }
});

// Lifecycle hooks
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('resize', updateDropdownPosition);
  window.addEventListener('scroll', updateDropdownPosition);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('resize', updateDropdownPosition);
  window.removeEventListener('scroll', updateDropdownPosition);

  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }
});
</script>

<style scoped>
/* Custom scrollbar for dropdown */
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
</style>
