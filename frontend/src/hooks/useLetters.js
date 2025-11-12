import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export function useLetters(sortBy = null, sortOrder = 'desc', statusFilter = null, searchQuery = null) {
  const { user } = useAuth();
  const [letters, setLetters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [total, setTotal] = useState(0);

  const fetchLetters = async () => {
    if (!user?.firmId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const params = {
        page: 1,
        page_size: 100, // Fetch larger set for client-side filtering
      };
      
      if (sortBy) {
        params.sort_by = sortBy;
        params.sort_order = sortOrder;
      }

      const response = await api.get(`/${user.firmId}/letters/`, { params });
      let items = response.data.items || [];
      
      // Client-side filtering by status
      if (statusFilter && statusFilter !== 'all') {
        items = items.filter(letter => letter.status === statusFilter);
      }
      
      // Client-side search
      if (searchQuery && searchQuery.trim()) {
        const query = searchQuery.toLowerCase().trim();
        items = items.filter(letter => 
          letter.title?.toLowerCase().includes(query) ||
          letter.template_name?.toLowerCase().includes(query)
        );
      }
      
      setLetters(items);
      setTotal(items.length); // Use filtered count for display
    } catch (err) {
      setError(err.message || 'Failed to fetch letters');
      setLetters([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLetters();
  }, [user?.firmId, sortBy, sortOrder, statusFilter, searchQuery]);

  return { 
    letters, 
    loading, 
    error, 
    total,
    refetch: fetchLetters
  };
}

export function useDeleteLetter() {
  const { user } = useAuth();
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);

  const deleteLetter = async (letterId) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setDeleting(true);
    setError(null);

    try {
      await api.delete(`/${user.firmId}/letters/${letterId}`);
      return true;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to delete letter';
      setError(errorMessage);
      throw err;
    } finally {
      setDeleting(false);
    }
  };

  return { deleteLetter, deleting, error };
}

export function useExportLetter() {
  const { user } = useAuth();
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState(null);

  const exportLetter = async (letterId) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setExporting(true);
    setError(null);

    try {
      const response = await api.post(`/${user.firmId}/letters/${letterId}/export`);
      const { download_url } = response.data;
      
      // Trigger browser download
      const link = document.createElement('a');
      link.href = download_url;
      link.download = '';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return download_url;
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to export letter';
      setError(errorMessage);
      throw err;
    } finally {
      setExporting(false);
    }
  };

  return { exportLetter, exporting, error };
}

