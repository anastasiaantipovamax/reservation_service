import { useState } from 'react';
import { api, saveAuth } from '../api/client';

export default function Login({ setPage }) {
  const [form, setForm] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.post('/auth/login/', form);
      saveAuth(res.data);
      setPage('menu');
    } catch (err) {
      setError(err.response?.data?.detail || 'Ошибка входа');
    }
  };

  return (
    <section className="card authCard">
      <h1>Вход в систему</h1>
      <form onSubmit={submit}>
        <input placeholder="Логин" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input placeholder="Пароль" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        {error && <p className="error">{error}</p>}
        <button>Войти</button>
      </form>
      <p>Нет аккаунта? <a href="#" onClick={(e) => { e.preventDefault(); setPage('register'); }}>Зарегистрироваться</a></p>
      <p className="hint">Демо: user/user12345 или admin/admin12345</p>
    </section>
  );
}
