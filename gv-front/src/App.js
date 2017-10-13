import React, { Component } from 'react';
import axios from 'axios';
import {
  BrowserRouter as Router,
  Route,
  Redirect
} from 'react-router-dom'

import { GrapeContainer } from './routes/shared/grape-container';
import { LoadScreen } from './routes/loading/load-screen';
import { Login, Register, Forgot } from './routes/forms/user-forms';


// 'App' holds state:
//      - auth token
//      -

// 'App' controls flow from login to main page and back

class App extends Component {

    constructor(props) {
        super(props);
        // assume an auth token already exists in localStorage (validity unknown)
        this.state = {
            authToken: localStorage.getItem('authToken'),
            isTokenValid: null,
        };

        this.validateToken = this.validateToken.bind(this);
        this.login = this.login.bind(this);
        this.logout = this.logout.bind(this);

        // validate the token
        this.validateToken(this.state.authToken);

    }

    // create a top-level instance of an axios client that is flexible enough to use throughout the app
    axios(base, method, ) {

    }

    validateToken(token) {
        if (token == null) {
            // called before component is mounted
            this.state = {isTokenValid: false};
            console.log("isTokenValid:", this.state.isTokenValid);
        } else {
            const baseURL = this.props.APIbaseURL;
            axios({
                method: 'get',
                url: baseURL + '/validate-token',
                headers: {'auth-token': token}
            }).then((response) => {
                // response status 200 - OK
                console.log(response);
                this.setState({
                    isTokenValid: true
                });
                console.log("isTokenValid:", this.state.isTokenValid);
            }).catch((error) => {
                if (error.response) {
                    // server side error
                    console.log("couldn't validate token with server");
                    console.log(error.response.data);
                } else if (error.request) {
                    // client side error
                    console.log("problem sending token validation request on client side");
                    console.log(error.request);
                } else {
                    console.log("error validating token");
                    console.log(error.message);
                }
                this.setState({isTokenValid: false}); 
                console.log("isTokenValid:", this.state.isTokenValid);
            });
        }
    }

    login(email, password) {
        console.log("logging in...")
        const baseURL = this.props.APIbaseURL;
        console.log("baseURL:", baseURL);
        axios({
            method: 'post',
            url: baseURL + '/login',
            data: {
                email: email,
                password: password
            }
        }).then((response) => {
            // response status 200 - OK
            console.log("response.data", response.data);
            // save the token
            const token = response.data.response.user.authentication_token;
            localStorage.setItem('authToken', token);
            this.setState({
                isTokenValid: true,
                authToken: localStorage.getItem('authToken')
            });
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

    // add an API call to logout
    logout() {
        console.log("killing token; logging out.")
        localStorage.removeItem('authToken');
        this.setState({
            authToken: localStorage.getItem('authToken'),
            isTokenValid: null
        });
    }

    render() {
        return (
            <Router>
                <div className="App">
                    <Route exact path="/" render={()=>(<Redirect to="/grapes/vine"/>)}/>
                    <Route exact path="/grapes" render={()=>(<Redirect to="/grapes/vine"/>)}/>
                    <Route path="/grapes" render={(props)=>(
                        this.state.isTokenValid
                        ? (<GrapeContainer 
                                {...props}
                                onLogout={ this.logout }/>)
                        : (<Redirect to="/login"/>)
                    )}/>
                    <Route path="/login" render={(props)=>(
                        this.state.isTokenValid
                        ? (<Redirect to="/"/>)
                        : (<Login 
                            {...props}
                            APIbaseURL={ this.props.APIbaseURL }
                            onLogin={ this.login }/>)
                    )}/>
                    <Route path="/register" component={Register}/>
                    <Route path="/forgot" component={Forgot}/>
                </div>
            </Router>
        )
    }
}

export default App;
