"use client";

import { useCallback, useState } from "react";

import {
  mapApiErrors,
  remapFieldErrors,
  type ApiFieldErrors,
  type MappedApiErrors,
} from "@/lib/forms/map-api-errors";

type UseFormSubmitOptions = {
  fallbackError?: string;
  fieldAliases?: Record<string, string>;
};

export function useFormSubmit(options: UseFormSubmitOptions = {}) {
  const [pending, setPending] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<ApiFieldErrors>({});

  const clearErrors = useCallback(() => {
    setFormError(null);
    setFieldErrors({});
  }, []);

  const applyMapped = useCallback(
    (mapped: MappedApiErrors) => {
      const fields = options.fieldAliases
        ? remapFieldErrors(mapped.fieldErrors, options.fieldAliases)
        : mapped.fieldErrors;
      setFieldErrors(fields);
      setFormError(
        mapped.formError ??
          (Object.keys(fields).length > 0 ? null : options.fallbackError ?? "Something went wrong"),
      );
    },
    [options.fieldAliases, options.fallbackError],
  );

  const run = useCallback(
    async <T>(fn: () => Promise<T>, fallback?: string): Promise<T | undefined> => {
      setPending(true);
      clearErrors();
      try {
        return await fn();
      } catch (err: unknown) {
        applyMapped(mapApiErrors(err, fallback ?? options.fallbackError ?? "Something went wrong"));
        return undefined;
      } finally {
        setPending(false);
      }
    },
    [applyMapped, clearErrors, options.fallbackError],
  );

  const setClientFieldErrors = useCallback((errors: ApiFieldErrors) => {
    const fields = options.fieldAliases
      ? remapFieldErrors(errors, options.fieldAliases)
      : errors;
    setFieldErrors(fields);
    setFormError(null);
  }, [options.fieldAliases]);

  return {
    pending,
    formError,
    fieldErrors,
    run,
    clearErrors,
    setClientFieldErrors,
    setFormError,
    setFieldErrors,
  };
}
