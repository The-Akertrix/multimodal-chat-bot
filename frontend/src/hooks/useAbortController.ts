import { useRef } from "react";

export function useAbortController(): AbortController {
  const controllerRef = useRef<AbortController | null>(null);

  if (!controllerRef.current) {
    controllerRef.current = new AbortController();
  }

  return controllerRef.current;
}
