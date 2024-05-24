import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MenuComponent.css';

const MenuComponent = () => {
    const navigate = useNavigate();

    const handleMakeReservation = () => {
        navigate('/make-reservation');
    };

    const handleViewReservations = () => {
        navigate('/view-reservations');
    };

    const handleCancelReservation = () => {
        navigate('/cancel-reservation');
    };

    return (
        <div className="menu-container">
            <h2>Menú Principal</h2>
            <button onClick={handleMakeReservation}>Realizar Reserva</button>
            <button onClick={handleViewReservations}>Ver Reservas Activas</button>
            <button onClick={handleCancelReservation}>Cancelar Reserva</button>
        </div>
    );
};

export default MenuComponent;
