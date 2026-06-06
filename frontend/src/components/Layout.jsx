import { Bell } from 'lucide-react';
import { currentUser, logout } from '../api/client';

export default function Layout({ page, setPage, children, unreadCount = 0 }) {
  const user = currentUser();
  const go = (name) => (e) => { e.preventDefault(); setPage(name); };
  const handleLogout = () => { logout(); setPage('login'); };

  return (
    <div>
      <header className="topbar">
        <a className="logo" href="#" onClick={go('menu')}>RestaurantBook</a>
        <nav>
          {user && <a href="#" onClick={go('menu')}>Меню</a>}
          {user && <a href="#" onClick={go('booking')}>Бронирование</a>}
          {user?.is_admin && <a href="#" onClick={go('adminBookings')}>Админ</a>}
          {user && <button className="bell" onClick={() => setPage('notifications')} title="Уведомления"><Bell size={20} />{unreadCount > 0 && <span>{unreadCount}</span>}</button>}
          {user ? <button className="linkButton" onClick={handleLogout}>Выйти</button> : <a href="#" onClick={go('login')}>Войти</a>}
        </nav>
      </header>
      <main className="container">{children}</main>
    </div>
  );
}
