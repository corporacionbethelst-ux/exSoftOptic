import type { FormEvent } from 'react';
import { useCallback, useMemo, useState } from 'react';
import { ConfirmDialog } from '../../components/ConfirmDialog';
import { InlineState } from '../../components/InlineState';
import { PageHeader } from '../../components/PageHeader';
import { Pagination } from '../../components/Pagination';
import { SectionPanel } from '../../components/SectionPanel';
import { StatusBadge } from '../../components/StatusBadge';
import { usersService } from '../../services';
import type { Rol, RolPayload, Usuario, UsuarioPayload, UsuarioUpdatePayload } from '../../types/auth';
import { dateTime } from '../../utils/format';
import { useApiResource } from '../../hooks/useApiResource';

const DEFAULT_USER_FORM: UsuarioPayload = {
  username: '',
  email: '',
  nombre_completo: '',
  telefono: '',
  password: 'Demo123!',
  rol_id: '',
  sucursal_id: null,
};

const DEFAULT_ROLE_FORM: RolPayload = {
  nombre: '',
  descripcion: '',
  nivel_acceso: 1,
  permisos: [],
};

function userToForm(user: Usuario): UsuarioPayload {
  return {
    username: user.username,
    email: user.email,
    nombre_completo: user.nombre_completo,
    telefono: user.telefono ?? '',
    password: '',
    rol_id: user.rol_id,
    sucursal_id: user.sucursal_id ?? null,
  };
}

function roleName(roles: Rol[], roleId: string) {
  return roles.find((role) => role.id === roleId)?.nombre ?? 'Sin rol';
}

export function UsersPage() {
  const [searchDraft, setSearchDraft] = useState('');
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(20);
  const [editingUser, setEditingUser] = useState<Usuario | null>(null);
  const [pendingDelete, setPendingDelete] = useState<Usuario | null>(null);
  const [userForm, setUserForm] = useState<UsuarioPayload>(DEFAULT_USER_FORM);
  const [roleForm, setRoleForm] = useState<RolPayload>(DEFAULT_ROLE_FORM);
  const [formError, setFormError] = useState<string | null>(null);
  const [roleError, setRoleError] = useState<string | null>(null);
  const [operationMessage, setOperationMessage] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [savingRole, setSavingRole] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const loadUsers = useCallback(() => usersService.list({ page, perPage, search }), [page, perPage, search]);
  const users = useApiResource(loadUsers);
  const roles = useApiResource(usersService.roles);
  const userItems = users.data?.users ?? [];
  const roleItems = roles.data ?? [];
  const total = users.data?.total ?? userItems.length;
  const isEditing = Boolean(editingUser);
  const totalLabel = useMemo(() => `${total} usuarios`, [total]);

  function openCreate() {
    setEditingUser(null);
    setUserForm({ ...DEFAULT_USER_FORM, rol_id: roleItems[0]?.id ?? '' });
    setFormError(null);
    setOperationMessage(null);
  }

  function openEdit(user: Usuario) {
    setEditingUser(user);
    setUserForm(userToForm(user));
    setFormError(null);
    setOperationMessage(null);
  }

  function applySearch(event?: FormEvent<HTMLFormElement>) {
    event?.preventDefault();
    setPage(1);
    setSearch(searchDraft.trim());
  }

  async function handleUserSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setFormError(null);
    setOperationMessage(null);
    try {
      if (editingUser) {
        const payload: UsuarioUpdatePayload = {
          email: userForm.email,
          nombre_completo: userForm.nombre_completo,
          telefono: userForm.telefono,
          rol_id: userForm.rol_id,
          sucursal_id: userForm.sucursal_id,
        };
        await usersService.update(editingUser.id, payload);
        setOperationMessage('Usuario actualizado correctamente.');
      } else {
        await usersService.create(userForm);
        setOperationMessage('Usuario creado correctamente.');
        setPage(1);
      }
      setEditingUser(null);
      setUserForm({ ...DEFAULT_USER_FORM, rol_id: roleItems[0]?.id ?? '' });
      await users.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo guardar el usuario');
    } finally {
      setSaving(false);
    }
  }

  async function handleRoleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSavingRole(true);
    setRoleError(null);
    try {
      await usersService.createRole(roleForm);
      setRoleForm(DEFAULT_ROLE_FORM);
      await roles.reload();
      setOperationMessage('Rol creado correctamente.');
    } catch (error) {
      setRoleError(error instanceof Error ? error.message : 'No se pudo crear el rol');
    } finally {
      setSavingRole(false);
    }
  }

  async function toggleActive(user: Usuario) {
    setFormError(null);
    await usersService.update(user.id, { esta_activo: !user.esta_activo });
    await users.reload();
  }

  async function confirmDelete() {
    if (!pendingDelete) return;
    setDeleting(true);
    setFormError(null);
    try {
      await usersService.remove(pendingDelete.id);
      setPendingDelete(null);
      setOperationMessage('Usuario eliminado correctamente.');
      await users.reload();
    } catch (error) {
      setFormError(error instanceof Error ? error.message : 'No se pudo eliminar el usuario');
    } finally {
      setDeleting(false);
    }
  }

  return (
    <section className="page-stack">
      <PageHeader
        eyebrow="Seguridad"
        title="Usuarios y roles"
        description="Fase completa de administración de usuarios: búsqueda, paginación, creación, edición, activación y eliminación lógica."
        actions={<button className="primary-button" onClick={openCreate}>Nuevo usuario</button>}
      />

      <SectionPanel title="Usuarios" footer={<span className="muted compact">{totalLabel}</span>}>
        <form className="toolbar-row" onSubmit={applySearch}>
          <input value={searchDraft} onChange={(event) => setSearchDraft(event.target.value)} placeholder="Buscar por nombre, usuario o email" />
          <button className="secondary-button">Buscar</button>
        </form>
        <InlineState loading={users.loading || roles.loading} error={users.error ?? roles.error} empty={userItems.length === 0} emptyTitle="Sin usuarios" emptyDescription="Crea usuarios o ejecuta make seed para cargar usuarios base.">
          <div className="table-wrap">
            <table>
              <thead><tr><th>Nombre</th><th>Usuario</th><th>Email</th><th>Rol</th><th>Último acceso</th><th>Estado</th><th>Acciones</th></tr></thead>
              <tbody>
                {userItems.map((user) => (
                  <tr key={user.id}>
                    <td>{user.nombre_completo}</td>
                    <td>{user.username}</td>
                    <td>{user.email}</td>
                    <td>{roleName(roleItems, user.rol_id)}</td>
                    <td>{dateTime(user.ultimo_acceso)}</td>
                    <td><StatusBadge tone={user.esta_activo ? 'success' : 'danger'}>{user.esta_activo ? 'Activo' : 'Inactivo'}</StatusBadge></td>
                    <td className="action-cell">
                      <button className="secondary-button" onClick={() => openEdit(user)}>Editar</button>
                      <button className="secondary-button" onClick={() => void toggleActive(user)}>{user.esta_activo ? 'Desactivar' : 'Activar'}</button>
                      <button className="danger-button" onClick={() => setPendingDelete(user)}>Eliminar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination
            page={page}
            pageSize={perPage}
            total={total}
            onPageChange={setPage}
            onPageSizeChange={(nextPageSize) => {
              setPage(1);
              setPerPage(nextPageSize);
            }}
          />
        </InlineState>
      </SectionPanel>

      <SectionPanel title={isEditing ? 'Editar usuario' : 'Nuevo usuario'} description="Asigna rol, datos de contacto y estado operativo del usuario.">
        {operationMessage ? <div className="alert success wide-field">{operationMessage}</div> : null}
        <form className="crud-form" onSubmit={(event) => void handleUserSubmit(event)}>
          <label>Usuario<input value={userForm.username} disabled={isEditing} onChange={(event) => setUserForm({ ...userForm, username: event.target.value })} required /></label>
          <label>Nombre completo<input value={userForm.nombre_completo} onChange={(event) => setUserForm({ ...userForm, nombre_completo: event.target.value })} required /></label>
          <label>Email<input type="email" value={userForm.email} onChange={(event) => setUserForm({ ...userForm, email: event.target.value })} required /></label>
          <label>Teléfono<input value={userForm.telefono ?? ''} onChange={(event) => setUserForm({ ...userForm, telefono: event.target.value })} /></label>
          <label>Rol
            <select value={userForm.rol_id} onChange={(event) => setUserForm({ ...userForm, rol_id: event.target.value })} required>
              <option value="">Selecciona rol</option>
              {roleItems.map((role) => <option key={role.id} value={role.id}>{role.nombre}</option>)}
            </select>
          </label>
          {!isEditing ? <label>Password<input type="password" value={userForm.password} onChange={(event) => setUserForm({ ...userForm, password: event.target.value })} required /></label> : null}
          {formError ? <div className="alert error wide-field">{formError}</div> : null}
          <div className="form-actions wide-field">
            <button className="primary-button" disabled={saving}>{saving ? 'Guardando…' : isEditing ? 'Actualizar usuario' : 'Crear usuario'}</button>
            <button className="secondary-button" type="button" onClick={openCreate}>Limpiar</button>
          </div>
        </form>
      </SectionPanel>

      <SectionPanel title="Roles" description="Consulta roles disponibles y crea roles operativos simples para pruebas del frontend.">
        <div className="role-grid">
          <InlineState loading={roles.loading} error={roles.error} empty={roleItems.length === 0} emptyTitle="Sin roles">
            <div className="list-stack">
              {roleItems.map((role) => (
                <div className="row-card" key={role.id}>
                  <div><strong>{role.nombre}</strong><span>Nivel {role.nivel_acceso} · {role.permisos.length} permisos</span></div>
                  <StatusBadge tone={role.esta_activo ? 'success' : 'neutral'}>{role.es_sistema ? 'Sistema' : 'Operativo'}</StatusBadge>
                </div>
              ))}
            </div>
          </InlineState>
          <form className="role-form" onSubmit={(event) => void handleRoleSubmit(event)}>
            <label>Nombre<input value={roleForm.nombre} onChange={(event) => setRoleForm({ ...roleForm, nombre: event.target.value })} required /></label>
            <label>Descripción<input value={roleForm.descripcion ?? ''} onChange={(event) => setRoleForm({ ...roleForm, descripcion: event.target.value })} /></label>
            <label>Nivel<input type="number" min="1" max="10" value={roleForm.nivel_acceso} onChange={(event) => setRoleForm({ ...roleForm, nivel_acceso: Number(event.target.value) })} /></label>
            <label className="wide-field">Permisos separados por coma<input value={roleForm.permisos.join(', ')} onChange={(event) => setRoleForm({ ...roleForm, permisos: event.target.value.split(',').map((value) => value.trim()).filter(Boolean) })} placeholder="usuarios.ver, productos.*" /></label>
            {roleError ? <div className="alert error wide-field">{roleError}</div> : null}
            <button className="primary-button" disabled={savingRole}>{savingRole ? 'Creando…' : 'Crear rol'}</button>
          </form>
        </div>
      </SectionPanel>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Eliminar usuario"
        description="Esta acción desactiva el usuario y lo oculta de operaciones normales, conservando trazabilidad histórica."
        confirmLabel="Eliminar usuario"
        busy={deleting}
        onConfirm={() => void confirmDelete()}
        onCancel={() => setPendingDelete(null)}
      >
        <strong>{pendingDelete?.nombre_completo}</strong>
      </ConfirmDialog>
    </section>
  );
}
