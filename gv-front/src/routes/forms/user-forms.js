import React, { Component } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom'

import './css/user-forms.css';

import grapes from '../shared/img/grapes.png';


export class Login extends Component {
	constructor(props) {
		super(props);
		this.state = {
			email: '',
			password: ''
		};

		this.handleCredChange = this.handleCredChange.bind(this);
		this.submitForm = this.submitForm.bind(this);
	}

	handleCredChange(e) {
	    const value = e.target.value;
	    const name = e.target.name;

	    this.setState({
	    	[name]: value
	    });
	}

	submitForm(e){
		this.props.onLogin(
			this.state.email,
			this.state.password
		)
	}

	render() {
		return (
			<div className="Login">
				<form>
					<img src={ grapes } className="App-logo" alt="logo" />
					<br />
					<input
						name="email"
						type="text"
						placeholder=" Email"
						value={ this.state.email }
						onChange={ this.handleCredChange } />
					<br />
					<input
						name="password"
						type="password"
						placeholder=" Password"
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
				<Link to="/forgot">Forgot Password?</Link>
				<br />
				<Link to="/register">Register</Link>
			</div>
		);
	  }
}


export class Register extends Component {
	constructor(props) {
		super(props);
		this.state = {
			first_name: '',
			last_name: '',
			email: '',
			password: ''
		};

		this.handleCredChange = this.handleCredChange.bind(this);
		this.submitForm = this.submitForm.bind(this);
		this.register = this.register.bind(this);
	}

	handleCredChange(e) {
	    const value = e.target.value;
	    const name = e.target.name;

	    this.setState({
	    	[name]: value
	    });
	}

	submitForm(e) {
		console.log("registering new user!");
		this.register();
	}

	register() {
		const baseURL = this.props.APIbaseURL;
		console.log("url:", baseURL + '/register');
		axios({
            method: 'post',
            url: baseURL + '/register',
            data: {
            	first_name: this.state.first_name,
            	last_name: this.state.last_name,
            	email: this.state.email,
            	password: this.state.password,
            	password_confirm: this.state.password
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
			<div className="Register">
				<form>
					<img src={ grapes } className="App-logo" alt="logo" />
					<br />
					<input
						name="first_name"
						type="text"
						placeholder=" First Name"
						value={ this.state.first_name }
						onChange={ this.handleCredChange } />
					<br />
					<input
						name="last_name"
						type="text"
						placeholder=" Last Name"
						value={ this.state.last_name }
						onChange={ this.handleCredChange } />
					<br />
					<input
						name="email"
						type="text"
						placeholder=" Email"
						value={ this.state.email }
						onChange={ this.handleCredChange } />
					<br />
					<input
						name="password"
						type="password"
						placeholder=" Password"
						value={ this.state.password }
						onChange={ this.handleCredChange } />
					<br />
					<button
						type="button"
						name="submit"
						onClick={ this.submitForm }>
						Register
					</button>
				</form>
				<Link to="/login">Already have an account?</Link>
			</div>
		);
	}
}


export class Forgot extends Component {
	constructor(props) {
		super(props);
		this.state = {
			email: '',
			password: ''
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
		this.getFreshToken();
	}

	render() {
		return (
			<div className="Login">
				<form>
					<img src={ grapes } className="App-logo" alt="logo" />
					<br />
					<input
						name="email"
						type="text"
						placeholder=" Email"
						value={ this.state.email }
						onChange={ this.handleCredChange } />
					<br />
					<input
						name="password"
						type="password"
						placeholder=" Password"
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
				<a>Forgot Password?</a>
				<br />
				<Link to="/register">Register</Link>
			</div>
		);
	}
}