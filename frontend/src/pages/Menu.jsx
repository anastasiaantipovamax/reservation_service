import { useEffect, useState } from 'react';
import { api } from '../api/client';

export default function Menu() {
  const [items, setItems] = useState([]);
  useEffect(() => { api.get('/menu/').then((res) => setItems(res.data)); }, []);
  return (
    <section>
      <h1>Меню ресторана</h1>
      <div className="grid">
        {items.map((item) => (
          <article className="card" key={item.id}>
            {item.image_url ? <img src={item.image_url} alt={item.name} /> : <div className="placeholder">Фото</div>}
            <h3>{item.name}</h3>
            <p>{item.description}</p>
            <strong>{item.price} ₽</strong>
          </article>
        ))}
      </div>
    </section>
  );
}
