import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers.dart';
import '../../../data/models/models.dart';
import '../../../services/ticket_printer.dart';
import '../../../ui/theme/app_theme.dart';
import 'capture_screen.dart';
import 'omit_screen.dart';

/// Shows corte header info + list of machine details.
/// Allows capturing data per machine and closing the corte.
class CorteDetailScreen extends ConsumerStatefulWidget {
  final String corteId;
  const CorteDetailScreen({super.key, required this.corteId});

  @override
  ConsumerState<CorteDetailScreen> createState() => _CorteDetailScreenState();
}

class _CorteDetailScreenState extends ConsumerState<CorteDetailScreen> {
  Corte? _corte;
  List<CorteDetalle> _detalles = [];
  List<Maquina> _maquinas = [];
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
      final [corteRaw, detallesRaw, maqRaw] = await Future.wait([
        api.getCorte(widget.corteId),
        api.getCorteDetalles(widget.corteId),
        api.getMaquinas(),
      ]);
      final apiDetalles = (detallesRaw as List)
          .map((j) => CorteDetalle.fromJson(j as Map<String, dynamic>))
          .toList();

      // Merge local pending detalles
      final db = ref.read(databaseProvider);
      final localPending = await db.getDetallesForCorte(widget.corteId);
      final pendingDetalles = localPending
          .where((r) => r['sync_status'] == 'pending')
          .map((r) {
            final d = CorteDetalle.fromDb(r);
            // Attach maquina_codigo from joined data
            return CorteDetalle(
              uuid: d.uuid,
              corteId: d.corteId,
              maquinaId: d.maquinaId,
              maquinaCodigo: r['maquina_codigo'] as String?,
              estadoMaquina: d.estadoMaquina,
              scoreTarjeta: d.scoreTarjeta,
              efectivoTotal: d.efectivoTotal,
              fondo: d.fondo,
              recaudable: d.recaudable,
              diferenciaScore: d.diferenciaScore,
              syncStatus: 'pending',
            );
          }).toList();

      // Deduplicate by maquinaId (API wins)
      final apiMaqIds = apiDetalles.map((d) => d.maquinaId).toSet();
      final uniquePending = pendingDetalles
          .where((d) => !apiMaqIds.contains(d.maquinaId))
          .toList();

      setState(() {
        _corte = Corte.fromJson(corteRaw as Map<String, dynamic>);
        _detalles = [...apiDetalles, ...uniquePending];
        _maquinas = (maqRaw as List)
            .map((j) => Maquina.fromJson(j as Map<String, dynamic>))
            .toList();
      });
    } catch (e) {
      // Fully offline — load from local DB
      try {
        final db = ref.read(databaseProvider);
        final corteRow = await db.getCorteById(widget.corteId);
        if (corteRow != null) {
          final localDetalles = await db.getDetallesForCorte(widget.corteId);
          final maquinaRows = await db.query('maquinas');

          setState(() {
            _corte = Corte(
              uuid: corteRow['uuid'] as String,
              clienteId: corteRow['cliente_id'] as String,
              clienteNombre: corteRow['cliente_nombre'] as String?,
              weekStart: corteRow['week_start'] as String,
              weekEnd: corteRow['week_end'] as String,
              fechaCorte: corteRow['fecha_corte'] as String?,
              comisionPctUsada: (corteRow['comision_pct_usada'] as num).toDouble(),
              netoCliente: (corteRow['neto_cliente'] as num).toDouble(),
              pagoCliente: (corteRow['pago_cliente'] as num).toDouble(),
              gananciaDueno: (corteRow['ganancia_dueno'] as num).toDouble(),
              estado: corteRow['estado'] as String,
              syncStatus: corteRow['sync_status'] as String? ?? 'synced',
            );
            _detalles = localDetalles.map((r) {
              final d = CorteDetalle.fromDb(r);
              return CorteDetalle(
                uuid: d.uuid,
                corteId: d.corteId,
                maquinaId: d.maquinaId,
                maquinaCodigo: r['maquina_codigo'] as String?,
                estadoMaquina: d.estadoMaquina,
                scoreTarjeta: d.scoreTarjeta,
                efectivoTotal: d.efectivoTotal,
                fondo: d.fondo,
                recaudable: d.recaudable,
                diferenciaScore: d.diferenciaScore,
                syncStatus: d.syncStatus,
              );
            }).toList();
            _maquinas = maquinaRows
                .map((r) => Maquina.fromDb(r))
                .toList();
          });
        }
      } catch (_) {}
      if (_corte == null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error cargando corte')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  /// Machines that haven't been captured yet.
  List<Maquina> get _pendingMaquinas {
    final captured = _detalles.map((d) => d.maquinaId).toSet();
    // Only show machines belonging to the same client.
    return _maquinas
        .where(
            (m) => m.clienteId == _corte?.clienteId && !captured.contains(m.uuid))
        .toList();
  }

  Future<void> _closeCorte() async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Cerrar Corte'),
        content: const Text(
            '¿Está seguro de cerrar este corte? Esta acción calcula los totales finales.'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Cancelar')),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(
                backgroundColor: ZorezaTheme.success),
            child: const Text('Cerrar Corte',
                style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
    if (confirm != true) return;

    try {
      final api = ref.read(apiClientProvider);
      await api.closeCorte(widget.corteId);
      await _load();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
              content: Text('Corte cerrado exitosamente'),
              backgroundColor: ZorezaTheme.success),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'), backgroundColor: ZorezaTheme.danger),
        );
      }
    }
  }

  void _navigateCapture(Maquina maq) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => CaptureScreen(
          corteId: widget.corteId,
          maquina: maq,
        ),
      ),
    ).then((_) => _load());
  }

  void _navigateOmit(Maquina maq) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => OmitScreen(
          corteId: widget.corteId,
          maquina: maq,
        ),
      ),
    ).then((_) => _load());
  }

  void _showTicketPreview(Corte corte) {
    final ticketMaquinas = _detalles.map((d) {
      if (d.isOmitida) {
        return TicketMaquina(
          nombre: d.maquinaCodigo ?? '',
          omitida: true,
          motivoOmision: d.motivoOmisionNombre,
        );
      }
      final efectivo = d.efectivoTotal ?? 0;
      final score = d.scoreTarjeta ?? 0;
      final fondo = d.fondo ?? 0;
      return TicketMaquina(
        nombre: d.maquinaCodigo ?? '',
        efectivo: efectivo,
        scoreTarjeta: score,
        fondo: fondo,
        neto: d.recaudable ?? (efectivo + score - fondo),
      );
    }).toList();

    final bytes = TicketPrinter.buildCorteTicket(
      clienteNombre: corte.clienteNombre ?? '',
      weekStart: corte.weekStart,
      weekEnd: corte.weekEnd,
      maquinas: ticketMaquinas,
      netoCliente: corte.netoCliente,
      gananciaDueno: corte.gananciaDueno,
      totalGastos: 0,
      operador: corte.operadorNombre,
    );

    // Show preview as text (the raw bytes can be sent to a Bluetooth printer)
    final text = String.fromCharCodes(
        bytes.where((b) => b >= 0x20 || b == 0x0A));

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        builder: (_, ctrl) => Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Vista previa del ticket',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  FilledButton.icon(
                    onPressed: () {
                      Navigator.pop(ctx);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                              'Conecta una impresora Bluetooth para imprimir'),
                        ),
                      );
                    },
                    icon: const Icon(Icons.print),
                    label: const Text('Imprimir'),
                  ),
                ],
              ),
            ),
            const Divider(height: 0),
            Expanded(
              child: SingleChildScrollView(
                controller: ctrl,
                padding: const EdgeInsets.all(16),
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    text,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return Scaffold(
        appBar: AppBar(title: const Text('Corte')),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    final corte = _corte;
    if (corte == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Corte')),
        body: const Center(child: Text('Corte no encontrado')),
      );
    }

    final pending = _pendingMaquinas;

    return Scaffold(
      appBar: AppBar(
        title: Text(corte.clienteNombre ?? 'Corte'),
        actions: [
          if (corte.isCerrado)
            IconButton(
              icon: const Icon(Icons.print),
              tooltip: 'Imprimir ticket',
              onPressed: () => _showTicketPreview(corte),
            ),
          if (corte.isBorrador)
            TextButton.icon(
              onPressed: _closeCorte,
              icon: const Icon(Icons.check_circle, color: Colors.white),
              label: const Text('Cerrar', style: TextStyle(color: Colors.white)),
            ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(12),
          children: [
            // Header card
            _CorteHeader(corte: corte),
            const SizedBox(height: 16),

            // Pending machines (only if BORRADOR)
            if (corte.isBorrador && pending.isNotEmpty) ...[
              Text('Máquinas pendientes (${pending.length})',
                  style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              ...pending.map((m) => Card(
                    child: ListTile(
                      leading: const CircleAvatar(
                        backgroundColor: Color(0xFFFFF3E0),
                        child: Icon(Icons.pending, color: Colors.orange),
                      ),
                      title: Text(m.codigo),
                      subtitle: Text(m.clienteNombre ?? ''),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.edit_note,
                                color: ZorezaTheme.primary),
                            tooltip: 'Capturar',
                            onPressed: () => _navigateCapture(m),
                          ),
                          IconButton(
                            icon: const Icon(Icons.block,
                                color: Colors.grey),
                            tooltip: 'Omitir',
                            onPressed: () => _navigateOmit(m),
                          ),
                        ],
                      ),
                    ),
                  )),
              const SizedBox(height: 16),
            ],

            // Captured details
            if (_detalles.isNotEmpty) ...[
              Text('Detalles registrados (${_detalles.length})',
                  style: Theme.of(context).textTheme.titleSmall),
              const SizedBox(height: 8),
              ..._detalles.map((d) => _DetalleCard(detalle: d)),
            ],
          ],
        ),
      ),
    );
  }
}

class _CorteHeader extends StatelessWidget {
  final Corte corte;
  const _CorteHeader({required this.corte});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: corte.isCerrado ? ZorezaTheme.success.withAlpha(15) : null,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(corte.clienteNombre ?? '',
                    style: Theme.of(context).textTheme.titleMedium),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  decoration: BoxDecoration(
                    color: corte.isCerrado ? ZorezaTheme.success : Colors.orange,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(corte.estado,
                      style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                          fontSize: 12)),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text('Semana: ${corte.weekStart} → ${corte.weekEnd}',
                style: Theme.of(context).textTheme.bodySmall),
            if (corte.operadorNombre != null)
              Text('Operador: ${corte.operadorNombre}',
                  style: Theme.of(context).textTheme.bodySmall),
            if (corte.isCerrado) ...[
              const Divider(),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _MiniKpi('Neto', corte.netoCliente),
                  _MiniKpi('Cliente', corte.pagoCliente),
                  _MiniKpi('Dueño', corte.gananciaDueno),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MiniKpi extends StatelessWidget {
  final String label;
  final double value;
  const _MiniKpi(this.label, this.value);

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('\$${value.toStringAsFixed(0)}',
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        Text(label, style: Theme.of(context).textTheme.bodySmall),
      ],
    );
  }
}

class _DetalleCard extends StatelessWidget {
  final CorteDetalle detalle;
  const _DetalleCard({required this.detalle});

  @override
  Widget build(BuildContext context) {
    final isOmitida = detalle.isOmitida;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isOmitida ? Icons.block : Icons.check,
                  color: isOmitida ? Colors.grey : ZorezaTheme.success,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(detalle.maquinaCodigo ?? 'Máquina',
                    style: const TextStyle(fontWeight: FontWeight.bold)),
                const Spacer(),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: isOmitida ? Colors.grey : ZorezaTheme.primary,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(detalle.estadoMaquina,
                      style:
                          const TextStyle(color: Colors.white, fontSize: 10)),
                ),
              ],
            ),
            if (!isOmitida) ...[
              const SizedBox(height: 8),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Efectivo: \$${detalle.efectivoTotal?.toStringAsFixed(2) ?? '-'}'),
                  Text('Score: \$${detalle.scoreTarjeta?.toStringAsFixed(2) ?? '-'}'),
                ],
              ),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Fondo: \$${detalle.fondo?.toStringAsFixed(2) ?? '-'}'),
                  Text('Recaudable: \$${detalle.recaudable?.toStringAsFixed(2) ?? '-'}',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                ],
              ),
              if (detalle.causaIrregularidadNombre != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Row(
                    children: [
                      const Icon(Icons.warning, color: Colors.orange, size: 16),
                      const SizedBox(width: 4),
                      Text(detalle.causaIrregularidadNombre!,
                          style: const TextStyle(
                              color: Colors.orange, fontSize: 12)),
                    ],
                  ),
                ),
            ] else ...[
              if (detalle.motivoOmisionNombre != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text('Motivo: ${detalle.motivoOmisionNombre}',
                      style: const TextStyle(color: Colors.grey)),
                ),
            ],
          ],
        ),
      ),
    );
  }
}
