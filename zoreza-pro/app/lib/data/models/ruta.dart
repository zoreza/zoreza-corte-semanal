/// Route model.
class Ruta {
  final String uuid;
  final String nombre;
  final String? descripcion;
  final bool activo;
  final String syncStatus;

  const Ruta({
    required this.uuid,
    required this.nombre,
    this.descripcion,
    required this.activo,
    this.syncStatus = 'synced',
  });

  factory Ruta.fromJson(Map<String, dynamic> json) => Ruta(
        uuid: json['uuid'] as String,
        nombre: json['nombre'] as String,
        descripcion: json['descripcion'] as String?,
        activo: json['activo'] as bool,
      );

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'nombre': nombre,
        'descripcion': descripcion,
        'activo': activo ? 1 : 0,
        'sync_status': syncStatus,
      };

  factory Ruta.fromDb(Map<String, dynamic> row) => Ruta(
        uuid: row['uuid'] as String,
        nombre: row['nombre'] as String,
        descripcion: row['descripcion'] as String?,
        activo: (row['activo'] as int) == 1,
        syncStatus: row['sync_status'] as String? ?? 'synced',
      );
}
