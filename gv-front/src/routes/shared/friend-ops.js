import React, { Component } from 'react';
import axios from 'axios';

export class AddFriendForm extends Component {

	constructor(props) {
		super(props);
		this.state = {friendEmail: ''};

		this.handleTextChange = this.handleTextChange.bind(this);
		this.submitForm = this.submitForm.bind(this);
	}

	handleTextChange(e) {
		const value = e.target.value;
		this.setState({friendEmail: value});
	}

	submitForm() {
		console.log("adding a friend");
	}

	render() {
		return (
			<div className="addFriendForm">
				<form>
					<input
						name="friendEmail"
						type="text"
						placeholder=" Friend's email"
						value={ this.state.friendEmail }
						onChange={ this.handleTextChange } />
					<button
						type="button"
						name="submit"
						onClick={ this.submitForm }>
						Connect
					</button>
				</form>
			</div>
		);
	}
}
