import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { OrderProvider } from './context/OrderContext';
import { AuthProvider } from './context/AuthContext';
import Home from './user/home/Home';
import DishSelectionPage from './user/DishSelectionPage';
import FeedbackPage from './user/feedback/FeedbackPage';
import AdminPanel from './admin/AdminPanel';
import OrderPanel from './admin/order/OrderPanel';
import Login from './admin/auth/Login';
import Register from './admin/auth/Register';
import Auth from './admin/auth/Auth';
import StaffRoute from './routes/StaffRoute';


export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/menu"
          element={
            <OrderProvider>
              <DishSelectionPage />
            </OrderProvider>
          }
        />
        <Route path="/feedback" element={<FeedbackPage />} />

        <Route element={<AuthProvider />}>
        <Route path="/auth" element={<Auth />}>
          <Route index element={<Navigate to="login" replace />} />
          <Route path="login" element={<Login />} />
          <Route path="register" element={<Register />} />
        </Route>
        <Route element={<StaffRoute />}>
          <Route path="/admin" element={<AdminPanel />} />
          <Route path="/admin/orders" element={<OrderPanel />} />
        </Route>
        </Route>
      </Routes>
      <ToastContainer position="top-center" autoClose={3000} />
    </Router>
  );
}

