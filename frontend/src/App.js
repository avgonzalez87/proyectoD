// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginComponent from './components/LoginComponent';
import RegisterComponent from './components/RegisterComponent';
import './App.css';

function App() {
    return (
        <Router>
            <Routes>
                <Route exact path="/" element={<LoginComponent />} />
                <Route path="/register" element={<RegisterComponent />} />
            </Routes>
        </Router>
    );
}

export default App;
