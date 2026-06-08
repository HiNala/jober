import { beforeEach, describe, expect, it } from "vitest";

import { useWorkspaceStore, WORKSPACE_PERSISTED_KEYS } from "@/stores/workspace-store";

describe("useWorkspaceStore", () => {
  beforeEach(() => {
    useWorkspaceStore.setState({
      navCollapsed: false,
      canvasOpen: true,
      focusMode: false,
      canvasViewMode: "single",
      filmstripVisible: true,
      commandMode: "plan",
      selectedModel: null,
      selectedArtifactId: "v1",
      commandDraft: "",
    });
  });

  it("toggles nav and canvas independently", () => {
    const { toggleNav, toggleCanvas } = useWorkspaceStore.getState();
    toggleNav();
    expect(useWorkspaceStore.getState().navCollapsed).toBe(true);
    toggleCanvas();
    expect(useWorkspaceStore.getState().canvasOpen).toBe(false);
  });

  it("toggles focus mode without losing other prefs", () => {
    useWorkspaceStore.setState({ navCollapsed: true, canvasOpen: true });
    useWorkspaceStore.getState().toggleFocusMode();
    expect(useWorkspaceStore.getState().focusMode).toBe(true);
    expect(useWorkspaceStore.getState().navCollapsed).toBe(true);
    expect(useWorkspaceStore.getState().canvasOpen).toBe(true);
  });

  it("does not persist ephemeral command draft, focus mode, or active run", () => {
    useWorkspaceStore.getState().setCommandDraft("draft text");
    expect(WORKSPACE_PERSISTED_KEYS).not.toContain("commandDraft");
    expect(WORKSPACE_PERSISTED_KEYS).not.toContain("focusMode");
    expect(WORKSPACE_PERSISTED_KEYS).not.toContain("activeRunId");
  });
});
