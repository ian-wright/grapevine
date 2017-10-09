import React, { Component } from 'react';

import './css/sidebar.css';

export class Sidebar extends Component {
	constructor(props) {
		super(props);
		this.state = {
			selection: "read"
		};

		this.handleClick = this.handleClick.bind(this);
	}

	handleClick(name) {
		// change selection state for button styling
		this.setState({ selection: name })

		// perform the button's action
		if (name==='logout') {
			this.props.onLogout();
		}
	}

	render() {
		const sidebarButtonMeta = [
			{name: "read", display: "Read"},
			{name: "archive", display: "Archive"},
			{name: "addfriend", display: "Add Friend"},
			{name: "profile", display: "Profile"},
			{name: "logout", display: "Logout"}
		];

		const buttonsToRender = sidebarButtonMeta.map((meta) =>
			<SidebarButton 
					key={meta.name}
					name={meta.name}
					isActive={this.state.selection===meta.name}
					onClick={this.handleClick}
					display={meta.display}/>
		);
		return (
			<div className="Sidebar">
				<div className="Sidebar-button-container">
					{buttonsToRender}
				</div>
			</div>
		);
	}
}

class SidebarButton extends Component {

	handleClick = () => this.props.onClick(this.props.name)

	render () {
		const activeClass = this.props.isActive 
		    		? 'Sidebar-active'
		    		: 'Sidebar-inactive'
		return (
		    <div 
		    	className={"Sidebar-button " + activeClass}
		    	onClick={this.handleClick}>
		        {this.props.display}
		    </div>
		)
	}
}