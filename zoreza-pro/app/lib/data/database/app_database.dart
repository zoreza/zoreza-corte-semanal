import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

/// Local SQLite database for offline-first operation.
class AppDatabase {
  static const int _version = 2;
  static const String _dbName = 'zoreza_pro.db';

  Database? _db;

  Future<Database> get database async {
    _db ??= await _open();
    return _db!;
  }

  Future<Database> _open() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, _dbName);
    return openDatabase(
      path,
      version: _version,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    final batch = db.batch();

    batch.execute('''
      CREATE TABLE usuarios (
        uuid TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        nombre TEXT NOT NULL,
        rol TEXT NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'synced'
      )
    ''');

    batch.execute('''
      CREATE TABLE clientes (
        uuid TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        comision_pct REAL NOT NULL DEFAULT 0.40,
        activo INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'synced'
      )
    ''');

    batch.execute('''
      CREATE TABLE maquinas (
        uuid TEXT PRIMARY KEY,
        codigo TEXT NOT NULL,
        cliente_id TEXT,
        activo INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'synced',
        FOREIGN KEY (cliente_id) REFERENCES clientes(uuid)
      )
    ''');

    batch.execute('''
      CREATE TABLE rutas (
        uuid TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        activo INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'synced'
      )
    ''');

    batch.execute('''
      CREATE TABLE maquina_ruta (
        uuid TEXT PRIMARY KEY,
        maquina_id TEXT NOT NULL,
        ruta_id TEXT NOT NULL,
        activo INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'synced',
        FOREIGN KEY (maquina_id) REFERENCES maquinas(uuid),
        FOREIGN KEY (ruta_id) REFERENCES rutas(uuid),
        UNIQUE(maquina_id, ruta_id)
      )
    ''');

    batch.execute('''
      CREATE TABLE cortes (
        uuid TEXT PRIMARY KEY,
        cliente_id TEXT NOT NULL,
        week_start TEXT NOT NULL,
        week_end TEXT NOT NULL,
        fecha_corte TEXT,
        comision_pct_usada REAL NOT NULL DEFAULT 0.0,
        neto_cliente REAL NOT NULL DEFAULT 0.0,
        pago_cliente REAL NOT NULL DEFAULT 0.0,
        ganancia_dueno REAL NOT NULL DEFAULT 0.0,
        estado TEXT NOT NULL DEFAULT 'BORRADOR',
        created_by TEXT,
        created_at TEXT,
        sync_status TEXT NOT NULL DEFAULT 'synced',
        FOREIGN KEY (cliente_id) REFERENCES clientes(uuid),
        UNIQUE(cliente_id, week_start)
      )
    ''');

    batch.execute('''
      CREATE TABLE corte_detalle (
        uuid TEXT PRIMARY KEY,
        corte_id TEXT NOT NULL,
        maquina_id TEXT NOT NULL,
        estado_maquina TEXT NOT NULL DEFAULT 'CAPTURADA',
        score_tarjeta REAL,
        efectivo_total REAL,
        fondo REAL,
        recaudable REAL,
        diferencia_score REAL,
        contador_entrada_actual INTEGER,
        contador_salida_actual INTEGER,
        contador_entrada_prev INTEGER,
        contador_salida_prev INTEGER,
        delta_entrada INTEGER,
        delta_salida INTEGER,
        monto_estimado_contadores REAL,
        causa_irregularidad_id TEXT,
        nota_irregularidad TEXT,
        evento_contador_id TEXT,
        nota_evento_contador TEXT,
        motivo_omision_id TEXT,
        nota_omision TEXT,
        sync_status TEXT NOT NULL DEFAULT 'synced',
        FOREIGN KEY (corte_id) REFERENCES cortes(uuid),
        FOREIGN KEY (maquina_id) REFERENCES maquinas(uuid),
        UNIQUE(corte_id, maquina_id)
      )
    ''');

    batch.execute('''
      CREATE TABLE gastos (
        uuid TEXT PRIMARY KEY,
        fecha TEXT NOT NULL,
        categoria TEXT NOT NULL,
        descripcion TEXT NOT NULL,
        monto REAL NOT NULL,
        notas TEXT,
        created_by TEXT,
        created_at TEXT,
        sync_status TEXT NOT NULL DEFAULT 'synced'
      )
    ''');

    batch.execute('''
      CREATE TABLE catalogs (
        uuid TEXT PRIMARY KEY,
        catalog_type TEXT NOT NULL,
        nombre TEXT NOT NULL,
        requiere_nota INTEGER NOT NULL DEFAULT 0,
        activo INTEGER NOT NULL DEFAULT 1,
        sync_status TEXT NOT NULL DEFAULT 'synced'
      )
    ''');

    // Indexes
    batch.execute(
        'CREATE INDEX idx_catalogs_type ON catalogs(catalog_type, activo)');
    batch.execute(
        'CREATE INDEX idx_cortes_sync ON cortes(sync_status)');
    batch.execute(
        'CREATE INDEX idx_corte_detalle_sync ON corte_detalle(sync_status)');
    batch.execute(
        'CREATE INDEX idx_gastos_sync ON gastos(sync_status)');

    await batch.commit(noResult: true);
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      // Allow nullable cliente_id for pool machines
      await db.execute('''
        CREATE TABLE maquinas_new (
          uuid TEXT PRIMARY KEY,
          codigo TEXT NOT NULL,
          cliente_id TEXT,
          activo INTEGER NOT NULL DEFAULT 1,
          sync_status TEXT NOT NULL DEFAULT 'synced',
          FOREIGN KEY (cliente_id) REFERENCES clientes(uuid)
        )
      ''');
      await db.execute('INSERT INTO maquinas_new SELECT * FROM maquinas');
      await db.execute('DROP TABLE maquinas');
      await db.execute('ALTER TABLE maquinas_new RENAME TO maquinas');
    }
  }

  // ── Generic helpers ──

  Future<List<Map<String, dynamic>>> query(
    String table, {
    String? where,
    List<Object?>? whereArgs,
    String? orderBy,
  }) async {
    final db = await database;
    return db.query(table, where: where, whereArgs: whereArgs, orderBy: orderBy);
  }

  Future<int> insert(String table, Map<String, dynamic> values) async {
    final db = await database;
    return db.insert(table, values, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<int> update(
    String table,
    Map<String, dynamic> values, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final db = await database;
    return db.update(table, values, where: where, whereArgs: whereArgs);
  }

  Future<int> delete(
    String table, {
    String? where,
    List<Object?>? whereArgs,
  }) async {
    final db = await database;
    return db.delete(table, where: where, whereArgs: whereArgs);
  }

  Future<void> upsertBatch(
      String table, List<Map<String, dynamic>> rows) async {
    final db = await database;
    final batch = db.batch();
    for (final row in rows) {
      batch.insert(table, row, conflictAlgorithm: ConflictAlgorithm.replace);
    }
    await batch.commit(noResult: true);
  }

  /// Get all records with pending sync status.
  Future<List<Map<String, dynamic>>> getPending(String table) async {
    return query(table, where: "sync_status = 'pending'");
  }

  /// Mark a record as synced.
  Future<void> markSynced(String table, String uuid) async {
    await update(
      table,
      {'sync_status': 'synced'},
      where: 'uuid = ?',
      whereArgs: [uuid],
    );
  }

  /// Count total pending records across sync-relevant tables.
  Future<int> countPending() async {
    final db = await database;
    int total = 0;
    for (final table in ['cortes', 'corte_detalle', 'gastos']) {
      final r = await db.rawQuery(
        "SELECT COUNT(*) as c FROM $table WHERE sync_status = 'pending'",
      );
      total += (r.first['c'] as int?) ?? 0;
    }
    return total;
  }

  /// Get cortes joined with client name, ordered by week_start desc.
  Future<List<Map<String, dynamic>>> getCortesWithCliente({
    String? syncStatus,
  }) async {
    final db = await database;
    final where = syncStatus != null
        ? "WHERE c.sync_status = '$syncStatus'"
        : '';
    return db.rawQuery('''
      SELECT c.*, cl.nombre AS cliente_nombre
      FROM cortes c
      LEFT JOIN clientes cl ON c.cliente_id = cl.uuid
      $where
      ORDER BY c.week_start DESC
    ''');
  }

  /// Get a single corte by UUID joined with client name.
  Future<Map<String, dynamic>?> getCorteById(String uuid) async {
    final db = await database;
    final rows = await db.rawQuery('''
      SELECT c.*, cl.nombre AS cliente_nombre
      FROM cortes c
      LEFT JOIN clientes cl ON c.cliente_id = cl.uuid
      WHERE c.uuid = ?
    ''', [uuid]);
    return rows.isEmpty ? null : rows.first;
  }

  /// Get detalles for a corte joined with machine code.
  Future<List<Map<String, dynamic>>> getDetallesForCorte(String corteId) async {
    final db = await database;
    return db.rawQuery('''
      SELECT d.*, m.codigo AS maquina_codigo
      FROM corte_detalle d
      LEFT JOIN maquinas m ON d.maquina_id = m.uuid
      WHERE d.corte_id = ?
    ''', [corteId]);
  }

  /// Remap corte_id for detalles (used when pushing offline cortes).
  Future<void> remapCorteId(String oldCorteId, String newCorteId) async {
    await update(
      'corte_detalle',
      {'corte_id': newCorteId},
      where: 'corte_id = ?',
      whereArgs: [oldCorteId],
    );
  }

  Future<void> close() async {
    _db?.close();
    _db = null;
  }

  /// Delete all local data (for cache reset).
  Future<void> deleteAllData() async {
    final db = await database;
    final tables = [
      'corte_detalle', 'cortes', 'gastos', 'maquina_ruta',
      'maquinas', 'clientes', 'rutas', 'usuarios', 'catalogs',
    ];
    final batch = db.batch();
    for (final t in tables) {
      batch.delete(t);
    }
    await batch.commit(noResult: true);
  }
}
