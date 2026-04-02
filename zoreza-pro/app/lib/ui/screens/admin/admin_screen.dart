import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants.dart';
import '../../../core/providers.dart';
import '../../theme/app_theme.dart';

class AdminScreen extends ConsumerStatefulWidget {
  const AdminScreen({super.key});

  @override
  ConsumerState<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends ConsumerState<AdminScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 5, vsync: this);
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Administración'),
        bottom: TabBar(
          controller: _tabCtrl,
          isScrollable: true,
          tabs: const [
            Tab(icon: Icon(Icons.people), text: 'Usuarios'),
            Tab(icon: Icon(Icons.business), text: 'Clientes'),
            Tab(icon: Icon(Icons.videogame_asset), text: 'Máquinas'),
            Tab(icon: Icon(Icons.route), text: 'Rutas'),
            Tab(icon: Icon(Icons.settings), text: 'Config'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabCtrl,
        children: const [_UsersTab(), _ClientesTab(), _MaquinasTab(), _RutasTab(), _ConfigTab()],
      ),
    );
  }
}

// ── Users Tab ──

class _UsersTab extends ConsumerStatefulWidget {
  const _UsersTab();

  @override
  ConsumerState<_UsersTab> createState() => _UsersTabState();
}

class _UsersTabState extends ConsumerState<_UsersTab> {
  List<Map<String, dynamic>> _users = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final api = ref.read(apiClientProvider);
      final data = await api.getUsuarios();
      setState(() => _users = data.cast<Map<String, dynamic>>());
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showCreateDialog() {
    final formKey = GlobalKey<FormState>();
    String username = '', nombre = '', password = '';
    String rol = AppConstants.roleOperador;

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Nuevo Usuario'),
        content: Form(
          key: formKey,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Username'),
                  validator: (v) =>
                      (v == null || v.length < 3) ? 'Mínimo 3 caracteres' : null,
                  onSaved: (v) => username = v!,
                ),
                const SizedBox(height: 8),
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Nombre completo'),
                  validator: (v) =>
                      (v == null || v.length < 2) ? 'Mínimo 2 caracteres' : null,
                  onSaved: (v) => nombre = v!,
                ),
                const SizedBox(height: 8),
                TextFormField(
                  decoration: const InputDecoration(labelText: 'Contraseña'),
                  obscureText: true,
                  validator: (v) =>
                      (v == null || v.length < 6) ? 'Mínimo 6 caracteres' : null,
                  onSaved: (v) => password = v!,
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<String>(
                  initialValue: rol,
                  decoration: const InputDecoration(labelText: 'Rol'),
                  items: const [
                    DropdownMenuItem(
                        value: 'ADMIN', child: Text('Administrador')),
                    DropdownMenuItem(
                        value: 'SUPERVISOR', child: Text('Supervisor')),
                    DropdownMenuItem(
                        value: 'OPERADOR', child: Text('Operador')),
                  ],
                  onChanged: (v) => rol = v!,
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancelar')),
          FilledButton(
            onPressed: () async {
              if (!formKey.currentState!.validate()) return;
              formKey.currentState!.save();
              Navigator.pop(ctx);
              try {
                final api = ref.read(apiClientProvider);
                await api.createUsuario({
                  'username': username,
                  'nombre': nombre,
                  'password': password,
                  'rol': rol,
                });
                _load();
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text('Error: $e')));
                }
              }
            },
            child: const Text('Crear'),
          ),
        ],
      ),
    );
  }

  void _showEditDialog(Map<String, dynamic> user) {
    final formKey = GlobalKey<FormState>();
    String nombre = user['nombre'] as String;
    String rol = user['rol'] as String;
    bool activo = user['activo'] as bool;
    String? newPassword;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: Text('Editar: ${user['username']}'),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  TextFormField(
                    initialValue: nombre,
                    decoration: const InputDecoration(labelText: 'Nombre'),
                    onSaved: (v) => nombre = v!,
                  ),
                  const SizedBox(height: 8),
                  DropdownButtonFormField<String>(
                    initialValue: rol,
                    decoration: const InputDecoration(labelText: 'Rol'),
                    items: const [
                      DropdownMenuItem(
                          value: 'ADMIN', child: Text('Administrador')),
                      DropdownMenuItem(
                          value: 'SUPERVISOR', child: Text('Supervisor')),
                      DropdownMenuItem(
                          value: 'OPERADOR', child: Text('Operador')),
                    ],
                    onChanged: (v) => rol = v!,
                  ),
                  const SizedBox(height: 8),
                  TextFormField(
                    decoration: const InputDecoration(
                        labelText: 'Nueva contraseña (opcional)'),
                    obscureText: true,
                    validator: (v) =>
                        (v != null && v.isNotEmpty && v.length < 6)
                            ? 'Mínimo 6 caracteres'
                            : null,
                    onSaved: (v) =>
                        newPassword = (v != null && v.isNotEmpty) ? v : null,
                  ),
                  const SizedBox(height: 8),
                  SwitchListTile(
                    title: const Text('Activo'),
                    value: activo,
                    onChanged: (v) => setDialogState(() => activo = v),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Cancelar')),
            FilledButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;
                formKey.currentState!.save();
                Navigator.pop(ctx);
                try {
                  final api = ref.read(apiClientProvider);
                  final patch = <String, dynamic>{
                    'nombre': nombre,
                    'rol': rol,
                    'activo': activo,
                  };
                  if (newPassword != null) patch['password'] = newPassword;
                  await api.updateUsuario(user['uuid'] as String, patch);
                  _load();
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context)
                        .showSnackBar(SnackBar(content: Text('Error: $e')));
                  }
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  Color _rolColor(String rol) => switch (rol) {
        'ADMIN' => ZorezaTheme.danger,
        'SUPERVISOR' => ZorezaTheme.warning,
        _ => ZorezaTheme.primary,
      };

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());

    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: _users.length,
          itemBuilder: (_, i) {
            final u = _users[i];
            final activo = u['activo'] as bool;
            return Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: _rolColor(u['rol'] as String).withAlpha(30),
                  child: Text(
                    (u['nombre'] as String).substring(0, 1).toUpperCase(),
                    style:
                        TextStyle(color: _rolColor(u['rol'] as String)),
                  ),
                ),
                title: Text(
                  u['nombre'] as String,
                  style: TextStyle(
                      decoration:
                          activo ? null : TextDecoration.lineThrough),
                ),
                subtitle: Text('${u['username']} · ${u['rol']}'),
                trailing: Icon(
                  activo ? Icons.check_circle : Icons.cancel,
                  color: activo ? ZorezaTheme.success : Colors.grey,
                ),
                onTap: () => _showEditDialog(u),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showCreateDialog,
        child: const Icon(Icons.person_add),
      ),
    );
  }
}

// ── Config Tab ──

/// Extract the detail message from Dio errors.
String _dioDetail(Object e) {
  if (e is DioException && e.response?.data != null) {
    final data = e.response!.data;
    if (data is Map && data.containsKey('detail')) {
      final d = data['detail'];
      return d is String ? d : d.toString();
    }
  }
  return e.toString();
}

// ── Clientes Tab ──

class _ClientesTab extends ConsumerStatefulWidget {
  const _ClientesTab();
  @override
  ConsumerState<_ClientesTab> createState() => _ClientesTabState();
}

class _ClientesTabState extends ConsumerState<_ClientesTab> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await ref.read(apiClientProvider).getClientes();
      setState(() => _items = data.cast<Map<String, dynamic>>());
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showForm([Map<String, dynamic>? existing]) {
    final formKey = GlobalKey<FormState>();
    String nombre = existing?['nombre'] as String? ?? '';
    double comision = (existing?['comision_pct'] as num?)?.toDouble() ?? 0.40;
    bool activo = existing?['activo'] as bool? ?? true;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setD) => AlertDialog(
          title: Text(existing == null ? 'Nuevo Cliente' : 'Editar Cliente'),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                TextFormField(
                  initialValue: nombre,
                  decoration: const InputDecoration(labelText: 'Nombre'),
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                  onSaved: (v) => nombre = v!.trim(),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  initialValue: comision.toString(),
                  decoration: const InputDecoration(labelText: 'Comisión (%)', hintText: '0.40 = 40%'),
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  validator: (v) {
                    final n = double.tryParse(v ?? '');
                    if (n == null || n < 0.01 || n > 0.99) return '0.01 – 0.99';
                    return null;
                  },
                  onSaved: (v) => comision = double.parse(v!),
                ),
                if (existing != null) ...[
                  const SizedBox(height: 8),
                  SwitchListTile(
                    title: const Text('Activo'),
                    value: activo,
                    onChanged: (v) => setD(() => activo = v),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ]),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            FilledButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;
                formKey.currentState!.save();
                Navigator.pop(ctx);
                try {
                  final api = ref.read(apiClientProvider);
                  final body = <String, dynamic>{'nombre': nombre, 'comision_pct': comision};
                  if (existing != null) body['activo'] = activo;
                  if (existing == null) {
                    await api.createCliente(body);
                  } else {
                    await api.updateCliente(existing['uuid'] as String, body);
                  }
                  _load();
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context)
                        .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
                  }
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: _items.length,
          itemBuilder: (_, i) {
            final c = _items[i];
            final activo = c['activo'] as bool;
            return Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: ZorezaTheme.primary.withAlpha(30),
                  child: const Icon(Icons.business, color: ZorezaTheme.primary),
                ),
                title: Text(c['nombre'] as String,
                    style: TextStyle(decoration: activo ? null : TextDecoration.lineThrough)),
                subtitle: Text('Comisión: ${((c['comision_pct'] as num) * 100).toStringAsFixed(0)}%'),
                trailing: Icon(activo ? Icons.check_circle : Icons.cancel,
                    color: activo ? ZorezaTheme.success : Colors.grey),
                onTap: () => _showForm(c),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showForm(),
        child: const Icon(Icons.add),
      ),
    );
  }
}

// ── Máquinas Tab ──

class _MaquinasTab extends ConsumerStatefulWidget {
  const _MaquinasTab();
  @override
  ConsumerState<_MaquinasTab> createState() => _MaquinasTabState();
}

class _MaquinasTabState extends ConsumerState<_MaquinasTab> {
  List<Map<String, dynamic>> _items = [];
  List<Map<String, dynamic>> _clientes = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final api = ref.read(apiClientProvider);
      final results = await Future.wait([api.getMaquinas(), api.getClientes()]);
      setState(() {
        _items = results[0].cast<Map<String, dynamic>>();
        _clientes = results[1].cast<Map<String, dynamic>>();
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showForm([Map<String, dynamic>? existing]) {
    final formKey = GlobalKey<FormState>();
    String codigo = existing?['codigo'] as String? ?? '';
    String? clienteId = existing?['cliente_id'] as String?;
    bool activo = existing?['activo'] as bool? ?? true;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setD) => AlertDialog(
          title: Text(existing == null ? 'Nueva Máquina' : 'Editar Máquina'),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                TextFormField(
                  initialValue: codigo,
                  decoration: const InputDecoration(labelText: 'Código', hintText: 'Ej: PB-001'),
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                  onSaved: (v) => codigo = v!.trim(),
                ),
                const SizedBox(height: 8),
                DropdownButtonFormField<String?>(
                  initialValue: clienteId,
                  decoration: const InputDecoration(labelText: 'Cliente'),
                  items: [
                    const DropdownMenuItem<String?>(value: null, child: Text('Sin asignar (pool)')),
                    ..._clientes.map((c) => DropdownMenuItem<String?>(
                      value: c['uuid'] as String,
                      child: Text(c['nombre'] as String),
                    )),
                  ],
                  onChanged: (v) => clienteId = v,
                ),
                if (existing != null) ...[
                  const SizedBox(height: 8),
                  SwitchListTile(
                    title: const Text('Activo'),
                    value: activo,
                    onChanged: (v) => setD(() => activo = v),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ]),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            FilledButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;
                formKey.currentState!.save();
                Navigator.pop(ctx);
                try {
                  final api = ref.read(apiClientProvider);
                  final body = <String, dynamic>{'codigo': codigo, 'cliente_id': clienteId};
                  if (existing != null) body['activo'] = activo;
                  if (existing == null) {
                    await api.createMaquina(body);
                  } else {
                    await api.updateMaquina(existing['uuid'] as String, body);
                  }
                  _load();
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context)
                        .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
                  }
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: _items.length,
          itemBuilder: (_, i) {
            final m = _items[i];
            final activo = m['activo'] as bool;
            final clienteNombre = m['cliente_nombre'] as String?;
            final displayCliente = clienteNombre ?? 'Sin asignar (pool)';
            final sinAsignar = clienteNombre == null || clienteNombre.isEmpty;
            return Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: sinAsignar
                      ? ZorezaTheme.warning.withAlpha(30)
                      : ZorezaTheme.primary.withAlpha(30),
                  child: Icon(Icons.videogame_asset,
                      color: sinAsignar ? ZorezaTheme.warning : ZorezaTheme.primary),
                ),
                title: Text(m['codigo'] as String,
                    style: TextStyle(decoration: activo ? null : TextDecoration.lineThrough)),
                subtitle: Text(displayCliente,
                    style: TextStyle(color: sinAsignar ? ZorezaTheme.warning : null)),
                trailing: Icon(activo ? Icons.check_circle : Icons.cancel,
                    color: activo ? ZorezaTheme.success : Colors.grey),
                onTap: () => _showForm(m),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showForm(),
        child: const Icon(Icons.add),
      ),
    );
  }
}

// ── Rutas Tab ──

class _RutasTab extends ConsumerStatefulWidget {
  const _RutasTab();
  @override
  ConsumerState<_RutasTab> createState() => _RutasTabState();
}

class _RutasTabState extends ConsumerState<_RutasTab> {
  List<Map<String, dynamic>> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final data = await ref.read(apiClientProvider).getRutas();
      setState(() => _items = data.cast<Map<String, dynamic>>());
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  void _showForm([Map<String, dynamic>? existing]) {
    final formKey = GlobalKey<FormState>();
    String nombre = existing?['nombre'] as String? ?? '';
    String descripcion = existing?['descripcion'] as String? ?? '';
    bool activo = existing?['activo'] as bool? ?? true;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setD) => AlertDialog(
          title: Text(existing == null ? 'Nueva Ruta' : 'Editar Ruta'),
          content: Form(
            key: formKey,
            child: SingleChildScrollView(
              child: Column(mainAxisSize: MainAxisSize.min, children: [
                TextFormField(
                  initialValue: nombre,
                  decoration: const InputDecoration(labelText: 'Nombre'),
                  validator: (v) => (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                  onSaved: (v) => nombre = v!.trim(),
                ),
                const SizedBox(height: 8),
                TextFormField(
                  initialValue: descripcion,
                  decoration: const InputDecoration(labelText: 'Descripción (opcional)'),
                  onSaved: (v) => descripcion = v?.trim() ?? '',
                ),
                if (existing != null) ...[
                  const SizedBox(height: 8),
                  SwitchListTile(
                    title: const Text('Activo'),
                    value: activo,
                    onChanged: (v) => setD(() => activo = v),
                    contentPadding: EdgeInsets.zero,
                  ),
                ],
              ]),
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            FilledButton(
              onPressed: () async {
                if (!formKey.currentState!.validate()) return;
                formKey.currentState!.save();
                Navigator.pop(ctx);
                try {
                  final api = ref.read(apiClientProvider);
                  final body = <String, dynamic>{'nombre': nombre};
                  if (descripcion.isNotEmpty) body['descripcion'] = descripcion;
                  if (existing != null) body['activo'] = activo;
                  if (existing == null) {
                    await api.createRuta(body);
                  } else {
                    await api.updateRuta(existing['uuid'] as String, body);
                  }
                  _load();
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context)
                        .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
                  }
                }
              },
              child: const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  void _showMaquinas(Map<String, dynamic> ruta) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => _RutaMaquinasScreen(
          rutaId: ruta['uuid'] as String,
          rutaNombre: ruta['nombre'] as String,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) return const Center(child: CircularProgressIndicator());
    return Scaffold(
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView.builder(
          padding: const EdgeInsets.all(12),
          itemCount: _items.length,
          itemBuilder: (_, i) {
            final r = _items[i];
            final activo = r['activo'] as bool;
            return Card(
              child: ListTile(
                leading: CircleAvatar(
                  backgroundColor: ZorezaTheme.primary.withAlpha(30),
                  child: const Icon(Icons.route, color: ZorezaTheme.primary),
                ),
                title: Text(r['nombre'] as String,
                    style: TextStyle(decoration: activo ? null : TextDecoration.lineThrough)),
                subtitle: Text(r['descripcion'] as String? ?? 'Sin descripción'),
                trailing: Row(mainAxisSize: MainAxisSize.min, children: [
                  IconButton(
                    icon: const Icon(Icons.videogame_asset, size: 20),
                    tooltip: 'Máquinas asignadas',
                    onPressed: () => _showMaquinas(r),
                  ),
                  Icon(activo ? Icons.check_circle : Icons.cancel,
                      color: activo ? ZorezaTheme.success : Colors.grey),
                ]),
                onTap: () => _showForm(r),
              ),
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showForm(),
        child: const Icon(Icons.add),
      ),
    );
  }
}

/// Screen to manage machines assigned to a specific route.
class _RutaMaquinasScreen extends ConsumerStatefulWidget {
  final String rutaId;
  final String rutaNombre;
  const _RutaMaquinasScreen({required this.rutaId, required this.rutaNombre});
  @override
  ConsumerState<_RutaMaquinasScreen> createState() => _RutaMaquinasScreenState();
}

class _RutaMaquinasScreenState extends ConsumerState<_RutaMaquinasScreen> {
  List<Map<String, dynamic>> _assigned = [];
  List<Map<String, dynamic>> _allMaquinas = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final api = ref.read(apiClientProvider);
      final results = await Future.wait([
        api.getRutaMaquinas(widget.rutaId),
        api.getMaquinas(),
      ]);
      setState(() {
        _assigned = results[0].cast<Map<String, dynamic>>();
        _allMaquinas = results[1].cast<Map<String, dynamic>>();
      });
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Set<String> get _assignedIds =>
      _assigned.map((a) => a['maquina_id'] as String).toSet();

  Future<void> _assign(String maquinaId) async {
    try {
      await ref.read(apiClientProvider).assignMaquinaToRuta(widget.rutaId, maquinaId);
      _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
      }
    }
  }

  Future<void> _unassign(String maquinaId) async {
    try {
      await ref.read(apiClientProvider).unassignMaquinaFromRuta(widget.rutaId, maquinaId);
      _load();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text(_dioDetail(e))));
      }
    }
  }

  void _showAddDialog() {
    final available = _allMaquinas
        .where((m) => !_assignedIds.contains(m['uuid'] as String) && m['activo'] as bool)
        .toList();

    if (available.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No hay máquinas disponibles para asignar')),
      );
      return;
    }

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Asignar Máquina'),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: available.length,
            itemBuilder: (_, i) {
              final m = available[i];
              return ListTile(
                leading: const Icon(Icons.videogame_asset),
                title: Text(m['codigo'] as String),
                subtitle: Text(m['cliente_nombre'] as String? ?? 'Sin cliente'),
                onTap: () {
                  Navigator.pop(ctx);
                  _assign(m['uuid'] as String);
                },
              );
            },
          ),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Máquinas: ${widget.rutaNombre}')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _assigned.isEmpty
              ? const Center(child: Text('No hay máquinas asignadas'))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _assigned.length,
                    itemBuilder: (_, i) {
                      final a = _assigned[i];
                      return Card(
                        child: ListTile(
                          leading: const CircleAvatar(
                            backgroundColor: Color(0x1A1B5E20),
                            child: Icon(Icons.videogame_asset, color: ZorezaTheme.primary),
                          ),
                          title: Text(a['codigo'] as String? ?? '?'),
                          subtitle: Text(a['cliente_nombre'] as String? ?? 'Sin cliente'),
                          trailing: IconButton(
                            icon: const Icon(Icons.remove_circle_outline, color: ZorezaTheme.danger),
                            tooltip: 'Desasignar',
                            onPressed: () => _unassign(a['maquina_id'] as String),
                          ),
                        ),
                      );
                    },
                  ),
                ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showAddDialog,
        child: const Icon(Icons.add),
      ),
    );
  }
}

// ── Config Tab ──

class _ConfigTab extends ConsumerStatefulWidget {
  const _ConfigTab();

  @override
  ConsumerState<_ConfigTab> createState() => _ConfigTabState();
}

class _ConfigTabState extends ConsumerState<_ConfigTab> {
  final _baseUrlCtrl = TextEditingController();
  final _slugCtrl = TextEditingController();
  bool _serverOk = false;
  bool _checking = false;

  @override
  void initState() {
    super.initState();
    final prefs = ref.read(sharedPrefsProvider);
    _baseUrlCtrl.text =
        prefs.getString(AppConstants.keyBaseUrl) ?? AppConstants.defaultBaseUrl;
    _slugCtrl.text =
        prefs.getString(AppConstants.keyTenantSlug) ?? AppConstants.defaultTenantSlug;
  }

  @override
  void dispose() {
    _baseUrlCtrl.dispose();
    _slugCtrl.dispose();
    super.dispose();
  }

  Future<void> _testConnection() async {
    setState(() => _checking = true);
    try {
      final api = ref.read(apiClientProvider);
      _serverOk = await api.isServerReachable();
    } catch (_) {
      _serverOk = false;
    }
    if (mounted) setState(() => _checking = false);
  }

  Future<void> _saveUrl() async {
    final prefs = ref.read(sharedPrefsProvider);
    await prefs.setString(AppConstants.keyBaseUrl, _baseUrlCtrl.text.trim());
    await prefs.setString(AppConstants.keyTenantSlug, _slugCtrl.text.trim().toLowerCase());
    if (mounted) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Configuración guardada. Reinicia la app.')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Servidor', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 12),
        TextField(
          controller: _slugCtrl,
          decoration: const InputDecoration(
            labelText: 'ID del negocio (tenant)',
            hintText: 'mi-negocio',
            helperText: 'Proporcionado por Zoreza Labs',
            prefixIcon: Icon(Icons.business),
          ),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _baseUrlCtrl,
          decoration: InputDecoration(
            labelText: 'URL del servidor',
            hintText: 'https://zorezalabs.mx',
            prefixIcon: const Icon(Icons.dns_outlined),
            suffixIcon: _checking
                ? const Padding(
                    padding: EdgeInsets.all(12),
                    child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2)),
                  )
                : Icon(
                    _serverOk ? Icons.cloud_done : Icons.cloud_off,
                    color: _serverOk ? ZorezaTheme.success : Colors.grey,
                  ),
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _testConnection,
                icon: const Icon(Icons.wifi_find),
                label: const Text('Probar conexión'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FilledButton.icon(
                onPressed: _saveUrl,
                icon: const Icon(Icons.save),
                label: const Text('Guardar URL'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 32),
        Text('Datos Locales', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 12),
        Card(
          child: ListTile(
            leading: const Icon(Icons.sync),
            title: const Text('Sincronización completa'),
            subtitle: const Text('Bajar todos los datos del servidor'),
            onTap: () async {
              try {
                final sync = ref.read(syncServiceProvider);
                await sync.fullSync();
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Sincronización completa')));
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context)
                      .showSnackBar(SnackBar(content: Text('Error: $e')));
                }
              }
            },
          ),
        ),
        Card(
          child: ListTile(
            leading: const Icon(Icons.delete_outline, color: ZorezaTheme.danger),
            title: const Text('Borrar datos locales'),
            subtitle: const Text('Eliminar caché y datos offline'),
            onTap: () async {
              final confirm = await showDialog<bool>(
                context: context,
                builder: (ctx) => AlertDialog(
                  title: const Text('¿Borrar datos locales?'),
                  content: const Text(
                      'Se eliminarán todos los datos guardados en el dispositivo. '
                      'Los datos del servidor no se afectan.'),
                  actions: [
                    TextButton(
                        onPressed: () => Navigator.pop(ctx, false),
                        child: const Text('Cancelar')),
                    FilledButton(
                      style: FilledButton.styleFrom(
                          backgroundColor: ZorezaTheme.danger),
                      onPressed: () => Navigator.pop(ctx, true),
                      child: const Text('Borrar'),
                    ),
                  ],
                ),
              );
              if (confirm == true) {
                final db = ref.read(databaseProvider);
                await db.deleteAllData();
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Datos locales borrados')));
                }
              }
            },
          ),
        ),
      ],
    );
  }
}
