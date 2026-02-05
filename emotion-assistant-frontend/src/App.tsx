import React from 'react';
import ChatContainer from './components/ChatContainer/ChatContainer';
import { AppProvider, useAppContext } from './context/AppContext';
import './App.css';

const AppContent: React.FC = () => {
  const { userId, userEmail } = useAppContext();

  if (!userId) {
    return (
      <div className="app-loading">
        <div className="app-loading__spinner"></div>
        <p>Initializing...</p>
      </div>
    );
  }

  return <ChatContainer userId={userId} userEmail={userEmail || undefined} />;
};

const App: React.FC = () => {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
};

export default App;
