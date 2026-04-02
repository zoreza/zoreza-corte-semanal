/// Expense model.
class Gasto {
  final String uuid;
  final String fecha;
  final String categoria;
  final String descripcion;
  final double monto;
  final String? notas;
  final String? createdBy;
  final String? createdAt;
  final String syncStatus;

  const Gasto({
    required this.uuid,
    required this.fecha,
    required this.categoria,
    required this.descripcion,
    required this.monto,
    this.notas,
    this.createdBy,
    this.createdAt,
    this.syncStatus = 'synced',
  });

  factory Gasto.fromJson(Map<String, dynamic> json) => Gasto(
        uuid: json['uuid'] as String,
        fecha: json['fecha'] as String,
        categoria: json['categoria'] as String,
        descripcion: json['descripcion'] as String,
        monto: (json['monto'] as num).toDouble(),
        notas: json['notas'] as String?,
        createdBy: json['created_by'] as String?,
        createdAt: json['created_at'] as String?,
      );

  Map<String, dynamic> toJson() => {
        'fecha': fecha,
        'categoria': categoria,
        'descripcion': descripcion,
        'monto': monto,
        if (notas != null) 'notas': notas,
      };

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'fecha': fecha,
        'categoria': categoria,
        'descripcion': descripcion,
        'monto': monto,
        'notas': notas,
        'created_by': createdBy,
        'created_at': createdAt,
        'sync_status': syncStatus,
      };

  factory Gasto.fromDb(Map<String, dynamic> row) => Gasto(
        uuid: row['uuid'] as String,
        fecha: row['fecha'] as String,
        categoria: row['categoria'] as String,
        descripcion: row['descripcion'] as String,
        monto: (row['monto'] as num).toDouble(),
        notas: row['notas'] as String?,
        createdBy: row['created_by'] as String?,
        createdAt: row['created_at'] as String?,
        syncStatus: row['sync_status'] as String? ?? 'synced',
      );
}
