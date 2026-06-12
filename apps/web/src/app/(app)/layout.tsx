import { AppChrome } from "@/app/(app)/app-chrome";
import { AppProviders } from "@/components/providers";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppProviders>
      <AppChrome>{children}</AppChrome>
    </AppProviders>
  );
}
