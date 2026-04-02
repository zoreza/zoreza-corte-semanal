import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/constants.dart';

/// Handles checking for new APK versions, downloading, and triggering install.
class UpdateService {
  final SharedPreferences prefs;

  UpdateService({required this.prefs});

  static const _channel = MethodChannel('com.zoreza.app/installer');

  String get _baseUrl =>
      prefs.getString(AppConstants.keyBaseUrl) ?? AppConstants.defaultBaseUrl;

  /// Checks the server for the latest release and compares with current build.
  /// Returns release info map if update is available, null otherwise.
  Future<Map<String, dynamic>?> checkForUpdate() async {
    try {
      final info = await PackageInfo.fromPlatform();
      final currentCode = int.tryParse(info.buildNumber) ?? 0;

      final dio = Dio(BaseOptions(
        baseUrl: _baseUrl,
        connectTimeout: const Duration(seconds: 5),
        receiveTimeout: const Duration(seconds: 5),
      ));

      final response = await dio.get('/zoreza-admin/api/releases/latest');
      if (response.statusCode == 200) {
        final data = response.data as Map<String, dynamic>;
        final serverCode = data['version_code'] as int;
        if (serverCode > currentCode) {
          return data;
        }
      }
    } catch (_) {
      // Silently fail — update check is best-effort
    }
    return null;
  }

  /// Downloads the APK to the cache directory with progress callback.
  /// Returns the local file path on success.
  Future<String> downloadApk(
    String downloadUrl, {
    void Function(int received, int total)? onProgress,
  }) async {
    final dir = await getTemporaryDirectory();
    final filePath = '${dir.path}/zoreza-update.apk';

    await Dio(BaseOptions(baseUrl: _baseUrl)).download(
      downloadUrl,
      filePath,
      onReceiveProgress: onProgress,
    );

    return filePath;
  }

  /// Triggers APK installation via platform channel.
  Future<void> installApk(String filePath) async {
    await _channel.invokeMethod('installApk', {'path': filePath});
  }

  /// Shows an update dialog. Returns true if user accepted.
  static Future<bool> showUpdateDialog(
    BuildContext context, {
    required String versionName,
    required bool isMandatory,
    String? releaseNotes,
  }) async {
    final result = await showDialog<bool>(
      context: context,
      barrierDismissible: !isMandatory,
      builder: (ctx) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.system_update, color: Colors.blue),
            const SizedBox(width: 8),
            const Expanded(child: Text('Actualización disponible')),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Versión $versionName está disponible.'),
            if (releaseNotes != null && releaseNotes.isNotEmpty) ...[
              const SizedBox(height: 12),
              const Text('Novedades:', style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Text(releaseNotes, style: const TextStyle(fontSize: 13)),
            ],
            if (isMandatory) ...[
              const SizedBox(height: 12),
              const Text(
                'Esta actualización es obligatoria.',
                style: TextStyle(color: Colors.red, fontWeight: FontWeight.w600),
              ),
            ],
          ],
        ),
        actions: [
          if (!isMandatory)
            TextButton(
              onPressed: () => Navigator.pop(ctx, false),
              child: const Text('Después'),
            ),
          FilledButton.icon(
            onPressed: () => Navigator.pop(ctx, true),
            icon: const Icon(Icons.download),
            label: const Text('Actualizar'),
          ),
        ],
      ),
    );
    return result ?? false;
  }

  /// Shows download progress and triggers install.
  static Future<void> showDownloadAndInstall(
    BuildContext context,
    UpdateService service,
    String downloadUrl,
  ) async {
    final progressNotifier = ValueNotifier<double>(0.0);
    final statusNotifier = ValueNotifier<String>('Descargando...');

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => PopScope(
        canPop: false,
        child: AlertDialog(
          title: const Text('Descargando actualización'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ValueListenableBuilder<double>(
                valueListenable: progressNotifier,
                builder: (_, val, __) => LinearProgressIndicator(value: val > 0 ? val : null),
              ),
              const SizedBox(height: 12),
              ValueListenableBuilder<String>(
                valueListenable: statusNotifier,
                builder: (_, text, __) => Text(text, style: const TextStyle(fontSize: 13)),
              ),
            ],
          ),
        ),
      ),
    );

    try {
      final path = await service.downloadApk(
        downloadUrl,
        onProgress: (received, total) {
          if (total > 0) {
            final pct = received / total;
            progressNotifier.value = pct;
            final mb = (received / 1024 / 1024).toStringAsFixed(1);
            final totalMb = (total / 1024 / 1024).toStringAsFixed(1);
            statusNotifier.value = '$mb MB / $totalMb MB';
          }
        },
      );

      statusNotifier.value = 'Instalando...';
      if (context.mounted) Navigator.pop(context);

      await service.installApk(path);
    } catch (e) {
      if (context.mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error al descargar: $e')),
        );
      }
    }
  }
}
