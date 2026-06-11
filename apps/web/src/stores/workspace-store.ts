import { create } from "zustand";
import { persist } from "zustand/middleware";

export type CanvasViewMode = "single" | "grid" | "layers";
export type CanvasSurface = "browser" | "document" | "fill-diff" | "review";
export type RunMobileTab = "work" | "canvas";

interface WorkspaceState {
  navCollapsed: boolean;
  canvasOpen: boolean;
  focusMode: boolean;
  canvasViewMode: CanvasViewMode;
  canvasSurface: CanvasSurface;
  filmstripVisible: boolean;
  selectedArtifactId: string | null;
  activeRunId: string | null;
  commandPaletteOpen: boolean;
  runMobileTab: RunMobileTab;
  setNavCollapsed: (collapsed: boolean) => void;
  toggleNav: () => void;
  setCanvasOpen: (open: boolean) => void;
  toggleCanvas: () => void;
  toggleFocusMode: () => void;
  setCanvasViewMode: (mode: CanvasViewMode) => void;
  setCanvasSurface: (surface: CanvasSurface) => void;
  setFilmstripVisible: (visible: boolean) => void;
  setSelectedArtifactId: (id: string | null) => void;
  setCommandPaletteOpen: (open: boolean) => void;
  toggleCommandPalette: () => void;
  setRunMobileTab: (tab: RunMobileTab) => void;
}

export const WORKSPACE_PERSISTED_KEYS = [
  "navCollapsed",
  "canvasOpen",
  "canvasViewMode",
  "canvasSurface",
  "filmstripVisible",
  "selectedArtifactId",
] as const satisfies ReadonlyArray<keyof WorkspaceState>;

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      navCollapsed: false,
      canvasOpen: true,
      focusMode: false,
      canvasViewMode: "single",
      canvasSurface: "browser",
      filmstripVisible: true,
      selectedArtifactId: null,
      activeRunId: null,
      commandPaletteOpen: false,
      runMobileTab: "work",
      setNavCollapsed: (navCollapsed) => set({ navCollapsed }),
      toggleNav: () => set((state) => ({ navCollapsed: !state.navCollapsed })),
      setCanvasOpen: (canvasOpen) => set({ canvasOpen }),
      toggleCanvas: () => set((state) => ({ canvasOpen: !state.canvasOpen })),
      toggleFocusMode: () =>
        set((state) => ({
          focusMode: !state.focusMode,
        })),
      setCanvasViewMode: (canvasViewMode) => set({ canvasViewMode }),
      setCanvasSurface: (canvasSurface) => set({ canvasSurface }),
      setFilmstripVisible: (filmstripVisible) => set({ filmstripVisible }),
      setSelectedArtifactId: (selectedArtifactId) => set({ selectedArtifactId }),
      setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
      toggleCommandPalette: () =>
        set((state) => ({ commandPaletteOpen: !state.commandPaletteOpen })),
      setRunMobileTab: (runMobileTab) => set({ runMobileTab }),
    }),
    {
      name: "jober-workspace-v1",
      partialize: (state) =>
        Object.fromEntries(
          WORKSPACE_PERSISTED_KEYS.map((key) => [key, state[key]]),
        ) as Pick<WorkspaceState, (typeof WORKSPACE_PERSISTED_KEYS)[number]>,
    },
  ),
);
