import React, { useState, useEffect } from 'react';
import { callApi } from '../services/api';
import { Save } from 'lucide-react';

export default function Settings() {
  const [settings, setSettings] = useState({
    your_name: '',
    your_cal_link: '',
    wa_default_msg: ''
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState('');

  useEffect(() => {
    callApi('/settings')
      .then(data => {
        setSettings(data || {});
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  const handleSave = async () => {
    setSaving(true);
    setMsg('');
    try {
      await callApi('/settings', {
        method: 'POST',
        body: JSON.stringify(settings)
      });
      setMsg('Settings saved successfully!');
      setTimeout(() => setMsg(''), 3000);
    } catch (err) {
      setMsg('Error: ' + err.message);
    }
    setSaving(false);
  };

  if (loading) return <div>Loading settings...</div>;

  return (
    <div className="settings-page max-w-md">
      <div className="page-header mb-6">
        <h1 className="h1 text-gradient">Settings</h1>
        <p className="subtitle">Configure your global profile and defaults</p>
      </div>

      <div className="glass-panel p-6">
        <div className="input-group mb-6">
          <label className="input-label">Your Name</label>
          <input 
            className="input-field" 
            value={settings.your_name || ''}
            onChange={e => setSettings({...settings, your_name: e.target.value})}
          />
        </div>

        <div className="input-group mb-6">
          <label className="input-label">Your Calendar Link</label>
          <input 
            className="input-field" 
            value={settings.your_cal_link || ''}
            onChange={e => setSettings({...settings, your_cal_link: e.target.value})}
            placeholder="https://cal.com/yourname"
          />
        </div>

        <div className="input-group mb-6">
          <label className="input-label">WhatsApp Default Message</label>
          <textarea 
            className="input-field" 
            value={settings.wa_default_msg || ''}
            onChange={e => setSettings({...settings, wa_default_msg: e.target.value})}
            rows={4}
          />
          <span className="text-tertiary text-sm mt-1">Variables: {'{name}'}</span>
        </div>

        <div className="flex items-center gap-4 mt-6">
          <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
            <Save size={16} /> {saving ? 'Saving...' : 'Save Settings'}
          </button>
          {msg && <span className={msg.includes('Error') ? 'text-danger' : 'text-success'}>{msg}</span>}
        </div>
      </div>
    </div>
  );
}
