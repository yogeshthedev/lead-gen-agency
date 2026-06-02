import React, { useState, useEffect } from 'react';
import { callApi } from '../services/api';
import { Search, Play, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function Scraper() {
  const [city, setCity] = useState('Mumbai');
  const [business, setBusiness] = useState('Dentists');
  const [source, setSource] = useState('both');
  const [maxLeads, setMaxLeads] = useState(30);
  
  const [status, setStatus] = useState('idle'); // idle, running, done, error
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    let interval;
    if (status === 'running') {
      interval = setInterval(pollStatus, 2000);
    }
    return () => clearInterval(interval);
  }, [status]);

  const pollStatus = async () => {
    try {
      const data = await callApi('/scrape/status');
      setLogs(data.logs || []);
      
      if (!data.running && data.logs && data.logs.length > 0) {
        const lastMsg = data.logs[data.logs.length - 1].msg;
        if (lastMsg.includes('COMPLETED SUCCESSFULLY')) {
          setStatus('done');
        } else if (lastMsg.includes('FAILED')) {
          setStatus('error');
        }
      }
    } catch (err) {
      console.error(err);
    }
  };

  const startScrape = async () => {
    if (!city || !business) {
      alert("City and Business Type are required");
      return;
    }
    
    setStatus('running');
    setLogs([{ type: 'i', msg: `$ starting scrape job for ${business} in ${city}...` }]);

    try {
      await callApi('/scrape/start', {
        method: 'POST',
        body: JSON.stringify({ city, business, source, max_leads: parseInt(maxLeads) })
      });
    } catch (err) {
      setLogs(prev => [...prev, { type: 'e', msg: err.message }]);
      setStatus('error');
    }
  };

  return (
    <div className="scraper-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">Web Scraper</h1>
        <p className="subtitle">Automate Google Maps & JustDial lead extraction</p>
      </div>

      <div className="glass-panel p-6 mb-6">
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="input-group">
            <label className="input-label">City</label>
            <input 
              className="input-field" 
              value={city} 
              onChange={e => setCity(e.target.value)} 
              placeholder="e.g. Mumbai"
            />
          </div>
          <div className="input-group">
            <label className="input-label">Business Type</label>
            <input 
              className="input-field" 
              value={business} 
              onChange={e => setBusiness(e.target.value)} 
              placeholder="e.g. Dentists"
            />
          </div>
          <div className="input-group">
            <label className="input-label">Source</label>
            <select 
              className="input-field" 
              value={source} 
              onChange={e => setSource(e.target.value)}
            >
              <option value="both">Both</option>
              <option value="maps">Google Maps</option>
              <option value="justdial">JustDial</option>
            </select>
          </div>
          <div className="input-group">
            <label className="input-label">Max Leads</label>
            <input 
              type="number" 
              className="input-field" 
              value={maxLeads} 
              onChange={e => setMaxLeads(e.target.value)} 
            />
          </div>
        </div>

        <div className="flex items-center gap-4">
          <button 
            className="btn btn-primary" 
            onClick={startScrape}
            disabled={status === 'running'}
          >
            {status === 'running' ? (
              <><span className="animate-spin">⏳</span> Scraping...</>
            ) : (
              <><Play size={18} /> Start Scraping</>
            )}
          </button>

          {status === 'running' && <span className="badge badge-warning">Running</span>}
          {status === 'done' && <span className="badge badge-success"><CheckCircle2 size={14} /> Completed</span>}
          {status === 'error' && <span className="badge badge-danger"><AlertCircle size={14} /> Failed</span>}
        </div>
      </div>

      <div className="glass-panel p-6">
        <h3 className="h3 mb-4 text-tertiary uppercase tracking-wide">Terminal Output</h3>
        <div className="terminal">
          {logs.length === 0 ? (
            <div className="term-dim">Waiting for scrape job to start...</div>
          ) : (
            logs.map((l, i) => (
              <div key={i} className={l.type === 'e' ? 'term-err' : l.msg.startsWith('$') ? 'term-info font-bold' : 'term-info'}>
                {l.msg}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
