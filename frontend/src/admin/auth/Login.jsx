import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { login } from '../../utils/authUtils';
import { Form, Spinner } from '../../components';


export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuth()

  const handleSubmit = async (formData) => {
    setLoading(true);

    try {
      const id = await login(formData, setFieldErrors)
      if (id) {
        setUser(id);
      }

    } finally {
      setLoading(false);
    }
  };
  if (loading) return <Spinner />

  return (
    <Form
      fields={[
        { name: 'email', type: 'email', placeholder: 'Email', required: true, maxLength: 20},
        { name: 'password', type: 'password', placeholder: 'Пароль', required: true, maxLength: 20},
      ]}
      title= "Авторизація"
      buttonText="Логін"
      onSubmit={handleSubmit}
      fieldErrors={fieldErrors}
      loading={loading}
      note={
        <p className="form-note">
          Немає акаунту?
          <button className="m-btn" type="button" onClick={() => navigate("../register")}>
            Реєстрація
          </button>
        </p>
      }
    />
  );
}
