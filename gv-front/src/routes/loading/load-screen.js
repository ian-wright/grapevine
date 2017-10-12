// import React, { Component } from 'react';
import React from 'react';

import './css/load-screen.css'

import grapes from '../shared/img/grapes.png';


export const LoadScreen = () =>
    <div className="LoadScreen">
        <img src={ grapes } className="App-logo" alt="logo" />
        <h1 className="App-title">Grapevine</h1>
    </div>