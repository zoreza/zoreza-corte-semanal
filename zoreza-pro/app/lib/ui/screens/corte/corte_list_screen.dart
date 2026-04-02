import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../core/providers.dart';
import '../../../data/models/models.dart';
import '../../../ui/theme/app_theme.dart';
import 'corte_detail_screen.dart';

/// Corte list: shows existing cortes and allows creating new ones.
class CorteListScreen extends ConsumerStatefulWidget {
  const CorteListScreen({super.key});

  @override
  ConsumerState<CorteListScreen> createState() => _CorteListScreenState();
}

class _CorteListScreenState extends ConsumerState<CorteListScreen> {
  List<Corte> _cortes = [];
  List<Cliente> _clientes = [];
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
      final [cortesRaw, clientesRaw] = await Future.wait([
        api.getCortes(),
        api.getClientes(activo: true),
      ]);
      final apiCortes = cortesRaw
          .map((j) => Corte.fromSummaryJson(j as Map<String, dynamic>))
          .toList();

      // Merge with local pending cortes
      final db = ref.read(databaseProvider);
      final localPending = await db.getCortesWithCliente(syncStatus: 'pending');
      final pendingCortes = localPending.map((row) => Corte(
            uuid: row['uuid'] as String,
            clienteId: row['cliente_id'] as String,
            clienteNombre: row['cliente_nombre'] as String?,
            weekStart: row['week_start'] as String,
            weekEnd: row['week_end'] as String,
            comisionPctUsada: 0,
            netoCliente: 0,
            pagoCliente: 0,
            gananciaDueno: 0,
            estado: row['estado'] as String,
            syncStatus: 'pending',
          )).toList();

      setState(() {
        _cortes = [...pendingCortes, ...apiCortes];
        _clientes = clientesRaw
            .map((j) => Cliente.fromJson(j as Map<String, dynamic>))
            .toList();
      });
    } catch (_) {
      // Fully offline — load everything from local DB
      try {
        final db = ref.read(databaseProvider);
        final allCortes = await db.getCortesWithCliente();
        final clienteRows = await db.query('clientes', where: 'activo = 1');
        setState(() {
          _cortes = allCortes.map((row) => Corte(
                uuid: row['uuid'] as String,
                clienteId: row['cliente_id'] as String,
                clienteNombre: row['cliente_nombre'] as String?,
                weekStart: row['week_start'] as String,
                weekEnd: row['week_end'] as String,
                comisionPctUsada: (row['comision_pct_usada'] as num).toDouble(),
                netoCliente: (row['neto_cliente'] as num).toDouble(),
                pagoCliente: (row['pago_cliente'] as num).toDouble(),
                gananciaDueno: (row['ganancia_dueno'] as num).toDouble(),
                estado: row['estado'] as String,
                syncStatus: row['sync_status'] as String? ?? 'synced',
              )).toList();
          _clientes = clienteRows
              .map((r) => Cliente.fromDb(r))
              .toList();
        });
      } catch (_) {}
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  /// Calculate ISO week bounds (Monday–Sunday).
  static (String, String) _weekBounds(DateTime date) {
    final monday = date.subtract(Duration(days: date.weekday - DateTime.monday));
    final sunday = monday.add(const Duration(days: 6));
    String fmt(DateTime d) =>
        '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
    return (fmt(monday), fmt(sunday));
  }

  Future<void> _createCorte() async {
    if (_clientes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No hay clientes disponibles')),
      );
      return;
    }

    String? selectedClienteId;
    DateTime selectedDate = DateTime.now();

    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: const Text('Nuevo Corte'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(labelText: 'Cliente'),
                items: _clientes
                    .map((c) => DropdownMenuItem(
                        value: c.uuid, child: Text(c.nombre)))
                    .toList(),
                onChanged: (v) => selectedClienteId = v,
                validator: (v) => v == null ? 'Seleccione cliente' : null,
              ),
              const SizedBox(height: 16),
              ListTile(
                contentPadding: EdgeInsets.zero,
                title: const Text('Fecha del corte'),
                subtitle: Text(
                    '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}'),
                trailing: const Icon(Icons.calendar_today),
                onTap: () async {
                  final picked = await showDatePicker(
                    context: ctx,
                    initialDate: selectedDate,
                    firstDate: DateTime(2020),
                    lastDate: DateTime.now().add(const Duration(days: 7)),
                  );
                  if (picked != null) {
                    setDialogState(() => selectedDate = picked);
                  }
                },
              ),
            ],
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(ctx), child: const Text('Cancelar')),
            ElevatedButton(
              onPressed: () {
                if (selectedClienteId == null) return;
                final fecha =
                    '${selectedDate.year}-${selectedDate.month.toString().padLeft(2, '0')}-${selectedDate.day.toString().padLeft(2, '0')}';
                Navigator.pop(
                    ctx, {'cliente_id': selectedClienteId!, 'fecha': fecha});
              },
              child: const Text('Crear'),
            ),
          ],
        ),
      ),
    );

    if (result == null) return;

    try {
      final api = ref.read(apiClientProvider);
      final corte = await api.createCorte(result['cliente_id']!, result['fecha']!);
      if (mounted) {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) =>
                CorteDetailScreen(corteId: corte['uuid'] as String),
          ),
        );
      }
    } catch (e) {
      // Offline — create corte locally
      try {
        final db = ref.read(databaseProvider);
        final user = ref.read(currentUserProvider);
        final uuid = const Uuid().v4();
        final fecha = result['fecha']!;
        final parsed = DateTime.parse(fecha);
        final (weekStart, weekEnd) = _weekBounds(parsed);

        // Snapshot client commission
        final clienteRows = await db.query('clientes',
            where: 'uuid = ?', whereArgs: [result['cliente_id']!]);
        final comision = clienteRows.isNotEmpty
            ? (clienteRows.first['comision_pct'] as num).toDouble()
            : 0.40;

        await db.insert('cortes', {
          'uuid': uuid,
          'cliente_id': result['cliente_id']!,
          'week_start': weekStart,
          'week_end': weekEnd,
          'fecha_corte': fecha,
          'comision_pct_usada': comision,
          'neto_cliente': 0,
          'pago_cliente': 0,
          'ganancia_dueno': 0,
          'estado': 'BORRADOR',
          'created_by': user?['uuid'],
          'created_at': DateTime.now().toIso8601String(),
          'sync_status': 'pending',
        });

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Corte creado offline — se sincronizará'),
              backgroundColor: Colors.orange,
            ),
          );
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => CorteDetailScreen(corteId: uuid),
            ),
          );
        }
      } catch (innerE) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Error: $innerE'), backgroundColor: ZorezaTheme.danger),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cortes')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _createCorte,
        icon: const Icon(Icons.add),
        label: const Text('Nuevo Corte'),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _cortes.isEmpty
              ? const Center(
                  child: Text('No hay cortes.\nCrea uno nuevo.',
                      textAlign: TextAlign.center))
              : RefreshIndicator(
                  onRefresh: _load,
                  child: ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: _cortes.length,
                    itemBuilder: (_, i) => _CorteCard(
                      corte: _cortes[i],
                      onTap: () => Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => CorteDetailScreen(
                              corteId: _cortes[i].uuid),
                        ),
                      ),
                    ),
                  ),
                ),
    );
  }
}

class _CorteCard extends StatelessWidget {
  final Corte corte;
  final VoidCallback onTap;

  const _CorteCard({required this.corte, required this.onTap});

  @override
  Widget build(BuildContext context) {
    final isCerrado = corte.isCerrado;
    final isPending = corte.syncStatus == 'pending';
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: isPending
              ? Colors.orange.withAlpha(30)
              : isCerrado
                  ? ZorezaTheme.success.withAlpha(30)
                  : Colors.orange.withAlpha(30),
          child: Icon(
            isPending
                ? Icons.cloud_off
                : isCerrado
                    ? Icons.check_circle
                    : Icons.edit_note,
            color: isPending
                ? Colors.orange
                : isCerrado
                    ? ZorezaTheme.success
                    : Colors.orange,
          ),
        ),
        title: Text(corte.clienteNombre ?? 'Sin cliente'),
        subtitle: Text('${corte.weekStart} → ${corte.weekEnd}'),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (!isPending)
              Text(
                '\$${corte.netoCliente.toStringAsFixed(0)}',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: isPending
                    ? Colors.orange
                    : isCerrado
                        ? ZorezaTheme.success
                        : Colors.orange,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                isPending ? 'OFFLINE' : corte.estado,
                style: const TextStyle(color: Colors.white, fontSize: 10),
              ),
            ),
          ],
        ),
        onTap: onTap,
      ),
    );
  }
}
