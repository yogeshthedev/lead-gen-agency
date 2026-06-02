import React, { useState, useEffect } from 'react';
import { leadService } from '../services/api';
import { Search, Filter, Mail, Phone, MapPin, Edit2, Send } from 'lucide-react';
import OutreachModal from '../components/OutreachModal';
import './Leads.css';

export default function Leads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [responseFilter, setResponseFilter] = useState('');
  const [outreachLead, setOutreachLead] = useState(null);

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const data = await leadService.getLeads();
      setLeads(data.leads || []);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const filteredLeads = leads.filter(l => {
    const matchesSearch = Object.values(l).join(' ').toLowerCase().includes(search.toLowerCase());
    const matchesStatus = !statusFilter || l.email_status === statusFilter;
    const matchesResponse = !responseFilter || l.response === responseFilter;
    return matchesSearch && matchesStatus && matchesResponse;
  });

  return (
    <div className="leads-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">All Leads</h1>
        <p className="subtitle">Manage your lead database and update statuses</p>
      </div>

      <div className="glass-panel p-6 mb-6">
        <div className="flex gap-4 flex-wrap items-end">
          <div className="input-group" style={{ flex: 1, minWidth: '200px' }}>
            <label className="input-label">Search</label>
            <div className="relative">
              <input 
                className="input-field" 
                placeholder="Search business, phone, email..." 
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>
          <div className="input-group" style={{ width: '180px' }}>
            <label className="input-label">Status</label>
            <select className="input-field" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="not_sent">Not Sent</option>
              <option value="sent">Sent</option>
              <option value="follow_up">Follow Up</option>
              <option value="replied">Replied</option>
              <option value="interested">Interested</option>
              <option value="not_interested">Not Interested</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <div className="input-group" style={{ width: '180px' }}>
            <label className="input-label">Response</label>
            <select className="input-field" value={responseFilter} onChange={e => setResponseFilter(e.target.value)}>
              <option value="">All Responses</option>
              <option value="new">New</option>
              <option value="interested">Interested</option>
              <option value="not_interested">Not Interested</option>
              <option value="no_response">No Response</option>
            </select>
          </div>
          <button className="btn btn-secondary" onClick={() => {
            setSearch(''); setStatusFilter(''); setResponseFilter('');
          }}>
            Clear Filters
          </button>
        </div>
      </div>

      <div className="table-container">
        {loading ? (
          <div className="p-6 text-center text-tertiary">Loading leads...</div>
        ) : (
          <table className="table">
            <thead>
              <tr>
                <th>Business Name</th>
                <th>Contact</th>
                <th>Website</th>
                <th>Status</th>
                <th>Response</th>
                <th>Notes</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredLeads.map(lead => (
                <tr key={lead._id || lead.id}>
                  <td>
                    <div className="font-semibold">{lead.business_name}</div>
                    <div className="text-tertiary text-sm">{lead.city} • {lead.category}</div>
                  </td>
                  <td>
                    <div className="mono text-sm">{lead.phone || '-'}</div>
                    <div className="mono text-sm text-tertiary">{lead.email || '-'}</div>
                  </td>
                  <td>
                    {lead.website ? (
                      <a href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`} target="_blank" rel="noreferrer" className="text-info text-sm underline" style={{ wordBreak: 'break-all' }}>
                        {lead.website}
                      </a>
                    ) : (
                      <span className="text-tertiary text-sm">-</span>
                    )}
                  </td>
                  <td>
                    <span className={`badge badge-${lead.email_status === 'interested' ? 'success' : lead.email_status === 'replied' ? 'warning' : 'default'}`}>
                      {lead.email_status || 'not_sent'}
                    </span>
                  </td>
                  <td>
                    <select 
                      className="input-field text-sm"
                      style={{ padding: '0.25rem', minWidth: '130px' }}
                      defaultValue={lead.response || 'new'}
                      onChange={(e) => leadService.updateResponse(lead._id || lead.id, e.target.value)}
                    >
                      <option value="new">New</option>
                      <option value="no_response">No Response</option>
                      <option value="interested">Interested</option>
                      <option value="not_interested">Not Interested</option>
                    </select>
                  </td>
                  <td>
                    <textarea 
                      className="input-field text-sm"
                      style={{ minHeight: '60px', minWidth: '200px', resize: 'vertical' }}
                      defaultValue={lead.notes || ''}
                      placeholder="Add notes..."
                      onBlur={(e) => leadService.updateNotes(lead._id || lead.id, e.target.value)}
                    />
                  </td>
                  <td className="font-semibold">{lead.lead_score || 0}</td>
                  <td>
                    <div className="flex gap-2">
                      <button onClick={() => setOutreachLead(lead)} className="btn btn-primary bg-accent hover:bg-accent/90 p-2" title="Send Message">
                        <Send size={14} />
                      </button>
                      {lead.maps_url && (
                        <a href={lead.maps_url} target="_blank" rel="noreferrer" className="btn btn-outline p-2" title="View on Maps">
                          <MapPin size={14} />
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
              {filteredLeads.length === 0 && (
                <tr>
                  <td colSpan="8" className="text-center p-6 text-tertiary">No leads found matching your criteria.</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {outreachLead && (
        <OutreachModal 
          lead={outreachLead} 
          onClose={() => {
            setOutreachLead(null);
            fetchLeads(); // refresh in case status changed
          }} 
        />
      )}
    </div>
  );
}
