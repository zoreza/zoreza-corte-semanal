import 'dart:async';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';
import '../core/constants.dart';
import '../data/database/app_database.dart';
import '../data/models/models.dart';
import 'api_client.dart';

/// Offline-first sync engine.
/// Pulls reference data from server → local SQLite.
/// Pushes locally-created cortes/detalles/gastos → server.
class SyncService {
  final ApiClient api;
  final AppDatabase db;
  final SharedPreferences prefs;

  SyncService({required this.api, required this.db, required this.prefs});

  String get deviceId {
    var id = prefs.getString(AppConstants.keyDeviceId);
    if (id == null) {
      id = const Uuid().v4();
      prefs.setString(AppConstants.keyDeviceId, id);
    }
    return id;
  }

  /// Full synchronization: push pending changes, then pull reference data.
  Future<SyncResult> fullSync() async {
    final result = SyncResult();

    final connected = await _isOnline();
    if (!connected) {
      result.error = 'Sin conexión a internet';
      return result;
    }

    final reachable = await api.isServerReachable();
    if (!reachable) {
      result.error = 'Servidor no disponible';
      return result;
    }

    try {
      // 1. Push pending cortes first (detalles depend on server corte IDs)
      result.pushed += await _pushPendingCortes();

      // 2. Push remaining pending detalles (for cortes that were online)
      result.pushed += await _pushPendingDetalles();

      // 3. Push pending gastos
      result.pushed += await _pushPendingGastos();

      // 4. Pull reference data
      await _pullClientes();
      result.pulled += 1;
      await _pullMaquinas();
      result.pulled += 1;
      await _pullRutas();
      result.pulled += 1;
      await _pullCatalogs('irregularidad');
      await _pullCatalogs('omision');
      await _pullCatalogs('evento_contador');
      result.pulled += 3;
    } catch (e) {
      result.error = e.toString();
    }

    return result;
  }

  /// Pull only reference data (for initial login sync).
  Future<void> pullReferenceData() async {
    await _pullClientes();
    await _pullMaquinas();
    await _pullRutas();
    await _pullCatalogs('irregularidad');
    await _pullCatalogs('omision');
    await _pullCatalogs('evento_contador');
  }

  Future<void> _pullClientes() async {
    final data = await api.getClientes(activo: true);
    final rows =
        data.map((j) => Cliente.fromJson(j as Map<String, dynamic>).toDb()).toList();
    await db.upsertBatch('clientes', rows);
  }

  Future<void> _pullMaquinas() async {
    final data = await api.getMaquinas(activo: true);
    final rows =
        data.map((j) => Maquina.fromJson(j as Map<String, dynamic>).toDb()).toList();
    await db.upsertBatch('maquinas', rows);
  }

  Future<void> _pullRutas() async {
    final data = await api.getRutas(activo: true);
    final rows =
        data.map((j) => Ruta.fromJson(j as Map<String, dynamic>).toDb()).toList();
    await db.upsertBatch('rutas', rows);
  }

  Future<void> _pullCatalogs(String type) async {
    final data = await api.getCatalog(type);
    final rows = data
        .map((j) =>
            CatalogItem.fromJson(j as Map<String, dynamic>).toDb(type))
        .toList();
    await db.upsertBatch('catalogs', rows);
  }

  /// Push locally-created cortes to the server, remap UUIDs, push detalles.
  Future<int> _pushPendingCortes() async {
    final pending = await db.getPending('cortes');
    int count = 0;

    for (final row in pending) {
      try {
        final corte = Corte.fromDb(row);
        final localUuid = corte.uuid;

        // Create corte on server (server generates UUID + week bounds)
        final serverData = await api.createCorte(
          corte.clienteId,
          corte.fechaCorte ?? corte.weekStart,
        );
        final serverUuid = serverData['uuid'] as String;

        // Remap pending detalles from local corte UUID to server UUID
        await db.remapCorteId(localUuid, serverUuid);

        // Push detalles for this corte
        await _pushDetallesForCorte(serverUuid);

        // Remove local pending corte (server version will come from API)
        await db.delete('cortes',
            where: 'uuid = ?', whereArgs: [localUuid]);

        count++;
      } catch (_) {
        // Will retry on next sync
      }
    }

    return count;
  }

  /// Push pending detalles for cortes already on the server.
  Future<int> _pushPendingDetalles() async {
    final pending = await db.getPending('corte_detalle');
    int count = 0;

    for (final row in pending) {
      try {
        final detalle = CorteDetalle.fromDb(row);
        await _pushSingleDetalle(detalle);
        // Remove local pending (server version available via API)
        await db.delete('corte_detalle',
            where: 'uuid = ?', whereArgs: [detalle.uuid]);
        count++;
      } catch (_) {
        // Will retry on next sync
      }
    }

    return count;
  }

  Future<void> _pushDetallesForCorte(String corteId) async {
    final pending = await db.query(
      'corte_detalle',
      where: "corte_id = ? AND sync_status = 'pending'",
      whereArgs: [corteId],
    );

    for (final row in pending) {
      try {
        final detalle = CorteDetalle.fromDb(row);
        await _pushSingleDetalle(detalle);
        await db.delete('corte_detalle',
            where: 'uuid = ?', whereArgs: [detalle.uuid]);
      } catch (_) {
        // Will retry
      }
    }
  }

  Future<void> _pushSingleDetalle(CorteDetalle d) async {
    if (d.isCapturada) {
      final payload = <String, dynamic>{
        'maquina_id': d.maquinaId,
        'efectivo_total': d.efectivoTotal,
        'score_tarjeta': d.scoreTarjeta,
        'fondo': d.fondo,
        if (d.contadorEntradaActual != null)
          'contador_entrada_actual': d.contadorEntradaActual,
        if (d.contadorSalidaActual != null)
          'contador_salida_actual': d.contadorSalidaActual,
        if (d.causaIrregularidadId != null)
          'causa_irregularidad_id': d.causaIrregularidadId,
        if (d.notaIrregularidad != null)
          'nota_irregularidad': d.notaIrregularidad,
      };
      await api.captureDetalle(d.corteId, payload);
    } else if (d.isOmitida) {
      final payload = <String, dynamic>{
        'maquina_id': d.maquinaId,
        if (d.motivoOmisionId != null)
          'motivo_omision_id': d.motivoOmisionId,
        if (d.notaOmision != null)
          'nota_omision': d.notaOmision,
      };
      await api.omitDetalle(d.corteId, payload);
    }
  }

  Future<int> _pushPendingGastos() async {
    final pending = await db.getPending('gastos');
    int count = 0;
    for (final row in pending) {
      try {
        final gasto = Gasto.fromDb(row);
        await api.createGasto(gasto.toJson());
        // Remove local pending entry (server has its own copy)
        await db.delete('gastos',
            where: 'uuid = ?', whereArgs: [gasto.uuid]);
        count++;
      } catch (_) {
        // Will retry next sync
      }
    }
    return count;
  }

  Future<bool> _isOnline() async {
    final result = await Connectivity().checkConnectivity();
    return result.any((r) => r != ConnectivityResult.none);
  }
}

class SyncResult {
  int pulled = 0;
  int pushed = 0;
  String? error;

  bool get success => error == null;
}
