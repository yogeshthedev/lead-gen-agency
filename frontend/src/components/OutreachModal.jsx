import React, { useState, useEffect } from 'react';
import { X, Mail, MessageCircle, Send } from 'lucide-react';
import { callApi } from '../services/api';

export default function OutreachModal({ lead, onClose }) {
  const [activeTab, setActiveTab] = useState('email'); // 'email' or 'whatsapp'
  const [loading, setLoading] = useState(true);
  
  const [emailSubject, setEmailSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');
  
  const [waMessage, setWaMessage] = useState('');
  
  const [sending, setSending] = useState(false);
  const [statusMsg, setStatusMsg] = useState('');

  useEffect(() => {
    if (lead) fetchTemplate();
  }, [lead]);

  const fetchTemplate = async () => {
    try {
      setLoading(true);
      const data = await callApi(`/leads/${lead._id || lead.id}/template`);
      if (data) {
        setEmailSubject(data.email?.subject || '');
        setEmailBody(data.email?.body || '');
        setWaMessage(data.whatsapp || '');
      }
    } catch (err) {
      console.error('Failed to fetch template', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmail = async () => {
    try {
      setSending(true);
      setStatusMsg('');
      const res = await callApi(`/leads/${lead._id || lead.id}/send-custom-email`, 'POST', {
        subject: emailSubject,
        body: emailBody
      });
      if (res.ok) {
        setStatusMsg('Email sent successfully!');
        setTimeout(() => onClose(), 2000);
      }
    } catch (err) {
      setStatusMsg('Error sending email: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  const handleSendWhatsApp = async () => {
    try {
      setSending(true);
      setStatusMsg('');
      const res = await callApi(`/leads/send-whatsapp`, 'POST', {
        lead_id: lead._id || lead.id,
        custom_message: waMessage
      });
      if (res.url) {
        window.open(res.url, '_blank');
        setStatusMsg('WhatsApp opened in new tab!');
        setTimeout(() => onClose(), 2000);
      }
    } catch (err) {
      setStatusMsg('Error generating WhatsApp link: ' + err.message);
    } finally {
      setSending(false);
    }
  };

  if (!lead) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-primary border border-subtle rounded-xl shadow-2xl w-full max-w-3xl overflow-hidden flex flex-col max-h-[90vh]">
        
        {/* Header */}
        <div className="p-4 border-b border-subtle flex justify-between items-center bg-secondary/50">
          <div>
            <h2 className="text-xl font-bold flex items-center gap-2">
              Outreach: <span className="text-primary">{lead.business_name}</span>
            </h2>
            <p className="text-sm text-tertiary">
              {lead.city} • {lead.category} • {lead.email} • {lead.phone}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-secondary rounded-full transition-colors">
            <X size={20} className="text-tertiary hover:text-primary" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-subtle">
          <button
            className={`flex-1 py-3 px-4 font-semibold text-sm flex items-center justify-center gap-2 transition-colors ${activeTab === 'email' ? 'bg-secondary text-primary border-b-2 border-accent' : 'text-tertiary hover:bg-secondary/50'}`}
            onClick={() => setActiveTab('email')}
          >
            <Mail size={16} /> Email
          </button>
          <button
            className={`flex-1 py-3 px-4 font-semibold text-sm flex items-center justify-center gap-2 transition-colors ${activeTab === 'whatsapp' ? 'bg-secondary text-primary border-b-2 border-[#25D366]' : 'text-tertiary hover:bg-secondary/50'}`}
            onClick={() => setActiveTab('whatsapp')}
          >
            <MessageCircle size={16} /> WhatsApp
          </button>
        </div>

        {/* Body */}
        <div className="p-6 overflow-y-auto flex-1">
          {loading ? (
            <div className="text-center py-12 text-tertiary">Loading templates...</div>
          ) : (
            <>
              {activeTab === 'email' && (
                <div className="space-y-4">
                  {lead.email ? (
                    <>
                      <div className="input-group">
                        <label className="input-label">Subject</label>
                        <input
                          className="input-field"
                          value={emailSubject}
                          onChange={(e) => setEmailSubject(e.target.value)}
                        />
                      </div>
                      <div className="input-group">
                        <label className="input-label">Message Body</label>
                        <textarea
                          className="input-field font-mono text-sm leading-relaxed"
                          rows={12}
                          value={emailBody}
                          onChange={(e) => setEmailBody(e.target.value)}
                        />
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-8 text-warning border border-warning/20 bg-warning/5 rounded-lg">
                      This lead does not have an email address.
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'whatsapp' && (
                <div className="space-y-4">
                  {lead.phone ? (
                    <>
                      <div className="input-group">
                        <label className="input-label">WhatsApp Message</label>
                        <textarea
                          className="input-field font-mono text-sm leading-relaxed"
                          rows={12}
                          value={waMessage}
                          onChange={(e) => setWaMessage(e.target.value)}
                        />
                      </div>
                      <p className="text-xs text-tertiary">
                        * Note: Sending this will generate a deep link and open WhatsApp Web for you to manually hit send.
                      </p>
                    </>
                  ) : (
                    <div className="text-center py-8 text-warning border border-warning/20 bg-warning/5 rounded-lg">
                      This lead does not have a phone number.
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-subtle bg-secondary/30 flex justify-between items-center">
          <div className={`text-sm font-semibold ${statusMsg.includes('Error') ? 'text-danger' : 'text-success'}`}>
            {statusMsg}
          </div>
          <div className="flex gap-3">
            <button className="btn btn-outline" onClick={onClose} disabled={sending}>
              Cancel
            </button>
            {activeTab === 'email' && lead.email && (
              <button className="btn btn-primary bg-accent hover:bg-accent/90" onClick={handleSendEmail} disabled={sending}>
                {sending ? 'Sending...' : <><Send size={16} /> Send Email</>}
              </button>
            )}
            {activeTab === 'whatsapp' && lead.phone && (
              <button className="btn btn-primary" style={{ backgroundColor: '#25D366', borderColor: '#25D366' }} onClick={handleSendWhatsApp} disabled={sending}>
                {sending ? 'Processing...' : <><MessageCircle size={16} /> Open in WhatsApp</>}
              </button>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}
