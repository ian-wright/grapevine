import React, { Component } from 'react';
import { Sidebar } from './sidebar';
import { ReadContainer } from '../read/read-container';


import './css/grape-container.css';

import grapes from './img/grapes.png';

// make a reusable instance of axios here

export class GrapeContainer extends Component {

	render() {
		return (
			
			<div className="GrapeContainer">
				<header className="App-header">
                    <img src={ grapes } className="App-logo" alt="logo" />
                    <h1 className="App-title">Grapevine</h1>
                </header>
                <Sidebar 
                	onLogout={ this.props.onLogout }/>
                <ReadContainer />
			</div>
		)
	}
}