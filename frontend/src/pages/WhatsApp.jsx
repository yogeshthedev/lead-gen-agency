import React, { useState, useEffect } from 'react';
import { callApi, leadService } from '../services/api';
import { MessageCircle, Settings, Play, RefreshCw, Smartphone } from 'lucide-react';

export default function WhatsApp() {
  const [status, setStatus] = useState({ connected: false, running: false });
  const [stats, setStats] = useState({ sentToday: 0, dailyLimit: 30 });
  const [leads, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    checkStatus();
    fetchPendingWaLeads();
  }, []);

  const checkStatus = async () => {
    try {
      // Mocking check for now since backend relies on external bot server
      const data = await callApi('/whatsapp/status').catch(() => ({ connected: false, running: false }));
      setStatus(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchPendingWaLeads = async () => {
    try {
      const data = await leadService.getLeads();
      const pending = (data.leads || []).filter(l => l.phone && l.wa_status !== 'wa_done');
      setLeads(pending.slice(0, 50));
      setLoading(false);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  const runWaNow = async () => {
    try {
      await callApi('/whatsapp/run-now', { method: 'POST' });
      alert('WhatsApp outreach triggered!');
    } catch (err) {
      alert('Failed: ' + err.message);
    }
  };

  return (
    <div className="whatsapp-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">WhatsApp Outreach</h1>
        <p className="subtitle">Automated background messaging bot</p>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-6">
        <div className="glass-panel p-6">
          <h3 className="h3 mb-4 flex items-center gap-2"><Smartphone size={20} /> Bot Status</h3>
          <div className="mb-6 space-y-2">
            <div className="flex justify-between">
              <span className="text-tertiary">Connection:</span>
              <span className={`font-semibold ${status.connected ? 'text-success' : 'text-warning'}`}>
                {status.connected ? 'Connected' : 'Not Running'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-tertiary">Sent Today:</span>
              <span className="font-semibold">{stats.sentToday} / {stats.dailyLimit}</span>
            </div>
          </div>
          <div className="flex gap-4">
            <button className="btn btn-secondary" onClick={checkStatus}>
              <RefreshCw size={16} /> Refresh
            </button>
            <button className="btn btn-primary" onClick={runWaNow} disabled={!status.connected && false}>
              <Play size={16} /> Run Now
            </button>
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="h3 mb-4 flex items-center gap-2"><Settings size={20} /> Instructions</h3>
          <p className="text-tertiary mb-4 text-sm">
            The WhatsApp bot runs as a separate Node.js process to avoid blocking the main server.
          </p>
          <div className="bg-secondary p-3 rounded-md font-mono text-sm mb-2 text-info">
            cd whatsapp
          </div>
          <div className="bg-secondary p-3 rounded-md font-mono text-sm mb-4 text-info">
            node bot.js
          </div>
          <p className="text-sm text-tertiary">
            Scan the QR code with your spare WhatsApp device. Keep the terminal open.
          </p>
        </div>
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
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan="4" className="text-center p-4">Loading...</td></tr>
              ) : leads.length === 0 ? (
                <tr><td colSpan="4" className="text-center p-4 text-tertiary">No pending WhatsApp leads!</td></tr>
              ) : (
                leads.map(lead => (
                  <tr key={lead._id || lead.id}>
                    <td className="font-semibold">{lead.business_name}</td>
                    <td className="mono text-sm">{lead.phone}</td>
                    <td className="text-sm">{lead.category}</td>
                    <td>
                      <span className="badge badge-default">{lead.wa_status || 'pending'}</span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
