import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './index.css';
import 'bootstrap/dist/css/bootstrap.min.css';
import App from './App';

ReactDOM.createRoot(document.getElementById('root')!).render(React.createElement(React.StrictMode, null,
  React.createElement(BrowserRouter, null,
      React.createElement(App, null))));