import { useNavigate } from "react-router-dom";
import { Header, Footer } from '../components';
import Dashboard from './Dashboard';
import note from '../assets/images/note.svg';
import { useAuth } from '../context/AuthContext';


const navLinks =  [{ to: '/admin/orders', src: note, alt: 'Замовлення', name: 'Замовлення' }]

export default function AdminPanel() {
  const { user, logoutUser } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logoutUser();
    navigate("/auth/login", { replace: true });
  };

  return (
    <>
      <Header navLinks={navLinks} />
      <div className='order-note'>
        <span>
          Користувач: {user ?? "Не авторизований"}
        </span>
        <span>
          <button className="cancel-butt" onClick={handleLogout}>Вийти</button>
        </span>
      </div>

      <div className="content">
        <Dashboard />
      </div>
      <Footer />
    </>
  );
}
