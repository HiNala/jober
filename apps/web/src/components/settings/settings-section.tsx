import { Surface } from "@/components/ui/surface";
import { cn } from "@/lib/utils";

export function SettingsSection({
  headingId,
  title,
  children,
  className,
}: {
  headingId: string;
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <Surface
      as="section"
      family="workspace"
      padding="md"
      aria-labelledby={headingId}
      className={cn(className)}
    >
      <h2 id={headingId} className="text-sm font-medium">
        {title}
      </h2>
      <div className="mt-4">{children}</div>
    </Surface>
  );
}
