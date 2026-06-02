const API_URL = 'http://localhost:5000/api';

export const callApi = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    });
    
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'API Request Failed');
    }
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

export const leadService = {
  getLeads: (params) => {
    const query = new URLSearchParams(params).toString();
    return callApi(`/leads${query ? `?${query}` : ''}`);
  },
  getStats: () => callApi('/leads/stats'),
  updateStatus: (lead_id, status) => callApi('/leads/update-status', {
    method: 'POST',
    body: JSON.stringify({ lead_id, status })
  }),
  updateNotes: (lead_id, notes) => callApi('/leads/update-notes', {
    method: 'POST',
    body: JSON.stringify({ lead_id, notes })
  }),
  updateResponse: (lead_id, response) => callApi('/leads/update-response', {
    method: 'POST',
    body: JSON.stringify({ lead_id, response })
  }),
  updateLead: (lead_id, updates) => callApi('/leads/update', {
    method: 'POST',
    body: JSON.stringify({ lead_id, updates })
  })
};
