import React, { useState, useEffect } from 'react';
import { callApi } from '../services/api';
import { Save, RefreshCw, Eye } from 'lucide-react';
import './Templates.css';

const CATEGORIES = [
  'restaurants', 'chartered accountants', 'clinics', 'coaching institute', 'interior designers', 'real estate'
];

const DEFAULT_TEMPLATES = {
  "restaurants": [
    { subject: "Quick question about {name}'s website", body: "Hi,\n\nI was looking up {name} online and noticed you don't have a modern website yet.\n\nI specialize in building websites for restaurants in {city}. Before I send over more details, I just wanted to ask — are you currently interested in upgrading your online presence?\n\nPlease reply with a quick 'Yes' or 'No' so I know whether to send more info or cross you off my list.\n\nBest,\n{your_name}" },
    { subject: "Re: {name} — online visibility", body: "Hi,\n\nJust following up on my previous email.\n\nI can help {name} get more customers from Google with a new website. Are you interested in discussing this?\n\nA simple 'Yes' or 'No' would be super helpful!\n\nBest,\n{your_name}" },
    { subject: "Checking in one last time — {name}", body: "Hi,\n\nI'll make this short. I help restaurants in {city} build websites that actually drive reservations.\n\nIf you're interested, let me know. If not, just reply 'No' and I won't reach out again.\n\nBest,\n{your_name}\n{website}" },
    { subject: "Closing the loop — {name}", body: "Hi,\n\nI haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.\n\nIf that changes in the future, feel free to reach out.\n\nBest,\n{your_name}" }
  ],
  "chartered accountants": [
    { subject: "Quick question about {name}'s website", body: "Hi,\n\nI came across {name} while researching CA firms in {city} and noticed your website could use an upgrade.\n\nI build professional websites specifically for CA firms. Before I send over more details, are you currently interested in upgrading your online presence to get more clients?\n\nPlease reply with a quick 'Yes' or 'No'.\n\nBest,\n{your_name}" },
    { subject: "Re: {name} — client acquisition online", body: "Hi,\n\nFollowing up on my last email.\n\nI can help {name} attract more clients from Google with a modern website. Are you interested in discussing this?\n\nA simple 'Yes' or 'No' would be super helpful!\n\nBest,\n{your_name}" },
    { subject: "Checking in one last time — {name}", body: "Hi,\n\nI'll keep this short. I help CA firms in {city} build websites that rank on Google and bring in leads.\n\nIf you're interested, let me know. If not, just reply 'No' and I won't reach out again.\n\nBest,\n{your_name}\n{website}" },
    { subject: "Closing the loop — {name}", body: "Hi,\n\nI haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.\n\nIf that changes in the future, feel free to reach out.\n\nBest,\n{your_name}" }
  ],
  "clinics": [
    { subject: "Quick question about {name}'s website", body: "Hi,\n\nI was looking for clinics in {city} and noticed {name} doesn't have a modern website for patients to book appointments.\n\nI specialize in building clinic websites. Before I send over more details, I just wanted to ask — are you currently interested in upgrading your online presence?\n\nPlease reply with a quick 'Yes' or 'No'.\n\nBest,\n{your_name}" },
    { subject: "Re: {name} — more patients from Google", body: "Hi,\n\nJust following up on my previous email.\n\nI can help {name} get more patient bookings from Google with a new website. Are you interested in discussing this?\n\nA simple 'Yes' or 'No' would be super helpful!\n\nBest,\n{your_name}" },
    { subject: "Checking in one last time — {name}", body: "Hi,\n\nI'll make this short. I help clinics in {city} build websites that actually drive patient appointments.\n\nIf you're interested, let me know. If not, just reply 'No' and I won't reach out again.\n\nBest,\n{your_name}\n{website}" },
    { subject: "Closing the loop — {name}", body: "Hi,\n\nI haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.\n\nIf that changes in the future, feel free to reach out.\n\nBest,\n{your_name}" }
  ],
  "coaching institute": [
    { subject: "Students are searching online — {name}", body: "Hi,\n\nI noticed {name} while looking at coaching institutes in {city} and saw your website could use an upgrade.\n\nI build websites for coaching centres to help drive admissions. Before I send over more details, are you currently interested in upgrading your online presence?\n\nPlease reply with a quick 'Yes' or 'No'.\n\nBest,\n{your_name}" },
    { subject: "Re: {name} — online admissions", body: "Hi,\n\nJust following up on my previous email.\n\nI can help {name} get more admission enquiries from Google with a new website. Are you interested in discussing this?\n\nA simple 'Yes' or 'No' would be super helpful!\n\nBest,\n{your_name}" },
    { subject: "Checking in one last time — {name}", body: "Hi,\n\nI'll make this short. I help coaching centres in {city} build websites that actually drive enrollments.\n\nIf you're interested, let me know. If not, just reply 'No' and I won't reach out again.\n\nBest,\n{your_name}\n{website}" },
    { subject: "Closing the loop — {name}", body: "Hi,\n\nI haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.\n\nIf that changes in the future, feel free to reach out.\n\nBest,\n{your_name}" }
  ],
  "interior designers": [
    { subject: "Your portfolio online — {name}", body: "Hi,\n\nI came across {name} while looking at interior designers in {city} and noticed your website could use an upgrade.\n\nI build beautiful portfolio websites for interior designers. Before I send over more details, are you currently interested in upgrading your online presence to get more clients?\n\nPlease reply with a quick 'Yes' or 'No'.\n\nBest,\n{your_name}" },
    { subject: "Re: {name} — showcasing your work online", body: "Hi,\n\nJust following up on my previous email.\n\nI can help {name} attract more high-value clients from Google with a modern website. Are you interested in discussing this?\n\nA simple 'Yes' or 'No' would be super helpful!\n\nBest,\n{your_name}" },
    { subject: "Checking in one last time — {name}", body: "Hi,\n\nI'll make this short. I help interior designers in {city} build websites that showcase their work and drive leads.\n\nIf you're interested, let me know. If not, just reply 'No' and I won't reach out again.\n\nBest,\n{your_name}\n{website}" },
    { subject: "Closing the loop — {name}", body: "Hi,\n\nI haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.\n\nIf that changes in the future, feel free to reach out.\n\nBest,\n{your_name}" }
  ],
  "real estate": [
    { subject: "Property buyers search online first — {name}", body: "Hi,\n\nI came across {name} while looking at real estate agents in {city}.\n\nI specialize in building professional websites for real estate agents to showcase properties. Before I send over more details, are you currently interested in upgrading your online presence?\n\nPlease reply with a quick 'Yes' or 'No'.\n\nBest,\n{your_name}" },
    { subject: "Re: {name} — property leads from Google", body: "Hi,\n\nJust following up on my previous email.\n\nI can help {name} get more property enquiries directly from Google with a new website. Are you interested in discussing this?\n\nA simple 'Yes' or 'No' would be super helpful!\n\nBest,\n{your_name}" },
    { subject: "Checking in one last time — {name}", body: "Hi,\n\nI'll make this short. I help real estate agents in {city} build websites that actually generate leads.\n\nIf you're interested, let me know. If not, just reply 'No' and I won't reach out again.\n\nBest,\n{your_name}\n{website}" },
    { subject: "Closing the loop — {name}", body: "Hi,\n\nI haven't heard back, so I'll assume growing {name}'s online presence isn't a priority right now.\n\nIf that changes in the future, feel free to reach out.\n\nBest,\n{your_name}" }
  ]
};

export default function Templates() {
  const [templates, setTemplates] = useState({});
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [day, setDay] = useState(0); // 0=Day1, 1=Day3, 2=Day7, 3=Day14
  
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [preview, setPreview] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    // In a real app, you'd fetch from backend. For now, mimicking localStorage logic
    const saved = localStorage.getItem('lg_t');
    if (saved) {
      setTemplates(JSON.parse(saved));
    } else {
      setTemplates(DEFAULT_TEMPLATES);
      localStorage.setItem('lg_t', JSON.stringify(DEFAULT_TEMPLATES));
    }
  }, []);

  useEffect(() => {
    const catTmpls = templates[category] || [];
    const tmpl = catTmpls[day] || { subject: '', body: '' };
    setSubject(tmpl.subject || '');
    setBody(tmpl.body || '');
    setPreview(false);
  }, [category, day, templates]);

  const handleSave = () => {
    const updated = { ...templates };
    if (!updated[category]) updated[category] = [];
    while (updated[category].length <= day) updated[category].push({ subject: '', body: '' });
    updated[category][day] = { subject, body };
    
    setTemplates(updated);
    localStorage.setItem('lg_t', JSON.stringify(updated));
    // Also save to backend if needed
    
    setMsg('Template saved!');
    setTimeout(() => setMsg(''), 2000);
  };

  const renderPreview = (text) => {
    let t = text;
    t = t.replace(/{name}/g, 'Demo Business');
    t = t.replace(/{city}/g, 'Mumbai');
    t = t.replace(/{your_name}/g, 'Yogesh');
    t = t.replace(/{cal_link}/g, 'https://cal.com/yogesh');
    t = t.replace(/{website}/g, 'https://demo.com');
    return t;
  };

  return (
    <div className="templates-page">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">Email Templates</h1>
        <p className="subtitle">Customize outreach sequences per industry</p>
      </div>

      <div className="glass-panel p-6">
        <div className="mb-6">
          <label className="input-label block mb-2">Category</label>
          <div className="flex gap-2 flex-wrap">
            {CATEGORIES.map(c => (
              <button 
                key={c}
                className={`btn ${category === c ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setCategory(c)}
                style={{ padding: '0.5rem 1rem', textTransform: 'capitalize' }}
              >
                {c}
              </button>
            ))}
          </div>
        </div>

        <div className="mb-6">
          <label className="input-label block mb-2">Sequence Stage</label>
          <div className="flex gap-2">
            {[0, 1, 2, 3].map(d => (
              <button 
                key={d}
                className={`btn ${day === d ? 'btn-primary' : 'btn-secondary'}`}
                onClick={() => setDay(d)}
                style={{ padding: '0.4rem 1rem' }}
              >
                {d === 0 ? 'Day 1' : d === 1 ? 'Day 3' : d === 2 ? 'Day 7' : 'Day 14'}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-6 mb-6">
          <div className="col-span-2">
            <div className="input-group mb-4">
              <label className="input-label">Subject</label>
              <input 
                className="input-field font-mono" 
                value={subject} 
                onChange={e => setSubject(e.target.value)} 
              />
            </div>
            <div className="input-group">
              <label className="input-label">Body</label>
              <textarea 
                className="input-field font-mono" 
                value={body} 
                onChange={e => setBody(e.target.value)}
                rows={12}
              />
            </div>
          </div>
          <div className="col-span-1">
            <div className="bg-secondary p-4 rounded-md border border-subtle">
              <h4 className="text-sm font-semibold uppercase tracking-wide text-tertiary mb-3">Variables</h4>
              <ul className="space-y-2 font-mono text-sm text-info">
                <li>{'{name}'} <span className="text-tertiary">- Business Name</span></li>
                <li>{'{city}'} <span className="text-tertiary">- City</span></li>
                <li>{'{your_name}'} <span className="text-tertiary">- Your Name</span></li>
                <li>{'{cal_link}'} <span className="text-tertiary">- Booking Link</span></li>
                <li>{'{website}'} <span className="text-tertiary">- Website URL</span></li>
              </ul>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-4 border-t border-subtle pt-6">
          <button className="btn btn-primary" onClick={handleSave}>
            <Save size={16} /> Save Template
          </button>
          <button className="btn btn-outline" onClick={() => setPreview(!preview)}>
            <Eye size={16} /> {preview ? 'Hide Preview' : 'Show Preview'}
          </button>
          {msg && <span className="text-success text-sm font-semibold">{msg}</span>}
        </div>

        {preview && (
          <div className="mt-6 bg-secondary p-6 rounded-md border border-subtle">
            <div className="text-xs uppercase text-tertiary font-semibold mb-4">Email Preview</div>
            <div className="mb-4">
              <span className="text-tertiary mr-2">Subject:</span>
              <span className="font-semibold text-primary">{renderPreview(subject)}</span>
            </div>
            <div className="whitespace-pre-wrap text-sm leading-relaxed">
              {renderPreview(body)}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
