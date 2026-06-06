import React, { useState, useEffect } from 'react';
import { X, MessageCircle, Phone, MapPin, Star, Mail } from 'lucide-react';
import { callApi } from '../services/api';

export default function OutreachModal({ lead, onClose }) {
  const [loading, setLoading] = useState(true);
  const [visible, setVisible] = useState(false);
  const [waMessage, setWaMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  // Trigger slide-in animation after mount
  useEffect(() => {
    requestAnimationFrame(() => setVisible(true));
  }, []);

  useEffect(() => {
    if (lead) fetchTemplate();
  }, [lead]);

  const handleClose = () => {
    setVisible(false);
    setTimeout(() => onClose(), 300); // wait for slide-out animation
  };

  const fetchTemplate = async () => {
    try {
      setLoading(true);
      const data = await callApi(`/leads/${lead._id || lead.id}/template`);
      if (data && data.whatsapp) {
        setWaMessage(data.whatsapp);
      } else {
        throw new Error('No template');
      }
    } catch (err) {
      console.error('Failed to fetch template', err);
      // Set defaults so user can still type
      setWaMessage(`Hi ${lead.business_name}! 👋\n\nI noticed your business doesn't have a website yet. We help businesses like yours get online with a professional website + Google presence.\n\nWould you be interested in a quick chat?`);
    } finally {
      setLoading(false);
    }
  };

  const handleSendWhatsApp = async () => {
    try {
      setSending(true);
      setStatusMsg('');
      const res = await callApi(`/leads/send-whatsapp`, {
        method: 'POST',
        body: JSON.stringify({ lead_id: lead._id || lead.id, custom_message: waMessage })
      });
      if (res.url) {
        window.open(res.url, '_blank');
        setStatusMsg('✅ WhatsApp opened!');
        setTimeout(() => handleClose(), 2000);
      }
    } catch (err) {
      setStatusMsg('❌ Error: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  if (!lead) return null;

  return (
    <div className={`sidebar-overlay ${visible ? 'sidebar-overlay--visible' : ''}`} onClick={handleClose}>
      <div className={`sidebar-panel ${visible ? 'sidebar-panel--open' : ''}`} onClick={e => e.stopPropagation()}>
        
        {/* Header */}
        <div className="sidebar-header">
          <div>
            <h2 className="sidebar-title">WhatsApp Outreach</h2>
            <p className="sidebar-subtitle">Customize and send message</p>
          </div>
          <button onClick={handleClose} className="sidebar-close-btn">
            <X size={20} />
          </button>
        </div>

        {/* Lead Info Card */}
        <div className="sidebar-lead-card">
          <div className="sidebar-lead-avatar">
            {(lead.business_name || '?')[0].toUpperCase()}
          </div>
          <div className="sidebar-lead-info">
            <div className="sidebar-lead-name">{lead.business_name}</div>
            <div className="sidebar-lead-meta">
              {lead.city && <span><MapPin size={12} /> {lead.city}</span>}
              {lead.category && <span><Star size={12} /> {lead.category}</span>}
            </div>
            <div className="sidebar-lead-meta">
              {lead.phone && <span><Phone size={12} /> {lead.phone}</span>}
              {lead.email && <span><Mail size={12} /> {lead.email}</span>}
            </div>
          </div>
        </div>

        {/* Body */}
        <div className="sidebar-body">
          {loading ? (
            <div className="sidebar-loading">
              <div className="sidebar-spinner"></div>
              <span>Loading...</span>
            </div>
          ) : (
            <div className="sidebar-form">
              {lead.phone ? (
                <>
                  <div className="input-group">
                    <label className="input-label">To</label>
                    <div className="sidebar-to-field">
                      <MessageCircle size={14} style={{ color: '#25D366' }} /> {lead.phone}
                    </div>
                  </div>
                  <div className="input-group">
                    <label className="input-label">WhatsApp Message</label>
                    <textarea
                      className="input-field sidebar-textarea"
                      value={waMessage}
                      onChange={(e) => setWaMessage(e.target.value)}
                      placeholder="Write your WhatsApp message..."
                    />
                  </div>
                  <p className="sidebar-hint">
                    This will open WhatsApp Web with your message pre-filled. You'll need to press Send manually.
                  </p>
                </>
              ) : (
                <div className="sidebar-warning">
                  <Phone size={24} />
                  <p>No phone number found for this lead.</p>
                  <p className="sidebar-warning-hint">Try calling via Google Maps listing.</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="sidebar-footer">
          {statusMsg && (
            <div className={`sidebar-status ${statusMsg.includes('❌') ? 'sidebar-status--error' : 'sidebar-status--success'}`}>
              {statusMsg}
            </div>
          )}
          <div className="sidebar-actions">
            <button className="btn btn-outline" onClick={handleClose} disabled={sending}>
              Cancel
            </button>
            {lead.phone && (
              <button className="btn sidebar-wa-btn" onClick={handleSendWhatsApp} disabled={sending}>
                {sending ? 'Processing...' : <><MessageCircle size={16} /> Send via WhatsApp</>}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
