<template>
  <Teleport to="body">
    <!-- Modal Backdrop -->
    <div
      v-if="modelValue"
      aria-hidden="true"
      class="tw-fixed tw-inset-0 tw-bg-gray-900/50 dark:tw-bg-black/70 tw-backdrop-blur-sm tw-z-[9998] tw-transition-opacity tw-hidden xl:tw-block"
    ></div>

    <!-- Modal Container -->
    <div
      v-if="modelValue"
      class="tw-fixed tw-inset-0 tw-z-[9999] tw-flex tw-items-center tw-justify-center tw-p-0 xl:tw-p-4"
    >
      <Transition
        enter-active-class="tw-transition-all tw-duration-300"
        enter-from-class="tw-opacity-0 tw-scale-95"
        enter-to-class="tw-opacity-100 tw-scale-100"
        leave-active-class="tw-transition-all tw-duration-300"
        leave-from-class="tw-opacity-100 tw-scale-100"
        leave-to-class="tw-opacity-0 tw-scale-95"
      >
        <div
          v-if="modelValue"
          class="tw-relative tw-z-[9999] tw-w-full tw-h-[100dvh]
                 xl:tw-max-w-7xl xl:tw-h-[700px]
                 tw-bg-white dark:tw-bg-[#1F2937]
                 xl:tw-rounded-xl
                 tw-shadow-none xl:tw-shadow-2xl
                 tw-overflow-hidden
                 tw-flex tw-flex-col
                 xl:tw-flex-row
                 tw-transition-colors tw-duration-300"
        >

          <!-- Desktop Order Queue Sidebar (Only for xl and above) -->
          <div class="tw-hidden xl:tw-flex tw-w-64 tw-bg-gray-50 dark:tw-bg-gray-900 tw-border-r tw-border-gray-200 dark:tw-border-gray-700 tw-flex-col tw-h-full tw-z-10 tw-flex-shrink-0">
            <div class="tw-p-6 tw-border-b tw-border-gray-200 dark:tw-border-gray-700 tw-bg-gray-50/50 dark:tw-bg-gray-900/50 tw-backdrop-blur-sm tw-sticky tw-top-0">
              <h2 class="tw-text-xs tw-font-bold tw-uppercase tw-tracking-wider tw-text-gray-500 dark:tw-text-gray-400 tw-font-display tw-mb-1">Order Queue</h2>
              <p class="tw-text-sm tw-font-medium tw-text-gray-900 dark:tw-text-white tw-flex tw-items-center tw-gap-2">
                <span class="material-symbols-outlined tw-text-base">format_list_bulleted</span>
                {{ selectedOrders.length }} Selected
              </p>
            </div>
            <div class="tw-flex-1 tw-overflow-y-auto custom-scrollbar tw-p-3 tw-space-y-2">
              <div v-for="(order, index) in selectedOrders" :key="order.id">
                <!-- Completed -->
                <div v-if="index < currentOrderIndex" class="tw-flex tw-items-center tw-justify-between tw-p-3 tw-rounded-lg tw-opacity-50 hover:tw-opacity-80 tw-transition-opacity">
                  <div>
                    <span class="tw-block tw-text-xs tw-font-bold tw-text-gray-600 dark:tw-text-gray-400 tw-line-through">{{ order.id }}</span>
                    <span class="tw-block tw-text-sm tw-text-gray-500 tw-font-mono">{{ formatWeight(getOrderWeight(order)) }}g</span>
                  </div>
                  <span class="material-symbols-outlined tw-text-green-500 tw-text-lg">check_circle</span>
                </div>
                <!-- Current -->
                <div v-else-if="index === currentOrderIndex" class="tw-relative tw-group tw-cursor-default">
                  <div class="tw-absolute tw-inset-0 tw-bg-white dark:tw-bg-gray-800 tw-shadow-md tw-border-l-[3px] tw-border-[#0066b3] tw-rounded-r-lg tw-transform tw-scale-[1.02] tw-transition-transform"></div>
                  <div class="tw-relative tw-p-3 tw-pl-4 tw-flex tw-items-center tw-justify-between">
                    <div>
                      <span class="tw-flex tw-items-center tw-gap-2 tw-text-xs tw-font-bold tw-text-[#0066b3] dark:tw-text-blue-400">
                        {{ order.id }}
                        <span class="tw-w-1.5 tw-h-1.5 tw-rounded-full tw-bg-[#0066b3] tw-animate-pulse"></span>
                      </span>
                      <span class="tw-block tw-text-sm tw-font-bold tw-text-gray-900 dark:tw-text-white tw-font-mono tw-mt-0.5">{{ formatWeight(getOrderWeight(order)) }}g</span>
                    </div>
                    <span class="material-symbols-outlined tw-text-[#0066b3] tw-text-xl">arrow_right</span>
                  </div>
                </div>
                <!-- Pending -->
                <button v-else class="tw-w-full tw-text-left tw-flex tw-items-center tw-justify-between tw-p-3 tw-pl-4 tw-rounded-lg hover:tw-bg-white dark:hover:tw-bg-gray-800 tw-border tw-border-transparent hover:tw-border-gray-200 dark:hover:tw-border-gray-700 tw-transition-all tw-group">
                  <div>
                    <span class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 group-hover:tw-text-gray-800 dark:group-hover:tw-text-gray-200">{{ order.id }}</span>
                    <span class="tw-block tw-text-sm tw-text-gray-500 dark:tw-text-gray-400 tw-font-mono">{{ formatWeight(getOrderWeight(order)) }}g</span>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <!-- Mobile Header (Only for mobile/tablet) -->
          <div class="xl:tw-hidden tw-flex-none tw-z-30 tw-bg-white dark:tw-bg-[#1F2937] tw-border-b tw-border-gray-200 dark:tw-border-gray-700 tw-shadow-sm">
            <div class="tw-flex tw-items-center tw-justify-between tw-px-4 tw-py-3">
              <div class="tw-flex tw-items-center tw-gap-3">
                <button @click="closeModal" class="tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-700 dark:hover:tw-text-gray-300 tw-transition-colors">
                  <span class="material-symbols-outlined">arrow_back</span>
                </button>
                <div>
                  <div class="tw-flex tw-items-center tw-gap-2">
                    <span class="tw-text-sm tw-font-bold tw-text-gray-900 dark:tw-text-white tw-font-display">Order {{ currentOrder.id }}</span>
                    <span class="tw-inline-flex tw-items-center tw-px-2 tw-py-0.5 tw-rounded-full tw-text-[10px] tw-font-bold tw-bg-[#0066b3]/10 tw-text-[#0066b3] dark:tw-bg-blue-900/30 dark:tw-text-blue-300">
                      {{ currentOrderIndex + 1 }} of {{ selectedOrders.length }}
                    </span>
                  </div>
                </div>
              </div>
              <button @click="closeModal" class="tw-text-gray-400 hover:tw-text-gray-600 dark:hover:tw-text-gray-300 tw-transition-colors">
                <span class="material-symbols-outlined">more_vert</span>
              </button>
            </div>

            <!-- Mobile Order Chips -->
            <div class="tw-flex tw-overflow-x-auto tw-gap-2 tw-px-4 tw-pb-3 no-scrollbar tw-items-center">
              <div
                v-for="(order, index) in selectedOrders"
                :key="order.id"
                class="tw-flex-shrink-0"
              >
                <!-- Completed order chip -->
                <div
                  v-if="index < currentOrderIndex"
                  class="tw-flex tw-items-center tw-justify-center tw-w-8 tw-h-8 tw-rounded-full tw-bg-green-50 dark:tw-bg-green-900/20 tw-text-green-600 dark:tw-text-green-400 tw-border tw-border-green-200 dark:tw-border-green-800 tw-text-xs tw-font-bold"
                >
                  <span class="material-symbols-outlined tw-text-sm">check</span>
                </div>
                <!-- Current order chip -->
                <div
                  v-else-if="index === currentOrderIndex"
                  class="tw-px-3 tw-py-1.5 tw-rounded-full tw-bg-[#0066b3] tw-text-white tw-text-xs tw-font-bold tw-shadow-md tw-shadow-blue-500/20 tw-whitespace-nowrap tw-border tw-border-[#0066b3]"
                >
                  {{ order.id }} • {{ formatWeight(getOrderWeight(order)) }}g
                </div>
                <!-- Pending order chip -->
                <button
                  v-else
                  @click="currentOrderIndex = index"
                  class="tw-px-3 tw-py-1.5 tw-rounded-full tw-bg-gray-50 dark:tw-bg-gray-800 tw-text-gray-600 dark:tw-text-gray-300 tw-border tw-border-gray-200 dark:tw-border-gray-700 tw-text-xs tw-font-medium tw-whitespace-nowrap hover:tw-border-[#0066b3] hover:tw-text-[#0066b3] dark:hover:tw-text-blue-400 tw-transition-colors"
                >
                  {{ order.id }} • {{ formatWeight(getOrderWeight(order)) }}g
                </button>
              </div>
            </div>
          </div>

          <!-- Main Content Wrapper -->
          <div class="tw-flex-1 tw-flex tw-flex-col xl:tw-flex-row tw-h-full tw-overflow-y-auto xl:tw-overflow-hidden tw-relative custom-scrollbar scroll-smooth">

            <!-- Current Order Info Panel -->
            <div class="tw-w-full xl:tw-w-80 tw-bg-[#F9FAFB] dark:tw-bg-[#161e2e] xl:tw-border-r tw-border-gray-200 dark:tw-border-gray-700 tw-flex tw-flex-col xl:tw-h-full tw-relative tw-overflow-hidden tw-flex-shrink-0">
              <div class="tw-absolute tw-top-0 tw-left-0 tw-w-full tw-h-48 tw-bg-gradient-to-b tw-from-blue-50/50 tw-to-transparent dark:tw-from-blue-900/10 tw-pointer-events-none"></div>
              <div class="tw-p-4 xl:tw-p-8 tw-flex tw-flex-col tw-h-full tw-relative tw-z-10">
                <div class="tw-bg-white dark:tw-bg-gray-800/50 xl:tw-bg-transparent tw-rounded-xl tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700 xl:tw-shadow-none xl:tw-border-0 tw-p-5 xl:tw-p-0 tw-flex tw-flex-col xl:tw-h-full">

                  <!-- Header (hidden on mobile/tablet, visible on xl+) -->
                  <div class="tw-hidden xl:tw-flex tw-justify-between tw-items-start tw-mb-8">
                    <div>
                      <h2 class="tw-text-xs tw-font-bold tw-uppercase tw-tracking-wider tw-text-gray-500 dark:tw-text-gray-400 tw-font-display tw-mb-1">Source Batch</h2>
                      <p class="tw-text-base tw-font-bold tw-text-gray-900 dark:tw-text-white tw-flex tw-items-center tw-gap-2">Order {{ currentOrder.id }}</p>
                    </div>
                    <div class="tw-flex tw-items-center tw-gap-1.5 tw-bg-white dark:tw-bg-gray-800 tw-px-3 tw-py-1.5 tw-rounded-full tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                      <span class="tw-relative tw-flex tw-h-2 tw-w-2">
                        <span class="tw-animate-ping tw-absolute tw-inline-flex tw-h-full tw-w-full tw-rounded-full tw-bg-[#0066b3] tw-opacity-75"></span>
                        <span class="tw-relative tw-inline-flex tw-rounded-full tw-h-2 tw-w-2 tw-bg-[#0066b3]"></span>
                      </span>
                      <span class="tw-text-xs tw-font-bold tw-text-gray-700 dark:tw-text-gray-200">{{ currentOrderIndex + 1 }} of {{ selectedOrders.length }}</span>
                    </div>
                  </div>

                  <!-- Weight Display - Horizontal on mobile/tablet, vertical on xl+ -->
                  <div class="tw-flex-1 tw-flex tw-flex-row xl:tw-flex-col tw-justify-between xl:tw-justify-center tw-items-center tw-text-center tw-space-x-6 xl:tw-space-x-0 xl:tw-space-y-6">
                    <div class="tw-relative tw-group tw-flex tw-flex-col tw-items-center">
                      <div class="tw-absolute tw-inset-0 tw-bg-[#0066b3]/5 tw-blur-3xl tw-rounded-full tw-transform tw-scale-150 tw-opacity-100 tw-transition-opacity tw-duration-700"></div>
                      <span class="material-symbols-outlined tw-text-4xl xl:tw-text-5xl tw-text-gray-300 dark:tw-text-gray-600 tw-mb-2 xl:tw-mb-4 tw-block">scale</span>
                      <div class="tw-text-left xl:tw-text-center">
                        <h3 class="tw-text-3xl xl:tw-text-5xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white tw-tracking-tight">
                          {{ formatWeight(getOrderWeight(currentOrder)) }}<span class="tw-text-xl xl:tw-text-2xl tw-text-gray-400 dark:tw-text-gray-500">.g</span>
                        </h3>
                        <p class="tw-text-[10px] xl:tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-mt-1 tw-font-medium tw-uppercase tw-tracking-wide">Source Weight</p>
                      </div>
                    </div>

                    <!-- Order Details Grid -->
                    <div class="tw-grid tw-grid-cols-1 xl:tw-grid-cols-2 tw-gap-2 xl:tw-gap-4 tw-w-32 xl:tw-w-full xl:tw-pt-8 xl:tw-border-t tw-border-gray-200 dark:tw-border-gray-700">
                      <div class="tw-text-center tw-p-2 xl:tw-p-3 tw-rounded-lg tw-bg-gray-50 xl:tw-bg-white dark:tw-bg-gray-900 xl:dark:tw-bg-gray-800 tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                        <span class="tw-block tw-text-sm xl:tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white tw-font-display tw-truncate">{{ currentOrder.item_code || 'N/A' }}</span>
                        <span class="tw-text-[10px] xl:tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-uppercase tw-tracking-wider">Item Code</span>
                      </div>
                      <div class="tw-text-center tw-p-2 xl:tw-p-3 tw-rounded-lg tw-bg-gray-50 xl:tw-bg-white dark:tw-bg-gray-900 xl:dark:tw-bg-gray-800 tw-shadow-sm tw-border tw-border-gray-100 dark:tw-border-gray-700">
                        <span class="tw-block tw-text-sm xl:tw-text-lg tw-font-bold tw-text-gray-900 dark:tw-text-white tw-font-display tw-truncate">{{ currentOrder.texture || 'N/A' }}</span>
                        <span class="tw-text-[10px] xl:tw-text-xs tw-text-gray-500 dark:tw-text-gray-400 tw-uppercase tw-tracking-wider">Texture</span>
                      </div>
                    </div>
                  </div>

                  <div class="tw-hidden xl:tw-block tw-mt-auto tw-pt-6 tw-text-center">
                    <div class="tw-inline-flex tw-items-center tw-gap-2 tw-px-3 tw-py-1.5 tw-rounded-full tw-bg-blue-50 dark:tw-bg-blue-900/20 tw-text-blue-700 dark:tw-text-blue-300 tw-text-xs tw-font-semibold">
                      Ready to Split
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Split Builder Panel -->
            <div class="tw-flex-1 tw-flex tw-flex-col tw-relative xl:tw-h-full tw-bg-white dark:tw-bg-[#1F2937] tw-w-full">
              <!-- Close button (desktop only) -->
              <button class="tw-absolute tw-top-6 tw-right-6 tw-text-gray-400 hover:tw-text-gray-600 dark:hover:tw-text-gray-300 tw-transition-colors tw-z-30 tw-p-1 tw-rounded-full hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800 tw-hidden xl:tw-block" @click="closeModal">
                <span class="material-symbols-outlined tw-text-2xl">close</span>
              </button>

              <div class="tw-px-4 tw-py-4 xl:tw-px-12 xl:tw-pt-10 xl:tw-pb-4">
                <h1 class="tw-text-3xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white tw-mb-6 tw-hidden xl:tw-block">Split Order {{ currentOrder.id }}</h1>
                <div class="tw-flex tw-w-full xl:tw-inline-flex tw-bg-gray-100 dark:tw-bg-gray-800 tw-p-1 tw-rounded-lg">
                  <button
                    :class="splitMode === 'equal' ? 'tw-bg-white dark:tw-bg-gray-700 tw-shadow-sm tw-text-gray-900 dark:tw-text-white' : 'tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-900 dark:hover:tw-text-white'"
                    class="tw-flex-1 xl:tw-flex-none tw-px-5 tw-py-2 tw-rounded-md tw-text-sm tw-font-semibold tw-transition-all tw-text-center"
                    @click="splitMode = 'equal'"
                  >
                    Equal Split
                  </button>
                  <button
                    :class="splitMode === 'custom' ? 'tw-bg-white dark:tw-bg-gray-700 tw-shadow-sm tw-text-gray-900 dark:tw-text-white' : 'tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-900 dark:hover:tw-text-white'"
                    class="tw-flex-1 xl:tw-flex-none tw-px-5 tw-py-2 tw-rounded-md tw-text-sm tw-font-medium tw-transition-all tw-text-center"
                    @click="splitMode = 'custom'"
                  >
                    Custom Split
                  </button>
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
                <div v-if="showFilters" class="tw-px-4 xl:tw-px-12 tw-pb-4 xl:tw-pb-6 tw-border-b tw-border-gray-200 dark:tw-border-gray-700">
                  <div class="tw-bg-gray-50 dark:tw-bg-gray-800/50 tw-rounded-lg tw-p-4 xl:tw-p-6 tw-space-y-4">
                    <div class="tw-grid tw-grid-cols-1 xl:tw-grid-cols-3 tw-gap-3 xl:tw-gap-4">
                      <!-- Customer Filter -->
                      <div>
                        <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 tw-mb-2 tw-uppercase tw-tracking-wide">Customer</label>
                        <input
                          v-model="filters.customer"
                          type="text"
                          placeholder="Filter by customer..."
                          class="tw-w-full tw-px-3 xl:tw-px-4 tw-py-2 tw-bg-white dark:tw-bg-gray-700 tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-rounded-lg tw-text-sm tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-400 focus:tw-ring-2 focus:tw-ring-[#0066b3] focus:tw-border-transparent tw-transition-all"
                        />
                      </div>

                      <!-- Karigar Filter -->
                      <div>
                        <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 tw-mb-2 tw-uppercase tw-tracking-wide">Karigar</label>
                        <input
                          v-model="filters.karigar"
                          type="text"
                          placeholder="Filter by karigar..."
                          class="tw-w-full tw-px-3 xl:tw-px-4 tw-py-2 tw-bg-white dark:tw-bg-gray-700 tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-rounded-lg tw-text-sm tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-400 focus:tw-ring-2 focus:tw-ring-[#0066b3] focus:tw-border-transparent tw-transition-all"
                        />
                      </div>

                      <!-- Item Name Filter -->
                      <div>
                        <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-500 dark:tw-text-gray-400 tw-mb-2 tw-uppercase tw-tracking-wide">Item Name</label>
                        <input
                          v-model="filters.itemName"
                          type="text"
                          placeholder="Filter by item name..."
                          class="tw-w-full tw-px-3 xl:tw-px-4 tw-py-2 tw-bg-white dark:tw-bg-gray-700 tw-border tw-border-gray-200 dark:tw-border-gray-600 tw-rounded-lg tw-text-sm tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-400 focus:tw-ring-2 focus:tw-ring-[#0066b3] focus:tw-border-transparent tw-transition-all"
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

              <!-- Split Parts List - overflow-visible on mobile/tablet, overflow-y-auto on xl+ -->
              <div class="tw-flex-1 tw-overflow-visible xl:tw-overflow-y-auto custom-scrollbar tw-px-4 xl:tw-px-12 tw-py-2 xl:tw-py-6 tw-space-y-6 xl:tw-space-y-8 tw-pb-24 xl:tw-pb-6">
                <div v-for="(part, index) in splitParts" :key="part.id" class="tw-group tw-flex tw-flex-col sm:tw-flex-row tw-items-start sm:tw-items-end tw-gap-2 sm:tw-gap-6 tw-w-full tw-relative tw-bg-[#F9FAFB] dark:tw-bg-[#161e2e]/50 sm:tw-bg-transparent tw-p-4 sm:tw-p-0 tw-rounded-xl tw-border tw-border-gray-100 dark:tw-border-gray-800 sm:tw-border-0">
                  <div class="tw-hidden sm:tw-flex tw-items-center tw-justify-center tw-w-8 tw-h-12 tw-text-xl tw-font-bold tw-text-gray-300 dark:tw-text-gray-600 tw-font-display tw-select-none">{{ getPartLabel(index) }}</div>
                  <div class="sm:tw-hidden tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1">PART {{ getPartLabel(index) }}</div>

                  <div class="tw-flex-1 tw-w-full">
                    <div class="tw-border-b-2 tw-border-gray-200 dark:tw-border-gray-700 group-focus-within:tw-border-[#0066b3] tw-transition-colors tw-pb-1">
                      <label class="tw-block tw-text-xs tw-font-bold tw-text-gray-400 dark:tw-text-gray-500 tw-mb-1 tw-uppercase tw-tracking-wide">Weight Allocation</label>
                      <div class="tw-flex tw-items-baseline">
                        <input
                          v-model="part.qty"
                          :disabled="splitMode === 'equal'"
                          :max="getOrderQty(currentOrder)"
                          class="tw-w-full tw-bg-transparent tw-border-none tw-p-0 tw-text-2xl tw-font-display tw-font-bold tw-text-gray-900 dark:tw-text-white placeholder:tw-text-gray-300 focus:tw-ring-0"
                          type="text"
                          inputmode="decimal"
                          placeholder="0"
                          @input="handleQtyInput(index, $event)"
                        />
                        <span class="tw-text-base tw-text-gray-400 tw-font-medium tw-ml-2">g</span>
                      </div>
                    </div>
                  </div>
                  <!-- Remove button - positioned for touch on mobile -->
                  <button
                    v-if="splitParts.length > 2"
                    class="tw-absolute tw-right-2 tw-top-2 sm:tw--right-8 sm:tw-top-auto sm:tw-bottom-3 tw-text-gray-300 hover:tw-text-red-500 tw-transition-colors tw-p-1 tw-hidden lg:tw-block"
                    @click="removePart(index)"
                  >
                    <span class="material-symbols-outlined tw-text-xl">close</span>
                  </button>
                </div>

                <div class="tw-pl-0 sm:tw-pl-14 tw-pt-2 tw-pb-6">
                  <button class="tw-w-full xl:tw-w-auto tw-justify-center tw-text-[#0066b3] hover:tw-text-[#005291] dark:tw-text-blue-400 dark:hover:tw-text-blue-300 tw-transition-colors tw-flex tw-items-center tw-gap-2 tw-text-sm tw-font-semibold tw-group tw-py-2 tw-border tw-border-dashed tw-border-[#0066b3]/30 tw-rounded-lg xl:tw-border-0" @click="addPart">
                    <span class="material-symbols-outlined tw-text-xl group-hover:tw-scale-110 tw-transition-transform">add_circle</span>
                    Add Split Part
                  </button>
                </div>
              </div>

              <!-- Bottom Action Bar -->
              <div class="tw-sticky tw-bottom-0 tw-z-30 tw-px-4 xl:tw-px-12 tw-py-4 xl:tw-py-6 tw-border-t tw-border-gray-200 dark:tw-border-gray-800 tw-bg-white dark:tw-bg-[#1F2937] xl:tw-rounded-br-xl tw-shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] xl:tw-shadow-none">
                <div class="tw-flex tw-flex-row xl:tw-flex-row tw-justify-between tw-items-center tw-gap-4 xl:tw-gap-6">
                  <div class="tw-text-sm tw-flex tw-flex-col xl:tw-flex-row xl:tw-items-center tw-gap-1 xl:tw-gap-3">
                    <div class="tw-flex tw-items-center tw-gap-2">
                      <span class="tw-text-gray-500 dark:tw-text-gray-400 tw-font-medium">Remaining:</span>
                      <span
                        :class="remainingQty === 0 ? 'tw-text-green-600 dark:tw-text-green-400' : 'tw-text-red-600 dark:tw-text-red-400'"
                        class="tw-font-mono tw-font-bold tw-text-lg"
                      >
                        {{ formatWeight(Math.abs(remainingQty)) }} g
                      </span>
                    </div>
                    <span class="tw-text-xs tw-text-gray-400 dark:tw-text-gray-600 tw-flex tw-items-center tw-gap-1">
                      <span v-if="remainingQty === 0" class="material-symbols-outlined tw-text-base">check_circle</span>
                      {{ remainingQty === 0 ? 'Balanced' : 'Unbalanced' }}
                    </span>
                  </div>
                  <div class="tw-flex tw-items-center tw-gap-3 xl:tw-gap-4 tw-w-auto sm:tw-justify-end">
                    <button
                      class="tw-hidden xl:tw-block tw-text-sm tw-font-medium tw-text-gray-500 dark:tw-text-gray-400 hover:tw-text-gray-900 dark:hover:tw-text-white tw-transition-colors tw-cursor-pointer tw-px-3 tw-py-2 tw-rounded hover:tw-bg-gray-100 dark:hover:tw-bg-gray-800"
                      @click="skipOrder"
                    >
                      Skip
                    </button>
                    <button
                      :disabled="!isValidSplit"
                      class="tw-bg-[#0066b3] hover:tw-bg-[#005291] tw-text-white tw-text-sm tw-font-semibold tw-py-3 tw-px-6 xl:tw-px-8 tw-rounded-lg tw-shadow-lg tw-shadow-blue-500/20 tw-transition-all tw-transform active:tw-scale-95 tw-flex tw-items-center tw-gap-2 tw-whitespace-nowrap disabled:tw-opacity-50 disabled:tw-cursor-not-allowed"
                      @click="processSplit"
                    >
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
    </div>
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
const splitMode = ref('custom');
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
  const allocated = splitParts.value.reduce((sum, p) => sum + (parseFloat(p.qty) || 0), 0);
  return getOrderWeight(currentOrder.value) - allocated;
});

const isValidSplit = computed(() => {
  return splitParts.value.length >= 2 &&
         splitParts.value.every(p => parseFloat(p.qty) > 0) &&
         Math.abs(remainingQty.value) < 0.01;
});

function getOrderQty(order) {
  return parseFloat(order.qty || 0);
}

function getOrderWeight(order) {
  const weight = order.karigar_received_weight || order.item_weight;
  if (weight === null || weight === undefined) return 0;
  const num = parseFloat(weight);
  return isNaN(num) ? 0 : num;
}

function formatWeight(w) {
  if (w === null || w === undefined) return '0';
  const num = parseFloat(w);
  return isNaN(num) ? '0' : num.toFixed(2);
}

function getPartLabel(i) {
  return String.fromCharCode(65 + i);
}

function handleQtyInput(index, e) {
  // Allow digits and decimal point
  let v = e.target.value.replace(/[^\d.]/g, '');
  // Ensure only one decimal point
  const parts = v.split('.');
  if (parts.length > 2) {
    v = parts[0] + '.' + parts.slice(1).join('');
  }

  const numValue = parseFloat(v) || 0;
  const totalWeight = getOrderWeight(currentOrder.value);

  // Calculate total of other parts
  const otherPartsTotal = splitParts.value.reduce((sum, p, i) => {
    if (i !== index) {
      return sum + (parseFloat(p.qty) || 0);
    }
    return sum;
  }, 0);

  // Maximum this part can have
  const maxForThisPart = totalWeight - otherPartsTotal;

  // Don't allow exceeding the maximum
  if (numValue > maxForThisPart) {
    splitParts.value[index].qty = maxForThisPart.toFixed(2);
    if (maxForThisPart >= 0) {
      props.frappe.show_alert({
        message: `Maximum weight for this part is ${maxForThisPart.toFixed(2)}g`,
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
  const totalWeight = getOrderWeight(currentOrder.value);
  const numParts = splitParts.value.length;
  const perPart = totalWeight / numParts;

  splitParts.value.forEach((p, i) => {
    if (i === numParts - 1) {
      // Last part gets any remaining to avoid floating point issues
      const allocated = splitParts.value.slice(0, -1).reduce((sum, part) => sum + parseFloat(part.qty || 0), 0);
      p.qty = (totalWeight - allocated).toFixed(2);
    } else {
      p.qty = perPart.toFixed(2);
    }
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
    props.frappe.msgprint('Please ensure all split parts have valid weights and the total matches the order weight');
    return;
  }

  // Process splits sequentially using the existing split_order_item API
  const parts = splitParts.value.filter(p => parseFloat(p.qty) > 0);

  // Confirm split action
  const splitSummary = parts.map((p, i) => `${getPartLabel(i)}: ${p.qty}g`).join(', ');
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
      parts: parts.map((p, i) => ({ label: getPartLabel(i), qty: parseFloat(p.qty) }))
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

  // Split the first weight from the original
  const splitQty = parseFloat(parts[index].qty);

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
  splitMode.value = 'custom';
  splitParts.value = [{ id: 1, qty: '' }, { id: 2, qty: '' }];
  nextPartId = 3;
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

.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Touch scrolling fix for tablets/mobile */
.touch-scroll-fix {
  -webkit-overflow-scrolling: touch;
  touch-action: pan-y;
  overscroll-behavior-y: contain;
}
</style>