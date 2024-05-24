import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './LoginComponent.css';

const LoginComponent = () => {
    const [correo, setCorreo] = useState('');
    const [contrasena, setContrasena] = useState('');
    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault();
        fetch('http://127.0.0.1:3200/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ correo, contrasena }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'error') {
                console.error('Error:', data.message);
            } else {
                console.log('Success:', data);
                navigate('/menu');
            }
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    };

    const handleNavigateToRegister = () => {
        navigate('/register');
    };

    return (
        <div className="login-container">
            <h2>Login</h2>
            <form onSubmit={handleLogin}>
                <div>
                    <label htmlFor="correo">Correo:</label>
                    <input
                        type="email"
                        id="correo"
                        value={correo}
                        onChange={(e) => setCorreo(e.target.value)}
                    />
                </div>
                <div>
                    <label htmlFor="contrasena">Contraseña:</label>
                    <input
                        type="password"
                        id="contrasena"
                        value={contrasena}
                        onChange={(e) => setContrasena(e.target.value)}
                    />
                </div>
                <button type="submit">Login</button>
            </form>
            <button onClick={handleNavigateToRegister} className="navigate-button">
                Go to Register
            </button>
        </div>
    );
};

export default LoginComponent;
