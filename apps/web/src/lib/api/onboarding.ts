import { apiFetch } from "./client";

export type DemoWorkspaceResult = {
  jobs_created: number;
  profile_seeded: number;
};

export async function seedDemoWorkspace(): Promise<DemoWorkspaceResult> {
  return apiFetch<DemoWorkspaceResult>("/api/onboarding/demo-workspace", {
    method: "POST",
    body: "{}",
  });
}
