import React, { Component } from 'react';
import axios from 'axios';

import grapes from '../shared/img/grapes.png';

export class Login extends Component {
	constructor(props) {
		super(props);
		this.state = {
			email: '',
			password: '',
		};

		this.handleCredChange = this.handleCredChange.bind(this);
		this.submitForm = this.submitForm.bind(this);
		this.getFreshToken = this.getFreshToken.bind(this);
	}

	handleCredChange(e) {
	    const value = e.target.value;
	    const name = e.target.name;

	    this.setState({
	    	[name]: value
	    });
	}

	submitForm(e) {
		console.log("logging in!");
		this.getFreshToken(
			this.state.email,
			this.state.password
		);
	}

	getFreshToken(email, password) {
		const baseURL = this.props.APIbaseURL;
		axios({
            method: 'post',
            url: baseURL + '/login',
            data: {
            	email: this.state.email,
            	password: this.state.password
            }
        }).then((response) => {
        	// response status 200 - OK
            console.log("response.data", response.data);
            // save the token
            const token = response.data.response.user.authentication_token;
            localStorage.setItem('authToken', token);
            this.props.onFreshToken();
        }).catch((error) => {
            if (error.response) {
                console.log(error.response.data);
            } else if (error.request) {
                console.log(error.request);
            } else {
                console.log(error.message);
            }
		});
    }

	render() {
		return (
			<form>
				<img src={ grapes } className="App-logo" alt="logo" />
				<br />
				<input
					name="email"
					type="text"
					placeholder=" email"
					value={ this.state.email }
					onChange={ this.handleCredChange } />
				<br />
				<input
					name="password"
					type="text"
					placeholder=" password"
					value={ this.state.password }
					onChange={ this.handleCredChange } />
				<br />
				<button
					type="button"
					name="submit"
					onClick={ this.submitForm }>
					Login
				</button>

			</form>
		);
	  }
}