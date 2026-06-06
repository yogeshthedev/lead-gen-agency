import React, { useState, useEffect } from 'react';
import { leadService } from '../services/api';
import { Search, MapPin, Send, MessageCircle, ArrowRightToLine, Check } from 'lucide-react';
import OutreachModal from '../components/OutreachModal';
import './Leads.css';

export default function Leads() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [responseFilter, setResponseFilter] = useState('');
  const [websiteFilter, setWebsiteFilter] = useState('');
  const [outreachLead, setOutreachLead] = useState(null);

  // Track local edits for notes and response per lead
  const [editedNotes, setEditedNotes] = useState({});
  const [editedResponses, setEditedResponses] = useState({});
  const [savingNotes, setSavingNotes] = useState({});
  const [savingResponses, setSavingResponses] = useState({});
  const [pipelineFilter, setPipelineFilter] = useState('');
  const [togglingPipeline, setTogglingPipeline] = useState({});

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const data = await leadService.getLeads();
      const fetchedLeads = data.leads || [];
      setLeads(fetchedLeads);
      
      const notesMap = {};
      const responsesMap = {};
      fetchedLeads.forEach(l => {
        const id = l._id || l.id;
        notesMap[id] = l.notes || '';
        responsesMap[id] = l.response || 'new';
      });
      setEditedNotes(prev => {
        const merged = { ...notesMap };
        Object.keys(prev).forEach(key => {
          if (savingNotes[key]) merged[key] = prev[key];
        });
        return merged;
      });
      setEditedResponses(prev => {
        const merged = { ...responsesMap };
        Object.keys(prev).forEach(key => {
          if (savingResponses[key]) merged[key] = prev[key];
        });
        return merged;
      });
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleNotesChange = (leadId, value) => {
    setEditedNotes(prev => ({ ...prev, [leadId]: value }));
  };

  const handleNotesSave = async (leadId) => {
    const notes = editedNotes[leadId] ?? '';
    setSavingNotes(prev => ({ ...prev, [leadId]: true }));
    try {
      await leadService.updateNotes(leadId, notes);
      setLeads(prev => prev.map(l => {
        const id = l._id || l.id;
        if (id === leadId) return { ...l, notes };
        return l;
      }));
    } catch (err) {
      console.error('Failed to save notes:', err);
    } finally {
      setSavingNotes(prev => ({ ...prev, [leadId]: false }));
    }
  };

  const handleResponseChange = async (leadId, value) => {
    setEditedResponses(prev => ({ ...prev, [leadId]: value }));
    setSavingResponses(prev => ({ ...prev, [leadId]: true }));
    try {
      await leadService.updateResponse(leadId, value);
      setLeads(prev => prev.map(l => {
        const id = l._id || l.id;
        if (id === leadId) return { ...l, response: value };
        return l;
      }));
    } catch (err) {
      console.error('Failed to save response:', err);
    } finally {
      setSavingResponses(prev => ({ ...prev, [leadId]: false }));
    }
  };

  const handleTogglePipeline = async (leadId, currentValue) => {
    const newValue = !currentValue;
    setTogglingPipeline(prev => ({ ...prev, [leadId]: true }));
    try {
      await leadService.updateLead(leadId, { in_pipeline: newValue });
      setLeads(prev => prev.map(l => {
        const id = l._id || l.id;
        if (id === leadId) return { ...l, in_pipeline: newValue };
        return l;
      }));
    } catch (err) {
      console.error('Failed to toggle pipeline:', err);
    } finally {
      setTogglingPipeline(prev => ({ ...prev, [leadId]: false }));
    }
  };

  const filteredLeads = leads.filter(l => {
    const matchesSearch = Object.values(l).join(' ').toLowerCase().includes(search.toLowerCase());
    const matchesResponse = !responseFilter || (editedResponses[l._id || l.id] || l.response || 'new') === responseFilter;
    
    let matchesWebsite = true;
    if (websiteFilter === 'has_website') matchesWebsite = !!(l.website || l.has_website === 'yes');
    if (websiteFilter === 'no_website') matchesWebsite = !(l.website || l.has_website === 'yes');

    let matchesPipeline = true;
    if (pipelineFilter === 'in_pipeline') matchesPipeline = !!l.in_pipeline;
    if (pipelineFilter === 'not_in_pipeline') matchesPipeline = !l.in_pipeline;

    return matchesSearch && matchesResponse && matchesWebsite && matchesPipeline;
  });

  return (
    <div className="leads-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">All Leads (Indian)</h1>
        <p className="subtitle">Manage your local WhatsApp lead database</p>
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
            <label className="input-label">Response</label>
            <select className="input-field" value={responseFilter} onChange={e => setResponseFilter(e.target.value)}>
              <option value="">All Responses</option>
              <option value="new">New</option>
              <option value="interested">Interested</option>
              <option value="not_interested">Not Interested</option>
              <option value="no_response">No Response</option>
            </select>
          </div>
          <div className="input-group" style={{ width: '180px' }}>
            <label className="input-label">Website</label>
            <select className="input-field" value={websiteFilter} onChange={e => setWebsiteFilter(e.target.value)}>
              <option value="">All</option>
              <option value="has_website">Has Website</option>
              <option value="no_website">No Website</option>
            </select>
          </div>
          <div className="input-group" style={{ width: '180px' }}>
            <label className="input-label">Pipeline</label>
            <select className="input-field" value={pipelineFilter} onChange={e => setPipelineFilter(e.target.value)}>
              <option value="">All</option>
              <option value="in_pipeline">In Pipeline</option>
              <option value="not_in_pipeline">Not in Pipeline</option>
            </select>
          </div>
          <button className="btn btn-secondary" onClick={() => {
            setSearch(''); setResponseFilter(''); setWebsiteFilter(''); setPipelineFilter('');
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
                <th>Response</th>
                <th>Notes</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredLeads.map(lead => {
                const leadId = lead._id || lead.id;
                return (
                <tr key={leadId}>
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
                      <span className={`badge ${lead.has_website === 'yes' ? 'badge-success' : 'badge-default'}`}>
                        {lead.has_website === 'yes' ? 'Has Website' : 'No Website'}
                      </span>
                    )}
                  </td>
                  <td>
                    <select 
                      className="input-field text-sm"
                      style={{ padding: '0.25rem', minWidth: '130px' }}
                      value={editedResponses[leadId] || lead.response || 'new'}
                      onChange={(e) => handleResponseChange(leadId, e.target.value)}
                    >
                      <option value="new">New</option>
                      <option value="no_response">No Response</option>
                      <option value="interested">Interested</option>
                      <option value="not_interested">Not Interested</option>
                    </select>
                    {savingResponses[leadId] && <span className="text-xs text-tertiary">saving...</span>}
                  </td>
                  <td>
                    <textarea 
                      className="input-field text-sm"
                      style={{ minHeight: '60px', minWidth: '200px', resize: 'vertical' }}
                      value={editedNotes[leadId] ?? lead.notes ?? ''}
                      placeholder="Add notes..."
                      onChange={(e) => handleNotesChange(leadId, e.target.value)}
                      onBlur={() => handleNotesSave(leadId)}
                    />
                    {savingNotes[leadId] && <span className="text-xs text-tertiary">saving...</span>}
                  </td>
                  <td className="font-semibold">{lead.lead_score || 0}</td>
                  <td>
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleTogglePipeline(leadId, lead.in_pipeline)}
                        className={`btn p-2 ${lead.in_pipeline ? 'btn-pipeline-active' : 'btn-outline'}`}
                        title={lead.in_pipeline ? 'Remove from Pipeline' : 'Add to Pipeline'}
                        disabled={togglingPipeline[leadId]}
                      >
                        {lead.in_pipeline ? <Check size={14} /> : <ArrowRightToLine size={14} />}
                      </button>
                      <button 
                        onClick={() => setOutreachLead(lead)} 
                        className="btn btn-primary p-2" 
                        style={{ backgroundColor: '#25D366', borderColor: '#25D366' }}
                        title="Send WhatsApp"
                      >
                        <MessageCircle size={14} />
                      </button>
                      {lead.maps_url ? (
                        <a href={lead.maps_url} target="_blank" rel="noreferrer" className="btn btn-outline p-2" title="View on Maps">
                          <MapPin size={14} />
                        </a>
                      ) : (
                        <a href={`https://www.google.com/maps/search/${encodeURIComponent((lead.business_name || '') + ' ' + (lead.city || ''))}`} target="_blank" rel="noreferrer" className="btn btn-outline p-2" title="Search on Maps">
                          <MapPin size={14} />
                        </a>
                      )}
                    </div>
                  </td>
                </tr>
                );
              })}
              {filteredLeads.length === 0 && (
                <tr>
                  <td colSpan="7" className="text-center p-6 text-tertiary">No leads found matching your criteria.</td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>

      {outreachLead && (
        <OutreachModal 
          lead={outreachLead} 
          initialTab="whatsapp"
          onClose={() => {
            setOutreachLead(null);
            fetchLeads(); // refresh in case status changed
          }} 
        />
      )}
    </div>
  );
}
