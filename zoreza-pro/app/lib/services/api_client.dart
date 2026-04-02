import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../core/constants.dart';

/// HTTP client with JWT token handling and base URL configuration.
class ApiClient {
  final SharedPreferences prefs;
  late final Dio dio;

  ApiClient({required this.prefs}) {
    dio = Dio(BaseOptions(
      baseUrl: _fullApiBase,
      connectTimeout: const Duration(seconds: 10),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) {
        // Re-read base URL on every request so changes take effect immediately.
        dio.options.baseUrl = _fullApiBase;
        final token = prefs.getString(AppConstants.keyAccessToken);
        if (token != null) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          final refreshed = await _tryRefresh();
          if (refreshed) {
            // Retry the original request with new token.
            final opts = error.requestOptions;
            opts.headers['Authorization'] =
                'Bearer ${prefs.getString(AppConstants.keyAccessToken)}';
            final response = await dio.fetch(opts);
            return handler.resolve(response);
          }
        }
        handler.next(error);
      },
    ));
  }

  String get _baseUrl =>
      prefs.getString(AppConstants.keyBaseUrl) ?? AppConstants.defaultBaseUrl;

  String get _tenantSlug =>
      prefs.getString(AppConstants.keyTenantSlug) ?? AppConstants.defaultTenantSlug;

  String get _fullApiBase => _baseUrl + AppConstants.apiPrefix(_tenantSlug);

  Future<bool> _tryRefresh() async {
    final refreshToken = prefs.getString(AppConstants.keyRefreshToken);
    if (refreshToken == null) return false;
    try {
      final response = await Dio(BaseOptions(
        baseUrl: _fullApiBase,
      )).post('/auth/refresh', data: {'refresh_token': refreshToken});
      final data = response.data as Map<String, dynamic>;
      await prefs.setString(
          AppConstants.keyAccessToken, data['access_token'] as String);
      await prefs.setString(
          AppConstants.keyRefreshToken, data['refresh_token'] as String);
      return true;
    } catch (_) {
      return false;
    }
  }

  // ── Auth ──

  Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await dio.post('/auth/login', data: {
      'username': username,
      'password': password,
    });
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> getMe() async {
    final response = await dio.get('/auth/me');
    return response.data as Map<String, dynamic>;
  }

  // ── Clientes ──

  Future<List<dynamic>> getClientes({bool? activo}) async {
    final response = await dio.get('/clientes', queryParameters: {
      if (activo != null) 'activo': activo,
    });
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createCliente(Map<String, dynamic> data) async {
    final response = await dio.post('/clientes', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateCliente(String id, Map<String, dynamic> data) async {
    final response = await dio.patch('/clientes/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  // ── Máquinas ──

  Future<List<dynamic>> getMaquinas({String? clienteId, bool? activo}) async {
    final response = await dio.get('/maquinas', queryParameters: {
      if (clienteId != null) 'cliente_id': clienteId,
      if (activo != null) 'activo': activo,
    });
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createMaquina(Map<String, dynamic> data) async {
    final response = await dio.post('/maquinas', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateMaquina(String id, Map<String, dynamic> data) async {
    final response = await dio.patch('/maquinas/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  // ── Rutas ──

  Future<List<dynamic>> getRutas({bool? activo}) async {
    final response = await dio.get('/rutas', queryParameters: {
      if (activo != null) 'activo': activo,
    });
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createRuta(Map<String, dynamic> data) async {
    final response = await dio.post('/rutas', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateRuta(String id, Map<String, dynamic> data) async {
    final response = await dio.patch('/rutas/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<void> assignMaquinaToRuta(String rutaId, String maquinaId) async {
    await dio.post('/rutas/$rutaId/maquinas/$maquinaId');
  }

  Future<void> unassignMaquinaFromRuta(String rutaId, String maquinaId) async {
    await dio.delete('/rutas/$rutaId/maquinas/$maquinaId');
  }

  Future<List<dynamic>> getRutaMaquinas(String rutaId) async {
    final response = await dio.get('/rutas/$rutaId/maquinas');
    return response.data as List<dynamic>;
  }

  // ── Catálogos ──

  Future<List<dynamic>> getCatalog(String catalogType) async {
    final response = await dio.get('/catalogs/$catalogType');
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createCatalogItem(String catalogType, Map<String, dynamic> data) async {
    final response = await dio.post('/catalogs/$catalogType', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateCatalogItem(String catalogType, String id, Map<String, dynamic> data) async {
    final response = await dio.patch('/catalogs/$catalogType/$id', data: data);
    return response.data as Map<String, dynamic>;
  }

  // ── Cortes ──

  Future<List<dynamic>> getCortes({
    String? clienteId,
    String? estado,
    int limit = 100,
    int offset = 0,
  }) async {
    final response = await dio.get('/cortes', queryParameters: {
      if (clienteId != null) 'cliente_id': clienteId,
      if (estado != null) 'estado': estado,
      'limit': limit,
      'offset': offset,
    });
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> getCorte(String corteId) async {
    final response = await dio.get('/cortes/$corteId');
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> createCorte(
      String clienteId, String fechaCorte) async {
    final response = await dio.post('/cortes', data: {
      'cliente_id': clienteId,
      'fecha_corte': fechaCorte,
    });
    return response.data as Map<String, dynamic>;
  }

  Future<List<dynamic>> getCorteDetalles(String corteId) async {
    final response = await dio.get('/cortes/$corteId/detalles');
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> captureDetalle(
      String corteId, Map<String, dynamic> payload) async {
    final response =
        await dio.post('/cortes/$corteId/detalle/capturada', data: payload);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> omitDetalle(
      String corteId, Map<String, dynamic> payload) async {
    final response =
        await dio.post('/cortes/$corteId/detalle/omitida', data: payload);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> closeCorte(String corteId) async {
    final response = await dio.post('/cortes/$corteId/close');
    return response.data as Map<String, dynamic>;
  }

  // ── Gastos ──

  Future<List<dynamic>> getGastos({
    String? fechaInicio,
    String? fechaFin,
    String? categoria,
  }) async {
    final response = await dio.get('/gastos', queryParameters: {
      if (fechaInicio != null) 'fecha_inicio': fechaInicio,
      if (fechaFin != null) 'fecha_fin': fechaFin,
      if (categoria != null) 'categoria': categoria,
    });
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createGasto(Map<String, dynamic> data) async {
    final response = await dio.post('/gastos', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<void> deleteGasto(String gastoId) async {
    await dio.delete('/gastos/$gastoId');
  }

  // ── Dashboard ──

  Future<Map<String, dynamic>> getDashboardSummary({
    String? fechaInicio,
    String? fechaFin,
  }) async {
    final response = await dio.get('/dashboard/summary', queryParameters: {
      if (fechaInicio != null) 'fecha_inicio': fechaInicio,
      if (fechaFin != null) 'fecha_fin': fechaFin,
    });
    return response.data as Map<String, dynamic>;
  }

  // ── Sync ──

  Future<Map<String, dynamic>> syncPull(
      int sinceVersion, String deviceId) async {
    final response = await dio.post('/sync/pull', data: {
      'since_version': sinceVersion,
      'device_id': deviceId,
    });
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> syncPush(
      String deviceId, List<Map<String, dynamic>> changes) async {
    final response = await dio.post('/sync/push', data: {
      'device_id': deviceId,
      'changes': changes,
    });
    return response.data as Map<String, dynamic>;
  }

  // ── Usuarios (admin) ──

  Future<List<dynamic>> getUsuarios({bool? activo}) async {
    final response = await dio.get('/usuarios', queryParameters: {
      if (activo != null) 'activo': activo,
    });
    return response.data as List<dynamic>;
  }

  Future<Map<String, dynamic>> createUsuario(Map<String, dynamic> data) async {
    final response = await dio.post('/usuarios', data: data);
    return response.data as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> updateUsuario(
      String userId, Map<String, dynamic> data) async {
    final response = await dio.patch('/usuarios/$userId', data: data);
    return response.data as Map<String, dynamic>;
  }

  /// Check if the server is reachable.
  Future<bool> isServerReachable() async {
    try {
      final response = await Dio(BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: const Duration(seconds: 3),
        receiveTimeout: const Duration(seconds: 3),
      )).get('/health');
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
