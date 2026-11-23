import { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { Header, Footer } from '../../components';
import OrderBoard from './OrderBoard';
import OrderCard from './OrderCard';
import control from '../../assets/images/control.svg';
import { useAuth } from '../../context/AuthContext';


export default function OrderPanel() {
  const navigate = useNavigate();
  const [selectedOrder, setSelectedOrder] = useState(null);
  const { user, setUser, logoutUser } = useAuth();

  const handleLogout = async () => {
    await logoutUser();
    navigate("/auth/login", { replace: true });
  };

  const navLinks =  [{ to: '/admin', src: control, alt: 'Панель', name: 'Панель' }]

  return (
    <>
      <Header navLinks={navLinks}/>
      <div className='order-note'>
        <span>Користувач: {user ? user : "Не авторизований"}</span>
        <span>
          <button className="cancel-butt" onClick={handleLogout}>Вийти</button>
        </span>
      </div>

      <div className='content'>
        {selectedOrder ? (
          <OrderCard selectedOrder={selectedOrder} setSelectedOrder={setSelectedOrder} />
        ) : (
          <OrderBoard setSelectedOrder={setSelectedOrder} name={user}/>
        )}
      </div>
      <Footer />
    </>
  );
}