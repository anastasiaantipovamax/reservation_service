import { useEffect, useState } from 'react';
import { api, currentUser } from './api/client';
import Layout from './components/Layout.jsx';
import Login from './pages/Login.jsx';
import Register from './pages/Register.jsx';
import Menu from './pages/Menu.jsx';
import Booking from './pages/Booking.jsx';
import Notifications from './pages/Notifications.jsx';
import AdminBookings from './pages/AdminBookings.jsx';
import AdminTables from './pages/AdminTables.jsx';
import AdminMenu from './pages/AdminMenu.jsx';
import Reports from './pages/Reports.jsx';

export default function App() {
  const [page, setPage] = useState(currentUser() ? 'menu' : 'login');
  const [unreadCount, setUnreadCount] = useState(0);

  const loadUnread = async () => {
    if (!currentUser()) return setUnreadCount(0);
    try {
      const res = await api.get('/notifications/');
      setUnreadCount(res.data.filter((item) => !item.is_read).length);
    } catch { setUnreadCount(0); }
  };

  useEffect(() => { loadUnread(); }, [page]);
  useEffect(() => {
    const handler = (event) => setPage(event.detail);
    window.addEventListener('admin-nav', handler);
    return () => window.removeEventListener('admin-nav', handler);
  }, []);

  const pages = {
    login: <Login setPage={setPage} />,
    register: <Register setPage={setPage} />,
    menu: <Menu />,
    booking: <Booking onCreated={loadUnread} />,
    notifications: <Notifications onRead={loadUnread} />,
    adminBookings: <AdminBookings />,
    adminTables: <AdminTables />,
    adminMenu: <AdminMenu />,
    reports: <Reports />,
  };

  return <Layout page={page} setPage={setPage} unreadCount={unreadCount}>{pages[page]}</Layout>;
}
