import React, { Component } from 'react';
import checkedIcon from './checked.png';
import unCheckedIcon from './unchecked.png';
import './Extension.css';
declare var chrome: any;


class Extension extends Component {

    constructor(props) {
        console.log("constructing extension component...");
        super(props);

        this.toggleFriend = this.toggleFriend.bind(this);
        this.share = this.share.bind(this);
        this.mirrorBackgroundState = this.mirrorBackgroundState.bind(this);

        chrome.runtime.getBackgroundPage(this.mirrorBackgroundState);

        this.state = {
            friends2: null,
            friends: [
                {
                    first_name: 'Mike',
                    last_name: 'Cancilla',
                    email: 'mc@gmail.com'
                },
                {
                    first_name: 'Flora',
                    last_name: 'Devlin',
                    email: 'fd@gmail.com'
                },
                {
                    first_name: 'Piers',
                    last_name: 'Bonifant',
                    email: 'pb@gmail.com'
                }
            ],
            valid: null,
            selection: []
        };
    }

    mirrorBackgroundState(bg) {
        console.log("background state:", bg.GVstate);
            // intial state just mirrors that of the background page state

        this.setState({
            friends2: bg.GVstate.friends,
            valid: bg.GVstate.valid,
            user: bg.GVstate.user
        });

        console.log("extension state:", this.state);
    }

    toggleFriend(email) {
        let oldSelection = this.state.selection;
        const index = oldSelection.indexOf(email);
        let newSelection = oldSelection;
        if (index === -1) {
            newSelection.push(email);
            this.setState({
                selection: newSelection
            });
        } else {
            newSelection.splice(index, 1);
            this.setState({
                selection: newSelection
            }) ;
        };
    }

    share() {
        // send a URL and set of emails to background script here
        console.log("sending shares:", this.state.selection);

        chrome.runtime.sendMessage({
            action: "share",
            selection: this.state.selection
        }, function(response) {
            console.log("response from background", response);
        });
    }

    render() {
        const selection = this.state.selection;
        const renderedFriends = this.state.friends.map(meta => 
            <Friend
                key={meta.email}
                email={meta.email}
                firstName={meta.first_name}
                lastName={meta.last_name}
                isSelected={ selection.indexOf(meta.email) !== -1 }
                onClickHandler={this.toggleFriend}/>
        );

        if (this.state.valid) {
            return (
                <div className="Extension">
                    {renderedFriends}
                    <br/>
                        <Friend
                            email={this.state.user.email}
                            firstName="save"
                            lastName="for myself."
                            isSelected={ selection.indexOf(this.state.user.email) !== -1 }
                            onClickHandler={this.toggleFriend}/>
                    <br/>
                    <button
                        type="button"
                        onClick={this.share}>
                        Share
                    </button>
                </div>
            );
        } else {
            return (
                <div className="Extension">
                    <Login 
                        mirrorBackgroundState={this.mirrorBackgroundState}/>
                </div>
            );
        }
    }
}


class Friend extends Component {

    constructor(props) {
        super(props);
        this.handleClick = this.handleClick.bind(this);
    }

    handleClick() {
        this.props.onClickHandler(this.props.email);
    }

    render() {
        return (
            <div
                className={ "Friend-container Friend-isSelected-" + this.props.isSelected }
                onClick={this.handleClick}>
                <div className="Friend-name">
                    { this.props.firstName + ' ' + this.props.lastName }
                </div>
                <IsSelectedIcon
                    isSelected={this.props.isSelected} />
            </div>
        )
    }
}


const IsSelectedIcon = props => (
    <div className="Friend-isSelectedIcon-container">
        {props.isSelected
    ? <img src={checkedIcon} alt="checked"/>
    : <img src={unCheckedIcon} alt="unchecked"/>}
    </div>
)


class Login extends Component {
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
        console.log("logging in from extension");
        const mirrorBackgroundState = this.props.mirrorBackgroundState;
        chrome.runtime.sendMessage({
            action: "login",
            email: this.state.email,
            password: this.state.password
        }, function(response) {
            // TODO - for some reason I'm not getting the expected response (when I pass the sendResponse
            // function down a few levels as a callback) - seems to be returning too quickly

            // can either send the values right in the response
            console.log("response from background", response);
            chrome.runtime.getBackgroundPage(mirrorBackgroundState);
        });
    }

    render() {
        return (
                <form>
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
        );
      }
}

export default Extension;
