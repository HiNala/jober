"use client";

import { AppRouteError } from "@/components/states/app-route-error";

export default function AdminRunsError(props: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <AppRouteError {...props} />;
}
