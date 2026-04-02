import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_client.dart';
import '../services/auth_service.dart';
import '../services/sync_service.dart';
import '../services/update_service.dart';
import '../services/passkey_service.dart';
import '../data/database/app_database.dart';

/// SharedPreferences provider.
final sharedPrefsProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('Must be overridden at startup');
});

/// Local database provider.
final databaseProvider = Provider<AppDatabase>((ref) {
  return AppDatabase();
});

/// API client provider.
final apiClientProvider = Provider<ApiClient>((ref) {
  final prefs = ref.watch(sharedPrefsProvider);
  return ApiClient(prefs: prefs);
});

/// Auth service provider.
final authServiceProvider = Provider<AuthService>((ref) {
  final api = ref.watch(apiClientProvider);
  final prefs = ref.watch(sharedPrefsProvider);
  return AuthService(api: api, prefs: prefs);
});

/// Sync service provider.
final syncServiceProvider = Provider<SyncService>((ref) {
  final api = ref.watch(apiClientProvider);
  final db = ref.watch(databaseProvider);
  final prefs = ref.watch(sharedPrefsProvider);
  return SyncService(api: api, db: db, prefs: prefs);
});

/// Update service provider.
final updateServiceProvider = Provider<UpdateService>((ref) {
  final prefs = ref.watch(sharedPrefsProvider);
  return UpdateService(prefs: prefs);
});

/// Passkey service provider.
final passkeyServiceProvider = Provider<PasskeyService>((ref) {
  final api = ref.watch(apiClientProvider);
  return PasskeyService(api: api);
});

/// Current user auth state.
final authStateProvider = NotifierProvider<AuthStateNotifier, AuthState>(AuthStateNotifier.new);

class AuthStateNotifier extends Notifier<AuthState> {
  @override
  AuthState build() => AuthState.unknown;
  void set(AuthState value) => state = value;
}

enum AuthState { unknown, authenticated, unauthenticated }

/// Currently logged-in user info.
final currentUserProvider = NotifierProvider<CurrentUserNotifier, Map<String, dynamic>?>(CurrentUserNotifier.new);

class CurrentUserNotifier extends Notifier<Map<String, dynamic>?> {
  @override
  Map<String, dynamic>? build() => null;
  void set(Map<String, dynamic>? value) => state = value;
}
