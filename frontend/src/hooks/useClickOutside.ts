import { useEffect, useRef } from 'react';

/**
 * Hook to handle clicks outside of a ref element
 * More efficient than adding/removing listeners on every state change
 */
export function useClickOutside<T extends HTMLElement = HTMLElement>(
  handler: () => void,
  active: boolean = true
) {
  const ref = useRef<T>(null);

  useEffect(() => {
    if (!active) return;

    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handler();
      }
    };

    // Use capture phase for better performance
    document.addEventListener('click', handleClickOutside, true);

    return () => {
      document.removeEventListener('click', handleClickOutside, true);
    };
  }, [handler, active]);

  return ref;
}
