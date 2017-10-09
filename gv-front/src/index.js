// ignoring the service worker from create-react-app for now

import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';
// import registerServiceWorker from './registerServiceWorker';

ReactDOM.render(
	<App 
		APIbaseURL='http://localhost:5000'/>,
	document.getElementById('root')
);

// registerServiceWorker();
