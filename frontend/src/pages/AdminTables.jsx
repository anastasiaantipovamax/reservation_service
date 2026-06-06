import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';
import { AdminHeader, AdminNav } from './AdminBookings.jsx';

export default function AdminTables() {
  const [items, setItems] = useState([]);
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ number: '', capacity: '', description: '', image: null });

  const load = () => api.get('/tables/').then((res) => setItems(res.data));
  useEffect(() => { load(); }, []);

  const editingTable = useMemo(() => items.find((item) => item.id === editId), [items, editId]);
  const selectedImagePreview = useMemo(() => (form.image ? URL.createObjectURL(form.image) : null), [form.image]);

  const reset = (formEl) => {
    setEditId(null);
    setMessage('');
    setForm({ number: '', capacity: '', description: '', image: null });
    formEl?.reset();
  };

  const submit = async (e) => {
    e.preventDefault();
    setMessage('');
    try {
      const data = new FormData();
      data.append('number', form.number);
      data.append('capacity', form.capacity);
      data.append('description', form.description || '');
      if (form.image) data.append('image', form.image);

      if (editId) await api.patch(`/tables/${editId}/`, data);
      else await api.post('/tables/', data);

      setMessage(editId ? 'Столик обновлён.' : 'Столик добавлен.');
      reset(e.target);
      await load();
    } catch (err) {
      setMessage(JSON.stringify(err.response?.data || 'Ошибка сохранения столика'));
    }
  };

  const startEdit = (table) => {
    setMessage('');
    setEditId(table.id);
    setForm({ number: table.number, capacity: table.capacity, description: table.description || '', image: null });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const remove = async (id) => {
    if (!window.confirm('Удалить столик?')) return;
    await api.delete(`/tables/${id}/`);
    load();
  };

  return (
    <section className="adminPage">
      <AdminHeader title="Столики" subtitle="Добавление, редактирование и загрузка изображений столиков" />
      <AdminNav active="adminTables" />
      <div className="adminPanel splitPanel">
        <form onSubmit={submit} className="adminForm">
          <h2>{editId ? 'Редактировать столик' : 'Добавить столик'}</h2>
          <label>Номер<input placeholder="Например, 6" value={form.number} onChange={(e) => setForm({ ...form, number: e.target.value })} required /></label>
          <label>Количество мест<input placeholder="Например, 4" value={form.capacity} onChange={(e) => setForm({ ...form, capacity: e.target.value })} required /></label>
          <label>Описание<input placeholder="У окна, диван + стулья" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} /></label>
          <label>Изображение столика<input type="file" accept="image/png,image/jpeg,image/webp,image/svg+xml" onChange={(e) => setForm({ ...form, image: e.target.files?.[0] || null })} /></label>
          <div className="uploadPreviewBox">
            <span>Предпросмотр изображения</span>
            {(selectedImagePreview || editingTable?.image_url) ? (
              <img className="uploadPreviewImage" src={selectedImagePreview || editingTable.image_url} alt="Предпросмотр столика" />
            ) : (
              <div className="uploadPreviewEmpty">После выбора файла изображение появится здесь</div>
            )}
          </div>
          <div className="formActions"><button>{editId ? 'Сохранить' : 'Добавить'}</button>{editId && <button type="button" className="ghost" onClick={(e) => reset(e.currentTarget.closest('form'))}>Отмена</button>}</div>
          {message && <p className={message.includes('Ошибка') ? 'error' : 'success'}>{message}</p>}
        </form>
        <div className="tableWrap">
          <table className="adminTable">
            <thead><tr><th>Фото</th><th>Номер</th><th>Мест</th><th>Описание</th><th>Действие</th></tr></thead>
            <tbody>
              {items.map((t) => <tr key={t.id}><td>{t.image_url ? <img className="tableThumb" src={t.image_url} alt={`Столик ${t.number}`} /> : <span className="miniPlaceholder">Схема</span>}</td><td>Столик {t.number}</td><td>{t.capacity}</td><td>{t.description || 'Без описания'}</td><td className="actionCell"><button className="smallButton" onClick={() => startEdit(t)}>Ред.</button><button className="smallButton danger" onClick={() => remove(t.id)}>Удал.</button></td></tr>)}
              {!items.length && <tr><td colSpan="5" className="emptyCell">Столики не добавлены</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
