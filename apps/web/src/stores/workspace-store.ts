import { create } from "zustand";
import { persist } from "zustand/middleware";

export type CanvasViewMode = "single" | "grid" | "layers";
export type CommandMode = "plan" | "execute";

export type WorkspaceArtifact = {
  id: string;
  label: string;
  kind: "screenshot" | "pdf" | "trace";
};

interface WorkspaceState {
  navCollapsed: boolean;
  canvasOpen: boolean;
  focusMode: boolean;
  canvasViewMode: CanvasViewMode;
  filmstripVisible: boolean;
  commandMode: CommandMode;
  selectedModel: string | null;
  selectedArtifactId: string | null;
  commandDraft: string;
  setNavCollapsed: (collapsed: boolean) => void;
  toggleNav: () => void;
  setCanvasOpen: (open: boolean) => void;
  toggleCanvas: () => void;
  toggleFocusMode: () => void;
  setCanvasViewMode: (mode: CanvasViewMode) => void;
  setFilmstripVisible: (visible: boolean) => void;
  setCommandMode: (mode: CommandMode) => void;
  setSelectedModel: (model: string) => void;
  setSelectedArtifactId: (id: string | null) => void;
  setCommandDraft: (draft: string) => void;
}

export const useWorkspaceStore = create<WorkspaceState>()(
  persist(
    (set) => ({
      navCollapsed: false,
      canvasOpen: true,
      focusMode: false,
      canvasViewMode: "single",
      filmstripVisible: true,
      commandMode: "plan",
      selectedModel: null,
      selectedArtifactId: "v1",
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
      setFilmstripVisible: (filmstripVisible) => set({ filmstripVisible }),
      setCommandMode: (commandMode) => set({ commandMode }),
      setSelectedModel: (selectedModel) => set({ selectedModel }),
      setSelectedArtifactId: (selectedArtifactId) => set({ selectedArtifactId }),
      setCommandDraft: (commandDraft) => set({ commandDraft }),
    }),
    {
      name: "jober-workspace-v1",
      partialize: (state) => ({
        navCollapsed: state.navCollapsed,
        canvasOpen: state.canvasOpen,
        canvasViewMode: state.canvasViewMode,
        filmstripVisible: state.filmstripVisible,
        commandMode: state.commandMode,
        selectedModel: state.selectedModel,
        selectedArtifactId: state.selectedArtifactId,
      }),
    },
  ),
);

/** Placeholder artifacts until run console streams into the canvas. */
export const WORKSPACE_DEMO_ARTIFACTS: WorkspaceArtifact[] = [
  { id: "v1", label: "v1", kind: "screenshot" },
  { id: "v2", label: "v2", kind: "screenshot" },
  { id: "v3", label: "v3", kind: "pdf" },
];
