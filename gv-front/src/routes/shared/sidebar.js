import React, { Component } from 'react';
import { withRouter } from 'react-router-dom'
import ReactModal from 'react-modal';

import { AddFriendForm } from './friend-ops';

import './css/sidebar.css';

export class Sidebar extends Component {

	/*
	required PROPS:
		- onLogout function
		- axios grapevine API instance
	*/

	constructor(props) {
		super(props);
		//TODO - look at the this.props.location.pathname - and set the selection state accordingly
		this.state = {
			currentSelection: "vine",
			lastSelection: null
		};

		this.handleActiveStyle = this.handleActiveStyle.bind(this);
		this.revertSelection = this.revertSelection.bind(this);
	}

	handleActiveStyle(name) {
		// change selection state for button styling
		const selectionBeforeChange = this.state.currentSelection;
		this.setState({
			currentSelection: name,
			lastSelection: selectionBeforeChange
		});
	}

	revertSelection() {
		const selectionBeforeFriend = this.state.lastSelection;
		this.setState({
			currentSelection: selectionBeforeFriend,
		});
	}



	render() {
		// the sidebar is made up of a mixture of react-router links (to defined paths),
		// and regular buttons that trigger actions. If a 'routePath' is provided, the button
		// is a ReactRouter route, but if an 'action' is provided, it's a normal button.
		const sidebarButtonMeta = [
			{
				routePath: "/grapes/vine",
				name: "vine",
				display: "Vine"
			},
			{
				routePath: "/grapes/fridge",
				name: "fridge",
				display: "Fridge"
			},
			{
				action: (() => undefined),
				name: "friend",
				display: "Add Friend"
			},
			{
				routePath: "/grapes/me",
				name: "me",
				display: "Me"
			},
			{
				action: this.props.onLogout,
				name: "logout",
				display: "Logout"
			}
		];



		const buttonsToRender = sidebarButtonMeta.map((meta) => {
			if (meta.routePath) {
				return (
					<SidebarLink 
						key={meta.name}
						name={meta.name}
						isActive={this.state.currentSelection===meta.name}
						path={meta.routePath}
						display={meta.display}
						handleActiveStyle={this.handleActiveStyle}/>
				)
			} else {
				return (
					<SidebarAction
						key={meta.name}
						name={meta.name}
						isActive={this.state.currentSelection===meta.name}
						action={meta.action}
						display={meta.display}
						handleActiveStyle={this.handleActiveStyle}/>
				)
			}
		});

		return (
			<div>
				<div className="Sidebar">
					<div className="Sidebar-button-container">
						{buttonsToRender}
					</div>
				</div>

				<ReactModal
		            isOpen={this.state.currentSelection==="friend"}
		            shouldCloseOnOverlayClick={true}
		            onRequestClose={this.revertSelection}
		            contentLabel="Connect with a friend."
		            style={{
		            	overlay: {},
		            	content: {
		            		position: "relative",
							bottom: "180px",
							left: "90px",
							height: "90px",
							width: "360px"
		            	} 
		            }}>
		            <div>
		            	<AddFriendForm 
		            		ax={ this.props.ax }/>
		           	</div>
		        </ReactModal>
	        </div>
		);
	}
}


const SidebarAction = props => {

	const activeClass = props.isActive ? 'Sidebar-active' : 'Sidebar-inactive'

	return (
		<div
			className={"Sidebar-button " + activeClass}
	    	onClick={() => {
	    		props.handleActiveStyle(props.name)
	    		props.action()
	    	}}>
	    	{props.display}
		</div>
	)
}


const SidebarLink = withRouter(props => {

	const activeClass = props.isActive ? 'Sidebar-active' : 'Sidebar-inactive'

	return (
		<div
			className={"Sidebar-button " + activeClass}
	    	onClick={() => {
	    		props.handleActiveStyle(props.name)
	    		props.history.push(props.path)
	    	}}>
	    	{props.display}
		</div>
	)
})