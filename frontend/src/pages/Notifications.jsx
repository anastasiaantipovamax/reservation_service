import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function Notifications({ onRead }) {
  const [items, setItems] = useState([]);
  const load = () => api.get('/notifications/').then((res) => setItems(res.data));
  useEffect(() => { load(); }, []);
  const markRead = async (id) => { await api.patch(`/notifications/${id}/read/`); await load(); onRead?.(); };

  return (
    <section>
      <h1>Уведомления</h1>
      {items.map((item) => (
        <article key={item.id} className={`card notification ${item.is_read ? '' : 'unread'}`}>
          <h3>{item.title}</h3>
          <p>{item.message}</p>
          <p className="hint">Канал: {item.delivery_channel}; email: {item.email_status}</p>
          {!item.is_read && <button onClick={() => markRead(item.id)}>Отметить прочитанным</button>}
        </article>
      ))}
    </section>
  );
}
