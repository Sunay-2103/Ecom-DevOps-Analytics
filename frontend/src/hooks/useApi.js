import { useState, useEffect, useCallback } from 'react';

/**
 * Generic data-fetching hook.
 * @param {Function} apiFn  - Function that returns a Promise (from api.js)
 * @param {Array}    deps   - Re-fetch whenever these change
 */
export default function useApi(apiFn, deps = []) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiFn();
      setData(result);
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.message ?? 'Unknown error';
      setError(msg);
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { fetch(); }, [fetch]);

  return { data, loading, error, refetch: fetch };
}
