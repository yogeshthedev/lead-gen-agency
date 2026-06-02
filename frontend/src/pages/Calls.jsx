import React, { useState, useEffect } from 'react';
import { leadService, callApi } from '../services/api';
import { Phone, Calendar, Check, X, Clock } from 'lucide-react';
import './Calls.css';

export default function Calls() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedLead, setSelectedLead] = useState(null);
  const [callNote, setCallNote] = useState('');
  const [callDisposition, setCallDisposition] = useState('no_answer');

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const data = await leadService.getLeads();
      // Filter leads that are interested or need follow-up
      const callList = (data.leads || []).filter(l => 
        l.email_status === 'interested' || 
        l.email_status === 'replied' || 
        l.response === 'interested' ||
        l.needs_call === true
      );
      setLeads(callList);
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const handleLogCall = async () => {
    if (!selectedLead) return;
    
    try {
      const updates = {
        last_call_date: new Date().toISOString(),
        call_disposition: callDisposition,
        notes: (selectedLead.notes ? selectedLead.notes + '\n\n' : '') + `[Call - ${new Date().toLocaleDateString()}] ${callDisposition}: ${callNote}`
      };
      
      await leadService.updateLead(selectedLead._id || selectedLead.id, updates);
      
      // Clear and refresh
      setSelectedLead(null);
      setCallNote('');
      fetchLeads();
    } catch (err) {
      console.error('Failed to log call:', err);
    }
  };

  if (loading) return <div>Loading calls...</div>;

  return (
    <div className="calls-page">
      <div className="page-header">
        <h1 className="h1 text-gradient">Call List & Tasks</h1>
        <p className="subtitle">Manage your daily follow-ups and log calls</p>
      </div>

      <div className="calls-layout">
        <div className="call-list-panel glass-panel">
          <h3 className="h3 mb-4 p-4 border-b border-subtle">To Call Today</h3>
          <div className="call-list">
            {leads.length === 0 ? (
              <div className="empty-state">No calls scheduled for today! 🎉</div>
            ) : (
              leads.map(lead => (
                <div 
                  key={lead._id || lead.id}
                  className={`call-list-item ${selectedLead && (selectedLead._id || selectedLead.id) === (lead._id || lead.id) ? 'active' : ''}`}
                  onClick={() => setSelectedLead(lead)}
                >
                  <div className="call-item-header">
                    <span className="font-semibold">{lead.business_name}</span>
                    <span className={`badge badge-${lead.email_status === 'interested' ? 'success' : 'warning'}`}>
                      {lead.email_status || 'Unknown'}
                    </span>
                  </div>
                  <div className="call-item-meta">
                    <span className="mono text-tertiary">📞 {lead.phone || 'No phone'}</span>
                    <span className="text-tertiary">{lead.city}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="call-detail-panel glass-panel">
          {selectedLead ? (
            <div className="call-logger p-6">
              <h2 className="h2 mb-2">{selectedLead.business_name}</h2>
              <div className="flex gap-4 mb-6">
                <a href={`tel:${selectedLead.phone}`} className="btn btn-success">
                  <Phone size={16} /> Call {selectedLead.phone}
                </a>
                {selectedLead.website && (
                  <a href={selectedLead.website} target="_blank" rel="noreferrer" className="btn btn-outline">
                    View Website
                  </a>
                )}
              </div>

              <div className="mb-6">
                <h4 className="text-sm font-semibold text-tertiary uppercase mb-2">Previous Notes</h4>
                <div className="bg-secondary p-4 rounded-md text-sm whitespace-pre-wrap max-h-40 overflow-y-auto">
                  {selectedLead.notes || 'No previous notes.'}
                </div>
              </div>

              <div className="log-form">
                <h3 className="h3 mb-4">Log Call</h3>
                
                <div className="input-group mb-4">
                  <label className="input-label">Disposition</label>
                  <select 
                    className="input-field"
                    value={callDisposition}
                    onChange={(e) => setCallDisposition(e.target.value)}
                  >
                    <option value="no_answer">No Answer / Voicemail</option>
                    <option value="connected_not_interested">Connected - Not Interested</option>
                    <option value="connected_follow_up">Connected - Follow Up Later</option>
                    <option value="meeting_booked">Meeting Booked!</option>
                    <option value="wrong_number">Wrong Number</option>
                  </select>
                </div>

                <div className="input-group mb-6">
                  <label className="input-label">Call Notes</label>
                  <textarea 
                    className="input-field"
                    placeholder="Enter notes from the call..."
                    value={callNote}
                    onChange={(e) => setCallNote(e.target.value)}
                  />
                </div>

                <div className="flex justify-end gap-3">
                  <button className="btn btn-outline" onClick={() => setSelectedLead(null)}>Cancel</button>
                  <button className="btn btn-primary" onClick={handleLogCall}>Save Log</button>
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-state h-full flex items-center justify-center">
              Select a lead from the list to view details and log a call.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
