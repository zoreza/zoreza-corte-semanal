/// User model.
class Usuario {
  final String uuid;
  final String username;
  final String nombre;
  final String rol;
  final bool activo;

  const Usuario({
    required this.uuid,
    required this.username,
    required this.nombre,
    required this.rol,
    required this.activo,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) => Usuario(
        uuid: json['uuid'] as String,
        username: json['username'] as String,
        nombre: json['nombre'] as String,
        rol: json['rol'] as String,
        activo: json['activo'] as bool,
      );

  Map<String, dynamic> toJson() => {
        'uuid': uuid,
        'username': username,
        'nombre': nombre,
        'rol': rol,
        'activo': activo,
      };

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'username': username,
        'nombre': nombre,
        'rol': rol,
        'activo': activo ? 1 : 0,
        'sync_status': 'synced',
      };

  factory Usuario.fromDb(Map<String, dynamic> row) => Usuario(
        uuid: row['uuid'] as String,
        username: row['username'] as String,
        nombre: row['nombre'] as String,
        rol: row['rol'] as String,
        activo: (row['activo'] as int) == 1,
      );
}
