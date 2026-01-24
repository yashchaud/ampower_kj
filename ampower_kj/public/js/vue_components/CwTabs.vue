<template>
  <div class="tw-relative tw-flex tw-w-full tw-border-b-2 tw-border-slate-200 tw-overflow-x-auto tw-overflow-y-hidden no-scrollbar">
    <template v-for="(tab, index) in tabs" :key="tab.name">
      <!-- Hidden radio input for state management -->
      <input
        :id="`tab-${index}`"
        type="radio"
        name="workflow-tabs"
        :value="tab.name"
        :checked="tab.name === modelValue"
        class="tw-peer tw-hidden"
        :data-peer-name="`tab${index}`"
        @change="handleTabClick(tab.name)"
      />

      <!-- Label acts as the clickable tab -->
      <label
        :ref="(el) => { if (el) tabRefs[index] = el }"
        :for="`tab-${index}`"
        class="tw-flex tw-items-center tw-justify-center tw-gap-2 tw-py-4 tw-px-6 tw-text-sm tw-font-medium tw-cursor-pointer tw-transition-colors tw-duration-400 tw-ease-in-out tw-whitespace-nowrap tw-flex-1"
        :class="[
          tab.name === modelValue
            ? 'tw-text-blue-600 tw-font-semibold'
            : 'tw-text-slate-500 hover:tw-text-slate-700'
        ]"
      >
        <span>{{ tab.label || tab.name }}</span>
        <span
          v-if="tab.count !== undefined"
          class="tw-px-2 tw-py-0.5 tw-text-xs tw-font-semibold tw-rounded-full tw-transition-colors tw-duration-400 tw-ease-in-out"
          :class="[
            tab.name === modelValue
              ? 'tw-bg-blue-100 tw-text-blue-700'
              : 'tw-bg-slate-100 tw-text-slate-600'
          ]"
        >
          {{ tab.count }}
        </span>
      </label>
    </template>

    <!-- The Glider (Fluid Line) -->
    <div
      v-show="gliderWidth > 0"
      class="tw-absolute tw-bottom-0 tw-left-0 tw-h-[2px] tw-bg-blue-600"
      :style="gliderStyle"
    ></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue';

const props = defineProps({
  tabs: {
    type: Array,
    required: true
    // Each tab: { name: string, label?: string, count?: number }
  },
  modelValue: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['update:modelValue']);

const tabRefs = ref([]);
const gliderWidth = ref(0);
const gliderOffset = ref(0);

const activeTabIndex = computed(() => {
  return props.tabs.findIndex(tab => tab.name === props.modelValue);
});

const updateGliderPosition = () => {
  nextTick(() => {
    requestAnimationFrame(() => {
      if (tabRefs.value.length > 0 && activeTabIndex.value >= 0) {
        const activeTab = tabRefs.value[activeTabIndex.value];
        if (activeTab) {
          gliderWidth.value = activeTab.offsetWidth;
          gliderOffset.value = activeTab.offsetLeft;
        }
      }
    });
  });
};

const gliderStyle = computed(() => {
  return {
    width: `${gliderWidth.value}px`,
    transform: `translateX(${gliderOffset.value}px)`,
    transition: 'transform 500ms cubic-bezier(0.25, 0.8, 0.25, 1), width 500ms cubic-bezier(0.25, 0.8, 0.25, 1)'
  };
});

const handleTabClick = (tabName) => {
  emit('update:modelValue', tabName);
};

// Watch for tab changes and update glider
watch(() => props.modelValue, () => {
  updateGliderPosition();
}, { immediate: true });

// Watch for tabs array changes
watch(() => props.tabs, () => {
  updateGliderPosition();
}, { deep: true, immediate: true });

onMounted(() => {
  updateGliderPosition();

  // Update on window resize
  window.addEventListener('resize', updateGliderPosition);
});

onUnmounted(() => {
  window.removeEventListener('resize', updateGliderPosition);
});
</script>

<style scoped>
/* Hide scrollbar for tabs on all browsers */
.no-scrollbar::-webkit-scrollbar {
  display: none;
}

.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}

/* Enable smooth scrolling on mobile */
@media (max-width: 768px) {
  .tw-overflow-x-auto {
    -webkit-overflow-scrolling: touch;
    scroll-behavior: smooth;
  }
}
</style>
