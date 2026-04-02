/// Client model.
class Cliente {
  final String uuid;
  final String nombre;
  final double comisionPct;
  final bool activo;
  final String syncStatus;

  const Cliente({
    required this.uuid,
    required this.nombre,
    required this.comisionPct,
    required this.activo,
    this.syncStatus = 'synced',
  });

  factory Cliente.fromJson(Map<String, dynamic> json) => Cliente(
        uuid: json['uuid'] as String,
        nombre: json['nombre'] as String,
        comisionPct: (json['comision_pct'] as num).toDouble(),
        activo: json['activo'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'uuid': uuid,
        'nombre': nombre,
        'comision_pct': comisionPct,
        'activo': activo,
      };

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'nombre': nombre,
        'comision_pct': comisionPct,
        'activo': activo ? 1 : 0,
        'sync_status': syncStatus,
      };

  factory Cliente.fromDb(Map<String, dynamic> row) => Cliente(
        uuid: row['uuid'] as String,
        nombre: row['nombre'] as String,
        comisionPct: (row['comision_pct'] as num).toDouble(),
        activo: (row['activo'] as int) == 1,
        syncStatus: row['sync_status'] as String? ?? 'synced',
      );
}
