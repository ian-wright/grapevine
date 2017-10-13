import React, { Component } from 'react';
import { Route } from 'react-router-dom';
// import ReactModal from 'react-modal';

import { Sidebar } from './sidebar';
import { ReadContainer } from '../read/read-container';
import { ArchiveContainer } from '../archive/archive-container';
import { ProfileContainer } from '../profile/profile-container';

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
			// render a redirect to login if not logged in
			<div className="GrapeContainer">
				<GrapeHeader />
				<div className="Sidebar-container">
	                <Sidebar 
	                	onLogout={ this.props.onLogout }/>
	            </div>
	        	{/* this is where children get rendered (nested routes) */}
	        	<Route path={`${this.props.match.url}/vine`} component={ReadContainer}/>
                <Route path={`${this.props.match.url}/fridge`} component={ArchiveContainer}/>
                <Route path={`${this.props.match.url}/me`} component={ProfileContainer}/>
			</div>
		)
	}
}

const GrapeHeader = () => 
	<header className="GrapeHeader">
		<img src={ grapes } className="GrapeLogo" alt="logo" />
		<h1 className="GrapeHeader-title">Grapevine</h1>
	</header>
