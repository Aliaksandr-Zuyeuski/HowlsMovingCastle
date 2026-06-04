import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { App } from './App.jsx';
import './index.css';

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js').catch(e => console.log('SW error:', e));
}

createRoot(document.getElementById('app')).render(
  <StrictMode>
    <App />
  </StrictMode>
);
