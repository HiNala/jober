"use client";

import { useEffect, useRef } from "react";

/**
 * Wires an IntersectionObserver to the returned ref. When the element enters
 * the viewport, adds the CSS class `jober-revealed` and removes `jober-hidden`.
 * Use with the `.jober-scroll-reveal` stylesheet rule in globals.css.
 */
export function useScrollReveal<T extends HTMLElement = HTMLElement>(
  threshold = 0.15,
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      el.classList.remove("jober-hidden");
      return;
    }

    el.classList.add("jober-hidden");

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          el.classList.add("jober-revealed");
          el.classList.remove("jober-hidden");
          observer.disconnect();
        }
      },
      { threshold },
    );

    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold]);

  return ref;
}
