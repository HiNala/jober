import { create } from "zustand";
import { persist } from "zustand/middleware";

export type CanvasViewMode = "single" | "grid" | "layers";
export type CanvasSurface = "browser" | "document" | "fill-diff" | "review";
export type CommandMode = "plan" | "execute";

interface WorkspaceState {
  navCollapsed: boolean;
  canvasOpen: boolean;
  focusMode: boolean;
  canvasViewMode: CanvasViewMode;
  canvasSurface: CanvasSurface;
  filmstripVisible: boolean;
  commandMode: CommandMode;
  selectedModel: string | null;
  selectedArtifactId: string | null;
  activeRunId: string | null;
  commandDraft: string;
  setNavCollapsed: (collapsed: boolean) => void;
  toggleNav: () => void;
  setCanvasOpen: (open: boolean) => void;
  toggleCanvas: () => void;
  toggleFocusMode: () => void;
  setCanvasViewMode: (mode: CanvasViewMode) => void;
  setCanvasSurface: (surface: CanvasSurface) => void;
  setFilmstripVisible: (visible: boolean) => void;
  setCommandMode: (mode: CommandMode) => void;
  setSelectedModel: (model: string) => void;
  setSelectedArtifactId: (id: string | null) => void;
  setCommandDraft: (draft: string) => void;
}

export const WORKSPACE_PERSISTED_KEYS = [
  "navCollapsed",
  "canvasOpen",
  "canvasViewMode",
  "canvasSurface",
  "filmstripVisible",
  "commandMode",
  "selectedModel",
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
      commandMode: "plan",
      selectedModel: null,
      selectedArtifactId: null,
      activeRunId: null,
      commandDraft: "",
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
      setCommandMode: (commandMode) => set({ commandMode }),
      setSelectedModel: (selectedModel) => set({ selectedModel }),
      setSelectedArtifactId: (selectedArtifactId) => set({ selectedArtifactId }),
      setCommandDraft: (commandDraft) => set({ commandDraft }),
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
