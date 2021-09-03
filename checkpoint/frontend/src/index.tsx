// import { OpenAPI } from '@domino/polaris-cp-api';
import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
// import '@domino-research/ui/dist/index.css';
import './antd.less';
import './index.scss';

// OpenAPI.BASE = process.env.HOSTNAME || window.location.protocol + '//' + window.location.host;

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root'),
);
