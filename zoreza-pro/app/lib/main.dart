import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'core/constants.dart';
import 'core/providers.dart';
import 'services/update_service.dart';
import 'ui/theme/app_theme.dart';
import 'ui/screens/login/login_screen.dart';
import 'ui/screens/home/home_screen.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();

  runApp(
    ProviderScope(
      overrides: [
        sharedPrefsProvider.overrideWithValue(prefs),
      ],
      child: const ZorezaApp(),
    ),
  );
}

class ZorezaApp extends ConsumerStatefulWidget {
  const ZorezaApp({super.key});

  // This widget is the root of your application.
  @override
  ConsumerState<ZorezaApp> createState() => _ZorezaAppState();
}

class _ZorezaAppState extends ConsumerState<ZorezaApp> {
  final _navigatorKey = GlobalKey<NavigatorState>();

  @override
  void initState() {
    super.initState();
    _checkAuth();
    _checkForUpdates();
  }

  Future<void> _checkAuth() async {
    final auth = ref.read(authServiceProvider);
    try {
      final user = await auth.getCurrentUser();
      if (user != null && mounted) {
        ref.read(currentUserProvider.notifier).set(user.toJson());
        ref.read(authStateProvider.notifier).set(AuthState.authenticated);
        return;
      }
    } catch (_) {}
    if (mounted) {
      ref.read(authStateProvider.notifier).set(AuthState.unauthenticated);
    }
  }

  Future<void> _checkForUpdates() async {
    // Small delay to let the UI settle
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;

    final updateService = ref.read(updateServiceProvider);
    final release = await updateService.checkForUpdate();
    if (release == null || !mounted) return;

    final ctx = _navigatorKey.currentContext;
    if (ctx == null) return;

    final accepted = await UpdateService.showUpdateDialog(
      ctx,
      versionName: release['version_name'] as String,
      isMandatory: release['is_mandatory'] as bool? ?? false,
      releaseNotes: release['release_notes'] as String?,
    );

    if (accepted && ctx.mounted) {
      await UpdateService.showDownloadAndInstall(
        ctx,
        updateService,
        release['download_url'] as String,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authStateProvider);

    return MaterialApp(
      navigatorKey: _navigatorKey,
      title: AppConstants.appName,
      theme: ZorezaTheme.light,
      debugShowCheckedModeBanner: false,
      home: switch (authState) {
        AuthState.unknown => const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          ),
        AuthState.authenticated => const HomeScreen(),
        AuthState.unauthenticated => const LoginScreen(),
      },
    );
  }
}
