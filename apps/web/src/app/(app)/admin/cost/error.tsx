"use client";

import { AppRouteError } from "@/components/states/app-route-error";

export default function AdminCostError(props: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <AppRouteError {...props} />;
}
