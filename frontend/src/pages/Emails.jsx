import React, { useState } from 'react';
import { callApi } from '../services/api';
import { Mail, CheckCircle2, AlertCircle, RefreshCw } from 'lucide-react';

export default function Emails() {
  const [status, setStatus] = useState({ type: '', msg: '' });
  const [loading, setLoading] = useState(false);

  const sendDay1 = async () => {
    setLoading(true);
    setStatus({ type: 'info', msg: 'Sending Day 1 cold emails...' });
    try {
      await callApi('/send-emails', { method: 'POST' });
      setStatus({ type: 'success', msg: 'Day 1 emails sent successfully!' });
    } catch (err) {
      setStatus({ type: 'error', msg: err.message });
    }
    setLoading(false);
  };

  const sendFollowUps = async () => {
    setLoading(true);
    setStatus({ type: 'info', msg: 'Sending follow-up emails...' });
    try {
      await callApi('/send-followups', { method: 'POST' });
      setStatus({ type: 'success', msg: 'Follow-ups sent successfully!' });
    } catch (err) {
      setStatus({ type: 'error', msg: err.message });
    }
    setLoading(false);
  };

  const checkReplies = async () => {
    setLoading(true);
    setStatus({ type: 'info', msg: 'Checking Gmail for replies...' });
    try {
      await callApi('/check-replies', { method: 'POST' });
      setStatus({ type: 'success', msg: 'Inbox checked. Leads updated.' });
    } catch (err) {
      setStatus({ type: 'error', msg: err.message });
    }
    setLoading(false);
  };

  return (
    <div className="emails-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">Email Campaigns</h1>
        <p className="subtitle">Manage cold outreach and automate follow-ups</p>
      </div>

      {status.msg && (
        <div className={`glass-panel p-4 mb-6 border-l-4 ${
          status.type === 'error' ? 'border-danger bg-danger-subtle' : 
          status.type === 'success' ? 'border-success bg-success-subtle' : 
          'border-info bg-info-subtle'
        }`}>
          {status.msg}
        </div>
      )}

      <div className="grid grid-cols-2 gap-6">
        <div className="glass-panel p-6 flex flex-col justify-between">
          <div>
            <h3 className="h3 mb-2 flex items-center gap-2"><Mail size={20} className="text-info" /> Day 1 Outreach</h3>
            <p className="text-tertiary mb-6">
              Sends the initial cold email to all leads with a "Not Sent" status. 
              The template used depends on the lead's category.
            </p>
          </div>
          <button className="btn btn-primary w-full" onClick={sendDay1} disabled={loading}>
            {loading ? <RefreshCw className="animate-spin" size={16} /> : 'Send Day 1 Emails'}
          </button>
        </div>

        <div className="glass-panel p-6 flex flex-col justify-between">
          <div>
            <h3 className="h3 mb-2 flex items-center gap-2"><RefreshCw size={20} className="text-warning" /> Automated Follow-ups</h3>
            <p className="text-tertiary mb-6">
              Sends follow-up emails (Day 3, 7, 14) to leads who haven't replied. 
              Automatically skips if marked Interested or Not Interested.
            </p>
          </div>
          <button className="btn btn-outline w-full text-warning border-warning" onClick={sendFollowUps} disabled={loading}>
            {loading ? <RefreshCw className="animate-spin" size={16} /> : 'Send Follow-ups'}
          </button>
        </div>

        <div className="glass-panel p-6 flex flex-col justify-between col-span-2">
          <div>
            <h3 className="h3 mb-2 flex items-center gap-2"><CheckCircle2 size={20} className="text-success" /> Auto-detect Replies</h3>
            <p className="text-tertiary mb-6">
              Scans your connected Gmail inbox for replies to your cold emails.
              Automatically updates the lead status to "Replied" in the pipeline.
            </p>
          </div>
          <button className="btn btn-secondary w-full max-w-md" onClick={checkReplies} disabled={loading}>
            {loading ? <RefreshCw className="animate-spin" size={16} /> : 'Check Gmail for Replies'}
          </button>
        </div>
      </div>
    </div>
  );
}
