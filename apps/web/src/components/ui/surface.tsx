import * as React from "react";

import {
  surfaceVariants,
  type SurfaceFamily,
  type SurfacePadding,
} from "@/lib/design/surface-variants";
import { cn } from "@/lib/utils";

type SurfaceElement = keyof Pick<
  React.JSX.IntrinsicElements,
  "div" | "section" | "article" | "aside" | "li" | "figure"
>;

export interface SurfaceProps extends React.HTMLAttributes<HTMLElement> {
  family?: SurfaceFamily;
  padding?: SurfacePadding;
  as?: SurfaceElement;
}

export function Surface({
  family = "workspace",
  padding = "none",
  as: Component = "div",
  className,
  ...props
}: SurfaceProps) {
  return (
    <Component
      data-surface-family={family}
      className={cn(surfaceVariants({ family, padding }), className)}
      {...props}
    />
  );
}
