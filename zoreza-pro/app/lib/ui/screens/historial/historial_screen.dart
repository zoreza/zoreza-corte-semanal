import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/providers.dart';
import '../../../data/models/models.dart';
import '../../../ui/theme/app_theme.dart';
import '../corte/corte_detail_screen.dart';

/// Previously closed cortes.
class HistorialScreen extends ConsumerStatefulWidget {
  const HistorialScreen({super.key});

  @override
  ConsumerState<HistorialScreen> createState() => _HistorialScreenState();
}

class _HistorialScreenState extends ConsumerState<HistorialScreen> {
  List<Corte> _cortes = [];
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
      final data = await api.getCortes(estado: 'CERRADO');
      setState(() {
        _cortes = data
            .map((j) => Corte.fromSummaryJson(j as Map<String, dynamic>))
            .toList();
      });
    } catch (_) {
      // No offline historial for now.
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final totalNeto = _cortes.fold(0.0, (s, c) => s + c.netoCliente);

    return Scaffold(
      appBar: AppBar(title: const Text('Historial de Cortes')),
      body: Column(
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(20),
            color: ZorezaTheme.success.withAlpha(15),
            child: Column(
              children: [
                Text('${_cortes.length} cortes cerrados',
                    style: const TextStyle(color: Colors.grey)),
                Text('\$${totalNeto.toStringAsFixed(2)}',
                    style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold, color: ZorezaTheme.success)),
                const Text('Total neto', style: TextStyle(color: Colors.grey)),
              ],
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _cortes.isEmpty
                    ? const Center(child: Text('No hay cortes cerrados'))
                    : RefreshIndicator(
                        onRefresh: _load,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(12),
                          itemCount: _cortes.length,
                          itemBuilder: (_, i) {
                            final c = _cortes[i];
                            return Card(
                              child: ListTile(
                                leading: const CircleAvatar(
                                  backgroundColor: Color(0xFFE8F5E9),
                                  child: Icon(Icons.check_circle,
                                      color: ZorezaTheme.success),
                                ),
                                title:
                                    Text(c.clienteNombre ?? ''),
                                subtitle: Text(
                                    '${c.weekStart} → ${c.weekEnd}'),
                                trailing: Column(
                                  mainAxisAlignment:
                                      MainAxisAlignment.center,
                                  crossAxisAlignment:
                                      CrossAxisAlignment.end,
                                  children: [
                                    Text(
                                      '\$${c.netoCliente.toStringAsFixed(0)}',
                                      style: const TextStyle(
                                          fontWeight: FontWeight.bold),
                                    ),
                                    Text(
                                      'Dueño: \$${c.gananciaDueno.toStringAsFixed(0)}',
                                      style: const TextStyle(
                                          fontSize: 11, color: Colors.grey),
                                    ),
                                  ],
                                ),
                                onTap: () => Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) =>
                                        CorteDetailScreen(corteId: c.uuid),
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
