import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export function useLetter(letterId) {
  const { user } = useAuth();
  const [letter, setLetter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchLetter = async () => {
    if (!user?.firmId || !letterId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await api.get(`/${user.firmId}/letters/${letterId}`);
      setLetter(response.data);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to fetch letter';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLetter();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [letterId, user?.firmId]);

  return { letter, loading, error, refetch: fetchLetter };
}

export function useUpdateLetter() {
  const { user } = useAuth();
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  const updateLetter = async (letterId, title = null, content = null) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    if (!letterId) {
      throw new Error('Letter ID is required');
    }

    setUpdating(true);
    setError(null);

    try {
      const updateData = {};
      if (title !== null) {
        updateData.title = title;
      }
      if (content !== null) {
        updateData.content = content;
      }

      const response = await api.put(
        `/${user.firmId}/letters/${letterId}`,
        updateData
      );

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to update letter';
      setError(errorMessage);
      throw err;
    } finally {
      setUpdating(false);
    }
  };

  return { updateLetter, updating, error, setError };
}

export function useFinalizeLetter() {
  const { user } = useAuth();
  const [finalizing, setFinalizing] = useState(false);
  const [error, setError] = useState(null);

  const finalizeLetter = async (letterId) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    if (!letterId) {
      throw new Error('Letter ID is required');
    }

    setFinalizing(true);
    setError(null);

    try {
      const response = await api.post(
        `/${user.firmId}/letters/${letterId}/finalize`
      );

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to finalize letter';
      setError(errorMessage);
      throw err;
    } finally {
      setFinalizing(false);
    }
  };

  return { finalizeLetter, finalizing, error, setError };
}

