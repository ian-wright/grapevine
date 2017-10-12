import React, { Component } from 'react';
import { Sidebar } from './sidebar';
import { ReadContainer } from '../read/read-container';

import './css/grape-container.css';

import grapes from './img/grapes.png';

// 'GrapeContainer' holds state:
//      - all share content
// 		- (un)archived and archive tags

// make a reusable instance of axios here
// routing should all be contained to the grapecontainer

export class GrapeContainer extends Component {

	render() {
		return (
			<div className="GrapeContainer">
				<GrapeHeader />
				<div className="Sidebar-container">
	                <Sidebar 
	                	onLogout={ this.props.onLogout }/>
	            </div>
                <ReadContainer />
			</div>
		)
	}
}

const GrapeHeader = () => 
	<header className="GrapeHeader">
		<img src={ grapes } className="GrapeLogo" alt="logo" />
		<h1 className="GrapeHeader-title">Grapevine</h1>
	</header>
