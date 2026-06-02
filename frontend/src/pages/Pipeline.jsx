import React, { useState, useEffect } from 'react';
import { leadService } from '../services/api';
import { Send } from 'lucide-react';
import OutreachModal from '../components/OutreachModal';
import './Pipeline.css';

const STAGES = [
  { id: 'not_sent', label: 'New / Not Sent', color: 'var(--text-tertiary)' },
  { id: 'sent', label: 'Contacted (Sent)', color: 'var(--info)' },
  { id: 'replied', label: 'Replied', color: 'var(--warning)' },
  { id: 'interested', label: 'Interested / Meeting', color: 'var(--success)' },
  { id: 'closed', label: 'Closed Won', color: 'var(--accent-primary)' }
];

export default function Pipeline() {
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
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

  const handleDragStart = (e, leadId) => {
    e.dataTransfer.setData('leadId', leadId);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = async (e, targetStatus) => {
    e.preventDefault();
    const leadId = e.dataTransfer.getData('leadId');
    if (!leadId) return;

    // Optimistic update
    setLeads(prev => prev.map(l => 
      (l._id || l.id) === leadId ? { ...l, email_status: targetStatus } : l
    ));

    try {
      await leadService.updateStatus(leadId, targetStatus);
    } catch (err) {
      console.error(err);
      // Revert on error
      fetchLeads();
    }
  };

  if (loading) return <div>Loading pipeline...</div>;

  return (
    <div className="pipeline">
      <div className="page-header">
        <h1 className="h1 text-gradient">Sales Pipeline</h1>
        <p className="subtitle">Drag and drop leads to update their status</p>
      </div>

      <div className="kanban-board">
        {STAGES.map(stage => {
          const stageLeads = leads.filter(l => (l.email_status || 'not_sent') === stage.id);
          
          return (
            <div 
              key={stage.id} 
              className="kanban-column glass-panel"
              onDragOver={handleDragOver}
              onDrop={(e) => handleDrop(e, stage.id)}
            >
              <div className="column-header" style={{ borderBottomColor: stage.color }}>
                <h3 className="h3">{stage.label}</h3>
                <span className="badge badge-default">{stageLeads.length}</span>
              </div>
              
              <div className="column-content">
                {stageLeads.map(lead => (
                  <div 
                    key={lead._id || lead.id} 
                    className="kanban-card"
                    draggable
                    onDragStart={(e) => handleDragStart(e, lead._id || lead.id)}
                  >
                    <div className="card-title">{lead.business_name}</div>
                    <div className="card-subtitle">{lead.city || 'Unknown City'}</div>
                    <div className="card-meta flex justify-between items-center mt-2">
                      {lead.phone ? <span className="mono text-sm text-tertiary">📞 {lead.phone}</span> : <span></span>}
                      <button 
                        onClick={() => setOutreachLead(lead)} 
                        className="btn btn-outline p-1 rounded hover:bg-secondary transition-colors" 
                        title="Send Message"
                      >
                        <Send size={14} className="text-accent" />
                      </button>
                    </div>
                  </div>
                ))}
                {stageLeads.length === 0 && (
                  <div className="empty-column">Drop leads here</div>
                )}
              </div>
            </div>
          );
        })}
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
