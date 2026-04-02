/// Corte (weekly settlement) model.
class Corte {
  final String uuid;
  final String clienteId;
  final String? clienteNombre;
  final String weekStart;
  final String weekEnd;
  final String? fechaCorte;
  final double comisionPctUsada;
  final double netoCliente;
  final double pagoCliente;
  final double gananciaDueno;
  final String estado;
  final String? createdBy;
  final String? operadorNombre;
  final String? createdAt;
  final String syncStatus;

  const Corte({
    required this.uuid,
    required this.clienteId,
    this.clienteNombre,
    required this.weekStart,
    required this.weekEnd,
    this.fechaCorte,
    required this.comisionPctUsada,
    required this.netoCliente,
    required this.pagoCliente,
    required this.gananciaDueno,
    required this.estado,
    this.createdBy,
    this.operadorNombre,
    this.createdAt,
    this.syncStatus = 'synced',
  });

  bool get isBorrador => estado == 'BORRADOR';
  bool get isCerrado => estado == 'CERRADO';

  factory Corte.fromJson(Map<String, dynamic> json) => Corte(
        uuid: json['uuid'] as String,
        clienteId: json['cliente_id'] as String,
        clienteNombre: json['cliente_nombre'] as String?,
        weekStart: json['week_start'] as String,
        weekEnd: json['week_end'] as String,
        fechaCorte: json['fecha_corte'] as String?,
        comisionPctUsada: (json['comision_pct_usada'] as num).toDouble(),
        netoCliente: (json['neto_cliente'] as num).toDouble(),
        pagoCliente: (json['pago_cliente'] as num).toDouble(),
        gananciaDueno: (json['ganancia_dueno'] as num).toDouble(),
        estado: json['estado'] as String,
        createdBy: json['created_by'] as String?,
        operadorNombre: json['operador_nombre'] as String?,
        createdAt: json['created_at'] as String?,
      );

  /// From CorteSummary JSON (list endpoint).
  factory Corte.fromSummaryJson(Map<String, dynamic> json) => Corte(
        uuid: json['uuid'] as String,
        clienteId: '',
        clienteNombre: json['cliente_nombre'] as String?,
        weekStart: json['week_start'] as String,
        weekEnd: json['week_end'] as String,
        comisionPctUsada: 0,
        netoCliente: (json['neto_cliente'] as num).toDouble(),
        pagoCliente: (json['pago_cliente'] as num).toDouble(),
        gananciaDueno: (json['ganancia_dueno'] as num).toDouble(),
        estado: json['estado'] as String,
      );

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'cliente_id': clienteId,
        'week_start': weekStart,
        'week_end': weekEnd,
        'fecha_corte': fechaCorte,
        'comision_pct_usada': comisionPctUsada,
        'neto_cliente': netoCliente,
        'pago_cliente': pagoCliente,
        'ganancia_dueno': gananciaDueno,
        'estado': estado,
        'created_by': createdBy,
        'created_at': createdAt,
        'sync_status': syncStatus,
      };

  factory Corte.fromDb(Map<String, dynamic> row) => Corte(
        uuid: row['uuid'] as String,
        clienteId: row['cliente_id'] as String,
        weekStart: row['week_start'] as String,
        weekEnd: row['week_end'] as String,
        fechaCorte: row['fecha_corte'] as String?,
        comisionPctUsada: (row['comision_pct_usada'] as num).toDouble(),
        netoCliente: (row['neto_cliente'] as num).toDouble(),
        pagoCliente: (row['pago_cliente'] as num).toDouble(),
        gananciaDueno: (row['ganancia_dueno'] as num).toDouble(),
        estado: row['estado'] as String,
        createdBy: row['created_by'] as String?,
        createdAt: row['created_at'] as String?,
        syncStatus: row['sync_status'] as String? ?? 'synced',
      );
}
