<template>
  <div class="tw-h-full tw-bg-white dark:tw-bg-slate-800 tw-border tw-border-gray-200 dark:tw-border-gray-700 tw-rounded-lg tw-shadow-sm tw-flex tw-flex-col tw-relative">
    <!-- Keyboard Shortcuts Hint -->
    <div
      v-if="showKeyboardHint"
      class="tw-absolute tw-top-3 tw-right-3 tw-z-20 tw-bg-gradient-to-r tw-from-blue-500 tw-to-purple-600 tw-text-white tw-px-3 tw-py-1.5 tw-rounded-full tw-shadow-lg tw-flex tw-items-center tw-gap-2 tw-text-xs tw-font-medium tw-animate-pulse tw-cursor-pointer hover:tw-scale-105 tw-transition-transform"
      @click="toggleKeyboardPanel"
    >
      <span class="material-symbols-outlined tw-text-[16px]">keyboard</span>
      <span>Keyboard shortcuts</span>
    </div>

    <!-- Keyboard Shortcuts Panel -->
    <Teleport to="body">
      <Transition
        enter-active-class="tw-transition tw-ease-out tw-duration-200"
        enter-from-class="tw-opacity-0 tw-scale-95"
        enter-to-class="tw-opacity-100 tw-scale-100"
        leave-active-class="tw-transition tw-ease-in tw-duration-150"
        leave-from-class="tw-opacity-100 tw-scale-100"
        leave-to-class="tw-opacity-0 tw-scale-95"
      >
        <div
          v-if="showKeyboardPanel"
          class="tw-fixed tw-inset-0 tw-z-[9999] tw-flex tw-items-center tw-justify-center tw-bg-black/50 tw-backdrop-blur-sm"
          @click="showKeyboardPanel = false"
        >
          <div
            class="tw-bg-white dark:tw-bg-slate-800 tw-rounded-2xl tw-shadow-2xl tw-p-6 tw-max-w-md tw-w-full tw-mx-4"
            @click.stop
          >
            <div class="tw-flex tw-items-center tw-justify-between tw-mb-4">
              <h3 class="tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white tw-flex tw-items-center tw-gap-2">
                <span class="material-symbols-outlined tw-text-blue-600">keyboard</span>
                Keyboard Shortcuts
              </h3>
              <button
                @click="showKeyboardPanel = false"
                class="tw-p-1 tw-rounded-lg hover:tw-bg-gray-100 dark:hover:tw-bg-slate-700 tw-transition-colors"
              >
                <span class="material-symbols-outlined tw-text-gray-500">close</span>
              </button>
            </div>
            <div class="tw-space-y-3">
              <div class="tw-flex tw-items-center tw-justify-between tw-py-2">
                <span class="tw-text-sm tw-text-gray-600 dark:tw-text-gray-400">Navigate rows</span>
                <div class="tw-flex tw-gap-1">
                  <kbd class="kbd">↑</kbd>
                  <kbd class="kbd">↓</kbd>
                </div>
              </div>
              <div class="tw-flex tw-items-center tw-justify-between tw-py-2">
                <span class="tw-text-sm tw-text-gray-600 dark:tw-text-gray-400">Multi-select rows</span>
                <div class="tw-flex tw-gap-1">
                  <kbd class="kbd">Shift</kbd>
                  <span class="tw-text-gray-400">+</span>
                  <kbd class="kbd">↑</kbd>
                  <kbd class="kbd">↓</kbd>
                </div>
              </div>
              <div class="tw-flex tw-items-center tw-justify-between tw-py-2">
                <span class="tw-text-sm tw-text-gray-600 dark:tw-text-gray-400">Open selected row</span>
                <kbd class="kbd">Enter</kbd>
              </div>
              <div class="tw-flex tw-items-center tw-justify-between tw-py-2">
                <span class="tw-text-sm tw-text-gray-600 dark:tw-text-gray-400">Deselect all</span>
                <kbd class="kbd">Esc</kbd>
              </div>
              <div class="tw-flex tw-items-center tw-justify-between tw-py-2">
                <span class="tw-text-sm tw-text-gray-600 dark:tw-text-gray-400">Multi-select (click)</span>
                <div class="tw-flex tw-gap-1">
                  <kbd class="kbd">Ctrl</kbd>
                  <span class="tw-text-gray-400">+</span>
                  <kbd class="kbd">Click</kbd>
                </div>
              </div>
              <div class="tw-flex tw-items-center tw-justify-between tw-py-2">
                <span class="tw-text-sm tw-text-gray-600 dark:tw-text-gray-400">Select all</span>
                <div class="tw-flex tw-gap-1">
                  <kbd class="kbd">Ctrl</kbd>
                  <span class="tw-text-gray-400">+</span>
                  <kbd class="kbd">A</kbd>
                </div>
              </div>
            </div>
            <div class="tw-mt-4 tw-pt-4 tw-border-t tw-border-gray-200 dark:tw-border-gray-700">
              <label class="tw-flex tw-items-center tw-gap-2 tw-cursor-pointer">
                <input
                  type="checkbox"
                  v-model="dontShowAgain"
                  class="tw-rounded tw-border-gray-300 tw-text-blue-600 focus:tw-ring-blue-500"
                />
                <span class="tw-text-xs tw-text-gray-500 dark:tw-text-gray-400">Don't show this hint again</span>
              </label>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <div class="tw-overflow-x-auto tw-overflow-y-auto custom-scroll no-scrollbar-mobile tw-flex-1 tw-relative" tabindex="0" @keydown="handleKeyDown">
      <table class="tw-min-w-full tw-divide-y tw-divide-gray-200 dark:tw-divide-gray-700 tw-border-separate tw-border-spacing-0">
        <thead class="tw-bg-gray-50 dark:tw-bg-slate-800">
          <tr>
            <!-- Checkbox column -->
            <th v-if="selectable" scope="col" class="tw-sticky tw-top-0 tw-z-10 tw-bg-gray-50 dark:tw-bg-slate-800 tw-px-4 tw-py-3 tw-text-center tw-w-10 tw-border-b tw-border-gray-200 dark:tw-border-gray-700">
              <div class="tw-flex tw-items-center tw-justify-center">
                <input
                  ref="selectAllRef"
                  type="checkbox"
                  class="tw-rounded tw-border-gray-300 tw-text-primary tw-h-4 tw-w-4 tw-bg-white dark:tw-bg-slate-700 dark:tw-border-gray-600 tw-cursor-pointer focus:tw-ring-primary"
                  :checked="allSelected"
                  :indeterminate="someSelected"
                  @change="toggleSelectAll"
                />
              </div>
            </th>
            <!-- Dynamic columns -->
            <th
              v-for="col in columns"
              :key="col.key"
              scope="col"
              class="tw-sticky tw-top-0 tw-z-10 tw-bg-gray-50 dark:tw-bg-slate-800 tw-px-3 tw-py-3 tw-text-center tw-text-[11px] tw-font-bold tw-text-slate-500 dark:tw-text-slate-400 tw-uppercase tw-tracking-wider tw-border-b tw-border-gray-200 dark:tw-border-gray-700 group hover:tw-bg-gray-100 dark:hover:tw-bg-slate-700 tw-transition-colors"
              :class="[col.headerClass, col.sortable ? 'tw-cursor-pointer' : '']"
              :style="col.width ? { width: col.width } : {}"
              @click="col.sortable && handleSort(col.key)"
            >
              <div class="tw-flex tw-items-center tw-justify-center">
                {{ col.label }}
                <span
                  v-if="col.sortable"
                  class="material-symbols-outlined tw-text-[14px] tw-ml-1 tw-opacity-0 group-hover:tw-opacity-100 tw-transition-opacity"
                >
                  {{ getSortIcon(col.key) }}
                </span>
              </div>
            </th>
            <!-- Actions column -->
            <th v-if="hasActions" scope="col" class="tw-sticky tw-top-0 tw-z-10 tw-bg-gray-50 dark:tw-bg-slate-800 tw-px-3 tw-py-3 tw-text-center tw-text-[11px] tw-font-bold tw-text-slate-500 dark:tw-text-slate-400 tw-uppercase tw-tracking-wider tw-border-b tw-border-gray-200 dark:tw-border-gray-700 group hover:tw-bg-gray-100 dark:hover:tw-bg-slate-700 tw-transition-colors">
              <div class="tw-flex tw-items-center tw-justify-center">
                Actions
              </div>
            </th>
          </tr>
        </thead>
        <tbody class="tw-bg-white dark:tw-bg-slate-800 tw-divide-y tw-divide-gray-200 dark:tw-divide-gray-700">
          <tr
            v-if="data && data.length > 0"
            v-for="(row, index) in data"
            :key="row[rowKey] || index"
            :ref="el => { if (el) rowRefs[index] = el }"
            class="group hover:tw-bg-blue-50/40 dark:hover:tw-bg-slate-800/60 tw-transition-colors tw-cursor-pointer"
            :class="[
              isSelected(row) ? 'tw-bg-blue-50/30 dark:tw-bg-blue-900/10' : '',
              focusedRowIndex === index ? 'tw-ring-2 tw-ring-blue-500 tw-ring-inset' : '',
              index % 2 === 1 ? 'tw-bg-slate-50/30 dark:tw-bg-slate-800/20' : ''
            ]"
            @click="handleRowClick(row, index, $event)"
            @dblclick="emit('row-dblclick', row)"
          >
            <!-- Checkbox column -->
            <td v-if="selectable" class="tw-px-4 tw-py-2.5 tw-whitespace-nowrap" @click.stop>
              <input
                type="checkbox"
                class="tw-rounded tw-border-gray-300 tw-text-primary focus:tw-ring-primary tw-h-4 tw-w-4 tw-bg-white dark:tw-bg-slate-700 dark:tw-border-gray-600 tw-cursor-pointer tw-opacity-50 group-hover:tw-opacity-100 tw-transition-opacity"
                :checked="isSelected(row)"
                @change="toggleSelect(row)"
              />
            </td>
            <!-- Dynamic columns -->
            <td
              v-for="col in columns"
              :key="col.key"
              class="tw-px-3 tw-py-2.5 tw-whitespace-nowrap tw-text-sm"
              :class="col.cellClass"
            >
              <slot
                :name="`cell-${col.key}`"
                :row="row"
                :value="row[col.key]"
              >
                {{ formatCell(row[col.key], col) }}
              </slot>
            </td>
            <!-- Actions column -->
            <td v-if="hasActions" class="tw-px-3 tw-py-2.5 tw-whitespace-nowrap tw-text-xs tw-text-gray-400" @click.stop>
              <slot name="actions" :row="row">
                <button
                  class="tw-p-1 tw-rounded hover:tw-bg-gray-100 dark:hover:tw-bg-slate-700 tw-text-gray-500 tw-transition-colors"
                  @click="emit('action-click', row)"
                >
                  <span class="material-symbols-outlined tw-text-[18px]">more_horiz</span>
                </button>
              </slot>
            </td>
          </tr>
          <tr v-else>
            <td :colspan="totalColumns" class="tw-px-4 tw-py-12 tw-text-center tw-text-slate-500">
              <slot name="empty">
                <div class="tw-flex tw-flex-col tw-items-center tw-gap-2">
                  <span class="material-symbols-outlined tw-text-4xl tw-text-slate-300">inbox</span>
                  <p>No data available</p>
                </div>
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div
      v-if="showPagination && totalItems > 0"
      class="tw-bg-white dark:tw-bg-slate-800 tw-px-3 sm:tw-px-4 tw-py-3 tw-border-t tw-border-gray-200 dark:tw-border-gray-700 tw-flex-shrink-0"
    >
      <div class="tw-flex tw-flex-col md:tw-flex-row tw-items-start md:tw-items-center tw-justify-between tw-gap-3">
        <!-- Left section: Info and Per page -->
        <div class="tw-flex tw-flex-col sm:tw-flex-row tw-items-start sm:tw-items-center tw-gap-2 sm:tw-gap-4">
          <p class="tw-text-xs sm:tw-text-[11px] tw-text-gray-700 dark:tw-text-gray-300 tw-whitespace-nowrap tw-shrink-0">
            Showing <span class="tw-font-bold">{{ startItem }}</span> to <span class="tw-font-bold">{{ endItem }}</span> of <span class="tw-font-bold">{{ totalItems }}</span> results
          </p>
          <div class="tw-flex tw-items-center tw-gap-2 tw-shrink-0">
            <label class="tw-text-xs sm:tw-text-[11px] tw-text-gray-600 dark:tw-text-gray-400 tw-whitespace-nowrap">Per page:</label>
            <select
              :value="pageSize"
              @change="emit('page-size-change', parseInt($event.target.value))"
              class="tw-text-xs sm:tw-text-[11px] tw-px-2 tw-py-1 tw-border tw-border-gray-300 dark:tw-border-gray-600 tw-rounded tw-bg-white dark:tw-bg-slate-800 tw-text-gray-700 dark:tw-text-gray-300 focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-primary-500 tw-min-w-[60px] tw-max-w-[80px]"
            >
              <option value="10">10</option>
              <option value="25">25</option>
              <option value="50">50</option>
              <option value="100">100</option>
              <option value="200">200</option>
            </select>
          </div>
        </div>

        <!-- Right section: Pagination controls -->
        <div class="tw-flex tw-justify-start md:tw-justify-end tw-w-full md:tw-w-auto">
          <nav aria-label="Pagination" class="tw-relative tw-z-0 tw-inline-flex tw-rounded-md tw-shadow-sm -tw-space-x-px">
            <a
              href="#"
              class="tw-relative tw-inline-flex tw-items-center tw-px-1.5 sm:tw-px-2 tw-py-1.5 tw-rounded-l-md tw-border tw-border-gray-300 dark:tw-border-gray-600 tw-bg-white dark:tw-bg-slate-800 tw-text-xs tw-font-medium tw-text-gray-500 dark:tw-text-gray-400 hover:tw-bg-gray-50 dark:hover:tw-bg-slate-700 tw-transition-colors"
              :class="{ 'tw-opacity-50 tw-cursor-not-allowed': currentPage === 1 }"
              @click.prevent="currentPage > 1 && emit('page-change', currentPage - 1)"
            >
              <span class="tw-sr-only">Previous</span>
              <span class="material-symbols-outlined tw-text-sm sm:tw-text-[16px]">chevron_left</span>
            </a>
            <a
              v-for="page in visiblePages"
              :key="page"
              href="#"
              class="tw-relative tw-inline-flex tw-items-center tw-px-2 sm:tw-px-3 tw-py-1.5 tw-border tw-text-xs tw-font-medium tw-transition-colors tw-min-w-[32px] tw-justify-center"
              :class="[
                page === currentPage
                  ? 'tw-z-10 tw-bg-blue-50 dark:tw-bg-blue-900/20 tw-border-primary tw-text-primary tw-font-bold'
                  : 'tw-bg-white dark:tw-bg-slate-800 tw-border-gray-300 dark:tw-border-gray-600 tw-text-gray-500 dark:tw-text-gray-400 hover:tw-bg-gray-50 dark:hover:tw-bg-slate-700'
              ]"
              @click.prevent="emit('page-change', page)"
            >
              {{ page }}
            </a>
            <a
              href="#"
              class="tw-relative tw-inline-flex tw-items-center tw-px-1.5 sm:tw-px-2 tw-py-1.5 tw-rounded-r-md tw-border tw-border-gray-300 dark:tw-border-gray-600 tw-bg-white dark:tw-bg-slate-800 tw-text-xs tw-font-medium tw-text-gray-500 dark:tw-text-gray-400 hover:tw-bg-gray-50 dark:hover:tw-bg-slate-700 tw-transition-colors"
              :class="{ 'tw-opacity-50 tw-cursor-not-allowed': currentPage === totalPages }"
              @click.prevent="currentPage < totalPages && emit('page-change', currentPage + 1)"
            >
              <span class="tw-sr-only">Next</span>
              <span class="material-symbols-outlined tw-text-sm sm:tw-text-[16px]">chevron_right</span>
            </a>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  columns: {
    type: Array,
    required: true
    // Each column: { key: string, label: string, sortable?: boolean, width?: string, headerClass?: string, cellClass?: string, format?: function }
  },
  data: {
    type: Array,
    default: () => []
  },
  rowKey: {
    type: String,
    default: 'id'
  },
  selectable: {
    type: Boolean,
    default: false
  },
  selected: {
    type: Array,
    default: () => []
  },
  hasActions: {
    type: Boolean,
    default: false
  },
  showPagination: {
    type: Boolean,
    default: false
  },
  totalItems: {
    type: Number,
    default: 0
  },
  currentPage: {
    type: Number,
    default: 1
  },
  pageSize: {
    type: Number,
    default: 20
  },
  sortKey: {
    type: String,
    default: ''
  },
  sortOrder: {
    type: String,
    default: 'asc',
    validator: (v) => ['asc', 'desc'].includes(v)
  }
});

const emit = defineEmits(['update:selected', 'row-click', 'row-dblclick', 'action-click', 'page-change', 'page-size-change', 'sort-change']);

const selectAllRef = ref(null);
const rowRefs = ref([]);
const focusedRowIndex = ref(-1);
const showKeyboardHint = ref(false);
const showKeyboardPanel = ref(false);
const dontShowAgain = ref(false);
const lastSelectedIndex = ref(-1);

// Show keyboard hint on mount (only if user hasn't dismissed it)
onMounted(() => {
  const dismissed = localStorage.getItem('cw-table-keyboard-hint-dismissed');
  if (!dismissed) {
    setTimeout(() => {
      showKeyboardHint.value = true;
      // Auto-hide after 8 seconds
      setTimeout(() => {
        showKeyboardHint.value = false;
      }, 8000);
    }, 1000);
  }
});

// Watch dontShowAgain checkbox
watch(dontShowAgain, (newVal) => {
  if (newVal) {
    localStorage.setItem('cw-table-keyboard-hint-dismissed', 'true');
    showKeyboardHint.value = false;
  }
});

const toggleKeyboardPanel = () => {
  showKeyboardPanel.value = !showKeyboardPanel.value;
};

const totalColumns = computed(() => {
  let count = props.columns.length;
  if (props.selectable) count++;
  if (props.hasActions) count++;
  return count;
});

const allSelected = computed(() => {
  return props.data.length > 0 && props.selected.length === props.data.length;
});

const someSelected = computed(() => {
  return props.selected.length > 0 && !allSelected.value;
});

// Handle indeterminate checkbox state
watch(() => someSelected.value, (newVal) => {
  if (selectAllRef.value) {
    selectAllRef.value.indeterminate = newVal;
  }
});

const totalPages = computed(() => {
  return Math.ceil(props.totalItems / props.pageSize);
});

const startItem = computed(() => {
  return (props.currentPage - 1) * props.pageSize + 1;
});

const endItem = computed(() => {
  return Math.min(props.currentPage * props.pageSize, props.totalItems);
});

const visiblePages = computed(() => {
  const pages = [];
  const total = totalPages.value;
  const current = props.currentPage;

  if (total <= 3) {
    for (let i = 1; i <= total; i++) pages.push(i);
  } else {
    if (current <= 2) {
      pages.push(1, 2, 3);
    } else if (current >= total - 1) {
      pages.push(total - 2, total - 1, total);
    } else {
      pages.push(current - 1, current, current + 1);
    }
  }

  return pages;
});

const isSelected = (row) => {
  return props.selected.some(s => s[props.rowKey] === row[props.rowKey]);
};

const toggleSelect = (row) => {
  const newSelected = isSelected(row)
    ? props.selected.filter(s => s[props.rowKey] !== row[props.rowKey])
    : [...props.selected, row];
  emit('update:selected', newSelected);
};

const toggleSelectAll = (e) => {
  const newSelected = e.target.checked ? [...props.data] : [];
  emit('update:selected', newSelected);
};

const formatCell = (value, col) => {
  if (col.format && typeof col.format === 'function') {
    return col.format(value);
  }
  return value ?? '-';
};

const getSortIcon = (key) => {
  if (props.sortKey !== key) return 'arrow_drop_down';
  return props.sortOrder === 'asc' ? 'arrow_drop_up' : 'arrow_drop_down';
};

const handleSort = (key) => {
  const newOrder = props.sortKey === key && props.sortOrder === 'asc' ? 'desc' : 'asc';
  emit('sort-change', { key, order: newOrder });
};

// Keyboard navigation
const handleRowClick = (row, index, event) => {
  focusedRowIndex.value = index;

  // Ctrl/Cmd + Click for multi-select
  if (event.ctrlKey || event.metaKey) {
    if (props.selectable) {
      toggleSelect(row);
      lastSelectedIndex.value = index;
    }
    return;
  }

  // Shift + Click for range selection
  if (event.shiftKey && props.selectable && lastSelectedIndex.value !== -1) {
    const start = Math.min(lastSelectedIndex.value, index);
    const end = Math.max(lastSelectedIndex.value, index);
    const rangeRows = props.data.slice(start, end + 1);

    // Add all rows in range to selection
    const newSelected = [...props.selected];
    rangeRows.forEach(r => {
      if (!isSelected(r)) {
        newSelected.push(r);
      }
    });
    emit('update:selected', newSelected);
    return;
  }

  lastSelectedIndex.value = index;
  emit('row-click', row);
};

const handleKeyDown = (event) => {
  if (!props.data || props.data.length === 0) return;

  const key = event.key;
  const isShift = event.shiftKey;
  const isCtrl = event.ctrlKey || event.metaKey;

  // Ctrl/Cmd + A - Select all
  if (isCtrl && key === 'a') {
    event.preventDefault();
    if (props.selectable) {
      emit('update:selected', [...props.data]);
      lastSelectedIndex.value = props.data.length - 1;
    }
    return;
  }

  // Escape - Deselect all
  if (key === 'Escape') {
    event.preventDefault();
    emit('update:selected', []);
    focusedRowIndex.value = -1;
    lastSelectedIndex.value = -1;
    return;
  }

  // Arrow Up/Down navigation
  if (key === 'ArrowUp' || key === 'ArrowDown') {
    event.preventDefault();

    let newIndex = focusedRowIndex.value;

    if (key === 'ArrowDown') {
      newIndex = focusedRowIndex.value === -1 ? 0 : Math.min(focusedRowIndex.value + 1, props.data.length - 1);
    } else {
      newIndex = focusedRowIndex.value === -1 ? 0 : Math.max(focusedRowIndex.value - 1, 0);
    }

    focusedRowIndex.value = newIndex;

    // Scroll into view
    if (rowRefs.value[newIndex]) {
      rowRefs.value[newIndex].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }

    // Shift + Arrow for multi-select
    if (isShift && props.selectable) {
      const row = props.data[newIndex];
      if (!isSelected(row)) {
        emit('update:selected', [...props.selected, row]);
      }
      lastSelectedIndex.value = newIndex;
    } else {
      lastSelectedIndex.value = newIndex;
    }

    return;
  }

  // Enter - Open focused row
  if (key === 'Enter') {
    event.preventDefault();
    if (focusedRowIndex.value !== -1 && props.data[focusedRowIndex.value]) {
      emit('row-click', props.data[focusedRowIndex.value]);
    }
    return;
  }
};

// Reset focused row when data changes
watch(() => props.data, () => {
  focusedRowIndex.value = -1;
  rowRefs.value = [];
});
</script>

<style scoped>
.custom-scroll::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.custom-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background: #CBD5E1;
  border-radius: 4px;
}

.dark .custom-scroll::-webkit-scrollbar-thumb {
  background: #475569;
}

/* Mobile Scrollbar - Hide on mobile devices */
@media (max-width: 768px) {
  .no-scrollbar-mobile::-webkit-scrollbar {
    display: none;
  }
  .no-scrollbar-mobile {
    -ms-overflow-style: none;
    scrollbar-width: none;
  }
}

/* Mobile responsive pagination */
@media (max-width: 768px) {
  /* Ensure pagination wraps properly */
  nav a {
    font-size: 0.75rem;
  }

  /* Smaller page number buttons */
  nav a.tw-min-w-\[32px\] {
    min-width: 28px;
    padding-left: 0.375rem;
    padding-right: 0.375rem;
  }
}

/* Tablet adjustments */
@media (max-width: 1024px) and (min-width: 769px) {
  /* Maintain readable text on tablets */
  th {
    font-size: 0.75rem !important;
    padding: 0.5rem !important;
  }

  td {
    font-size: 0.875rem !important;
    padding: 0.5rem !important;
  }
}

/* Mobile table adjustments */
@media (max-width: 768px) {
  /* Enable horizontal scroll */
  table {
    min-width: 800px; /* Force table to be wider than viewport on mobile */
  }

  /* Better readable text and padding on mobile */
  th {
    font-size: 0.75rem !important;
    padding: 0.5rem 0.375rem !important;
    white-space: nowrap;
  }

  td {
    font-size: 0.875rem !important;
    padding: 0.5rem 0.375rem !important;
    white-space: nowrap;
  }

  /* Reduce checkbox size on mobile */
  input[type="checkbox"] {
    width: 0.875rem !important;
    height: 0.875rem !important;
  }

  /* Better text sizing */
  select {
    font-size: 0.75rem;
  }
}

/* Extra small screens - compact everything */
@media (max-width: 480px) {
  th, td {
    font-size: 0.75rem !important;
    padding: 0.375rem 0.25rem !important;
  }

  /* Even smaller checkboxes */
  input[type="checkbox"] {
    width: 0.75rem !important;
    height: 0.75rem !important;
  }

  /* Compact pagination */
  nav a {
    padding: 0.25rem 0.375rem !important;
  }

  .material-symbols-outlined {
    font-size: 0.875rem !important;
  }
}

/* Keyboard shortcut badge styling */
.kbd {
  @apply tw-inline-flex tw-items-center tw-justify-center tw-px-2 tw-py-1 tw-min-w-[2rem] tw-text-xs tw-font-semibold tw-text-gray-700 dark:tw-text-gray-300 tw-bg-gray-100 dark:tw-bg-slate-700 tw-border tw-border-gray-300 dark:tw-border-gray-600 tw-rounded tw-shadow-sm;
}
</style>
