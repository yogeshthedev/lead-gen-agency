import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Scraper from './pages/Scraper';
import Emails from './pages/Emails';
import Templates from './pages/Templates';
import Leads from './pages/Leads';
import Pipeline from './pages/Pipeline';
import Calls from './pages/Calls';
import WhatsApp from './pages/WhatsApp';
import Settings from './pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="scraper" element={<Scraper />} />
          <Route path="emails" element={<Emails />} />
          <Route path="templates" element={<Templates />} />
          <Route path="leads" element={<Leads />} />
          <Route path="pipeline" element={<Pipeline />} />
          <Route path="calls" element={<Calls />} />
          <Route path="whatsapp" element={<WhatsApp />} />
          <Route path="settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
