import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { Spinner } from '../../components';
import { useAuth } from '../../context/AuthContext';


export default function Auth() {
  const location = useLocation();
  const { user } = useAuth();

  const from = location.state?.from?.pathname || '/admin';

  if (user === undefined) {
    return <Spinner />;
  }

  if (user) {
    return <Navigate to={from} replace />;
  }

  return <Outlet />;
}
