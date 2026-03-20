import { toast } from 'react-toastify';
import { sendToServer } from './api';


const validateEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const handleError = (error, setFieldErrors) => {
  if (error?.status === 401) {
    toast.error(error.message || "Не вірний Логін або Пароль!");
  } else {
    toast.error(error.message || "Помилка з'єднання з сервером.");
  }
  setFieldErrors({});
};


export async function login(credentials, setFieldErrors) {
  const newErrors = {};

  if (!validateEmail(credentials.email)) {
    newErrors.email = 'Некоректна електронна пошта';
  }

  if (Object.keys(newErrors).length > 0) {
    setFieldErrors(newErrors);
    return null;
  }

  try {
    const { data } = await sendToServer('/api/admin/auth/login', credentials, 'POST');
    toast.success('Ви увійшли успішно!');
    return data.user_id
  } catch (error) {
    handleError(error, setFieldErrors);
    return null;
  }
}

export async function logout() {
  try {
    const { data } = await sendToServer('/api/admin/auth/logout', null, 'POST');
    toast.success(data.message || 'Ви вийшли з системи.');
  } catch (error) {
    if (error?.status === 401) {
      toast.error('Ви не авторизовані!');
    } else {
      toast.error("Зв'язок з сервером втрачено.");
    }
  }
}

export async function register(credentials, setFieldErrors) {
  const newErrors = {};

  if (!validateEmail(credentials.email)) {
    newErrors.email = 'Некоректна електронна пошта';
  }

  if (credentials.password && credentials.password !== credentials.confirmPassword) {
    newErrors.confirmPassword = 'Паролі не співпадають';
  }

  if (Object.keys(newErrors).length > 0) {
    setFieldErrors(newErrors);
    return null;
  }

  try {
    const { confirmPassword, ...dataToSend } = credentials;
    const { data } = await sendToServer('/api/admin/auth/register', dataToSend, 'POST');
    toast.success(data.message || 'Успішна реєстрація!');
    return data.user_id
  } catch (error) {
    handleError(error, setFieldErrors);
    return null;
  }
}

export async function checkAuth(role) {
  const endpoint =
    role === "client" ? "/api/users/me" : "/api/admin/me";

 try {
    const { data } = await sendToServer(endpoint, null, "GET");
    return data.id;
  } catch (error) {
    if (error?.status === 401 && role === "client") {
      const createdUserId = await createUser();
      return createdUserId;
    }

    toast.error(
      error?.message || "Не вдалося перевірити авторизацію."
    );
    return null;
  }
}

export async function createUser() {
  try {
    const { data }  = await sendToServer('/api/users', null, 'POST');
    return data.user_id;
  } catch (error) {
    toast.error(error.message || "Помилка реєстрації нового користувача.");
    return null;
  }
}
