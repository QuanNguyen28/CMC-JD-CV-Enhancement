// frontend/src/components/Roles.jsx
import { useEffect, useState } from 'react';
import api from '../api';

export default function Roles() {
  const [roles, setRoles] = useState([]);
  const [err, setErr] = useState('');

  useEffect(() => {
    let mounted = true;
    api.get('/v1/roles/list')
      .then(({ data }) => mounted && setRoles(data || []))
      .catch((e) => setErr(e?.response?.data?.detail || String(e)));
    return () => { mounted = false; };
  }, []);

  if (err) return <div className="text-red-600 text-sm">{err}</div>;

  return (
    <div>
      <h2 className="text-lg font-semibold mb-3">Available Roles</h2>
      <ul className="space-y-2">
        {roles.map((r, i) => (
          <li key={`${r.role_name}-${i}`} className="bg-white rounded-md border px-3 py-2">
            <div className="font-medium">{r.role_name}</div>
            {r.description && <div className="text-sm text-gray-500">{r.description}</div>}
          </li>
        ))}
      </ul>
    </div>
  );
}