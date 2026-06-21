import { useState, useEffect, useCallback, useRef } from 'react';
import { getErrorMessage } from '../utils/errors';

export const useAsync = <T>(
  asyncFunction: (...args: any[]) => Promise<T>,
  immediate = false,
  ...immediateArgs: any[]
) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<string | null>(null);

  // Keep a stable ref to the async function to prevent loops
  const asyncFuncRef = useRef(asyncFunction);
  useEffect(() => {
    asyncFuncRef.current = asyncFunction;
  }, [asyncFunction]);

  const execute = useCallback(
    async (...args: any[]) => {
      setLoading(true);
      setError(null);
      try {
        const response = await asyncFuncRef.current(...args);
        setData(response);
        setLoading(false);
        return response;
      } catch (err) {
        const errMsg = getErrorMessage(err);
        setError(errMsg);
        setData(null);
        setLoading(false);
        throw err;
      }
    },
    [] // stable execute function
  );

  useEffect(() => {
    if (immediate) {
      execute(...immediateArgs).catch(() => {});
    }
  }, [immediate, execute]);

  return {
    data,
    loading,
    error,
    execute,
    setData,
  };
};
