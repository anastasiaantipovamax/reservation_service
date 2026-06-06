import { useEffect, useMemo, useState } from 'react';
import { api } from '../api/client';

const statusLabels = {
  pending: 'Ожидает',
  confirmed: 'Подтверждено',
  cancelled: 'Отменено',
  completed: 'Завершено',
};

const statusClass = {
  pending: 'status pending',
  confirmed: 'status confirmed',
  cancelled: 'status cancelled',
  completed: 'status completed',
};

export default function AdminBookings() {
  const [items, setItems] = useState([]);
  const [filters, setFilters] = useState({ date: '', table: '', status: '' });
  const load = () => api.get('/bookings/').then((res) => setItems(res.data));
  useEffect(() => { load(); }, []);

  const changeStatus = async (id, status) => {
    await api.patch(`/bookings/${id}/status/`, { status });
    load();
  };

  const remove = async (id) => {
    if (!window.confirm('Удалить бронирование?')) return;
    await api.delete(`/bookings/${id}/`);
    load();
  };

  const filteredItems = useMemo(() => items.filter((booking) => {
    const byDate = !filters.date || booking.date === filters.date;
    const byTable = !filters.table || String(booking.table_info?.number) === String(filters.table);
    const byStatus = !filters.status || booking.status === filters.status;
    return byDate && byTable && byStatus;
  }), [items, filters]);

  const stats = useMemo(() => ({
    total: items.length,
    today: items.filter((item) => item.date === new Date().toISOString().slice(0, 10)).length,
    pending: items.filter((item) => item.status === 'pending').length,
    cancelled: items.filter((item) => item.status === 'cancelled').length,
  }), [items]);

  const tableNumbers = Array.from(new Set(items.map((item) => item.table_info?.number).filter(Boolean))).sort((a, b) => a - b);

  return (
    <section className="adminPage">
      <AdminHeader title="Бронирования" subtitle="Просмотр заявок, изменение статуса и удаление записей" />
      <AdminNav active="adminBookings" />

      <div className="adminStats">
        <div className="statCard"><span>Всего броней</span><strong>{stats.total}</strong></div>
        <div className="statCard"><span>Сегодня</span><strong>{stats.today}</strong></div>
        <div className="statCard"><span>Ожидают</span><strong>{stats.pending}</strong></div>
        <div className="statCard"><span>Отменено</span><strong>{stats.cancelled}</strong></div>
      </div>

      <div className="adminPanel">
        <div className="filtersBar">
          <label>Дата<input type="date" value={filters.date} onChange={(e) => setFilters({ ...filters, date: e.target.value })} /></label>
          <label>Столик<select value={filters.table} onChange={(e) => setFilters({ ...filters, table: e.target.value })}><option value="">Все</option>{tableNumbers.map((number) => <option key={number} value={number}>Столик {number}</option>)}</select></label>
          <label>Статус<select value={filters.status} onChange={(e) => setFilters({ ...filters, status: e.target.value })}><option value="">Все</option><option value="pending">Ожидает</option><option value="confirmed">Подтверждено</option><option value="cancelled">Отменено</option><option value="completed">Завершено</option></select></label>
          <button type="button" onClick={() => setFilters({ date: '', table: '', status: '' })}>Сбросить</button>
        </div>

        <div className="tableWrap">
          <table className="adminTable">
            <thead><tr><th>ID</th><th>Пользователь</th><th>Столик</th><th>Дата</th><th>Время</th><th>Гостей</th><th>Статус</th><th>Действия</th></tr></thead>
            <tbody>
              {filteredItems.map((b) => (
                <tr key={b.id}>
                  <td>{b.id}</td>
                  <td>{b.user?.username}</td>
                  <td>Столик {b.table_info?.number}</td>
                  <td>{b.date}</td>
                  <td>{b.time_start?.slice(0,5)}-{b.time_end?.slice(0,5)}</td>
                  <td>{b.guests_count}</td>
                  <td><span className={statusClass[b.status] || 'status'}>{statusLabels[b.status] || b.status}</span></td>
                  <td className="actionCell">
                    <button type="button" className="smallButton" onClick={() => changeStatus(b.id, 'confirmed')}>Подтвердить</button>
                    <button type="button" className="smallButton ghost" onClick={() => changeStatus(b.id, 'cancelled')}>Отменить</button>
                    <button type="button" className="smallButton danger" onClick={() => remove(b.id)}>Удалить</button>
                  </td>
                </tr>
              ))}
              {!filteredItems.length && <tr><td colSpan="8" className="emptyCell">Бронирования не найдены</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

export function AdminHeader({ title, subtitle }) {
  return (
    <div className="adminHeader">
      <div>
        <h1>{title}</h1>
        {subtitle && <p>{subtitle}</p>}
      </div>
    </div>
  );
}

export function AdminNav({ active }) {
  const go = (page) => (e) => {
    e.preventDefault();
    window.dispatchEvent(new CustomEvent('admin-nav', { detail: page }));
  };
  const links = [
    ['adminBookings', 'Бронирования'],
    ['adminTables', 'Столики'],
    ['adminMenu', 'Меню'],
    ['reports', 'Отчёты'],
  ];
  return <nav className="adminTabs">{links.map(([page, label]) => <a key={page} href="#" className={active === page ? 'active' : ''} onClick={go(page)}>{label}</a>)}</nav>;
}
