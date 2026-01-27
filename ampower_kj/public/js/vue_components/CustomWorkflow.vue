<template>
  <div class="tw-font-sans tw-h-screen tw-flex tw-flex-col tw-px-4 tw-bg-white dark:tw-bg-gray-900">
    <!-- Tabs -->
    <CwTabs
      v-model="currentTab"
      :tabs="tabs"
      class="tw-mb-4 tw-flex-shrink-0 cw-tabs-list"
    />

    <!-- Toolbar -->
    <div class="tw-flex tw-flex-col sm:tw-flex-row tw-items-stretch sm:tw-items-center tw-justify-between tw-gap-3 sm:tw-gap-4 tw-mb-4 tw-py-3 tw-flex-shrink-0 tw-relative tw-z-[70]">
      <!-- Search -->
      <div class="tw-relative tw-w-full sm:tw-flex-1 sm:tw-max-w-md">
        <span class="material-symbols-outlined tw-absolute tw-left-3 tw-top-1/2 tw--translate-y-1/2 tw-text-slate-400 dark:tw-text-slate-500 tw-text-lg">
          search
        </span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search orders, customers, items..."
          class="tw-w-full tw-pl-10 tw-pr-12 tw-py-2.5 tw-text-sm tw-bg-slate-50 dark:tw-bg-slate-800 tw-border tw-border-slate-200 dark:tw-border-slate-700 tw-rounded-lg focus:tw-bg-white dark:focus:tw-bg-slate-700 focus:tw-border-primary-500 focus:tw-ring-2 focus:tw-ring-primary-100 dark:focus:tw-ring-primary-900 tw-outline-none tw-transition-all placeholder:tw-text-slate-400 dark:placeholder:tw-text-slate-500 tw-text-slate-900 dark:tw-text-slate-100"
          @input="handleSearch"
        />
      </div>

      <!-- Toolbar actions -->
      <div class="tw-flex tw-flex-wrap sm:tw-flex-nowrap tw-items-center tw-gap-2">
        <!-- Filters Dropdown -->
        <div class="tw-relative tw-inline-block tw-flex-1 sm:tw-flex-none cw-filter-section" ref="filtersDropdownRef">
          <CwButton
            variant="ghost"
            icon="filter_list"
            :icon-right="isFiltersOpen ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
            @click="toggleFilters"
            class="tw-w-full sm:tw-w-auto"
          >
            Filters
            <span v-if="activeFiltersCount > 0" class="tw-ml-1.5 tw-px-1.5 tw-py-0.5 tw-bg-primary-100 dark:tw-bg-primary-900 tw-text-primary-700 dark:tw-text-primary-300 tw-text-xs tw-font-semibold tw-rounded">
              {{ activeFiltersCount }}
            </span>
          </CwButton>

          <!-- Backdrop -->
          <Teleport to="body">
            <div v-if="isFiltersOpen" class="tw-fixed tw-inset-0 tw-z-[999]" @click="closeFilters"></div>
          </Teleport>

          <!-- Filters Dropdown Menu -->
          <Teleport to="body">
            <Transition
              enter-active-class="tw-transition tw-ease-out tw-duration-300"
              enter-from-class="tw-opacity-0 tw-translate-y-2"
              enter-to-class="tw-opacity-100 tw-translate-y-0"
              leave-active-class="tw-transition tw-ease-in tw-duration-200"
              leave-from-class="tw-opacity-100 tw-translate-y-0"
              leave-to-class="tw-opacity-0 tw-translate-y-2"
            >
              <div
                v-if="isFiltersOpen"
                :style="filterDropdownStyle"
                class="tw-fixed tw-z-[1000] tw-overflow-y-auto tw-bg-white dark:tw-bg-slate-800 tw-rounded-xl tw-shadow-[0_20px_40px_-5px_rgba(0,0,0,0.15),0_8px_16px_-6px_rgba(0,0,0,0.1)] tw-border tw-border-slate-200 dark:tw-border-slate-700 tw-transition-all tw-duration-300"
              >
              <!-- Content Padding -->
              <div class="tw-p-5 sm:tw-p-8 tw-flex tw-flex-col tw-gap-6 sm:tw-gap-8">
                <!-- Field 1: Customer Search -->
                <div class="tw-flex tw-flex-col tw-gap-2 tw-group">
                  <label class="tw-text-xs tw-font-bold tw-tracking-[0.15em] tw-text-slate-500 dark:tw-text-slate-400 tw-uppercase">
                    Customer
                  </label>
                  <div class="tw-relative tw-flex tw-items-center tw-w-full tw-border-b tw-border-slate-200 dark:tw-border-slate-600 tw-py-2 group-focus-within:tw-border-blue-600 tw-transition-colors tw-duration-200">
                    <span class="material-symbols-outlined tw-text-slate-400 dark:tw-text-slate-500 tw-text-[20px] tw-mr-3 group-focus-within:tw-text-blue-600 tw-transition-colors">
                      search
                    </span>
                    <input
                      v-model="filters.customer"
                      class="tw-w-full tw-bg-transparent tw-border-none tw-p-0 tw-text-sm tw-font-normal tw-text-slate-900 dark:tw-text-slate-100 placeholder:tw-text-slate-300 dark:placeholder:tw-text-slate-600 focus:tw-ring-0 tw-leading-normal focus:tw-outline-none"
                      placeholder="Search by name or ID"
                      type="text"
                    />
                  </div>
                </div>

                <!-- Field 2: Karigar Search -->
                <div class="tw-flex tw-flex-col tw-gap-2 tw-group">
                  <label class="tw-text-xs tw-font-bold tw-tracking-[0.15em] tw-text-slate-500 dark:tw-text-slate-400 tw-uppercase">
                    Karigar
                  </label>
                  <div class="tw-relative tw-flex tw-items-center tw-w-full tw-border-b tw-border-slate-200 dark:tw-border-slate-600 tw-py-2 group-focus-within:tw-border-blue-600 tw-transition-colors tw-duration-200">
                    <span class="material-symbols-outlined tw-text-slate-400 dark:tw-text-slate-500 tw-text-[20px] tw-mr-3 group-focus-within:tw-text-blue-600 tw-transition-colors">
                      search
                    </span>
                    <input
                      v-model="filters.karigar"
                      class="tw-w-full tw-bg-transparent tw-border-none tw-p-0 tw-text-sm tw-font-normal tw-text-slate-900 dark:tw-text-slate-100 placeholder:tw-text-slate-300 dark:placeholder:tw-text-slate-600 focus:tw-ring-0 tw-leading-normal focus:tw-outline-none"
                      placeholder="Search by karigar name"
                      type="text"
                    />
                  </div>
                </div>

                <!-- Field 3: Item Name -->
                <div class="tw-flex tw-flex-col tw-gap-2 tw-group">
                  <label class="tw-text-xs tw-font-bold tw-tracking-[0.15em] tw-text-slate-500 dark:tw-text-slate-400 tw-uppercase">
                    Item Name
                  </label>
                  <div class="tw-relative tw-flex tw-items-center tw-w-full tw-border-b tw-border-slate-200 dark:tw-border-slate-600 tw-py-2 group-focus-within:tw-border-blue-600 tw-transition-colors tw-duration-200">
                    <span class="material-symbols-outlined tw-text-slate-400 dark:tw-text-slate-500 tw-text-[20px] tw-mr-3 group-focus-within:tw-text-blue-600 tw-transition-colors">
                      inventory_2
                    </span>
                    <input
                      v-model="filters.itemName"
                      class="tw-w-full tw-bg-transparent tw-border-none tw-p-0 tw-text-sm tw-font-normal tw-text-slate-900 dark:tw-text-slate-100 placeholder:tw-text-slate-300 dark:placeholder:tw-text-slate-600 focus:tw-ring-0 tw-leading-normal focus:tw-outline-none"
                      placeholder="Search item name"
                      type="text"
                    />
                  </div>
                </div>
              </div>

              <!-- Footer Actions -->
              <div class="tw-px-5 sm:tw-px-8 tw-pb-5 sm:tw-pb-8 tw-pt-3 tw-flex tw-flex-wrap tw-items-center tw-justify-between tw-gap-3 tw-border-t tw-border-slate-200 dark:tw-border-slate-700">
                <button
                  @click="clearFilters"
                  class="tw-h-10 tw-inline-flex tw-items-center tw-text-sm tw-font-medium tw-text-slate-500 dark:tw-text-slate-400 hover:tw-text-slate-700 dark:hover:tw-text-slate-200 tw-transition-colors tw-px-2 tw-rounded"
                  :class="{ 'tw-opacity-50 tw-cursor-not-allowed': activeFiltersCount === 0 }"
                  :disabled="activeFiltersCount === 0"
                >
                  Clear all
                </button>
                <button
                  @click="applyFilters"
                  class="tw-h-10 tw-bg-primary-600 hover:tw-bg-primary-500 tw-text-white tw-text-sm tw-font-medium tw-px-6 sm:tw-px-8 tw-rounded-lg tw-shadow-lg tw-shadow-primary-200/20 tw-transition-all hover:tw-shadow-primary-200/30 active:tw-scale-[0.98]"
                >
                  Apply Filters
                </button>
              </div>
            </div>
            </Transition>
          </Teleport>
        </div>

        <!-- Columns Dropdown -->
        <div class="tw-relative tw-inline-block tw-flex-1 sm:tw-flex-none" ref="columnsDropdownRef">
          <CwButton
            variant="ghost"
            icon="view_column"
            :icon-right="isColumnsOpen ? 'keyboard_arrow_up' : 'keyboard_arrow_down'"
            @click="toggleColumns"
            class="tw-w-full sm:tw-w-auto"
          >
            Columns
          </CwButton>

          <!-- Backdrop -->
          <Teleport to="body">
            <div v-if="isColumnsOpen" class="tw-fixed tw-inset-0 tw-z-[999]" @click="closeColumns"></div>
          </Teleport>

          <!-- Columns Dropdown Menu -->
          <Teleport to="body">
            <Transition
              enter-active-class="tw-transition tw-ease-out tw-duration-200"
              enter-from-class="tw-opacity-0 tw-translate-y-2"
              enter-to-class="tw-opacity-100 tw-translate-y-0"
              leave-active-class="tw-transition tw-ease-in tw-duration-150"
              leave-from-class="tw-opacity-100 tw-translate-y-0"
              leave-to-class="tw-opacity-0 tw-translate-y-2"
            >
              <div
                v-if="isColumnsOpen"
                :style="columnDropdownStyle"
                class="tw-fixed tw-z-[1000] tw-flex tw-flex-col tw-rounded-xl tw-bg-white dark:tw-bg-slate-800 tw-shadow-[0_20px_40px_-10px_rgba(0,0,0,0.15),0_10px_20px_-5px_rgba(0,0,0,0.1)] tw-border tw-border-gray-200 dark:tw-border-slate-700 tw-overflow-hidden"
              >
              <!-- Search Header -->
              <div class="tw-px-4 tw-py-3 tw-border-b tw-border-gray-200/50 dark:tw-border-slate-700 tw-bg-white dark:tw-bg-slate-800 tw-z-10">
                <div class="tw-flex tw-items-center tw-gap-2.5 tw-bg-gray-50 dark:tw-bg-slate-700/50 tw-border tw-border-gray-200 dark:tw-border-slate-600 tw-rounded-lg tw-px-3 tw-py-2 tw-transition-colors focus-within:tw-border-blue-500/40 focus-within:tw-ring-2 focus-within:tw-ring-blue-500/10">
                  <span class="material-symbols-outlined tw-text-gray-400 dark:tw-text-slate-500 tw-text-[20px] tw-select-none">
                    search
                  </span>
                  <input
                    v-model="columnSearchQuery"
                    class="tw-flex-1 tw-bg-transparent tw-border-none tw-p-0 tw-text-sm tw-text-gray-800 dark:tw-text-slate-100 placeholder:tw-text-gray-500 dark:placeholder:tw-text-slate-600 focus:tw-ring-0 focus:tw-outline-none"
                    placeholder="Search columns..."
                    type="text"
                  />
                </div>
              </div>

              <!-- Scrollable Column List -->
              <div class="tw-flex-1 tw-overflow-y-auto tw-max-h-[360px] tw-p-2 tw-bg-white dark:tw-bg-slate-800 column-scrollbar">
                <label
                  v-for="column in filteredColumnsList"
                  :key="column.key"
                  class="tw-flex tw-items-center tw-gap-3 tw-px-3 tw-py-2.5 tw-rounded-lg hover:tw-bg-gray-50 dark:hover:tw-bg-slate-700 tw-cursor-pointer tw-transition-colors tw-group tw-select-none"
                >
                  <input
                    type="checkbox"
                    v-model="visibleColumns[column.key]"
                    class="custom-checkbox tw-focus:tw-ring-0 tw-focus:tw-ring-offset-0"
                  />
                  <span class="tw-text-sm tw-font-medium tw-text-gray-700 dark:tw-text-slate-300 group-hover:tw-text-gray-900 dark:group-hover:tw-text-slate-100 tw-transition-colors">{{ column.label }}</span>
                </label>
              </div>

              <!-- Footer Actions -->
              <div class="tw-px-4 tw-py-3 tw-border-t tw-border-gray-200/50 dark:tw-border-slate-700 tw-bg-white dark:tw-bg-slate-800 tw-flex tw-items-center tw-justify-between tw-gap-3">
                <button
                  @click="showAllColumns"
                  class="tw-flex-1 tw-px-3 tw-py-2 tw-rounded-lg tw-text-xs tw-font-semibold tw-text-blue-600 dark:tw-text-blue-400 hover:tw-bg-blue-50 dark:hover:tw-bg-blue-900/20 hover:tw-text-blue-700 dark:hover:tw-text-blue-300 tw-transition-colors tw-border tw-border-transparent focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-blue-500/20"
                >
                  Select All
                </button>
                <div class="tw-h-4 tw-w-[1px] tw-bg-gray-200 dark:tw-bg-slate-700"></div>
                <button
                  @click="hideAllColumns"
                  class="tw-flex-1 tw-px-3 tw-py-2 tw-rounded-lg tw-text-xs tw-font-semibold tw-text-gray-500 dark:tw-text-slate-400 hover:tw-text-gray-700 dark:hover:tw-text-slate-300 hover:tw-bg-gray-50 dark:hover:tw-bg-slate-700 tw-transition-colors focus:tw-outline-none focus:tw-ring-2 focus:tw-ring-gray-200 dark:focus:tw-ring-slate-600"
                >
                  Reset to Default
                </button>
              </div>
            </div>
            </Transition>
          </Teleport>
        </div>

        <div v-if="currentTab !== 'Delivered'" class="tw-hidden sm:tw-block tw-w-px tw-h-6 tw-bg-slate-200 tw-mx-2"></div>
        <CwDropdown
          v-if="currentTab !== 'Delivered'"
          label="Actions"
          icon="bolt"
          button-variant="primary"
          title="Workflow Actions"
          :items="actionItems"
          :disabled="selectedRows.length === 0"
          @select="handleAction"
          class="tw-w-full sm:tw-w-auto"
        />
      </div>
    </div>

    <!-- Table Container with flex-1 to fill remaining space -->
    <div class="tw-flex-1 tw-min-h-0 tw-relative">
      <!-- Loading Overlay -->
      <div
        v-if="isLoading"
        class="tw-absolute tw-inset-0 tw-bg-white/70 dark:tw-bg-slate-900/40 tw-z-10 tw-flex tw-items-center tw-justify-center"
      >
        <div class="tw-flex tw-flex-col tw-items-center tw-gap-2">
          <span class="material-symbols-outlined tw-text-3xl tw-text-primary-600 tw-animate-spin">
            progress_activity
          </span>
          <span class="tw-text-sm tw-text-slate-500">Loading...</span>
        </div>
      </div>

      <CwTable
        :columns="filteredColumns"
        :data="filteredData"
        row-key="id"
        selectable
        has-actions
        show-pagination
        v-model:selected="selectedRows"
        :total-items="totalItems"
        :current-page="currentPage"
        :page-size="pageSize"
        :sort-key="sortKey"
        :sort-order="sortOrder"
        @row-click="handleRowClick"
        @row-dblclick="handleRowDblClick"
        @page-change="handlePageChange"
        @page-size-change="handlePageSizeChange"
        @sort-change="handleSortChange"
        @action-click="handleRowAction"
      >
      <!-- Custom cell slots -->
      <template #cell-customer="{ row, value }">
        <button
          class="tw-font-semibold tw-text-slate-700 dark:tw-text-slate-200 hover:tw-text-primary-600 dark:hover:tw-text-primary-400 hover:tw-underline tw-text-left tw-transition-colors"
          @click.stop="openSalesOrder(row)"
        >
          {{ value }}
        </button>
      </template>

      <template #cell-karigar="{ row }">
        <div v-if="row.karigar" class="tw-flex tw-items-center tw-gap-2">
          <CwAvatar :name="row.karigar.name" size="sm" :color="getKarigarColor(row.karigar.color)" />
          <span class="tw-text-slate-700 dark:tw-text-slate-200">{{ row.karigar.name }}</span>
        </div>
        <CwBadge v-else variant="unassigned">Unassigned</CwBadge>
      </template>

      <template #cell-item_code="{ value }">
        <span class="tw-font-mono tw-text-slate-500 dark:tw-text-slate-400">{{ value }}</span>
      </template>

      <template #cell-status="{ row }">
        <span
          class="status-btn cw-badge tw-inline-flex tw-items-center tw-px-2.5 tw-py-0.5 tw-rounded-full tw-text-xs tw-font-medium tw-transition-all tw-border"
          :class="getStatusClass(row.status)"
        >
          <span class="status-dot tw-w-1.5 tw-h-1.5 tw-rounded-full tw-mr-1.5" :class="getStatusDotClass(row.status)"></span>
          {{ row.status }}
        </span>
      </template>

      <template #cell-sales_order="{ row }">
        <a
          :href="`/app/sales-order/${row.sales_order}`"
          class="tw-text-primary-600 hover:tw-text-primary-800 hover:tw-underline"
          @click.stop
        >
          {{ row.sales_order }}
        </a>
      </template>

      <template #cell-qty="{ value }">
        <span class="tw-font-semibold tw-text-slate-900 dark:tw-text-slate-100">{{ value }}</span>
      </template>

      <template #actions="{ row }">
        <CwDropdown
          align="right"
          :items="rowActionItems"
          @select="(item) => handleRowActionSelect(row, item)"
        >
          <template #trigger>
            <button class="tw-p-1.5 tw-rounded-lg tw-text-slate-400 hover:tw-text-slate-700 hover:tw-bg-slate-100 dark:hover:tw-bg-slate-700/60 dark:hover:tw-text-slate-200 tw-transition-colors">
              <span class="material-symbols-outlined">more_horiz</span>
            </button>
          </template>
        </CwDropdown>
      </template>
    </CwTable>
    </div>

    <!-- Status menu -->
    <Teleport to="body">
      <div v-if="statusMenuVisible" class="tw-fixed tw-inset-0 tw-z-40" @click="closeStatusMenu"></div>
      <div
        v-if="statusMenuVisible"
        class="tw-fixed tw-z-50 tw-bg-white dark:tw-bg-slate-800 tw-rounded-lg tw-shadow-dropdown tw-border tw-border-slate-200 dark:tw-border-slate-700 tw-py-1 tw-min-w-[170px]"
        :style="statusMenuStyle"
        role="menu"
      >
        <button
          v-for="tab in tabs"
          :key="tab.name"
          class="tw-w-full tw-flex tw-items-center tw-gap-2 tw-px-3 tw-py-2 tw-text-sm tw-text-left tw-text-slate-700 dark:tw-text-slate-200 hover:tw-bg-slate-50 dark:hover:tw-bg-slate-700/40 tw-transition-colors"
          :class="{ 'tw-bg-slate-50 dark:tw-bg-slate-700/30': statusMenuRow?.status === tab.name }"
          @click="changeStatus(tab.name)"
          role="menuitem"
        >
          <span class="tw-w-2 tw-h-2 tw-rounded-full" :class="getStatusDotClass(tab.name)"></span>
          {{ tab.name }}
        </button>
      </div>
    </Teleport>

    <!-- Order Item Details Modal -->
    <CwOrderItemModal
      v-model="showOrderModal"
      :order-data="selectedOrderData"
      :transition-type="selectedOrderData.transitionType || 'received'"
      :frappe="props.frappe"
      @save="handleModalSave"
    />

    <!-- Advanced Split Modal (New) -->
    <CwAdvancedSplitModal
      v-model="showAdvancedSplitModal"
      :selected-orders="selectedRows"
      :frappe="props.frappe"
      @refresh="handleSplitRefresh"
    />

    <!-- Bulk Weight Modal -->
    <CwBulkWeightModal
      v-model="showBulkWeightModal"
      :selected-count="selectedRows.length"
      :selected-orders="selectedRows"
      :frappe="props.frappe"
      @apply="handleBulkWeightApply"
    />

    <!-- Transition Modal -->
    <CwTransitionModal
      v-model="showTransitionModal"
      :from-stage="transitionData.fromStage"
      :to-stage="transitionData.toStage"
      :item-count="transitionData.itemCount"
      @confirm="handleTransitionConfirm"
      @cancel="handleTransitionCancel"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, reactive, watch } from 'vue';
import CwTabs from './CwTabs.vue';
import CwTable from './CwTable.vue';
import CwButton from './CwButton.vue';
import CwDropdown from './CwDropdown.vue';
import CwBadge from './CwBadge.vue';
import CwAvatar from './CwAvatar.vue';
import CwOrderItemModal from './CwOrderItemModal.vue';
import CwAdvancedSplitModal from './CwAdvancedSplitModal.vue';
import CwBulkWeightModal from './CwBulkWeightModal.vue';
import CwTransitionModal from './CwTransitionModal.vue';
import { useWorkflowApi } from '../composables/useWorkflowApi.js';
import { logger } from '../utils/logger.js';
import { getKarigarColor, getStatusClass, getStatusDotClass } from '../utils/colors.js';

const props = defineProps({
  frappe: {
    type: Object,
    required: true
  }
});

// API Composable
const {
  isLoading,
  fetchWorkflowStages,
  fetchOrders,
  fetchStatusCounts,
  fetchFilterOptions,
  updateOrderStatus,
  splitOrder,
  setupRealtimeListener
} = useWorkflowApi();

// State
const currentTab = ref('');
const searchQuery = ref('');
const selectedRows = ref([]);
const currentPage = ref(1);
const pageSize = ref(50);
const sortKey = ref('');
const sortOrder = ref('asc');
const statusMenuVisible = ref(false);
const statusMenuRow = ref(null);
const statusMenuStyle = ref({});
const showOrderModal = ref(false);
const selectedOrderData = ref({});
const showSplitModal = ref(false);
const showAdvancedSplitModal = ref(false);
const isFiltersOpen = ref(false);
const isColumnsOpen = ref(false);
const filtersDropdownRef = ref(null);
const columnsDropdownRef = ref(null);
const columnSearchQuery = ref('');
// Reactive window size to trigger dropdown repositioning
const windowSize = ref({ width: window.innerWidth, height: window.innerHeight });
const visibleColumns = ref({
  sno: true,
  customer: true,
  po_no: true,
  karigar: true,
  item_code: true,
  item_details: true,
  description: true,
  texture: true,
  item_weight: true,
  qty: true,
  status: true,
  sales_order: true,
  id: true
});
const showBulkWeightModal = ref(false);
const showTransitionModal = ref(false);
const transitionData = reactive({
  fromStage: '',
  toStage: '',
  itemCount: 0,
  callback: null
});

// Workflow data
const workflowStages = ref([]);
const tabs = ref([]);

// Orders data
const orders = ref([]);
const pagination = reactive({
  total: 0,
  totalPages: 0
});

// Filters
const filters = reactive({
  customer: '',
  karigar: '',
  itemName: ''
});

const filterOptions = reactive({
  customers: [],
  karigars: [],
  itemNames: []
});

// Static columns definition
const columns = [
  { key: 'sno', label: 'S.No', width: '16', sortable: true, headerClass: 'tw-text-center', cellClass: 'tw-text-center tw-text-gray-500 dark:tw-text-gray-400 tw-font-mono' },
  { key: 'customer', label: 'Customer', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-font-semibold tw-text-slate-700 dark:tw-text-slate-200' },
  { key: 'po_no', label: 'PO No.', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-font-mono tw-text-gray-600 dark:tw-text-gray-400' },
  { key: 'karigar', label: 'Karigar', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-text-slate-600 dark:tw-text-slate-300' },
  { key: 'item_code', label: 'Item Code', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-font-mono tw-text-gray-500 dark:tw-text-gray-400' },
  { key: 'item_details', label: 'Item Details', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-text-slate-800 dark:tw-text-slate-200 tw-max-w-xs tw-truncate tw-font-medium' },
  { key: 'description', label: 'Description', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-text-gray-600 dark:tw-text-gray-400 tw-max-w-xs tw-truncate' },
  { key: 'texture', label: 'Texture', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-text-gray-500 dark:tw-text-gray-400' },
  { key: 'item_weight', label: 'Item Weight (g)', sortable: true, headerClass: 'tw-text-right', cellClass: 'tw-text-right tw-text-gray-600 dark:tw-text-gray-400 tw-font-mono' },
  { key: 'qty', label: 'Qty', width: '16', sortable: true, headerClass: 'tw-text-center', cellClass: 'tw-text-center tw-font-bold tw-text-slate-700 dark:tw-text-slate-300' },
  { key: 'status', label: 'Status', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left' },
  { key: 'sales_order', label: 'Sales Order', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-text-primary hover:tw-underline tw-cursor-pointer tw-font-medium' },
  { key: 'id', label: 'ID', sortable: true, headerClass: 'tw-text-left', cellClass: 'tw-text-left tw-font-mono tw-text-xs tw-text-gray-500 dark:tw-text-gray-400' }
];

const actionItems = [
  {
    label: 'Next Stage',
    value: 'next',
    icon: 'arrow_forward',
    iconBg: 'tw-bg-emerald-100',
    iconClass: 'tw-text-emerald-600',
    description: 'Move to next workflow stage'
  },
  {
    label: 'Previous Stage',
    value: 'previous',
    icon: 'arrow_back',
    iconBg: 'tw-bg-amber-100',
    iconClass: 'tw-text-amber-600',
    description: 'Move back to previous stage'
  },
  {
    label: 'Split',
    value: 'split',
    icon: 'call_split',
    iconBg: 'tw-bg-blue-100',
    iconClass: 'tw-text-blue-600',
    description: 'Split into multiple items'
  }
];

const rowActionItems = [
  { label: 'View Details', value: 'view', icon: 'visibility' },
  { label: 'Edit', value: 'edit', icon: 'edit' },
  { divider: true },
  { label: 'Delete', value: 'delete', icon: 'delete', danger: true }
];

// Data loading functions
async function initializeData() {
  try {
    // Load workflow stages from backend
    const stages = await fetchWorkflowStages();
    workflowStages.value = stages;

    // Initialize tabs with zero counts
    tabs.value = stages.map((name, idx) => ({
      name,
      count: 0,
      stage_number: idx + 1
    }));

    // Set first stage as current
    if (stages.length > 0) {
      currentTab.value = stages[0];
    }

    // Load filter options
    await loadFilterOptions();

    // Load initial data
    await loadOrders();
    await loadStatusCounts();
  } catch (error) {
    console.error('Error initializing data:', error);
    props.frappe.msgprint({
      title: 'Initialization Error',
      message: error.message || 'Failed to load workflow data',
      indicator: 'red'
    });
  }
}

async function loadOrders(resetPage = false) {
  if (resetPage) {
    currentPage.value = 1;
  }

  const response = await fetchOrders({
    page: currentPage.value,
    pageSize: pageSize.value,
    orderStatus: currentTab.value,
    search: searchQuery.value,
    customer: filters.customer,
    karigar: filters.karigar,
    itemName: filters.itemName,
    sortBy: sortKey.value,
    sortOrder: sortOrder.value
  });

  if (response) {
    orders.value = response.data || [];
    pagination.total = response.total || 0;
    pagination.totalPages = response.total_pages || 0;
  }
}

async function loadStatusCounts() {
  const counts = await fetchStatusCounts({
    search: searchQuery.value,
    customer: filters.customer,
    karigar: filters.karigar,
    itemName: filters.itemName
  });

  if (counts) {
    tabs.value.forEach(tab => {
      tab.count = counts[tab.name] || 0;
    });
  }
}

async function loadFilterOptions() {
  const options = await fetchFilterOptions();
  if (options) {
    filterOptions.customers = options.customers || [];
    filterOptions.karigars = options.karigars || [];
    filterOptions.itemNames = options.item_names || [];
  }
}

// Computed
const filteredData = computed(() => {
  return orders.value.map((order, idx) => ({
    // Row identifier
    id: order.name,
    // Visible table columns
    sno: String((currentPage.value - 1) * pageSize.value + idx + 1).padStart(2, '0'),
    customer: order.customer || 'N/A',
    po_no: order.po_no || 'N/A',
    karigar: order.karigar ? { name: order.karigar } : null,
    item_code: order.item_code || 'N/A',
    item_details: formatItemDisplay(order),
    description: order.description || 'N/A',
    texture: order.texture || 'N/A',
    item_weight: order.item_weight ? `${order.item_weight}` : 'N/A',
    qty: order.qty || 0,
    status: order.order_status,
    sales_order: order.sales_order,
    // Additional fields for modal and internal use
    karigar_received_weight: order.karigar_received_weight,
    dispatch_weight: order.dispatch_weight,
    images: order.images || [],
    item_group: order.item_group
  }));
});

const totalItems = computed(() => pagination.total);

const filteredColumns = computed(() => {
  return columns.filter(col => visibleColumns.value[col.key]);
});

const activeFiltersCount = computed(() => {
  let count = 0;
  if (filters.customer) count++;
  if (filters.karigar) count++;
  if (filters.itemName) count++;
  return count;
});

const filteredColumnsList = computed(() => {
  if (!columnSearchQuery.value) {
    return columns;
  }
  const query = columnSearchQuery.value.toLowerCase();
  return columns.filter(col => col.label.toLowerCase().includes(query));
});

// Helper functions
function showAllColumns() {
  Object.keys(visibleColumns.value).forEach(key => {
    visibleColumns.value[key] = true;
  });
}

function hideAllColumns() {
  Object.keys(visibleColumns.value).forEach(key => {
    visibleColumns.value[key] = false;
  });
}

function toggleFilters() {
  isFiltersOpen.value = !isFiltersOpen.value;
  if (isFiltersOpen.value) {
    isColumnsOpen.value = false;
  }
}

function closeFilters() {
  isFiltersOpen.value = false;
}

function toggleColumns() {
  isColumnsOpen.value = !isColumnsOpen.value;
  if (isColumnsOpen.value) {
    isFiltersOpen.value = false;
  }
}

function closeColumns() {
  isColumnsOpen.value = false;
}

// Computed styles for dropdown positioning
const filterDropdownStyle = computed(() => {
  // Use reactive windowSize to trigger recalculation on resize
  const viewportWidth = windowSize.value.width;
  const viewportHeight = windowSize.value.height;

  if (!filtersDropdownRef.value) return {};
  const rect = filtersDropdownRef.value.getBoundingClientRect();
  const isMobile = viewportWidth < 640;

  // Calculate available height below button with 16px margin from bottom
  const availableHeight = viewportHeight - rect.bottom - 24;
  const maxHeight = Math.min(availableHeight, isMobile ? 400 : viewportHeight * 0.8);

  if (isMobile) {
    // Full width on mobile with padding, capped at 400px
    return {
      top: `${rect.bottom + 8}px`,
      left: '16px',
      right: '16px',
      width: 'auto',
      maxWidth: '400px',
      maxHeight: `${maxHeight}px`,
    };
  }

  // Desktop: position below button, constrain to viewport
  const dropdownWidth = 400;
  let left = rect.left;
  if (left + dropdownWidth > viewportWidth - 16) {
    left = viewportWidth - dropdownWidth - 16;
  }

  return {
    top: `${rect.bottom + 8}px`,
    left: `${Math.max(16, left)}px`,
    width: `${dropdownWidth}px`,
  };
});

const columnDropdownStyle = computed(() => {
  // Use reactive windowSize to trigger recalculation on resize
  const viewportWidth = windowSize.value.width;
  const viewportHeight = windowSize.value.height;

  if (!columnsDropdownRef.value) return {};
  const rect = columnsDropdownRef.value.getBoundingClientRect();
  const isMobile = viewportWidth < 640;

  // Calculate available height below button with 16px margin from bottom
  const availableHeight = viewportHeight - rect.bottom - 24;
  const maxHeight = Math.min(availableHeight, isMobile ? 400 : viewportHeight * 0.8);

  if (isMobile) {
    // Full width on mobile with padding, capped at 360px
    return {
      top: `${rect.bottom + 8}px`,
      left: '16px',
      right: '16px',
      width: 'auto',
      maxWidth: '360px',
      maxHeight: `${maxHeight}px`,
    };
  }

  // Desktop: right-align to button, constrain to viewport
  const dropdownWidth = 360;
  let left = rect.right - dropdownWidth;
  if (left < 16) {
    left = 16;
  }

  return {
    top: `${rect.bottom + 8}px`,
    left: `${left}px`,
    width: `${dropdownWidth}px`,
  };
});

function handlePageSizeChange(newSize) {
  pageSize.value = newSize;
  currentPage.value = 1;
  loadOrders();
}

// Helper functions
function formatItemDisplay(order) {
  const itemCode = order.item_code || '';
  const itemName = order.item_name || '';
  if (!itemCode) return 'N/A';
  if (!itemName) return itemCode;
  return `${itemCode}-${itemName}`;
}

function getStageInfo() {
  const stages = workflowStages.value;
  const currentIndex = stages.indexOf(currentTab.value);
  return {
    current: currentTab.value,
    currentIndex,
    prev: currentIndex > 0 ? stages[currentIndex - 1] : null,
    prevIndex: currentIndex > 0 ? currentIndex - 1 : -1,
    next: currentIndex < stages.length - 1 ? stages[currentIndex + 1] : null,
    nextIndex: currentIndex < stages.length - 1 ? currentIndex + 1 : -1,
    isFirst: currentIndex === 0,
    isLast: currentIndex === stages.length - 1
  };
}

function requiresWeightEntry(fromStage, toStage) {
  // Incoming to Internal QA
  if (fromStage === 'Incoming' && toStage === 'Internal QA') return true;
  // Pending Delivery to Delivered
  if (fromStage === 'Pending Delivery' && toStage === 'Delivered') return true;
  return false;
}

function getWeightType(fromStage, toStage) {
  if (fromStage === 'Incoming' && toStage === 'Internal QA') return 'received';
  if (fromStage === 'Pending Delivery' && toStage === 'Delivered') return 'dispatch';
  return null;
}

function needsRevertTimestamp(fromStage, toStage) {
  // Internal QA to Incoming
  return fromStage === 'Internal QA' && toStage === 'Incoming';
}

// Watch for tab changes
watch(currentTab, () => {
  // Clear selections when switching tabs
  selectedRows.value = [];
  loadOrders(true);
});

// Watch for filter changes
watch([() => filters.customer, () => filters.karigar, () => filters.itemName], () => {
  // Clear selections when filters change
  selectedRows.value = [];
  loadOrders(true);
  loadStatusCounts();
});

// Debounce search to prevent excessive API calls (reduced for faster search-as-you-type)
const searchDebounceTimeout = ref(null);
const SEARCH_DEBOUNCE_MS = 250;

// Methods
const handleSearch = () => {
  // Clear any pending debounce
  if (searchDebounceTimeout.value) {
    clearTimeout(searchDebounceTimeout.value);
  }

  // Debounce the search
  searchDebounceTimeout.value = setTimeout(() => {
    // Clear selections when searching
    selectedRows.value = [];
    loadOrders(true);
    loadStatusCounts();
    searchDebounceTimeout.value = null;
  }, SEARCH_DEBOUNCE_MS);
};

const applyFilters = () => {
  // Filters are already watched, so just close the dropdown
  closeFilters();
};

const clearFilters = () => {
  filters.customer = '';
  filters.karigar = '';
  filters.itemName = '';
};

const handleAction = async (item) => {
  if (selectedRows.value.length === 0) {
    props.frappe.msgprint({
      title: 'No Items Selected',
      message: 'Please select at least one item to perform this action',
      indicator: 'red'
    });
    return;
  }

  const stageInfo = getStageInfo();

  if (item.value === 'next') {
    if (!stageInfo.next) {
      props.frappe.msgprint({
        title: 'End of Workflow',
        message: 'Already at the final stage',
        indicator: 'orange'
      });
      return;
    }

    const needsWeight = requiresWeightEntry(stageInfo.current, stageInfo.next);

    if (needsWeight) {
      // Check if multiple items are selected
      if (selectedRows.value.length > 1) {
        // Open bulk weight modal for multiple selections
        showBulkWeightModal.value = true;
      } else {
        // Open single weight entry modal for one selection
        const transitionType = getWeightType(stageInfo.current, stageInfo.next);
        selectedOrderData.value = {
          ...selectedRows.value[0],
          transitionType: transitionType,
          targetStage: stageInfo.next
        };
        showOrderModal.value = true;
      }
    } else {
      // Show transition modal for confirmation
      transitionData.fromStage = stageInfo.current;
      transitionData.toStage = stageInfo.next;
      transitionData.itemCount = selectedRows.value.length;
      transitionData.callback = async () => {
        const itemNames = selectedRows.value.map(r => r.id);
        const results = await updateOrderStatus(itemNames, stageInfo.next);

        if (results && results.length > 0) {
          const successCount = results.filter(r => r.success).length;
          props.frappe.show_alert({
            message: `${successCount} item(s) moved to ${stageInfo.next}`,
            indicator: 'green'
          });
          await loadOrders();
          await loadStatusCounts();
          selectedRows.value = [];
        }
      };
      showTransitionModal.value = true;
    }
  } else if (item.value === 'previous') {
    if (!stageInfo.prev) {
      props.frappe.msgprint({
        title: 'Start of Workflow',
        message: 'Already at the first stage',
        indicator: 'orange'
      });
      return;
    }

    // Show transition modal for confirmation
    transitionData.fromStage = stageInfo.current;
    transitionData.toStage = stageInfo.prev;
    transitionData.itemCount = selectedRows.value.length;
    transitionData.callback = async () => {
      const itemNames = selectedRows.value.map(r => r.id);
      const extraArgs = {};

      if (needsRevertTimestamp(stageInfo.current, stageInfo.prev)) {
        extraArgs.received_to_incoming = props.frappe.datetime.now_datetime();
      }

      const results = await updateOrderStatus(itemNames, stageInfo.prev, extraArgs);

      if (results && results.length > 0) {
        const successCount = results.filter(r => r.success).length;
        props.frappe.show_alert({
          message: `${successCount} item(s) moved to ${stageInfo.prev}`,
          indicator: 'green'
        });
        await loadOrders();
        await loadStatusCounts();
        selectedRows.value = [];
      }
    };
    showTransitionModal.value = true;
  } else if (item.value === 'split') {
    // Use advanced split modal for better UX
    showAdvancedSplitModal.value = true;
  }
};

const handleRowClick = (row) => {
  logger.debug('Row clicked:', row.id);
};

const handleRowDblClick = (row) => {
  // Double-click now toggles checkbox in CwTable, this handler is kept for compatibility
  logger.debug('Row double-clicked:', row.id);
};

// Opens the next stage workflow (called when clicking customer name)
const openSalesOrder = async (row) => {
  const stageInfo = getStageInfo();

  if (!stageInfo.next) {
    props.frappe.msgprint({
      title: 'End of Workflow',
      message: 'Already at the final stage',
      indicator: 'orange'
    });
    return;
  }

  const needsWeight = requiresWeightEntry(stageInfo.current, stageInfo.next);

  if (needsWeight) {
    // Open single weight entry modal for this item
    const transitionType = getWeightType(stageInfo.current, stageInfo.next);
    selectedOrderData.value = {
      ...row,
      transitionType: transitionType,
      targetStage: stageInfo.next
    };
    showOrderModal.value = true;
  } else {
    // Show transition modal for confirmation
    transitionData.fromStage = stageInfo.current;
    transitionData.toStage = stageInfo.next;
    transitionData.itemCount = 1;
    transitionData.callback = async () => {
      const results = await updateOrderStatus([row.id], stageInfo.next);

      if (results && results.length > 0 && results[0].success) {
        props.frappe.show_alert({
          message: `Item moved to ${stageInfo.next}`,
          indicator: 'green'
        });
        await loadOrders();
        await loadStatusCounts();
      }
    };
    showTransitionModal.value = true;
  }
};

const handleRowAction = (row) => {
  logger.debug('Row action:', row.id);
};

const handleRowActionSelect = (row, item) => {
  if (item.value === 'view') {
    props.frappe.set_route('Form', 'Sales Order', row.sales_order);
  } else if (item.value === 'edit') {
    props.frappe.set_route('Form', 'Sales Order', row.sales_order);
  } else if (item.value === 'delete') {
    props.frappe.confirm(
      'Are you sure you want to delete this item?',
      () => {
        props.frappe.msgprint({
          title: 'Deleted',
          message: 'Item deleted successfully',
          indicator: 'green'
        });
      }
    );
  }
};

const handlePageChange = (page) => {
  currentPage.value = page;
  loadOrders();
};

const handleSortChange = ({ key, order }) => {
  sortKey.value = key;
  sortOrder.value = order;
  loadOrders(true);
};


const showStatusMenu = (row, event) => {
  statusMenuRow.value = row;
  const rect = (event.currentTarget || event.target).getBoundingClientRect();
  statusMenuStyle.value = {
    top: `${rect.bottom + 4}px`,
    left: `${rect.left}px`
  };
  statusMenuVisible.value = true;
};

const closeStatusMenu = () => {
  statusMenuVisible.value = false;
  statusMenuRow.value = null;
};

const changeStatus = async (newStatus) => {
  if (statusMenuRow.value) {
    const oldStatus = statusMenuRow.value.status;

    // Show transition modal for confirmation
    transitionData.fromStage = oldStatus;
    transitionData.toStage = newStatus;
    transitionData.itemCount = 1;
    transitionData.callback = async () => {
      const results = await updateOrderStatus([statusMenuRow.value.id], newStatus);

      if (results && results.length > 0 && results[0].success) {
        props.frappe.show_alert({
          message: `Item moved to ${newStatus}`,
          indicator: 'green'
        });
        await loadOrders();
        await loadStatusCounts();
      }
    };
    showTransitionModal.value = true;
  }
  closeStatusMenu();
};

// Status and color functions are now imported from utils/colors.js
// getStatusClass, getStatusDotClass, and getKarigarColor are available via imports

const handleModalSave = async (data) => {
  const stageInfo = getStageInfo();
  const itemNames = selectedRows.value.length > 0
    ? selectedRows.value.map(r => r.id)
    : (data?.orderId ? [data.orderId] : []);
  const transitionType = data.transitionType || 'received';

  if (itemNames.length === 0) {
    props.frappe.msgprint({
      title: 'No Items Selected',
      message: 'Please select an item (or open an item) before saving.',
      indicator: 'red'
    });
    showOrderModal.value = false;
    return;
  }

  if (!stageInfo.next) {
    props.frappe.msgprint({
      title: 'End of Workflow',
      message: 'No next stage available for this item.',
      indicator: 'orange'
    });
    showOrderModal.value = false;
    return;
  }

  const parsedWeight = parseFloat(data.grossWeight);
  if (!isFinite(parsedWeight) || parsedWeight <= 0 || parsedWeight > 999999) {
    props.frappe.msgprint({
      title: 'Invalid Weight',
      message: parsedWeight > 999999
        ? 'Weight cannot exceed 999,999g (999kg). Please enter a valid weight.'
        : 'Please enter a valid weight greater than 0.',
      indicator: 'red'
    });
    return;
  }

  const extraArgs = {};

  if (transitionType === 'received') {
    // Incoming to Internal QA
    const weight = parsedWeight;
    extraArgs.karigar_received_weight = weight;
    extraArgs.receive_notes = data.remarks || '';
  } else if (transitionType === 'dispatch') {
    // Pending Delivery to Delivered
    const weight = parsedWeight;
    extraArgs.dispatch_weight = weight;
    extraArgs.qa_notes = data.remarks || '';
  }

  const results = await updateOrderStatus(itemNames, stageInfo.next, extraArgs);

  if (results && results.length > 0) {
    const successCount = results.filter(r => r.success).length;
    const failureCount = results.filter(r => !r.success).length;

    if (successCount > 0) {
      props.frappe.show_alert({
        message: `${successCount} item(s) moved to ${stageInfo.next} with weight ${parsedWeight.toFixed(2)}g`,
        indicator: 'green'
      });

      // Reload data
      await loadOrders();
      await loadStatusCounts();

      // Clear selection and switch to target tab
      selectedRows.value = [];
      currentTab.value = stageInfo.next;
    }

    if (failureCount > 0) {
      const failedItems = results.filter(r => !r.success);
      const errorMessages = failedItems.map(r => r.error || 'Unknown error').join(', ');

      props.frappe.msgprint({
        title: `Failed to Update ${failureCount} Item(s)`,
        message: errorMessages.length > 200
          ? `${errorMessages.substring(0, 200)}... (${failureCount} items failed)`
          : errorMessages,
        indicator: 'red'
      });
    }
  } else {
    props.frappe.msgprint({
      title: 'Update Failed',
      message: 'No items were updated. Please try again or contact support.',
      indicator: 'red'
    });
  }

  showOrderModal.value = false;
};

const handleSplitComplete = async (data) => {
  const result = await splitOrder(data.itemName, data.splitQty);

  if (result && result.success) {
    props.frappe.show_alert({
      message: result.message || `Successfully split order: ${data.splitQty} qty kept, ${data.remainingQty} qty in new entry`,
      indicator: 'green'
    });

    // Reload data
    await loadOrders();
    await loadStatusCounts();

    // Clear selection
    selectedRows.value = [];
  }

  showSplitModal.value = false;
};

const handleBulkWeightApply = async (data) => {
  const stageInfo = getStageInfo();
  const itemNames = selectedRows.value.map(r => r.id);
  const transitionType = getWeightType(stageInfo.current, stageInfo.next);

  // Determine which weight field to use based on transition type
  const weightField = transitionType === 'received' ? 'karigar_received_weight' : 'dispatch_weight';

  // Prepare extra arguments for bulk update
  const extraArgs = {
    weight_per_unit: data.weightPerUnit,
    weight_field: weightField
  };

  // If dispatch transition, also include dispatch_notes field name for consistency
  if (transitionType === 'dispatch') {
    extraArgs.qa_notes = ''; // Optional bulk notes field
  } else if (transitionType === 'received') {
    extraArgs.receive_notes = ''; // Optional bulk notes field
  }

  const results = await updateOrderStatus(itemNames, stageInfo.next, extraArgs);

  if (results && results.length > 0) {
    const successCount = results.filter(r => r.success).length;
    const weight = parseFloat(data.totalWeight);
    const totalWeightGrams = isNaN(weight) ? '0' : weight.toFixed(2);

    props.frappe.show_alert({
      message: `${successCount} item(s) moved to ${stageInfo.next} with total weight ${totalWeightGrams}g distributed proportionally`,
      indicator: 'green'
    });

    // Reload data
    await loadOrders();
    await loadStatusCounts();

    // Clear selection and switch to target tab
    selectedRows.value = [];
    currentTab.value = stageInfo.next;
  }

  showBulkWeightModal.value = false;
};

const handleSplitRefresh = async () => {
  // Modal already handles the split API calls
  // Just reload data and clear selection
  await loadOrders();
  await loadStatusCounts();

  // Clear selection
  selectedRows.value = [];

  showAdvancedSplitModal.value = false;
};

// Transition modal handlers
const handleTransitionConfirm = async () => {
  if (transitionData.callback) {
    await transitionData.callback();
  }
  showTransitionModal.value = false;
};

const handleTransitionCancel = () => {
  showTransitionModal.value = false;
};

// Lifecycle hooks
let realtimeCleanup = null;

// Update window size on resize to trigger dropdown repositioning
const handleResize = () => {
  windowSize.value = { width: window.innerWidth, height: window.innerHeight };
};

onMounted(async () => {
  await initializeData();

  // Setup real-time listener
  realtimeCleanup = setupRealtimeListener(() => {
    props.frappe.show_alert({
      message: 'Status updated successfully',
      indicator: 'green'
    });
    loadOrders();
    loadStatusCounts();
  });

  // Add resize listener
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  if (realtimeCleanup) {
    realtimeCleanup();
  }

  // Remove resize listener
  window.removeEventListener('resize', handleResize);

  // Clear search debounce timeout
  if (searchDebounceTimeout.value) {
    clearTimeout(searchDebounceTimeout.value);
    searchDebounceTimeout.value = null;
  }
});
</script>

<style scoped>
/* Custom scrollbar for column list */
.column-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.column-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.column-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(0, 0, 0, 0.1);
  border-radius: 20px;
}

.column-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(0, 0, 0, 0.15);
}

/* Custom checkbox styling */
.custom-checkbox {
  appearance: none;
  background-color: white;
  margin: 0;
  font: inherit;
  width: 1.15em;
  height: 1.15em;
  border: 1.5px solid #d1d5db;
  border-radius: 0.25em;
  display: grid;
  place-content: center;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.custom-checkbox::before {
  content: "";
  width: 0.65em;
  height: 0.65em;
  transform: scale(0);
  transition: 120ms transform ease-in-out;
  box-shadow: inset 1em 1em white;
  transform-origin: center;
  clip-path: polygon(14% 44%, 0 65%, 50% 100%, 100% 16%, 80% 0%, 43% 62%);
}

.custom-checkbox:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.custom-checkbox:checked::before {
  transform: scale(1);
}

.custom-checkbox:focus {
  outline: 2px solid #3b82f6;
  outline-offset: 2px;
}

.group:hover .custom-checkbox:not(:checked) {
  border-color: #9ca3af;
}

/* Custom select styling for filters */
.filter-select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
}

.filter-select option {
  background-color: white;
  color: #1e293b;
  padding: 8px;
}
</style>
