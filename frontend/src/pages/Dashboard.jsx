import React, { useState, useEffect } from 'react';
import { leadService } from '../services/api';
import { BarChart, Users, Mail, Phone, TrendingUp } from 'lucide-react';
import './Dashboard.css';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    leadService.getStats()
      .then(data => {
        setStats(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load stats:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="loading-state">Loading dashboard...</div>;
  }

  if (!stats) return <div className="error-state">Failed to load statistics</div>;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1 className="h1 text-gradient">Dashboard Overview</h1>
        <p className="subtitle">Your lead generation and sales pipeline at a glance</p>
      </div>

      <div className="stats-grid">
        <StatCard 
          title="Total Leads" 
          value={stats.total || 0} 
          icon={<Users size={24} />} 
          color="primary"
        />
        <StatCard 
          title="Have Email" 
          value={stats.has_email || 0} 
          icon={<Mail size={24} />} 
          color="info"
        />
        <StatCard 
          title="Emails Sent" 
          value={(stats.sent || 0) + (stats.follow_up || 0)} 
          icon={<Phone size={24} />} 
          color="warning"
        />
        <StatCard 
          title="Interested" 
          value={stats.interested || 0} 
          icon={<TrendingUp size={24} />} 
          color="success"
        />
      </div>

      <div className="panels-grid">
        <div className="glass-panel p-6">
          <h3 className="h3 mb-4 text-tertiary uppercase tracking-wide">By Source</h3>
          <div className="data-list">
            {Object.entries(stats.by_source || {}).length === 0 ? (
              <div className="empty-state">No source data</div>
            ) : (
              Object.entries(stats.by_source).map(([k, v]) => (
                <div key={k} className="data-row">
                  <span className="data-key">{k}</span>
                  <span className="data-val">{v}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="h3 mb-4 text-tertiary uppercase tracking-wide">By Category</h3>
          <div className="data-list">
            {Object.entries(stats.by_category || {}).length === 0 ? (
              <div className="empty-state">No category data</div>
            ) : (
              Object.entries(stats.by_category).map(([k, v]) => (
                <div key={k} className="data-row">
                  <span className="data-key">{k}</span>
                  <span className="data-val">{v}</span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="h3 mb-4 text-tertiary uppercase tracking-wide">Email Pipeline</h3>
          <div className="data-list">
            <PipelineRow label="Not Sent" value={stats.not_sent || 0} type="default" />
            <PipelineRow label="Sent" value={stats.sent || 0} type="info" />
            <PipelineRow label="Follow Up" value={stats.follow_up || 0} type="warning" />
            <PipelineRow label="Replied" value={stats.replied || 0} type="primary" />
            <PipelineRow label="Interested" value={stats.interested || 0} type="success" />
            <PipelineRow label="Closed" value={stats.closed || 0} type="default" />
          </div>
        </div>
      </div>
      
      <div className="glass-panel p-6 mt-6">
        <h3 className="h3 mb-4 text-tertiary uppercase tracking-wide">Leads by Day</h3>
        <div className="days-grid">
          {Object.keys(stats.by_day || {}).length === 0 ? (
            <div className="empty-state">No daily data</div>
          ) : (
            Object.keys(stats.by_day).sort().reverse().map(day => (
              <div key={day} className="day-card">
                <div className="day-val">{stats.by_day[day]}</div>
                <div className="day-date">{day}</div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  return (
    <div className="stat-card glass-panel">
      <div className={`stat-icon bg-${color}-subtle color-${color}`}>
        {icon}
      </div>
      <div className="stat-info">
        <div className="stat-val">{value}</div>
        <div className="stat-title">{title}</div>
      </div>
    </div>
  );
}

function PipelineRow({ label, value, type }) {
  return (
    <div className="data-row">
      <span className={`badge badge-${type}`}>{label}</span>
      <span className="data-val">{value}</span>
    </div>
  );
}
