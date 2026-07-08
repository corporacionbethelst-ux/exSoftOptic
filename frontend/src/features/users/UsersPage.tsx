import { DataState } from '../../components/DataState';
import { StatusBadge } from '../../components/StatusBadge';
import { usersService } from '../../services';
import { dateTime } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

export function UsersPage() {
  const users = useApiResource(usersService.list);
  return (
    <section className="page-stack">
      <div className="page-header"><div><p className="eyebrow">Seguridad</p><h1>Usuarios</h1><p className="muted">Usuarios y roles cargados desde el backend.</p></div></div>
      <DataState loading={users.loading} error={users.error}>
        <div className="panel table-wrap">
          <table><thead><tr><th>Nombre</th><th>Usuario</th><th>Email</th><th>Último acceso</th><th>Estado</th></tr></thead>
          <tbody>{(users.data?.users ?? []).map((user) => <tr key={user.id}><td>{user.nombre_completo}</td><td>{user.username}</td><td>{user.email}</td><td>{dateTime(user.ultimo_acceso)}</td><td><StatusBadge tone={user.esta_activo ? 'success' : 'danger'}>{user.esta_activo ? 'Activo' : 'Inactivo'}</StatusBadge></td></tr>)}</tbody></table>
        </div>
      </DataState>
    </section>
  );
}
