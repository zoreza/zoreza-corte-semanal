import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../core/providers.dart';
import '../../../data/models/models.dart';
import '../../../ui/theme/app_theme.dart';

/// Omit a machine (mark as skipped with reason).
class OmitScreen extends ConsumerStatefulWidget {
  final String corteId;
  final Maquina maquina;

  const OmitScreen({
    super.key,
    required this.corteId,
    required this.maquina,
  });

  @override
  ConsumerState<OmitScreen> createState() => _OmitScreenState();
}

class _OmitScreenState extends ConsumerState<OmitScreen> {
  List<CatalogItem> _motivos = [];
  String? _selectedMotivoId;
  final _notaCtrl = TextEditingController();
  bool _loading = false;
  bool _requiresNote = false;

  @override
  void initState() {
    super.initState();
    _loadCatalogs();
  }

  @override
  void dispose() {
    _notaCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadCatalogs() async {
    try {
      final db = ref.read(databaseProvider);
      final rows = await db.query('catalogs',
          where: "catalog_type = 'omision' AND activo = 1");
      if (rows.isNotEmpty) {
        setState(() => _motivos = rows.map((r) => CatalogItem.fromDb(r)).toList());
        return;
      }
    } catch (_) {}

    try {
      final api = ref.read(apiClientProvider);
      final data = await api.getCatalog('omision');
      setState(() {
        _motivos = data
            .map((j) => CatalogItem.fromJson(j as Map<String, dynamic>))
            .toList();
      });
    } catch (_) {}
  }

  Future<void> _submit() async {
    if (_selectedMotivoId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Seleccione un motivo de omisión')),
      );
      return;
    }

    setState(() => _loading = true);
    try {
      final api = ref.read(apiClientProvider);
      final payload = <String, dynamic>{
        'maquina_id': widget.maquina.uuid,
        'motivo_omision_id': _selectedMotivoId,
      };
      if (_notaCtrl.text.isNotEmpty) {
        payload['nota_omision'] = _notaCtrl.text;
      }
      await api.omitDetalle(widget.corteId, payload);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${widget.maquina.codigo} omitida'),
            backgroundColor: Colors.grey,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      // Network error → save offline
      if (e is DioException &&
          (e.type == DioExceptionType.connectionTimeout ||
           e.type == DioExceptionType.connectionError ||
           e.type == DioExceptionType.unknown)) {
        await _saveOffline();
        return;
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('Error: $e'), backgroundColor: ZorezaTheme.danger),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _saveOffline() async {
    final db = ref.read(databaseProvider);
    final uuid = const Uuid().v4();
    await db.insert('corte_detalle', {
      'uuid': uuid,
      'corte_id': widget.corteId,
      'maquina_id': widget.maquina.uuid,
      'estado_maquina': 'OMITIDA',
      'motivo_omision_id': _selectedMotivoId,
      'nota_omision': _notaCtrl.text.isNotEmpty ? _notaCtrl.text : null,
      'sync_status': 'pending',
    });
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${widget.maquina.codigo} omitida offline — se sincronizará'),
          backgroundColor: Colors.orange,
        ),
      );
      Navigator.pop(context, true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Omitir ${widget.maquina.codigo}'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.grey.shade100,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    const Icon(Icons.block, color: Colors.grey),
                    const SizedBox(width: 12),
                    Text(widget.maquina.codigo,
                        style: const TextStyle(fontWeight: FontWeight.bold)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),

            DropdownButtonFormField<String>(
              decoration: const InputDecoration(
                labelText: 'Motivo de omisión',
                prefixIcon: Icon(Icons.help_outline),
              ),
              items: _motivos
                  .map((m) => DropdownMenuItem(
                        value: m.uuid,
                        child: Text(m.nombre),
                      ))
                  .toList(),
              onChanged: (v) {
                setState(() {
                  _selectedMotivoId = v;
                  _requiresNote = _motivos
                      .any((m) => m.uuid == v && m.requiereNota);
                });
              },
            ),
            const SizedBox(height: 16),

            TextFormField(
              controller: _notaCtrl,
              decoration: InputDecoration(
                labelText:
                    _requiresNote ? 'Nota (requerida)' : 'Nota (opcional)',
                prefixIcon: const Icon(Icons.note),
              ),
              maxLines: 3,
            ),
            const Spacer(),

            ElevatedButton.icon(
              onPressed: _loading ? null : _submit,
              icon: _loading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.block),
              label: const Text('OMITIR MÁQUINA'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.grey,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
