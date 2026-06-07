import { apiFetch } from "@/lib/api/client";

export type LlmModelOption = {
  id: string;
  role: string;
  label: string;
};

export type LlmConfig = {
  provider: string;
  default_model: string;
  models: LlmModelOption[];
  budget_usd: number;
};

export async function fetchLlmConfig(): Promise<LlmConfig> {
  return apiFetch<LlmConfig>("/api/llm/config");
}
