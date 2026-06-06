import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Search, 
  Users, 
  Kanban, 
  MessageCircle, 
  Settings,
  PhoneCall
} from 'lucide-react';
import './Sidebar.css';

export default function Sidebar() {
  const navItems = [
    { name: 'Dashboard', path: '/', icon: <LayoutDashboard size={18} /> },
    { name: 'Scraper', path: '/scraper', icon: <Search size={18} /> },
    { type: 'divider' },
    { name: 'All Leads', path: '/leads', icon: <Users size={18} /> },
    { name: 'Pipeline', path: '/pipeline', icon: <Kanban size={18} /> },
    { name: 'Calls / Tasks', path: '/calls', icon: <PhoneCall size={18} /> },
    { name: 'WhatsApp', path: '/whatsapp', icon: <MessageCircle size={18} /> },
    { type: 'divider' },
    { name: 'Settings', path: '/settings', icon: <Settings size={18} /> },
  ];

  return (
    <aside className="sidebar glass-panel">
      <div className="sidebar-header">
        <div className="logo-text">LeadGen</div>
        <div className="logo-sub">agency v2.0</div>
      </div>
      <nav className="sidebar-nav">
        {navItems.map((item, index) => 
          item.type === 'divider' ? (
            <div key={`div-${index}`} className="nav-divider" />
          ) : (
            <NavLink 
              key={item.path} 
              to={item.path} 
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              {item.icon}
              <span>{item.name}</span>
            </NavLink>
          )
        )}
      </nav>
    </aside>
  );
}
