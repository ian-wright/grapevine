import React, { Component } from 'react';
import checkedIcon from './checked.png';
import unCheckedIcon from './unchecked.png';
import './Extension.css';
declare var chrome: any;


class Extension extends Component {

    constructor(props) {
        super(props);
        // this is where the popup asks background.js for the current option set, then sets state
        chrome.runtime.getBackgroundPage(function(bg) {
            console.log("constructing extension component...");
            console.log(bg.GVvalid, bg.GVoptions);
        });
        this.state = {
            options: [
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
            selection: [],
            isLoggedIn: null
        };

        this.toggleOption = this.toggleOption.bind(this);
        this.share = this.share.bind(this);
    }

    componentWillMount() {
        // get logged in status from background; setState
        // render selectables if logged in, login form if not
    }

    toggleOption(email) {
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
        const renderedOptions = this.state.options.map(meta => 
            <Option
                key={meta.email}
                email={meta.email}
                firstName={meta.first_name}
                lastName={meta.last_name}
                isSelected={ selection.indexOf(meta.email) !== -1 }
                onClickHandler={this.toggleOption}/>
        );

        return (
            <div className="Extension">
                {renderedOptions}
                <button
                    type="button"
                    onClick={this.share}>
                    Share
                </button>
            </div>
        );
    }
}


class Option extends Component {

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
                className={ "Option-container Option-isSelected-" + this.props.isSelected }
                onClick={this.handleClick}>
                <div className="Option-name">
                    { this.props.firstName + ' ' + this.props.lastName }
                </div>
                <IsSelectedIcon
                    isSelected={this.props.isSelected} />
            </div>
        )
    }
}


const IsSelectedIcon = props => (
    <div className="Option-isSelectedIcon-container">
        {props.isSelected
    ? <img src={checkedIcon} alt="checked"/>
    : <img src={unCheckedIcon} alt="unchecked"/>}
    </div>
)

export default Extension;
