import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export function useDocuments(sortBy = null, sortOrder = 'desc') {
  const { user } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user?.firmId) {
      setLoading(false);
      return;
    }

    const fetchDocuments = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const params = {
          page: 1,
          page_size: 100,
        };
        
        if (sortBy) {
          params.sort_by = sortBy;
          params.sort_order = sortOrder;
        }

        const response = await api.get(`/${user.firmId}/documents/`, { params });
        setDocuments(response.data.items || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch documents');
        setDocuments([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [user?.firmId, sortBy, sortOrder]);

  return { documents, loading, error, refetch: () => {
    if (user?.firmId) {
      const fetchDocuments = async () => {
        try {
          setLoading(true);
          setError(null);
          
          const params = {
            page: 1,
            page_size: 100,
          };
          
          if (sortBy) {
            params.sort_by = sortBy;
            params.sort_order = sortOrder;
          }

          const response = await api.get(`/${user.firmId}/documents/`, { params });
          setDocuments(response.data.items || []);
        } catch (err) {
          setError(err.message || 'Failed to fetch documents');
        } finally {
          setLoading(false);
        }
      };
      fetchDocuments();
    }
  } };
}

export function useDocumentUpload() {
  const { user } = useAuth();

  const uploadDocument = async (file, onProgress) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    const formData = new FormData();
    formData.append('file', file);

    const params = {};
    if (user.id) {
      params.uploaded_by = user.id;
    }

    const response = await api.post(
      `/${user.firmId}/documents/`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        params,
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const percentCompleted = Math.min(
              100,
              Math.max(
                0,
                Math.round((progressEvent.loaded * 100) / progressEvent.total)
              )
            );
            onProgress(percentCompleted);
          } else if (onProgress && progressEvent.lengthComputable === false) {
            // If total is not available, we can't calculate accurate progress
            // But we can still show some indication (e.g., indeterminate)
            // For now, we'll just not update progress
          }
        },
      }
    );

    return response.data;
  };

  return { uploadDocument };
}

export function useDocumentDelete() {
  const { user } = useAuth();
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);

  const deleteDocument = async (documentId) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setDeleting(true);
    setError(null);

    try {
      await api.delete(`/${user.firmId}/documents/${documentId}`);
      return true;
    } catch (err) {
      setError(err.message || 'Failed to delete document');
      throw err;
    } finally {
      setDeleting(false);
    }
  };

  return { deleteDocument, deleting, error };
}

export function useDocumentDownload() {
  const { user } = useAuth();
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);

  const downloadDocument = async (documentId) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setDownloading(true);
    setError(null);

    try {
      const response = await api.get(`/${user.firmId}/documents/${documentId}/download`);
      const { url } = response.data;
      
      // Trigger browser download
      const link = document.createElement('a');
      link.href = url;
      link.download = '';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      return true;
    } catch (err) {
      setError(err.message || 'Failed to download document');
      throw err;
    } finally {
      setDownloading(false);
    }
  };

  return { downloadDocument, downloading, error };
}

