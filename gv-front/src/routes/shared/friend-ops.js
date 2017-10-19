import React, { Component } from 'react';

export class AddFriendForm extends Component {

	constructor(props) {
		super(props);
		this.state = {
			friendEmail: '',
			message: null
		};

		this.handleTextChange = this.handleTextChange.bind(this);
		this.submitForm = this.submitForm.bind(this);
	}

	handleTextChange(e) {
		const value = e.target.value;
		this.setState({friendEmail: value});
	}

	submitForm() {
		if (this.state.friendEmail === '') {
			this.setState({message: "Provide an email address."});
			return
		}

		this.setState({message: "pending"});
		console.log("adding a friend...");
		const ax = this.props.ax;
		ax({
			url: '/add-friend',
			method: 'POST',
			data: {target_email: this.state.friendEmail},
			cb: ((response) => {
				const data = response.data;
				if (data.existing_friend !== 'false') {
					this.setState({
						message: `You're already connected to ${data.existing_friend.first_name} on Grapevine.`
					});
				} else if (data.existing_user !== 'false' && data.existing_user.sent_request === 'true') {
					this.setState({
						message: `We sent ${data.existing_user.first_name} your request.`
					});
				} else if (data.new_user !== 'false' && data.new_user.sent_request === 'true') {
					this.setState({
						message: `We sent ${data.new_user.email} a Grapevine invite.`
					});
				} else {
					this.setState({
						message: "Error: tell Ian it broke."
					});
				}
			}),
			errCb: ((response) => {
				console.log("handling dat err");
				response.status === 400
				? this.setState({message: "Provide a valid email address."})
				: this.setState({message: "Error: tell Ian it broke."})
			})
		});
	}

	render() {
		return (
			<div className="addFriendForm">
				{
					this.state.message === "pending"
					? (<div>loading component</div>)
					: (<div>
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
						<div className="addFriendForm-message">{ this.state.message }</div>
					</div>)
				}
			</div>
		);
	}
}
