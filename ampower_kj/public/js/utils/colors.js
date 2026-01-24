/**
 * Color Utilities for Custom Workflow
 *
 * Provides consistent color mappings for karigar avatars
 * and other UI elements.
 */

/**
 * Karigar avatar color palette
 * Maps color names to hex values
 */
export const KARIGAR_COLORS = {
  indigo: '#6366f1',
  violet: '#8b5cf6',
  purple: '#a855f7',
  pink: '#ec4899',
  red: '#ef4444',
  orange: '#f97316',
  amber: '#f59e0b',
  yellow: '#eab308',
  lime: '#84cc16',
  green: '#22c55e',
  emerald: '#10b981',
  teal: '#14b8a6',
  cyan: '#06b6d4',
  sky: '#0ea5e9',
  blue: '#3b82f6'
};

/**
 * Default color when no color name matches
 */
export const DEFAULT_KARIGAR_COLOR = KARIGAR_COLORS.indigo;

/**
 * Get hex color value for a karigar by color name
 * @param {string} colorName - The color name (e.g., 'indigo', 'violet')
 * @returns {string} Hex color value
 */
export function getKarigarColor(colorName) {
  return KARIGAR_COLORS[colorName] || DEFAULT_KARIGAR_COLOR;
}

/**
 * Status color classes for workflow stages
 * Returns Tailwind CSS classes for background and text
 */
export const STATUS_COLORS = {
  'Unassigned': {
    bg: 'tw-bg-amber-50',
    text: 'tw-text-amber-700',
    dot: 'tw-bg-amber-500'
  },
  'Assigned': {
    bg: 'tw-bg-blue-50',
    text: 'tw-text-blue-700',
    dot: 'tw-bg-blue-500'
  },
  'Incoming': {
    bg: 'tw-bg-violet-50',
    text: 'tw-text-violet-700',
    dot: 'tw-bg-violet-500'
  },
  'Internal QA': {
    bg: 'tw-bg-cyan-50',
    text: 'tw-text-cyan-700',
    dot: 'tw-bg-cyan-500'
  },
  'Ready': {
    bg: 'tw-bg-emerald-50',
    text: 'tw-text-emerald-700',
    dot: 'tw-bg-emerald-500'
  },
  'Delivered': {
    bg: 'tw-bg-green-50',
    text: 'tw-text-green-700',
    dot: 'tw-bg-green-500'
  },
  'Cancelled': {
    bg: 'tw-bg-red-50',
    text: 'tw-text-red-700',
    dot: 'tw-bg-red-500'
  }
};

/**
 * Default status colors when status name doesn't match
 */
export const DEFAULT_STATUS_COLORS = {
  bg: 'tw-bg-slate-50',
  text: 'tw-text-slate-700',
  dot: 'tw-bg-slate-500'
};

/**
 * Get status colors by status name
 * @param {string} status - The workflow status name
 * @returns {Object} Object with bg, text, and dot color classes
 */
export function getStatusColors(status) {
  return STATUS_COLORS[status] || DEFAULT_STATUS_COLORS;
}

/**
 * Get combined status class string (bg + text)
 * @param {string} status - The workflow status name
 * @returns {string} Combined Tailwind classes
 */
export function getStatusClass(status) {
  const colors = getStatusColors(status);
  return `${colors.bg} ${colors.text}`;
}

/**
 * Get status dot class
 * @param {string} status - The workflow status name
 * @returns {string} Tailwind class for the dot
 */
export function getStatusDotClass(status) {
  return getStatusColors(status).dot;
}
