import { toast } from 'react-toastify';
import { useNavigate, useLocation } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { register } from '../../utils/authUtils';
import { Form, Spinner } from '../../components';


export default function Register() {
  const navigate = useNavigate();
  const location = useLocation();
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuth()

  const handleSubmit = async (formData) => {
    setLoading(true);

    try {
      const id = await register(formData, setFieldErrors)
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
        { name: 'username', type: 'text', placeholder: "Ім'я", required: true, maxLength: 20 },
        { name: 'email', type: 'email', placeholder: 'Email', required: true, maxLength: 20 },
        { name: 'password', type: 'password', placeholder: "Пароль", required: true, maxLength: 20 },
        { name: 'confirmPassword', type: 'password', placeholder: "Підтвердіть пароль", required: true, maxLength: 20 },
      ]}
        title= "Реєстрація"
        buttonText="Реєструватись"
        onSubmit={handleSubmit}
        fieldErrors={fieldErrors}
        loading={loading}
        note={
          <p className="form-note">
            Маєте акаунт?
            <button className="m-btn" type="button" onClick={() => navigate("../login")}>
             Авторизація
            </button>
          </p>
        }
      />
  );
}
