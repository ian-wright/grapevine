import React, { Component } from 'react';
import axios from 'axios';

import { GrapeContainer } from './routes/shared/grape-container';
import { LoadScreen } from './routes/loading/load-screen';
import { LoginRegister } from './routes/login-register/login-register';


// 'App' holds state:
//      - auth token

// 'App' controls flow from login to main page and back

class App extends Component {

    constructor(props) {
        super(props);
        // assume an auth token already exists in localStorage (validity unknown)
        this.state = {
            authToken: localStorage.getItem('authToken'),
            isTokenValid: null
        };

        this.validateToken = this.validateToken.bind(this);
        this.login = this.login.bind(this);
        this.logout = this.logout.bind(this);

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
                console.log(response);
                this.setState({isTokenValid: true});
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

    login() {
        console.log("valid token saved; logging in.")
        this.setState({
            isTokenValid: true
        });
    }

    logout() {
        console.log("killing token; logging out.")
        localStorage.removeItem('authToken');
        this.setState({
            isTokenValid: false
        });
    }

    render() {
        let toRender;
        if (this.state.isTokenValid === false) {
            // invalid or missing token
            toRender = <LoginRegister 
                            APIbaseURL={ this.props.APIbaseURL }
                            onFreshToken={ this.login }/>;
        } else if (this.state.isTokenValid === true) {
            // valid token
            toRender = <GrapeContainer 
                            onLogout={ this.logout }/>;
        } else {
            // status: still loading token (null)
            toRender = <LoadScreen />;
        }

        return (
            <div className="App">
                { toRender }
            </div>
        );
    }
}

export default App;
