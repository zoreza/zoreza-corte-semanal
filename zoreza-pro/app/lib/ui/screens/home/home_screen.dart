import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/constants.dart';
import '../../../core/providers.dart';
import '../../theme/app_theme.dart';
import '../corte/corte_list_screen.dart';
import '../gastos/gastos_screen.dart';
import '../historial/historial_screen.dart';
import '../admin/admin_screen.dart';
import '../login/login_screen.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  Map<String, dynamic>? _dashboard;
  bool _loading = true;
  bool _syncing = false;
  int _pendingCount = 0;

  @override
  void initState() {
    super.initState();
    _loadDashboard();
    _loadPendingCount();
  }

  Future<void> _loadPendingCount() async {
    try {
      final db = ref.read(databaseProvider);
      final count = await db.countPending();
      if (mounted) setState(() => _pendingCount = count);
    } catch (_) {}
  }

  Future<void> _loadDashboard() async {
    setState(() => _loading = true);
    try {
      final api = ref.read(apiClientProvider);
      final data = await api.getDashboardSummary();
      setState(() => _dashboard = data);
    } catch (_) {
      // Offline — show empty dashboard.
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _sync() async {
    setState(() => _syncing = true);
    try {
      final syncSvc = ref.read(syncServiceProvider);
      final result = await syncSvc.fullSync();
      if (mounted) {
        final msg = result.success
            ? 'Sincronizado: ${result.pushed} enviados, ${result.pulled} recibidos'
            : 'Error: ${result.error}';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(msg),
            backgroundColor: result.success ? ZorezaTheme.success : ZorezaTheme.danger,
          ),
        );
      }
      await _loadDashboard();
      await _loadPendingCount();
    } finally {
      if (mounted) setState(() => _syncing = false);
    }
  }

  Future<void> _logout() async {
    final auth = ref.read(authServiceProvider);
    await auth.logout();
    ref.read(authStateProvider.notifier).set(AuthState.unauthenticated);
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = ref.watch(currentUserProvider);
    final isAdmin = user?['rol'] == AppConstants.roleAdmin;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Zoreza Pro'),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: _syncing
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.sync),
                onPressed: _syncing ? null : _sync,
                tooltip: 'Sincronizar',
              ),
              if (_pendingCount > 0)
                Positioned(
                  right: 4,
                  top: 4,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: Colors.orange,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '$_pendingCount',
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
            ],
          ),
          PopupMenuButton<String>(
            onSelected: (v) {
              if (v == 'logout') _logout();
            },
            itemBuilder: (_) => [
              PopupMenuItem(
                enabled: false,
                child: Text(user?['nombre'] ?? 'Usuario',
                    style: const TextStyle(fontWeight: FontWeight.bold)),
              ),
              PopupMenuItem(
                enabled: false,
                child: Text(user?['rol'] ?? '',
                    style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
              ),
              const PopupMenuDivider(),
              const PopupMenuItem(
                  value: 'logout', child: Text('Cerrar sesión')),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadDashboard,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Dashboard summary cards
            if (_loading)
              const Center(child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(),
              ))
            else if (_dashboard != null) ...[
              _buildSummaryRow(context),
              const SizedBox(height: 16),
              _buildFinancialCards(context),
            ] else
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text('Sin datos. Sincroniza para empezar.',
                      textAlign: TextAlign.center),
                ),
              ),

            const SizedBox(height: 24),

            // Quick action buttons
            Text('Acciones rápidas',
                style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 12),
            _buildActionGrid(context, isAdmin),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryRow(BuildContext context) {
    final d = _dashboard!;
    return Row(
      children: [
        Expanded(
          child: _KpiCard(
            icon: Icons.receipt_long,
            label: 'Cortes',
            value: '${d['total_cortes']}',
            color: ZorezaTheme.primary,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _KpiCard(
            icon: Icons.check_circle,
            label: 'Cerrados',
            value: '${d['cortes_cerrados']}',
            color: ZorezaTheme.success,
          ),
        ),
      ],
    );
  }

  Widget _buildFinancialCards(BuildContext context) {
    final d = _dashboard!;
    return Column(
      children: [
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Resumen Financiero',
                    style: Theme.of(context).textTheme.titleSmall),
                const Divider(),
                _FinRow('Neto clientes', d['total_neto']),
                _FinRow('Pago clientes', d['total_pago_cliente']),
                _FinRow('Ganancia dueño', d['total_ganancia_dueno']),
                _FinRow('Total gastos', d['total_gastos'],
                    color: ZorezaTheme.danger),
                const Divider(),
                _FinRow('Ganancia neta', d['ganancia_neta'],
                    color: ZorezaTheme.success, bold: true),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildActionGrid(BuildContext context, bool isAdmin) {
    return Column(
      children: [
        _ActionTile(
          icon: Icons.add_chart,
          title: 'Nuevo Corte',
          subtitle: 'Iniciar corte semanal',
          color: ZorezaTheme.primary,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const CorteListScreen())),
        ),
        _ActionTile(
          icon: Icons.history,
          title: 'Historial',
          subtitle: 'Ver cortes anteriores',
          color: Colors.blueGrey,
          onTap: () => Navigator.push(context,
              MaterialPageRoute(builder: (_) => const HistorialScreen())),
        ),
        if (isAdmin)
          _ActionTile(
            icon: Icons.account_balance_wallet,
            title: 'Gastos',
            subtitle: 'Registrar y ver gastos',
            color: ZorezaTheme.warning,
            onTap: () => Navigator.push(context,
                MaterialPageRoute(builder: (_) => const GastosScreen())),
          ),
        if (isAdmin)
          _ActionTile(
            icon: Icons.admin_panel_settings,
            title: 'Administración',
            subtitle: 'Usuarios y configuración',
            color: ZorezaTheme.danger,
            onTap: () => Navigator.push(context,
                MaterialPageRoute(builder: (_) => const AdminScreen())),
          ),
      ],
    );
  }
}

class _KpiCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _KpiCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(value,
                style: Theme.of(context)
                    .textTheme
                    .headlineSmall
                    ?.copyWith(fontWeight: FontWeight.bold, color: color)),
            Text(label,
                style: Theme.of(context)
                    .textTheme
                    .bodySmall
                    ?.copyWith(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}

class _FinRow extends StatelessWidget {
  final String label;
  final dynamic amount;
  final Color? color;
  final bool bold;

  const _FinRow(this.label, this.amount, {this.color, this.bold = false});

  @override
  Widget build(BuildContext context) {
    final val = (amount is num) ? amount.toDouble() : 0.0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            '\$${val.toStringAsFixed(2)}',
            style: TextStyle(
              fontWeight: bold ? FontWeight.bold : FontWeight.normal,
              color: color,
              fontSize: bold ? 16 : 14,
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String subtitle;
  final Color color;
  final VoidCallback onTap;

  const _ActionTile({
    required this.icon,
    required this.title,
    required this.subtitle,
    required this.color,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withAlpha(30),
          child: Icon(icon, color: color),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        subtitle: Text(subtitle),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}
