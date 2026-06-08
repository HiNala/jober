type RecoverFn = () => Promise<boolean>;
type ExpiredFn = () => void;

let recoverSession: RecoverFn | null = null;
let onSessionExpired: ExpiredFn | null = null;

export function registerSessionHandlers(recover: RecoverFn, onExpired: ExpiredFn): void {
  recoverSession = recover;
  onSessionExpired = onExpired;
}

export async function tryRecoverSession(): Promise<boolean> {
  if (!recoverSession) return false;
  return recoverSession();
}

export function markSessionExpired(): void {
  onSessionExpired?.();
}
