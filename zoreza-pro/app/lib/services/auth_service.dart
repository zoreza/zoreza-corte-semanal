import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';
import '../data/models/usuario.dart';
import 'api_client.dart';

/// Handles login, logout, and token persistence.
class AuthService {
  final ApiClient api;
  final SharedPreferences prefs;

  AuthService({required this.api, required this.prefs});

  bool get isLoggedIn => prefs.containsKey(AppConstants.keyAccessToken);

  Future<Usuario> login(String username, String password) async {
    final data = await api.login(username, password);
    await prefs.setString(
        AppConstants.keyAccessToken, data['access_token'] as String);
    await prefs.setString(
        AppConstants.keyRefreshToken, data['refresh_token'] as String);

    final me = await api.getMe();
    return Usuario.fromJson(me);
  }

  Future<Usuario?> getCurrentUser() async {
    if (!isLoggedIn) return null;
    try {
      final me = await api.getMe();
      return Usuario.fromJson(me);
    } catch (_) {
      return null;
    }
  }

  Future<void> logout() async {
    await prefs.remove(AppConstants.keyAccessToken);
    await prefs.remove(AppConstants.keyRefreshToken);
  }
}
