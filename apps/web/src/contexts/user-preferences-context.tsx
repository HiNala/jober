"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useTheme } from "next-themes";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  type ReactNode,
} from "react";

import { useAuth } from "@/contexts/auth-context";
import {
  fetchUserPreferences,
  patchUserPreferences,
  type UserPreferences,
} from "@/lib/api/preferences";
import { useWorkspaceStore } from "@/stores/workspace-store";

type UserPreferencesContextValue = {
  preferences: UserPreferences | undefined;
  isLoading: boolean;
  updatePreferences: (patch: Partial<UserPreferences>) => Promise<void>;
};

const UserPreferencesContext = createContext<UserPreferencesContextValue | null>(null);

function applyAppearance(prefs: UserPreferences) {
  const root = document.documentElement;
  if (prefs.appearance.reduced_motion === true) {
    root.setAttribute("data-reduced-motion", "true");
  } else if (prefs.appearance.reduced_motion === false) {
    root.removeAttribute("data-reduced-motion");
  } else {
    root.removeAttribute("data-reduced-motion");
  }
  root.dataset.density = prefs.appearance.density;
}

export function UserPreferencesProvider({ children }: { children: ReactNode }) {
  const { user, bypass } = useAuth();
  const { setTheme } = useTheme();
  const queryClient = useQueryClient();
  const setCanvasViewMode = useWorkspaceStore((s) => s.setCanvasViewMode);
  const setFilmstripVisible = useWorkspaceStore((s) => s.setFilmstripVisible);

  const query = useQuery({
    queryKey: ["user-preferences"],
    queryFn: async () => (await fetchUserPreferences()).preferences,
    enabled: !bypass && Boolean(user),
  });

  useEffect(() => {
    if (!query.data) return;
    const prefs = query.data;
    if (
      prefs.appearance.theme === "light" ||
      prefs.appearance.theme === "dark" ||
      prefs.appearance.theme === "system"
    ) {
      setTheme(prefs.appearance.theme);
    }
    if (prefs.appearance.canvas_view_mode === "single" || prefs.appearance.canvas_view_mode === "grid") {
      setCanvasViewMode(prefs.appearance.canvas_view_mode);
    }
    setFilmstripVisible(prefs.appearance.filmstrip_visible);
    applyAppearance(prefs);
  }, [query.data, setCanvasViewMode, setFilmstripVisible, setTheme]);

  const updatePreferences = useCallback(
    async (patch: Partial<UserPreferences>) => {
      try {
        const res = await patchUserPreferences(patch);
        queryClient.setQueryData(["user-preferences"], res.preferences);
        if (patch.appearance?.theme) {
          setTheme(patch.appearance.theme);
        }
        if (patch.appearance) {
          applyAppearance(res.preferences);
        }
        if (patch.appearance?.canvas_view_mode) {
          setCanvasViewMode(patch.appearance.canvas_view_mode as "single" | "grid");
        }
        if (patch.appearance?.filmstrip_visible !== undefined) {
          setFilmstripVisible(patch.appearance.filmstrip_visible);
        }
      } catch (err) {
        const { toast } = await import("sonner");
        const { formatApiError } = await import("@/lib/api/errors");
        toast.error(formatApiError(err, "Could not save preferences"));
        throw err;
      }
    },
    [queryClient, setCanvasViewMode, setFilmstripVisible, setTheme],
  );

  return (
    <UserPreferencesContext.Provider
      value={{
        preferences: query.data,
        isLoading: query.isLoading,
        updatePreferences,
      }}
    >
      {children}
    </UserPreferencesContext.Provider>
  );
}

export function useUserPreferences() {
  const ctx = useContext(UserPreferencesContext);
  if (!ctx) {
    throw new Error("useUserPreferences must be used within UserPreferencesProvider");
  }
  return ctx;
}
