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
            user: null
        };

        this.validateToken = this.validateToken.bind(this);
        this.login = this.login.bind(this);
        this.logout = this.logout.bind(this);
        this.apiAxios = this.apiAxios.bind(this);

        // validate the token
        this.validateToken(this.state.authToken);

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
                this.setState({
                    isTokenValid: true,
                    user: {
                        firstName: response.data.first_name,
                        lastName: response.data.last_name,
                        email: response.data.email
                    }
                });
                console.log("isTokenValid:", this.state.isTokenValid);
            }).catch((error) => {
                if (error.response) {
                    // server side error
                    console.log("couldn't validate token with server");
                    this.setState({isTokenValid: false}); 
                    console.log("isTokenValid:", this.state.isTokenValid);
                } else if (error.request) {
                    // client side error
                    console.log("problem sending token validation request on client side");
                    console.log(error.request);
                } else {
                    console.log("error validating token");
                    console.log(error.message);
                }
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
            const user = response.data.response.user;
            localStorage.setItem('authToken', token);
            this.setState({
                isTokenValid: true,
                authToken: localStorage.getItem('authToken'),
                user: {
                    firstName: user.first_name,
                    lastName: user.last_name,
                    email: user.email
                }
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

    // ES6 object destructuring to simulate optional named params!
    apiAxios({url=null, method=null, data=null, cb=null, errCb=null}) {
        const baseURL = this.props.APIbaseURL;
        axios({
            method: method,
            baseURL: baseURL + url,
            headers: {'auth-token': this.state.authToken},
            data: data
        }).then((response) => {
            if (cb) {cb(response)};
        }).catch((error) => {
            if (error.response) {
                console.log("server side error", error.response);
                if (errCb) {errCb(error.response)};
            } else if (error.request) {
                console.log("client request error", error.request);
            } else {
                console.log("unexpected axios error", error.message);
            }
        });
    }

    render() {
        // TODO - add a third render state for isTokenValid==null (render a loading screen)

        return (
            <Router>
                <div className="App">
                    <Route exact path="/" render={()=>(<Redirect to="/grapes/vine"/>)}/>
                    <Route exact path="/grapes" render={()=>(<Redirect to="/grapes/vine"/>)}/>
                    <Route path="/grapes" render={(props)=>(
                        this.state.isTokenValid
                        ? (<GrapeContainer 
                                {...props}
                                onLogout={ this.logout }
                                ax={ this.apiAxios }
                                user={ this.state.user }/>)
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
