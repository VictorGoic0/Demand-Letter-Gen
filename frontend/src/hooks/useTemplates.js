import { useState, useEffect } from 'react';
import api from '@/lib/api';
import { useAuth } from '@/contexts/AuthContext';

export function useTemplates(sortBy = null, sortOrder = 'asc') {
  const { user } = useAuth();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user?.firmId) {
      setLoading(false);
      return;
    }

    const fetchTemplates = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const params = {};
        
        if (sortBy) {
          params.sort_by = sortBy;
          params.sort_order = sortOrder;
        }

        const response = await api.get(`/${user.firmId}/templates/`, { params });
        setTemplates(response.data.items || []);
      } catch (err) {
        setError(err.message || 'Failed to fetch templates');
        setTemplates([]);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplates();
  }, [user?.firmId, sortBy, sortOrder]);

  return { 
    templates, 
    loading, 
    error, 
    refetch: () => {
      if (user?.firmId) {
        const fetchTemplates = async () => {
          try {
            setLoading(true);
            setError(null);
            
            const params = {};
            
            if (sortBy) {
              params.sort_by = sortBy;
              params.sort_order = sortOrder;
            }

            const response = await api.get(`/${user.firmId}/templates/`, { params });
            setTemplates(response.data.items || []);
          } catch (err) {
            setError(err.message || 'Failed to fetch templates');
          } finally {
            setLoading(false);
          }
        };
        fetchTemplates();
      }
    }
  };
}

export function useDefaultTemplate() {
  const { user } = useAuth();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user?.firmId) {
      setLoading(false);
      return;
    }

    const fetchDefaultTemplate = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await api.get(`/${user.firmId}/templates/default`);
        setTemplate(response.data);
      } catch (err) {
        // 404 is expected if no default template exists
        if (err.status === 404) {
          setTemplate(null);
        } else {
          setError(err.message || 'Failed to fetch default template');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDefaultTemplate();
  }, [user?.firmId]);

  return { template, loading, error };
}

export function useCreateTemplate() {
  const { user } = useAuth();
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState(null);

  const createTemplate = async (templateData) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setCreating(true);
    setError(null);

    try {
      const params = {};
      if (user.id) {
        params.created_by = user.id;
      }

      const response = await api.post(
        `/${user.firmId}/templates/`,
        templateData,
        { params }
      );
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to create template';
      setError(errorMessage);
      throw err;
    } finally {
      setCreating(false);
    }
  };

  return { createTemplate, creating, error };
}

export function useUpdateTemplate() {
  const { user } = useAuth();
  const [updating, setUpdating] = useState(false);
  const [error, setError] = useState(null);

  const updateTemplate = async (templateId, templateData) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setUpdating(true);
    setError(null);

    try {
      const response = await api.put(
        `/${user.firmId}/templates/${templateId}`,
        templateData
      );
      return response.data;
    } catch (err) {
      const errorMessage = err.message || 'Failed to update template';
      setError(errorMessage);
      throw err;
    } finally {
      setUpdating(false);
    }
  };

  return { updateTemplate, updating, error };
}

export function useDeleteTemplate() {
  const { user } = useAuth();
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState(null);

  const deleteTemplate = async (templateId) => {
    if (!user?.firmId) {
      throw new Error('User not authenticated');
    }

    setDeleting(true);
    setError(null);

    try {
      await api.delete(`/${user.firmId}/templates/${templateId}`);
      return true;
    } catch (err) {
      const errorMessage = err.message || 'Failed to delete template';
      setError(errorMessage);
      throw err;
    } finally {
      setDeleting(false);
    }
  };

  return { deleteTemplate, deleting, error };
}

export function useTemplate(templateId) {
  const { user } = useAuth();
  const [template, setTemplate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!user?.firmId || !templateId) {
      setLoading(false);
      return;
    }

    const fetchTemplate = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await api.get(`/${user.firmId}/templates/${templateId}`);
        setTemplate(response.data);
      } catch (err) {
        setError(err.message || 'Failed to fetch template');
        setTemplate(null);
      } finally {
        setLoading(false);
      }
    };

    fetchTemplate();
  }, [user?.firmId, templateId]);

  return { template, loading, error, refetch: () => {
    if (user?.firmId && templateId) {
      const fetchTemplate = async () => {
        try {
          setLoading(true);
          setError(null);
          
          const response = await api.get(`/${user.firmId}/templates/${templateId}`);
          setTemplate(response.data);
        } catch (err) {
          setError(err.message || 'Failed to fetch template');
        } finally {
          setLoading(false);
        }
      };
      fetchTemplate();
    }
  }};
}

