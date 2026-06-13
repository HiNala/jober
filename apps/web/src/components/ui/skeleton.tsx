import { motionSkeleton } from "@/lib/design/motion"
import { cn } from "@/lib/utils"

function Skeleton({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="skeleton"
      className={cn("rounded-md", motionSkeleton, className)}
      {...props}
    />
  )
}

export { Skeleton }
