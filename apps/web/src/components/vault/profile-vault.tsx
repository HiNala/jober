"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Lock, ShieldAlert } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { formatApiError } from "@/lib/api/errors";
import { useUnsavedChanges } from "@/lib/forms/use-unsaved-changes";

import { FileUpload } from "@/components/import/file-upload";
import { PageError, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Textarea } from "@/components/ui/textarea";
import { surface } from "@/lib/design/tokens";
import {
  fetchCommonAnswers,
  fetchProfile,
  patchProfile,
  patchVault,
  saveCommonAnswer,
  uploadResume,
  type VaultField,
} from "@/lib/api/vault";

function tierLabel(tier: string) {
  if (tier === "sensitive") return "Sensitive EEO";
  if (tier === "preference") return "Preferences";
  return "Public / standard";
}

function maskValue(value: string): string {
  if (!value) return "";
  return "•".repeat(Math.min(Math.max(value.length, 6), 12));
}

function FieldRow({
  field,
  onSavePublic,
  onSaveSensitive,
  onDirtyChange,
}: {
  field: VaultField;
  onSavePublic: (key: string, value: string) => void;
  onSaveSensitive: (
    key: string,
    value: string,
    consent: { consent: boolean; never_autofill: boolean },
  ) => void;
  onDirtyChange?: (key: string, dirty: boolean) => void;
}) {
  const savedValue = typeof field.value === "string" ? field.value : "";
  const [draft, setDraft] = useState(savedValue);

  useEffect(() => {
    onDirtyChange?.(field.key, draft !== savedValue);
  }, [draft, field.key, onDirtyChange, savedValue]);
  const [revealed, setRevealed] = useState(false);
  const sensitive = field.tier === "sensitive";
  const fieldId = `vault-field-${field.key}`;
  const hasStoredSensitive =
    sensitive && typeof field.value === "string" && field.value.length > 0;

  return (
    <div className="space-y-2 rounded-lg border border-border/60 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <label htmlFor={fieldId} className="text-sm font-medium">
          {field.label}
        </label>
        {sensitive && (
          <Badge variant="outline" className="gap-1 text-amber-600">
            <Lock className="size-3" aria-hidden />
            Encrypted at rest
          </Badge>
        )}
      </div>
      {field.tier !== "sensitive" ? (
        typeof field.value === "boolean" ? (
          <label className="flex items-center gap-2 text-sm" htmlFor={fieldId}>
            <Checkbox
              id={fieldId}
              checked={field.value}
              onCheckedChange={(checked) =>
                onSavePublic(field.key, checked === true ? "true" : "false")
              }
            />
            Enabled
          </label>
        ) : (
          <Input
            id={fieldId}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onBlur={() => onSavePublic(field.key, draft)}
            autoComplete="off"
          />
        )
      ) : (
        <>
          {hasStoredSensitive && !revealed ? (
            <div className="flex items-center justify-between gap-2 rounded-md border border-dashed border-border/80 bg-muted/30 px-3 py-2">
              <span className="font-mono text-sm tracking-widest text-muted-foreground" aria-hidden>
                {maskValue(draft)}
              </span>
              <span className="sr-only">Value stored and masked</span>
              <Button type="button" size="sm" variant="outline" onClick={() => setRevealed(true)}>
                Update value
              </Button>
            </div>
          ) : (
            <Textarea
              id={fieldId}
              value={draft}
              onChange={(e) => setDraft(e.target.value)}
              rows={2}
              placeholder="Enter only facts you choose to store — never inferred"
              autoComplete="off"
            />
          )}
          <div className="flex flex-wrap gap-4 text-xs">
            <label className="flex items-center gap-2">
              <Checkbox
                checked={field.consent.consent}
                onCheckedChange={(checked) =>
                  onSaveSensitive(field.key, draft, {
                    consent: checked === true,
                    never_autofill: field.consent.never_autofill,
                  })
                }
              />
              Consent to store
            </label>
            <label className="flex items-center gap-2">
              <Checkbox
                checked={field.consent.never_autofill}
                onCheckedChange={(checked) =>
                  onSaveSensitive(field.key, draft, {
                    consent: field.consent.consent,
                    never_autofill: checked === true,
                  })
                }
              />
              Always ask me (never auto-fill)
            </label>
          </div>
          <Button
            size="sm"
            variant="secondary"
            onClick={() =>
              onSaveSensitive(field.key, draft, {
                consent: field.consent.consent,
                never_autofill: field.consent.never_autofill,
              })
            }
          >
            Save sensitive value
          </Button>
          {field.consent.consented_at && (
            <p className="text-[11px] text-muted-foreground">
              Consent recorded {new Date(field.consent.consented_at).toLocaleString()}
            </p>
          )}
        </>
      )}
    </div>
  );
}

function CommonAnswerField({
  answerKey,
  label,
  initialBody,
  onSave,
  onDirtyChange,
}: {
  answerKey: string;
  label: string;
  initialBody: string;
  onSave: (body: string) => void;
  onDirtyChange?: (key: string, dirty: boolean) => void;
}) {
  const [body, setBody] = useState(initialBody);

  useEffect(() => {
    onDirtyChange?.(answerKey, body !== initialBody);
  }, [answerKey, body, initialBody, onDirtyChange]);

  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-muted-foreground" htmlFor={`answer-${answerKey}`}>
        {label}
      </label>
      <Textarea
        id={`answer-${answerKey}`}
        value={body}
        rows={3}
        onChange={(e) => setBody(e.target.value)}
        onBlur={() => {
          if (body !== initialBody) onSave(body);
        }}
      />
    </div>
  );
}

export function ProfileVault() {
  const queryClient = useQueryClient();
  const [dirtyKeys, setDirtyKeys] = useState<Set<string>>(new Set());

  const markDirty = (key: string, dirty: boolean) => {
    setDirtyKeys((prev) => {
      const next = new Set(prev);
      if (dirty) next.add(key);
      else next.delete(key);
      return next;
    });
  };

  useUnsavedChanges(dirtyKeys.size > 0);
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["profile"],
    queryFn: fetchProfile,
  });
  const answersQuery = useQuery({
    queryKey: ["common-answers"],
    queryFn: fetchCommonAnswers,
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["profile"] });
    void queryClient.invalidateQueries({ queryKey: ["common-answers"] });
  };

  const profileMutation = useMutation({
    mutationFn: patchProfile,
    onSuccess: invalidate,
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not save profile")),
  });

  const vaultMutation = useMutation({
    mutationFn: patchVault,
    onSuccess: invalidate,
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not save vault field")),
  });

  const resumeMutation = useMutation({
    mutationFn: uploadResume,
    onSuccess: () => {
      toast.success("Resume uploaded and parsed");
      invalidate();
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not upload resume")),
  });

  const answerMutation = useMutation({
    mutationFn: ({ key, body, label }: { key: string; body: string; label: string }) =>
      saveCommonAnswer(key, body, label),
    onSuccess: invalidate,
  });

  const grouped = useMemo(() => {
    const map: Record<string, VaultField[]> = {
      public: [],
      preference: [],
      sensitive: [],
    };
    for (const field of data?.fields ?? []) {
      map[field.tier]?.push(field);
    }
    return map;
  }, [data?.fields]);

  if (isLoading) return <PageLoading label="Loading profile vault…" />;
  if (isError || !data) {
    return (
      <PageError
        title="Vault unavailable"
        message="Ensure the API is running with VAULT_ENCRYPTION_KEY set."
        onRetry={() => void refetch()}
      />
    );
  }

  const score = Math.round((data.profile_completeness_score ?? 0) * 100);

  return (
    <div className="space-y-6">
      <Card className={surface.workspace}>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Profile completeness</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="flex items-center gap-3">
            <Progress value={score} className="flex-1" />
            <span className="text-sm font-medium tabular-nums">{score}%</span>
          </div>
          <ul className="grid gap-1 text-xs text-muted-foreground sm:grid-cols-2">
            {data.checklist.map((item) => (
              <li key={item.key} className="flex items-center gap-2">
                <span aria-hidden>{item.filled ? "✓" : "○"}</span>
                {item.label}
                {item.required && <span className="text-amber-600">*</span>}
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>

      <section className="space-y-3">
        <h2 className="text-sm font-medium">Canonical resume</h2>
        <p className="text-xs text-muted-foreground">
          PDF or DOCX — parsed skills feed generation and claims checks.
        </p>
        <FileUpload
          kind="resume"
          accept=".pdf,.docx"
          busy={resumeMutation.isPending}
          onFile={(file) => resumeMutation.mutate(file)}
        />
        {data.active_resume && (
          <div className="rounded-lg border border-border/60 p-3 text-sm">
            <p className="font-medium">{data.active_resume.original_filename}</p>
            <p className="mt-2 text-xs text-muted-foreground">Parsed skills</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {data.active_resume.skills.map((skill) => (
                <Badge key={skill} variant="secondary" className="font-normal">
                  {skill}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </section>

      {(["public", "preference", "sensitive"] as const).map((tier) => (
        <fieldset key={tier} className="space-y-3">
          <legend className="flex items-center gap-2 text-sm font-medium">
            {tierLabel(tier)}
            {tier === "sensitive" && (
              <ShieldAlert className="size-4 text-amber-500" aria-hidden />
            )}
          </legend>
          {tier === "sensitive" && (
            <p className="text-xs text-muted-foreground">
              Sensitive fields require explicit consent. Jober never auto-fills without your
              permission.
            </p>
          )}
          <div className="grid gap-3 md:grid-cols-2">
            {grouped[tier].map((field) => (
              <FieldRow
                key={`${field.key}:${String(field.value)}`}
                field={field}
                onDirtyChange={markDirty}
                onSavePublic={(key, value) => {
                  const patch: Record<string, unknown> = { [key]: value };
                  if (value === "true" || value === "false") {
                    patch[key] = value === "true";
                  }
                  profileMutation.mutate(patch);
                }}
                onSaveSensitive={(key, value, consent) =>
                  vaultMutation.mutate({
                    [key]: value,
                    field_consent: { [key]: consent },
                  })
                }
              />
            ))}
          </div>
        </fieldset>
      ))}

      <section className="space-y-3">
        <h2 className="text-sm font-medium">Common answers</h2>
        <div className="space-y-3">
          {(answersQuery.data ?? []).map((answer) => (
            <CommonAnswerField
              key={`${answer.id}:${answer.body}`}
              answerKey={answer.answer_key}
              label={answer.label}
              initialBody={answer.body}
              onDirtyChange={markDirty}
              onSave={(body) =>
                answerMutation.mutate({
                  key: answer.answer_key,
                  body,
                  label: answer.label,
                })
              }
            />
          ))}
        </div>
      </section>
    </div>
  );
}
