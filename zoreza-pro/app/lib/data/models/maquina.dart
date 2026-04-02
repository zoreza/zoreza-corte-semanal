/// Machine model.
class Maquina {
  final String uuid;
  final String codigo;
  final String? clienteId;
  final bool activo;
  final String? clienteNombre;
  final String syncStatus;

  const Maquina({
    required this.uuid,
    required this.codigo,
    this.clienteId,
    required this.activo,
    this.clienteNombre,
    this.syncStatus = 'synced',
  });

  factory Maquina.fromJson(Map<String, dynamic> json) => Maquina(
        uuid: json['uuid'] as String,
        codigo: json['codigo'] as String,
        clienteId: json['cliente_id'] as String?,
        activo: json['activo'] as bool,
        clienteNombre: json['cliente_nombre'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'uuid': uuid,
        'codigo': codigo,
        'cliente_id': clienteId,
        'activo': activo,
      };

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'codigo': codigo,
        'cliente_id': clienteId,
        'activo': activo ? 1 : 0,
        'sync_status': syncStatus,
      };

  factory Maquina.fromDb(Map<String, dynamic> row) => Maquina(
        uuid: row['uuid'] as String,
        codigo: row['codigo'] as String,
        clienteId: row['cliente_id'] as String?,
        activo: (row['activo'] as int) == 1,
        syncStatus: row['sync_status'] as String? ?? 'synced',
      );
}
