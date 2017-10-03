import React, { Component } from 'react';

import closedMail from './img/closed-mail.png';
import openMail from './img/open-mail.png';

import './css/shares.css';

export class Stack extends Component {
    constructor(props) {
        super(props);
        this.state = {
            
        }
    }

    render() {
        const data = this.props.stackData;
        const allItems = data.items.map((item) =>
        <Item
            key={item.title + item.source} 
            title={item.title}
            author={item.author}
            source={item.source}
            content={item.content}
            isRead={item.isRead}
            isArchived={item.isArchived}
            isTrash={item.isTrash}/>
        );
        // const nonArchivedItems = allItems.filter((item) =>
        //     !item.state.isArchived
        // );
        return (
            <div className="Stack">
                <StackHeader 
                    sender={data.sender}/>
                {allItems}
            </div>
        )
    }
}

class Item extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isRead: this.props.isRead,
            isArchived: this.props.isArchived,
            isTrash: this.props.isTrash
        };
        this.toggleIsRead = this.toggleIsRead.bind(this);
        this.toggleIsArchived = this.toggleIsArchived.bind(this);
    }

    toggleIsRead() {
        // TODO - should only be allowed to go from read to unread
        this.setState({
            isRead: !this.state.isRead
        });
    }

    toggleIsArchived() {
        this.setState({
            isArchived: !this.state.isArchived
        });
    }

    render() {
        const title = this.props.title;
        const source = this.props.source;
        return (
            <div className="Item">
                <div className="Item-content-container Item-container">
                    <IsReadIndicator 
                        onClickHandler={this.toggleIsRead}
                        isRead={this.state.isRead}/>
                    <div className="Item-title Item-content">{title}</div>
                    <div className="Item-source Item-content">{source}</div>
                </div>
                <div className="Item-control-container Item-container">
                    <ControlButton 
                        text="Archive"
                        onClickHandler={this.toggleIsArchived}/>
                    <ControlButton text="Trash"/>
                </div>
            </div>
        );
    }
}

const StackHeader = props =>
    <div className="Stack-header">
        from: <b>{props.sender}</b>
    </div>

const ControlButton = props =>
    <button onClick={props.onClickHandler} className="Item-control" type="button">
        {props.text}
    </button>


const IsReadIndicator = props => {
    const mailImg = props.isRead
        ? <img src={openMail} alt="read"/>
        : <img src={closedMail} alt="unread"/>;
    
    return (
        <div className="Item-isRead Item-content" onClick={props.onClickHandler}>
            {mailImg}
        </div>
    );
	
}



