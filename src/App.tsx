import React, { useState, useEffect } from 'react';
import { Sidebar, NavTab } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/DashboardPage';
import { UsersPage } from './pages/UsersPage';
import { LoginPage } from './pages/LoginPage';
import { FileManagerPage } from './pages/FileManagerPage';

export function App() {
  const [authToken, setAuthToken] = useState<string | null>(() => localStorage.getItem('admin_token'));
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');

  if (!authToken) {
    return <LoginPage onLoginSuccess={(token, admin) => setAuthToken(token)} />;
  }

  return (
    <div className="flex h-screen bg-[#070b14] text-slate-100 font-sans overflow-hidden dir-rtl">
      <Sidebar currentTab={currentTab} onSelectTab={setCurrentTab} />
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-radial from-[#0d1322] to-[#070b14]">
          {currentTab === 'dashboard' && <DashboardPage />}
          {currentTab === 'users' && <UsersPage />}
          {currentTab === 'files' && <FileManagerPage />}
        </main>
      </div>
    </div>
  );
}