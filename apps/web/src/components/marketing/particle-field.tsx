"use client";

import { usePrefersReducedMotion } from "@/lib/hooks/use-prefers-reduced-motion";

interface ParticleFieldProps {
  className?: string;
  density?: "low" | "medium" | "high";
}

const DOTS: { cx: string; cy: string; r: number; delay: string; dur: string }[] = [
  { cx: "8%",  cy: "12%", r: 1.5, delay: "0s",    dur: "4.2s" },
  { cx: "18%", cy: "72%", r: 1,   delay: "1.1s",  dur: "3.8s" },
  { cx: "25%", cy: "38%", r: 2,   delay: "0.4s",  dur: "5.1s" },
  { cx: "35%", cy: "88%", r: 1,   delay: "2.2s",  dur: "4.7s" },
  { cx: "42%", cy: "22%", r: 1.5, delay: "0.8s",  dur: "6.0s" },
  { cx: "52%", cy: "60%", r: 1,   delay: "1.6s",  dur: "3.5s" },
  { cx: "61%", cy: "14%", r: 2,   delay: "0.2s",  dur: "4.9s" },
  { cx: "68%", cy: "78%", r: 1.5, delay: "2.8s",  dur: "5.3s" },
  { cx: "74%", cy: "44%", r: 1,   delay: "1.3s",  dur: "4.1s" },
  { cx: "82%", cy: "30%", r: 2,   delay: "0.6s",  dur: "5.8s" },
  { cx: "89%", cy: "65%", r: 1,   delay: "2.0s",  dur: "3.9s" },
  { cx: "94%", cy: "18%", r: 1.5, delay: "1.5s",  dur: "4.6s" },
  { cx: "12%", cy: "50%", r: 1,   delay: "3.1s",  dur: "5.2s" },
  { cx: "47%", cy: "82%", r: 2,   delay: "0.9s",  dur: "4.4s" },
  { cx: "78%", cy: "90%", r: 1,   delay: "2.5s",  dur: "6.1s" },
  { cx: "5%",  cy: "88%", r: 1.5, delay: "1.8s",  dur: "3.7s" },
  { cx: "30%", cy: "6%",  r: 1,   delay: "0.3s",  dur: "5.5s" },
  { cx: "58%", cy: "95%", r: 2,   delay: "2.3s",  dur: "4.3s" },
  { cx: "87%", cy: "8%",  r: 1,   delay: "1.0s",  dur: "5.0s" },
  { cx: "97%", cy: "52%", r: 1.5, delay: "3.4s",  dur: "4.8s" },
];

export function ParticleField({ className, density = "medium" }: ParticleFieldProps) {
  const reduced = usePrefersReducedMotion();
  const dots = density === "low" ? DOTS.slice(0, 10) : density === "high" ? DOTS : DOTS.slice(0, 14);

  return (
    <svg
      aria-hidden="true"
      className={className}
      style={{ position: "absolute", inset: 0, width: "100%", height: "100%", pointerEvents: "none" }}
      xmlns="http://www.w3.org/2000/svg"
    >
      {dots.map((d, i) => (
        <circle key={i} cx={d.cx} cy={d.cy} r={d.r} fill="oklch(0.78 0.14 68)" opacity="0.3">
          {!reduced && (
            <animate
              attributeName="opacity"
              values="0.15;0.45;0.15"
              dur={d.dur}
              begin={d.delay}
              repeatCount="indefinite"
            />
          )}
        </circle>
      ))}
    </svg>
  );
}
