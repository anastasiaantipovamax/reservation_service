import { useState } from 'react';
import { api, saveAuth } from '../api/client';

export default function Register({ setPage }) {
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');

  const submit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      const res = await api.post('/auth/register/', form);
      saveAuth(res.data);
      setPage('menu');
    } catch (err) {
      setError(JSON.stringify(err.response?.data || 'Ошибка регистрации'));
    }
  };

  return (
    <section className="card authCard">
      <h1>Регистрация</h1>
      <form onSubmit={submit}>
        <input placeholder="Логин" value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} />
        <input placeholder="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input placeholder="Пароль" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        {error && <p className="error">{error}</p>}
        <button>Создать аккаунт</button>
      </form>
      <p><a href="#" onClick={(e) => { e.preventDefault(); setPage('login'); }}>Вернуться ко входу</a></p>
    </section>
  );
}
