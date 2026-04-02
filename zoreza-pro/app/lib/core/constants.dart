/// App-wide constants.
class AppConstants {
  AppConstants._();

  static const String appName = 'Zoreza Pro';
  static const String defaultBaseUrl = 'https://zorezalabs.mx';
  static const String defaultTenantSlug = 'demo';

  /// Build the API prefix for a given tenant slug.
  static String apiPrefix(String tenantSlug) => '/$tenantSlug/api/v1';

  // Token / config storage keys
  static const String keyAccessToken = 'access_token';
  static const String keyRefreshToken = 'refresh_token';
  static const String keyBaseUrl = 'base_url';
  static const String keyTenantSlug = 'tenant_slug';
  static const String keyDeviceId = 'device_id';
  static const String keyLastSyncVersion = 'last_sync_version';

  // Gasto categories
  static const List<String> gastoCategories = [
    'REFACCIONES',
    'FONDOS_ROBOS',
    'PERMISOS',
    'EMPLEADOS',
    'SERVICIOS',
    'TRANSPORTE',
    'OTRO',
  ];

  // Roles
  static const String roleAdmin = 'ADMIN';
  static const String roleSupervisor = 'SUPERVISOR';
  static const String roleOperador = 'OPERADOR';
}
