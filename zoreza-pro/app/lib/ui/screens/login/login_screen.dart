import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/constants.dart';
import '../../../core/providers.dart';
import '../../../data/models/usuario.dart';
import '../../theme/app_theme.dart';
import '../home/home_screen.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _userCtrl = TextEditingController();
  final _passCtrl = TextEditingController();
  bool _loading = false;
  String? _error;
  bool _obscure = true;
  bool _passkeySupported = false;

  @override
  void initState() {
    super.initState();
    _checkPasskeySupport();
  }

  Future<void> _checkPasskeySupport() async {
    final passkey = ref.read(passkeyServiceProvider);
    final supported = await passkey.isSupported();
    if (mounted) setState(() => _passkeySupported = supported);
  }

  @override
  void dispose() {
    _userCtrl.dispose();
    _passCtrl.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final auth = ref.read(authServiceProvider);
      final user = await auth.login(
        _userCtrl.text.trim(),
        _passCtrl.text,
      );

      ref.read(currentUserProvider.notifier).set(user.toJson());
      ref.read(authStateProvider.notifier).set(AuthState.authenticated);

      // Pull reference data for offline use.
      try {
        final sync = ref.read(syncServiceProvider);
        await sync.pullReferenceData();
      } catch (_) {
        // Non-critical — user can still work.
      }

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      }
    } catch (e) {
      setState(() {
        _error = _parseError(e);
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  String _parseError(Object e) {
    final msg = e.toString();
    if (msg.contains('Credenciales') || msg.contains('401')) {
      return 'Usuario o contraseña incorrectos';
    }
    if (msg.contains('SocketException') || msg.contains('Connection')) {
      return 'Sin conexión al servidor';
    }
    return 'Error de inicio de sesión';
  }

  Future<void> _loginWithPasskey() async {
    setState(() {
      _loading = true;
      _error = null;
    });
    try {
      final passkey = ref.read(passkeyServiceProvider);
      final data = await passkey.authenticate();
      final prefs = ref.read(sharedPrefsProvider);
      await prefs.setString(AppConstants.keyAccessToken, data['access_token'] as String);
      await prefs.setString(AppConstants.keyRefreshToken, data['refresh_token'] as String);

      final api = ref.read(apiClientProvider);
      final me = await api.getMe();
      final user = Usuario.fromJson(me);

      ref.read(currentUserProvider.notifier).set(user.toJson());
      ref.read(authStateProvider.notifier).set(AuthState.authenticated);

      try {
        final sync = ref.read(syncServiceProvider);
        await sync.pullReferenceData();
      } catch (_) {}

      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      }
    } catch (e) {
      setState(() {
        final msg = e.toString();
        if (msg.contains('cancelad') || msg.contains('NotAllowed')) {
          _error = 'Autenticación cancelada';
        } else {
          _error = _parseError(e);
        }
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _showServerDialog() async {
    final prefs = await SharedPreferences.getInstance();
    final currentUrl = prefs.getString(AppConstants.keyBaseUrl) ?? AppConstants.defaultBaseUrl;
    final currentSlug = prefs.getString(AppConstants.keyTenantSlug) ?? AppConstants.defaultTenantSlug;
    final urlCtrl = TextEditingController(text: currentUrl);
    final slugCtrl = TextEditingController(text: currentSlug);
    final result = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Configuración'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: slugCtrl,
              decoration: const InputDecoration(
                labelText: 'ID del negocio (tenant)',
                hintText: 'mi-negocio',
                helperText: 'Proporcionado por Zoreza Labs',
                prefixIcon: Icon(Icons.business),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: urlCtrl,
              decoration: const InputDecoration(
                labelText: 'URL del servidor',
                hintText: 'https://zorezalabs.mx',
                prefixIcon: Icon(Icons.dns_outlined),
              ),
              keyboardType: TextInputType.url,
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancelar')),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Guardar'),
          ),
        ],
      ),
    );
    if (result == true) {
      final slug = slugCtrl.text.trim().toLowerCase();
      final url = urlCtrl.text.trim();
      if (slug.isNotEmpty) await prefs.setString(AppConstants.keyTenantSlug, slug);
      if (url.isNotEmpty) await prefs.setString(AppConstants.keyBaseUrl, url);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Configurado: $url/$slug')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: ZorezaTheme.primary,
      body: SafeArea(
        child: Stack(
          children: [
            Align(
              alignment: Alignment.topRight,
              child: Padding(
                padding: const EdgeInsets.all(8),
                child: IconButton(
                  icon: const Icon(Icons.settings, color: Colors.white70, size: 28),
                  tooltip: 'Configurar servidor',
                  onPressed: _showServerDialog,
                ),
              ),
            ),
            Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Card(
            elevation: 8,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Form(
                key: _formKey,
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.point_of_sale_rounded,
                        size: 64, color: ZorezaTheme.primary),
                    const SizedBox(height: 8),
                    Text(
                      'Zoreza Pro',
                      style: Theme.of(context)
                          .textTheme
                          .headlineMedium
                          ?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: ZorezaTheme.primary,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Corte Semanal',
                      style: Theme.of(context)
                          .textTheme
                          .bodyMedium
                          ?.copyWith(color: Colors.grey),
                    ),
                    const SizedBox(height: 32),

                    // Username
                    TextFormField(
                      controller: _userCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Usuario',
                        prefixIcon: Icon(Icons.person_outline),
                      ),
                      textInputAction: TextInputAction.next,
                      validator: (v) =>
                          (v == null || v.trim().isEmpty) ? 'Requerido' : null,
                    ),
                    const SizedBox(height: 16),

                    // Password
                    TextFormField(
                      controller: _passCtrl,
                      obscureText: _obscure,
                      decoration: InputDecoration(
                        labelText: 'Contraseña',
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          icon: Icon(
                              _obscure ? Icons.visibility_off : Icons.visibility),
                          onPressed: () =>
                              setState(() => _obscure = !_obscure),
                        ),
                      ),
                      textInputAction: TextInputAction.done,
                      onFieldSubmitted: (_) => _login(),
                      validator: (v) =>
                          (v == null || v.isEmpty) ? 'Requerido' : null,
                    ),
                    const SizedBox(height: 24),

                    // Error message
                    if (_error != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: ZorezaTheme.danger.withAlpha(25),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(children: [
                          Icon(Icons.error_outline,
                              color: ZorezaTheme.danger, size: 20),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(_error!,
                                style:
                                    TextStyle(color: ZorezaTheme.danger)),
                          ),
                        ]),
                      ),
                      const SizedBox(height: 16),
                    ],

                    // Login button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _loading ? null : _login,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: ZorezaTheme.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                        ),
                        child: _loading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(
                                    strokeWidth: 2, color: Colors.white))
                            : const Text('INICIAR SESIÓN',
                                style: TextStyle(
                                    fontSize: 16, fontWeight: FontWeight.bold)),
                      ),
                    ),

                    // Passkey button
                    if (_passkeySupported) ...[
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          onPressed: _loading ? null : _loginWithPasskey,
                          icon: const Icon(Icons.fingerprint, size: 22),
                          label: const Text('Ingresar con Passkey',
                              style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600)),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 14),
                            side: BorderSide(color: ZorezaTheme.primary.withAlpha(128)),
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
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
}
