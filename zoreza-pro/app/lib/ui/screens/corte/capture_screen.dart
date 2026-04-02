import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../core/providers.dart';
import '../../../data/models/models.dart';
import '../../../ui/theme/app_theme.dart';

/// Machine data capture form.
class CaptureScreen extends ConsumerStatefulWidget {
  final String corteId;
  final Maquina maquina;

  const CaptureScreen({
    super.key,
    required this.corteId,
    required this.maquina,
  });

  @override
  ConsumerState<CaptureScreen> createState() => _CaptureScreenState();
}

class _CaptureScreenState extends ConsumerState<CaptureScreen> {
  final _formKey = GlobalKey<FormState>();
  final _efectivoCtrl = TextEditingController();
  final _scoreCtrl = TextEditingController();
  final _fondoCtrl = TextEditingController(text: '500');
  final _contEntradaCtrl = TextEditingController();
  final _contSalidaCtrl = TextEditingController();
  final _notaIrregCtrl = TextEditingController();

  List<CatalogItem> _irregularidades = [];
  String? _selectedIrregId;
  bool _loading = false;
  bool _showContadores = false;
  bool _irregRequired = false;

  @override
  void initState() {
    super.initState();
    _loadCatalogs();
  }

  @override
  void dispose() {
    _efectivoCtrl.dispose();
    _scoreCtrl.dispose();
    _fondoCtrl.dispose();
    _contEntradaCtrl.dispose();
    _contSalidaCtrl.dispose();
    _notaIrregCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadCatalogs() async {
    try {
      // Try local DB first, fallback to API.
      final db = ref.read(databaseProvider);
      final rows = await db.query('catalogs',
          where: "catalog_type = 'irregularidad' AND activo = 1");
      if (rows.isNotEmpty) {
        setState(() {
          _irregularidades = rows.map((r) => CatalogItem.fromDb(r)).toList();
        });
        return;
      }
    } catch (_) {}

    try {
      final api = ref.read(apiClientProvider);
      final data = await api.getCatalog('irregularidad');
      setState(() {
        _irregularidades = data
            .map((j) => CatalogItem.fromJson(j as Map<String, dynamic>))
            .toList();
      });
    } catch (_) {}
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _loading = true);

    final efectivo = double.parse(_efectivoCtrl.text);
    final score = double.parse(_scoreCtrl.text);
    final fondo = double.parse(_fondoCtrl.text);

    final payload = <String, dynamic>{
      'maquina_id': widget.maquina.uuid,
      'efectivo_total': efectivo,
      'score_tarjeta': score,
      'fondo': fondo,
    };

    if (_contEntradaCtrl.text.isNotEmpty) {
      payload['contador_entrada_actual'] = int.parse(_contEntradaCtrl.text);
    }
    if (_contSalidaCtrl.text.isNotEmpty) {
      payload['contador_salida_actual'] = int.parse(_contSalidaCtrl.text);
    }
    if (_selectedIrregId != null) {
      payload['causa_irregularidad_id'] = _selectedIrregId;
      if (_notaIrregCtrl.text.isNotEmpty) {
        payload['nota_irregularidad'] = _notaIrregCtrl.text;
      }
    }

    try {
      final api = ref.read(apiClientProvider);
      await api.captureDetalle(widget.corteId, payload);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${widget.maquina.codigo} capturada'),
            backgroundColor: ZorezaTheme.success,
          ),
        );
        Navigator.pop(context, true);
      }
    } catch (e) {
      // Check if this is a network/connectivity error → save offline
      if (_isNetworkError(e)) {
        await _saveOffline(efectivo, score, fondo);
        return;
      }

      final detail = _extractDetail(e);
      if (detail.contains('irregularidad') || detail.contains('tolerancia')) {
        setState(() => _irregRequired = true);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(detail),
              backgroundColor: ZorezaTheme.warning,
              duration: const Duration(seconds: 4),
            ),
          );
        }
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(detail), backgroundColor: ZorezaTheme.danger),
          );
        }
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  bool _isNetworkError(Object e) {
    if (e is DioException) {
      return e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          e.type == DioExceptionType.unknown;
    }
    return false;
  }

  Future<void> _saveOffline(double efectivo, double score, double fondo) async {
    final db = ref.read(databaseProvider);
    final recaudable = efectivo - fondo;
    final diferencia = recaudable - score;
    final uuid = const Uuid().v4();

    final row = <String, dynamic>{
      'uuid': uuid,
      'corte_id': widget.corteId,
      'maquina_id': widget.maquina.uuid,
      'estado_maquina': 'CAPTURADA',
      'score_tarjeta': score,
      'efectivo_total': efectivo,
      'fondo': fondo,
      'recaudable': recaudable,
      'diferencia_score': diferencia,
      'sync_status': 'pending',
    };

    if (_contEntradaCtrl.text.isNotEmpty) {
      row['contador_entrada_actual'] = int.parse(_contEntradaCtrl.text);
    }
    if (_contSalidaCtrl.text.isNotEmpty) {
      row['contador_salida_actual'] = int.parse(_contSalidaCtrl.text);
    }
    if (_selectedIrregId != null) {
      row['causa_irregularidad_id'] = _selectedIrregId;
      if (_notaIrregCtrl.text.isNotEmpty) {
        row['nota_irregularidad'] = _notaIrregCtrl.text;
      }
    }

    await db.insert('corte_detalle', row);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('${widget.maquina.codigo} guardada offline — se sincronizará'),
          backgroundColor: Colors.orange,
          duration: const Duration(seconds: 3),
        ),
      );
      Navigator.pop(context, true);
    }
  }

  /// Extract the `detail` string from a Dio 4xx/5xx response, or fall back to toString().
  String _extractDetail(Object e) {
    if (e is DioException && e.response?.data != null) {
      final data = e.response!.data;
      if (data is Map && data.containsKey('detail')) {
        final detail = data['detail'];
        if (detail is String) return detail;
        return detail.toString();
      }
    }
    return e.toString();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Capturar ${widget.maquina.codigo}'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Machine info
              Card(
                color: ZorezaTheme.primary.withAlpha(15),
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      const Icon(Icons.videogame_asset,
                          color: ZorezaTheme.primary),
                      const SizedBox(width: 12),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(widget.maquina.codigo,
                              style:
                                  const TextStyle(fontWeight: FontWeight.bold)),
                          if (widget.maquina.clienteNombre != null)
                            Text(widget.maquina.clienteNombre!,
                                style: const TextStyle(
                                    color: Colors.grey, fontSize: 12)),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 20),

              // Efectivo total
              TextFormField(
                controller: _efectivoCtrl,
                decoration: const InputDecoration(
                  labelText: 'Efectivo Total (\$)',
                  prefixIcon: Icon(Icons.attach_money),
                ),
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                inputFormatters: [
                  FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
                ],
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Requerido';
                  if (double.tryParse(v) == null) return 'Número inválido';
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Score tarjeta
              TextFormField(
                controller: _scoreCtrl,
                decoration: const InputDecoration(
                  labelText: 'Score Tarjeta (\$)',
                  prefixIcon: Icon(Icons.credit_card),
                ),
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                inputFormatters: [
                  FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
                ],
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Requerido';
                  if (double.tryParse(v) == null) return 'Número inválido';
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Fondo
              TextFormField(
                controller: _fondoCtrl,
                decoration: const InputDecoration(
                  labelText: 'Fondo (\$)',
                  prefixIcon: Icon(Icons.savings),
                ),
                keyboardType:
                    const TextInputType.numberWithOptions(decimal: true),
                inputFormatters: [
                  FilteringTextInputFormatter.allow(RegExp(r'[\d.]')),
                ],
                validator: (v) {
                  if (v == null || v.isEmpty) return 'Requerido';
                  if (double.tryParse(v) == null) return 'Número inválido';
                  return null;
                },
              ),
              const SizedBox(height: 16),

              // Contadores toggle
              SwitchListTile(
                title: const Text('Registrar contadores'),
                value: _showContadores,
                onChanged: (v) => setState(() => _showContadores = v),
                contentPadding: EdgeInsets.zero,
              ),
              if (_showContadores) ...[
                Row(
                  children: [
                    Expanded(
                      child: TextFormField(
                        controller: _contEntradaCtrl,
                        decoration:
                            const InputDecoration(labelText: 'Cont. Entrada'),
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextFormField(
                        controller: _contSalidaCtrl,
                        decoration:
                            const InputDecoration(labelText: 'Cont. Salida'),
                        keyboardType: TextInputType.number,
                        inputFormatters: [
                          FilteringTextInputFormatter.digitsOnly
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
              ],

              // Irregularidad
              if (_irregRequired) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: ZorezaTheme.warning.withAlpha(30),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: ZorezaTheme.warning),
                  ),
                  child: const Row(children: [
                    Icon(Icons.warning_amber, color: ZorezaTheme.warning, size: 20),
                    SizedBox(width: 8),
                    Expanded(child: Text(
                      'La diferencia excede la tolerancia. Seleccione una causa de irregularidad para continuar.',
                      style: TextStyle(fontSize: 13),
                    )),
                  ]),
                ),
                const SizedBox(height: 12),
              ],
              DropdownButtonFormField<String>(
                decoration: InputDecoration(
                  labelText: _irregRequired
                      ? 'Causa de irregularidad (requerida)'
                      : 'Causa de irregularidad (opcional)',
                  prefixIcon: const Icon(Icons.warning_amber),
                  enabledBorder: _irregRequired
                      ? OutlineInputBorder(borderSide: BorderSide(color: ZorezaTheme.warning))
                      : null,
                ),
                initialValue: _selectedIrregId,
                items: [
                  const DropdownMenuItem(value: null, child: Text('Ninguna')),
                  ..._irregularidades.map((item) => DropdownMenuItem(
                        value: item.uuid,
                        child: Text(item.nombre),
                      )),
                ],
                onChanged: (v) => setState(() => _selectedIrregId = v),
                validator: _irregRequired
                    ? (v) => v == null ? 'Requerido — diferencia excede tolerancia' : null
                    : null,
              ),
              if (_selectedIrregId != null) ...[
                const SizedBox(height: 12),
                TextFormField(
                  controller: _notaIrregCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Nota de irregularidad',
                    prefixIcon: Icon(Icons.note),
                  ),
                  maxLines: 2,
                ),
              ],
              const SizedBox(height: 32),

              // Submit
              ElevatedButton.icon(
                onPressed: _loading ? null : _submit,
                icon: _loading
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2))
                    : const Icon(Icons.save),
                label: const Text('GUARDAR CAPTURA'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: ZorezaTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
