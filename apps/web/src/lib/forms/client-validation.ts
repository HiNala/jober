import type { ApiFieldErrors } from "@/lib/forms/map-api-errors";

export const PASSWORD_MIN_LENGTH = 10;
export const PASSWORD_MAX_LENGTH = 128;
export const DISPLAY_NAME_MAX_LENGTH = 255;

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export function validateEmail(value: string): string | null {
  const trimmed = value.trim();
  if (!trimmed) return "Email is required";
  if (!EMAIL_PATTERN.test(trimmed)) return "Enter a valid email address";
  return null;
}

export function validatePassword(value: string, label = "Password"): string | null {
  if (!value) return `${label} is required`;
  if (value.length < PASSWORD_MIN_LENGTH) {
    return `Use at least ${PASSWORD_MIN_LENGTH} characters`;
  }
  if (value.length > PASSWORD_MAX_LENGTH) {
    return `${label} must be at most ${PASSWORD_MAX_LENGTH} characters`;
  }
  return null;
}

export function validateSignup(fields: {
  email: string;
  password: string;
  displayName?: string;
}): ApiFieldErrors {
  const errors: ApiFieldErrors = {};
  const emailError = validateEmail(fields.email);
  if (emailError) errors.email = emailError;
  const passwordError = validatePassword(fields.password);
  if (passwordError) errors.password = passwordError;
  if (fields.displayName && fields.displayName.length > DISPLAY_NAME_MAX_LENGTH) {
    errors.display_name = `Display name must be at most ${DISPLAY_NAME_MAX_LENGTH} characters`;
  }
  return errors;
}

export function validateResetPassword(password: string): ApiFieldErrors {
  const errors: ApiFieldErrors = {};
  const passwordError = validatePassword(password, "New password");
  if (passwordError) errors.password = passwordError;
  return errors;
}
