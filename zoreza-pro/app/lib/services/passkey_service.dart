import 'dart:convert';
import 'package:flutter/services.dart';
import 'api_client.dart';

/// Handles Passkey (WebAuthn) operations via Android Credential Manager.
///
/// Uses a MethodChannel to interact with the native Android Credential Manager
/// API, and communicates with the backend for challenge generation/verification.
class PasskeyService {
  final ApiClient api;

  PasskeyService({required this.api});

  static const _channel = MethodChannel('com.zoreza.app/passkeys');

  /// Check if the device supports passkeys.
  Future<bool> isSupported() async {
    try {
      final result = await _channel.invokeMethod<bool>('isSupported');
      return result ?? false;
    } catch (_) {
      return false;
    }
  }

  /// Register a new passkey for the current authenticated user.
  Future<Map<String, dynamic>> register({String deviceName = ''}) async {
    // 1. Get registration options from server
    final startRes = await api.dio.post('/passkeys/register/start', data: {});
    final optionsJson = startRes.data['options'] as String;

    // 2. Create credential via Android Credential Manager
    final credentialJson = await _channel.invokeMethod<String>(
      'createCredential',
      {'options': optionsJson},
    );
    if (credentialJson == null) {
      throw Exception('No se pudo crear la passkey');
    }

    // 3. Send result to server for verification
    final finishRes = await api.dio.post('/passkeys/register/finish', data: {
      'credential': credentialJson,
      'device_name': deviceName,
    });
    return finishRes.data as Map<String, dynamic>;
  }

  /// Authenticate using a passkey (no password needed).
  /// Returns JWT tokens on success.
  Future<Map<String, dynamic>> authenticate({String? username}) async {
    // 1. Get authentication options from server
    final startRes = await api.dio.post('/passkeys/authenticate/start', data: {
      'username': username,
    });
    final optionsJson = startRes.data['options'] as String;

    // 2. Get credential via Android Credential Manager
    final credentialJson = await _channel.invokeMethod<String>(
      'getCredential',
      {'options': optionsJson},
    );
    if (credentialJson == null) {
      throw Exception('Autenticación cancelada');
    }

    // 3. Verify with server and get tokens
    final finishRes = await api.dio.post('/passkeys/authenticate/finish', data: {
      'credential': credentialJson,
      'username': username,
    });
    return finishRes.data as Map<String, dynamic>;
  }

  /// List registered passkeys for the current user.
  Future<List<dynamic>> listCredentials() async {
    final response = await api.dio.get('/passkeys/credentials');
    return response.data as List<dynamic>;
  }

  /// Delete a passkey.
  Future<void> deleteCredential(String uuid) async {
    await api.dio.delete('/passkeys/credentials/$uuid');
  }
}
