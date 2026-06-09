import { useState, useCallback, useRef } from 'react';

export function useToast() {
  const [toast, setToast] = useState({ msg: '', retry: null, visible: false });
  const timerRef = useRef(null);

  const show = useCallback((msg, retryFn = null, duration = retryFn ? 4000 : 2200) => {
    clearTimeout(timerRef.current);
    setToast({ msg, retry: retryFn, visible: true });
    timerRef.current = setTimeout(() => setToast(t => ({ ...t, visible: false })), duration);
  }, []);

  const dismiss = useCallback(() => {
    clearTimeout(timerRef.current);
    setToast(t => ({ ...t, visible: false }));
  }, []);

  return { toast, show, dismiss };
}
