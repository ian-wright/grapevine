import React, { Component } from 'react';
import { Stack } from './stack/stack';

const fakeData = [
    {
        sender: "Mike",
        items: [
            {
                title: "Trump dead!",
                author: "Bill Smith",
                source: "NYT",
                content: "blerp",
                isRead: false,
                isArchived: false,
                isTrash: false
            },
            {
                title: "Rejoice!",
                author: "Rick Smith",
                source: "Huffpost",
                content: "blerp",
                isRead: false,
                isArchived: false,
                isTrash: false
            },
            {
                title: "Knicks lose.",
                author: "Steve Smith",
                source: "SportThing",
                content: "blerp",
                isRead: false,
                isArchived: false,
                isTrash: false
            }
        ]
    }
];

export class ReadContainer extends Component {

	render() {
		return (
			<div className="ReadContainer">
            	<Stack 
            		stackData={fakeData[0]}/>
            </div>
		)
	}
}
