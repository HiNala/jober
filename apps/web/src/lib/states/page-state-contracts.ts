/** Accessibility contracts for shared page-state shells (Mission 05). */

export const PAGE_LOADING_ARIA = {
  role: "status" as const,
  live: "polite" as const,
  busy: true,
};

export const PAGE_ERROR_ARIA = {
  role: "alert" as const,
};

export const PAGE_SUCCESS_ARIA = {
  role: "status" as const,
};
