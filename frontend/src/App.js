// frontend/src/App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import LoginComponent from './components/LoginComponent';
import RegisterComponent from './components/RegisterComponent';
import MenuComponent from './components/MenuComponent';
import './App.css';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<LoginComponent />} />
                <Route path="/register" element={<RegisterComponent />} />
                <Route path="/menu" element={<MenuComponent />} />
                {/* Añadir rutas para las acciones del menú cuando se implementen */}
            </Routes>
        </Router>
    );
}

export default App;
