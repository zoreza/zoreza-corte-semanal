import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../core/constants.dart';
import '../../../core/providers.dart';
import '../../../data/models/models.dart';
import '../../../ui/theme/app_theme.dart';

class GastosScreen extends ConsumerStatefulWidget {
  const GastosScreen({super.key});

  @override
  ConsumerState<GastosScreen> createState() => _GastosScreenState();
}

class _GastosScreenState extends ConsumerState<GastosScreen> {
  List<Gasto> _gastos = [];
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
      final data = await api.getGastos();
      setState(() {
        _gastos = data
            .map((j) => Gasto.fromJson(j as Map<String, dynamic>))
            .toList();
      });
    } catch (_) {
      // Try local.
      try {
        final db = ref.read(databaseProvider);
        final rows = await db.query('gastos', orderBy: 'fecha DESC');
        setState(() => _gastos = rows.map((r) => Gasto.fromDb(r)).toList());
      } catch (_) {}
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _addGasto() async {
    final result = await showModalBottomSheet<Gasto>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => const _GastoForm(),
    );
    if (result == null) return;

    try {
      final api = ref.read(apiClientProvider);
      await api.createGasto(result.toJson());
    } catch (_) {
      // Save locally with pending status.
      final db = ref.read(databaseProvider);
      final row = result.toDb();
      row['sync_status'] = 'pending';
      await db.insert('gastos', row);
    }
    await _load();
  }

  Future<void> _deleteGasto(Gasto gasto) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Eliminar gasto'),
        content: Text('¿Eliminar "${gasto.descripcion}"?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: ZorezaTheme.danger),
            child: const Text('Eliminar', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    if (confirm != true) return;

    try {
      final api = ref.read(apiClientProvider);
      await api.deleteGasto(gasto.uuid);
    } catch (_) {
      final db = ref.read(databaseProvider);
      await db.delete('gastos', where: 'uuid = ?', whereArgs: [gasto.uuid]);
    }
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final total = _gastos.fold(0.0, (sum, g) => sum + g.monto);

    return Scaffold(
      appBar: AppBar(title: const Text('Gastos')),
      floatingActionButton: FloatingActionButton(
        onPressed: _addGasto,
        child: const Icon(Icons.add),
      ),
      body: Column(
        children: [
          // Total card
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            color: ZorezaTheme.primary.withAlpha(15),
            child: Column(
              children: [
                const Text('Total gastos',
                    style: TextStyle(color: Colors.grey)),
                Text('\$${total.toStringAsFixed(2)}',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold, color: ZorezaTheme.primary)),
              ],
            ),
          ),

          // List
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _gastos.isEmpty
                    ? const Center(child: Text('Sin gastos registrados'))
                    : RefreshIndicator(
                        onRefresh: _load,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(12),
                          itemCount: _gastos.length,
                          itemBuilder: (_, i) {
                            final g = _gastos[i];
                            return Dismissible(
                              key: ValueKey(g.uuid),
                              direction: DismissDirection.endToStart,
                              background: Container(
                                alignment: Alignment.centerRight,
                                padding: const EdgeInsets.only(right: 20),
                                color: ZorezaTheme.danger,
                                child: const Icon(Icons.delete,
                                    color: Colors.white),
                              ),
                              onDismissed: (_) => _deleteGasto(g),
                              child: Card(
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor:
                                        ZorezaTheme.warning.withAlpha(30),
                                    child: const Icon(
                                        Icons.account_balance_wallet,
                                        color: ZorezaTheme.warning),
                                  ),
                                  title: Text(g.descripcion),
                                  subtitle:
                                      Text('${g.fecha} · ${g.categoria}'),
                                  trailing: Text(
                                    '\$${g.monto.toStringAsFixed(2)}',
                                    style: const TextStyle(
                                        fontWeight: FontWeight.bold),
                                  ),
                                ),
                              ),
                            );
                          },
                        ),
                      ),
          ),
        ],
      ),
    );
  }
}

class _GastoForm extends StatefulWidget {
  const _GastoForm();

  @override
  State<_GastoForm> createState() => _GastoFormState();
}

class _GastoFormState extends State<_GastoForm> {
  final _formKey = GlobalKey<FormState>();
  final _descCtrl = TextEditingController();
  final _montoCtrl = TextEditingController();
  final _notasCtrl = TextEditingController();
  String _categoria = AppConstants.gastoCategories.first;
  DateTime _fecha = DateTime.now();

  @override
  void dispose() {
    _descCtrl.dispose();
    _montoCtrl.dispose();
    _notasCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 16,
        bottom: MediaQuery.of(context).viewInsets.bottom + 16,
      ),
      child: Form(
        key: _formKey,
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Nuevo Gasto',
                  style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 16),

              // Fecha
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.calendar_today),
                title: Text(
                    '${_fecha.year}-${_fecha.month.toString().padLeft(2, '0')}-${_fecha.day.toString().padLeft(2, '0')}'),
                onTap: () async {
                  final d = await showDatePicker(
                    context: context,
                    initialDate: _fecha,
                    firstDate: DateTime(2020),
                    lastDate: DateTime.now(),
                  );
                  if (d != null) setState(() => _fecha = d);
                },
              ),

              // Categoría
              DropdownButtonFormField<String>(
                initialValue: _categoria,
                decoration:
                    const InputDecoration(labelText: 'Categoría'),
                items: AppConstants.gastoCategories
                    .map((c) => DropdownMenuItem(value: c, child: Text(c)))
                    .toList(),
                onChanged: (v) => setState(() => _categoria = v!),
              ),
              const SizedBox(height: 12),

              // Descripción
              TextFormField(
                controller: _descCtrl,
                decoration:
                    const InputDecoration(labelText: 'Descripción'),
                validator: (v) =>
                    (v == null || v.isEmpty) ? 'Requerido' : null,
              ),
              const SizedBox(height: 12),

              // Monto
              TextFormField(
                controller: _montoCtrl,
                decoration:
                    const InputDecoration(labelText: 'Monto (\$)'),
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                inputFormatters: [
                  FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
                ],
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Requerido';
                  final n = double.tryParse(v);
                  if (n == null || n <= 0) return 'Monto inválido';
                  return null;
                },
              ),
              const SizedBox(height: 12),

              // Notas
              TextFormField(
                controller: _notasCtrl,
                decoration:
                    const InputDecoration(labelText: 'Notas (opcional)'),
                maxLines: 2,
              ),
              const SizedBox(height: 24),

              ElevatedButton(
                onPressed: () {
                  if (!_formKey.currentState!.validate()) return;
                  final fecha =
                      '${_fecha.year}-${_fecha.month.toString().padLeft(2, '0')}-${_fecha.day.toString().padLeft(2, '0')}';
                  final gasto = Gasto(
                    uuid: const Uuid().v4(),
                    fecha: fecha,
                    categoria: _categoria,
                    descripcion: _descCtrl.text.trim(),
                    monto: double.parse(_montoCtrl.text),
                    notas: _notasCtrl.text.isEmpty
                        ? null
                        : _notasCtrl.text.trim(),
                  );
                  Navigator.pop(context, gasto);
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: ZorezaTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
                child: const Text('GUARDAR GASTO'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
