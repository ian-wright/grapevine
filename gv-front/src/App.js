import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import { Stack } from './components/shares/index';

const fakeData = 
[
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
]
;

class App extends Component {
  render() {

    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <div>

        </div>
        <Stack 
          stackData={fakeData[0]}/>
      </div>
    );
  }
}

export default App;
