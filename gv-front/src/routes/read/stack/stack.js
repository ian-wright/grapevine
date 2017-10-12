import React, { Component } from 'react';

import closedMail from './img/closed-mail.png';
import openMail from './img/open-mail.png';

import './css/stack.css';

// note - isArchived and isTrash are just tags used to persist state on server side;
//        on client-side, this state is maintained at the stack level, with a list
//        of items for: archived, notArchived, trash, notTrash


export class Stack extends Component {
    constructor(props) {
        super(props);

        this.archive = this.archive.bind(this);
    }

    componentWillMount() {
        const notArchived = [];
        const archived = [];
        this.props.stackData.items.forEach(function(item) {
            if (item.isArchived) {
                // relinquish archive state control to react
                delete item.isArchived;
                archived.push(item);
            } else {
                // relinquish archive state control to react
                delete item.isArchived;
                notArchived.push(item);
            }
        });

        this.setState({
            archived: archived,
            notArchived: notArchived
        });
    }

    // move an item from notArchived -> archived state
    archive(index) {
        const archived = this.state.archived;
        const notArchived = this.state.notArchived;
        archived.push(notArchived.splice(index, 1));
        this.setState({
            archived: archived,
            notArchived: notArchived
        });
    } 

    render() {
        const itemsToRender = this.state.notArchived.map((item) =>
            <Item
                key={item.title + item.source} 
                stackIndex={this.state.notArchived.indexOf(item)}
                title={item.title}
                author={item.author}
                source={item.source}
                content={item.content}
                isRead={item.isRead}
                archiveHandler={this.archive} />
        );

        return (
            <div className="Stack">
                <StackHeader 
                    sender={this.props.stackData.sender}/>
                {itemsToRender}
            </div>
        );
    }
}


class Item extends Component {
    constructor(props) {
        super(props);
        this.state = {
            isRead: this.props.isRead
        };
        this.toggleIsRead = this.toggleIsRead.bind(this);
        this.archive = this.archive.bind(this);
        
    }

    toggleIsRead() {
        // TODO - should only be allowed to go from read to unread
        this.setState({
            isRead: !this.state.isRead
        });
    }

    archive(e) {
        
        const indexToArchive = e.target.getAttribute("stack-index");
        console.log(e.target, indexToArchive);
        this.props.archiveHandler(indexToArchive);
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
                        stackIndex={this.props.stackIndex}
                        onClickHandler={this.archive}/>
                    <ControlButton 
                        text="Trash"/>
                </div>
            </div>
        );
    }
}


const StackHeader = props => (
    <div className="Stack-header">
        from: <b>{props.sender}</b>
    </div>
)


const ControlButton = props => (
    <button onClick={props.onClickHandler}
        className="Item-control"
        type="button"
        stack-index={props.stackIndex}>
        {props.text}
    </button>
)


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



