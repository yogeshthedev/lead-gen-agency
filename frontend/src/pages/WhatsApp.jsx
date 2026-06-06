import React, { useState, useEffect } from 'react';
import { leadService } from '../services/api';
import { MessageCircle, RefreshCw, Smartphone, Send } from 'lucide-react';
import OutreachModal from '../components/OutreachModal';

export default function WhatsApp() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [outreachLead, setOutreachLead] = useState(null);
  
  useEffect(() => {
    fetchPendingWaLeads();
  }, []);

  const fetchPendingWaLeads = async () => {
    setLoading(true);
    try {
      const data = await leadService.getLeads();
      const pending = (data.leads || []).filter(l => l.phone && l.wa_status !== 'wa_done' && l.wa_status !== 'wa_sent');
      setLeads(pending.slice(0, 50));
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="whatsapp-page">
      <div className="page-header mb-6 flex justify-between items-end">
        <div>
          <h1 className="h1 text-gradient">WhatsApp Outreach</h1>
          <p className="subtitle">Manual WhatsApp messaging pipeline</p>
        </div>
        <button className="btn btn-secondary" onClick={fetchPendingWaLeads} disabled={loading}>
          <RefreshCw size={16} className={loading ? "animate-spin" : ""} /> Refresh
        </button>
      </div>

      <div className="glass-panel p-6">
        <h3 className="h3 mb-4">Pending WhatsApp Leads ({leads.length})</h3>
        <div className="table-container">
          <table className="table">
            <thead>
              <tr>
                <th>Business Name</th>
                <th>Phone</th>
                <th>Category</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="5" className="text-center p-4">Loading...</td></tr>
              ) : leads.length === 0 ? (
                <tr><td colSpan="5" className="text-center p-4 text-tertiary">No pending WhatsApp leads!</td></tr>
              ) : (
                leads.map(lead => (
                  <tr key={lead._id || lead.id}>
                    <td className="font-semibold">{lead.business_name}</td>
                    <td className="mono text-sm">{lead.phone}</td>
                    <td className="text-sm">{lead.category}</td>
                    <td>
                      <span className="badge badge-default">{lead.wa_status || 'pending'}</span>
                    </td>
                    <td>
                      <button 
                        onClick={() => setOutreachLead(lead)} 
                        className="btn btn-primary btn-sm flex items-center gap-2"
                      >
                        <Send size={14} /> Send Message
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {outreachLead && (
        <OutreachModal 
          lead={outreachLead} 
          initialTab="whatsapp"
          onClose={() => {
            setOutreachLead(null);
            fetchPendingWaLeads(); // refresh in case status changed
          }} 
        />
      )}
    </div>
  );
}
