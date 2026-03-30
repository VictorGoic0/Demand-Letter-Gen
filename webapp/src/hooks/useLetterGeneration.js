import { useState } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export function useGenerateLetter() {
  const { user } = useAuth();
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  const generateLetter = async (templateId, documentIds, title = null) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    if (!templateId) {
      throw new Error('Template is required');
    }

    if (!documentIds || documentIds.length === 0) {
      throw new Error('At least one document is required');
    }

    if (documentIds.length > 5) {
      throw new Error('Maximum 5 documents allowed');
    }

    setGenerating(true);
    setError(null);

    try {
      const params = {
        firm_id: user.firmId,
      };

      if (user.id) {
        params.created_by = user.id;
      }

      const requestBody = {
        template_id: templateId,
        document_ids: documentIds,
      };

      if (title && title.trim()) {
        requestBody.title = title.trim();
      }

      const response = await api.post(
        '/generate/letter',
        requestBody,
        { params }
      );

      return response.data;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to generate letter';
      setError(errorMessage);
      throw err;
    } finally {
      setGenerating(false);
    }
  };

  return { generateLetter, generating, error, setError };
}

