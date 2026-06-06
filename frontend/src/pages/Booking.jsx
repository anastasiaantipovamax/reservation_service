import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

function tableImage(table) {
  if (!table) return '/table-images/table-default.svg';
  const predefined = [1, 2, 3, 4, 5].includes(Number(table.number));
  return table.image_url || (predefined ? `/table-images/table-${table.number}.svg` : '/table-images/table-default.svg');
}

export default function Booking({ onCreated }) {
  const [tables, setTables] = useState([]);
  const [message, setMessage] = useState('');
  const [form, setForm] = useState({ table: '', date: '', time_start: '18:00', time_end: '20:00', guests_count: 2, comment: '' });

  useEffect(() => { api.get('/tables/').then((res) => setTables(res.data)); }, []);

  const selectedTable = useMemo(
    () => tables.find((table) => String(table.id) === String(form.table)),
    [tables, form.table]
  );

  const check = async () => {
    setMessage('');
    if (!form.table || !form.date || !form.time_start || !form.time_end) {
      setMessage('Заполните дату, время и выберите столик для проверки доступности.');
      return;
    }
    const params = new URLSearchParams({ table: form.table, date: form.date, time_start: form.time_start, time_end: form.time_end });
    const res = await api.get(`/bookings/availability/?${params.toString()}`);
    setMessage(res.data.available ? 'Столик доступен для выбранного времени' : 'Столик занят на выбранное время');
  };

  const submit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/bookings/', form);
      setMessage('Бронирование создано. Подтверждение отправлено на email и доступно в уведомлениях.');
      onCreated?.();
    } catch (err) {
      setMessage(JSON.stringify(err.response?.data || 'Ошибка бронирования'));
    }
  };

  return (
    <section className="card bookingCard">
      <h1>Бронирование столика</h1>
      <div className="bookingLayout">
        <form onSubmit={submit} className="formGrid bookingForm">
          <label>Дата<input type="date" value={form.date} onChange={(e) => setForm({ ...form, date: e.target.value })} required /></label>
          <label>Время начала<input type="time" value={form.time_start} onChange={(e) => setForm({ ...form, time_start: e.target.value })} required /></label>
          <label>Время окончания<input type="time" value={form.time_end} onChange={(e) => setForm({ ...form, time_end: e.target.value })} required /></label>
          <label>Гости<input type="number" min="1" value={form.guests_count} onChange={(e) => setForm({ ...form, guests_count: Number(e.target.value) })} /></label>
          <label className="fullRow">Столик<select value={form.table} onChange={(e) => setForm({ ...form, table: e.target.value })} required><option value="">Выберите столик</option>{tables.map((table) => <option key={table.id} value={table.id}>Столик {table.number}, {table.capacity} мест</option>)}</select></label>
          <label className="fullRow">Комментарий<input value={form.comment} onChange={(e) => setForm({ ...form, comment: e.target.value })} /></label>
          <div className="bookingActions fullRow">
            <button type="button" onClick={check}>Проверить доступность</button>
            <button>Забронировать</button>
          </div>
        </form>

        <aside className="tablePreview">
          <h2>Выбранный столик</h2>
          {selectedTable ? (
            <>
              <img
                className="tablePreviewImage"
                src={tableImage(selectedTable)}
                alt={`Столик ${selectedTable.number}`}
                onError={(e) => { e.currentTarget.src = '/table-images/table-default.svg'; }}
              />
              <h3>Столик №{selectedTable.number}</h3>
              <p className="hint">Вместимость: {selectedTable.capacity} чел.</p>
              <p className="hint">На схеме показано расположение и тип посадочных мест.</p>
            </>
          ) : (
            <div className="tablePreviewEmpty">Выберите номер столика, чтобы увидеть его схему</div>
          )}
        </aside>
      </div>
      {message && <p className={message.includes('доступен') || message.includes('создано') ? 'success' : 'error'}>{message}</p>}
    </section>
  );
}
