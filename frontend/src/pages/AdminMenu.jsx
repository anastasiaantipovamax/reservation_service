import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import { AdminHeader, AdminNav } from './AdminBookings.jsx';

export default function AdminMenu() {
  const [items, setItems] = useState([]);
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ name: '', category: '', price: '', description: '', image: null });

  const load = () => api.get('/menu/').then((res) => setItems(res.data));
  useEffect(() => { load(); }, []);

  const editingItem = useMemo(() => items.find((item) => item.id === editId), [items, editId]);
  const selectedImagePreview = useMemo(() => (form.image ? URL.createObjectURL(form.image) : null), [form.image]);

  const reset = (formEl) => {
    setEditId(null);
    setMessage('');
    setForm({ name: '', category: '', price: '', description: '', image: null });
    formEl?.reset();
  };

  const submit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const data = new FormData();
      data.append('name', form.name);
      data.append('category', form.category || '');
      data.append('price', form.price);
      data.append('description', form.description || '');
      if (form.image) data.append('image', form.image);

      if (editId) await api.patch(`/menu/${editId}/`, data);
      else await api.post('/menu/', data);

      setMessage(editId ? 'Блюдо обновлено.' : 'Блюдо добавлено.');
      reset(e.target);
      await load();
    } catch (err) {
      setMessage(JSON.stringify(err.response?.data || 'Ошибка сохранения блюда'));
    }
  };

  const startEdit = (item) => {
    setMessage('');
    setEditId(item.id);
    setForm({ name: item.name, category: item.category || '', price: item.price, description: item.description || '', image: null });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const remove = async (id) => {
    if (!window.confirm('Удалить позицию меню?')) return;
    await api.delete(`/menu/${id}/`);
    load();
  };

  return (
    <section className="adminPage">
      <AdminHeader title="Меню" subtitle="Управление блюдами, ценами, категориями и изображениями" />
      <AdminNav active="adminMenu" />
      <div className="adminPanel splitPanel">
        <form onSubmit={submit} className="adminForm">
          <h2>{editId ? 'Редактировать блюдо' : 'Добавить блюдо'}</h2>
          <label>Название<input placeholder="Паста" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required /></label>
          <label>Категория<input placeholder="Горячее" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} /></label>
          <label>Цена<input placeholder="780" value={form.price} onChange={(e) => setForm({ ...form, price: e.target.value })} required /></label>
          <label>Описание<input placeholder="Краткое описание блюда" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
          <label>Изображение блюда<input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" onChange={(e) => setForm({ ...form, image: e.target.files?.[0] || null })} /></label>
          <div className="uploadPreviewBox">
            <span>Предпросмотр изображения</span>
            {(selectedImagePreview || editingItem?.image_url) ? (
              <img className="uploadPreviewImage" src={selectedImagePreview || editingItem.image_url} alt="Предпросмотр блюда" />
            ) : (
              <div className="uploadPreviewEmpty">После выбора файла изображение появится здесь</div>
            )}
          </div>
          <div className="formActions"><button>{editId ? 'Сохранить' : 'Добавить'}</button>{editId && <button type="button" className="ghost" onClick={(e) => reset(e.currentTarget.closest('form'))}>Отмена</button>}</div>
          {message && <p className={message.includes('Ошибка') ? 'error' : 'success'}>{message}</p>}
        </form>
        <div className="tableWrap">
          <table className="adminTable">
            <thead><tr><th>Фото</th><th>Название</th><th>Категория</th><th>Цена</th><th>Действие</th></tr></thead>
            <tbody>
              {items.map((m) => <tr key={m.id}><td>{m.image_url ? <img className="tableThumb" src={m.image_url} alt={m.name} /> : <span className="miniPlaceholder">Фото</span>}</td><td>{m.name}</td><td>{m.category || '-'}</td><td>{m.price} ₽</td><td className="actionCell"><button className="smallButton" onClick={() => startEdit(m)}>Ред.</button><button className="smallButton danger" onClick={() => remove(m.id)}>Удал.</button></td></tr>)}
              {!items.length && <tr><td colSpan="5" className="emptyCell">Позиции меню не добавлены</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
