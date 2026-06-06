import React, { useState, useEffect, useRef } from 'react';
import { callApi } from '../services/api';
import { Search, Play, AlertCircle, CheckCircle2 } from 'lucide-react';

const TARGET_GROUPS = [
  {
    name: 'Priority 1 (High Paying)',
    options: ['Interior Designers', 'Architects', 'Real Estate Consultants', 'Wedding Photographers', 'Event Planners', 'Coaching Institutes', 'CA Firms', 'Lawyers']
  },
  {
    name: 'Priority 2',
    options: ['Dental Clinics', 'Physiotherapy Clinics', 'Skin Clinics', 'Gyms', 'Beauty Salons', 'Travel Agencies']
  }
];

export default function Scraper() {
  const [city, setCity] = useState('jaipur');
  const [business, setBusiness] = useState('CA Firms');
  const [source, setSource] = useState('both');
  const [maxLeads, setMaxLeads] = useState(30);
  const [websiteFilter, setWebsiteFilter] = useState('all');
  
  const [status, setStatus] = useState('idle'); // idle, running, done, error
  const [logs, setLogs] = useState([]);

  const [showTargets, setShowTargets] = useState(false);
  const targetRef = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (targetRef.current && !targetRef.current.contains(event.target)) {
        setShowTargets(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

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
        body: JSON.stringify({ city, business, source, max_leads: parseInt(maxLeads), website_filter: websiteFilter })
      });
    } catch (err) {
      setLogs(prev => [...prev, { type: 'e', msg: err.message }]);
      setStatus('error');
    }
  };

  const filteredGroups = TARGET_GROUPS.map(g => ({
    name: g.name,
    options: g.options.filter(o => o.toLowerCase().includes(business.toLowerCase()))
  })).filter(g => g.options.length > 0);

  return (
    <div className="scraper-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">Web Scraper</h1>
        <p className="subtitle">Automate Google Maps & JustDial lead extraction</p>
      </div>

      <div className="glass-panel p-6 mb-6">
        <div className="grid grid-cols-5 gap-4 mb-6">
          <div className="input-group">
            <label className="input-label">City</label>
            <input 
              className="input-field" 
              value={city} 
              onChange={e => setCity(e.target.value)} 
              placeholder="e.g. Mumbai"
            />
          </div>
          <div className="input-group" ref={targetRef}>
            <label className="input-label">Business Type</label>
            <div className="dropdown-container">
              <input 
                className="input-field" 
                value={business} 
                onChange={e => {
                  setBusiness(e.target.value);
                  setShowTargets(true);
                }} 
                onFocus={() => setShowTargets(true)}
                placeholder="Search or type custom target..."
              />
              {showTargets && (
                <div className="dropdown-menu">
                  {filteredGroups.length > 0 ? (
                    filteredGroups.map(group => (
                      <div key={group.name}>
                        <div className="dropdown-group-header">
                          {group.name}
                        </div>
                        {group.options.map(opt => (
                          <div 
                            key={opt}
                            className="dropdown-item"
                            onClick={() => {
                              setBusiness(opt);
                              setShowTargets(false);
                            }}
                          >
                            {opt}
                          </div>
                        ))}
                      </div>
                    ))
                  ) : (
                    <div className="dropdown-item text-tertiary">
                      Press 'Start Scraping' to use "{business}"
                    </div>
                  )}
                </div>
              )}
            </div>
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
          <div className="input-group">
            <label className="input-label">Website Filter</label>
            <select 
              className="input-field" 
              value={websiteFilter} 
              onChange={e => setWebsiteFilter(e.target.value)}
            >
              <option value="all">All Leads</option>
              <option value="with_website">Only With Website</option>
              <option value="without_website">Only Without Website</option>
            </select>
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
