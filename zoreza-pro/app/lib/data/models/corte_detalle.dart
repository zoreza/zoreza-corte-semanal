/// Corte detail (per-machine reading).
class CorteDetalle {
  final String uuid;
  final String corteId;
  final String maquinaId;
  final String? maquinaCodigo;
  final String estadoMaquina; // CAPTURADA or OMITIDA
  final double? scoreTarjeta;
  final double? efectivoTotal;
  final double? fondo;
  final double? recaudable;
  final double? diferenciaScore;
  final int? contadorEntradaActual;
  final int? contadorSalidaActual;
  final int? contadorEntradaPrev;
  final int? contadorSalidaPrev;
  final int? deltaEntrada;
  final int? deltaSalida;
  final double? montoEstimadoContadores;
  final String? causaIrregularidadId;
  final String? causaIrregularidadNombre;
  final String? notaIrregularidad;
  final String? eventoContadorId;
  final String? eventoContadorNombre;
  final String? notaEventoContador;
  final String? motivoOmisionId;
  final String? motivoOmisionNombre;
  final String? notaOmision;
  final String syncStatus;

  const CorteDetalle({
    required this.uuid,
    required this.corteId,
    required this.maquinaId,
    this.maquinaCodigo,
    required this.estadoMaquina,
    this.scoreTarjeta,
    this.efectivoTotal,
    this.fondo,
    this.recaudable,
    this.diferenciaScore,
    this.contadorEntradaActual,
    this.contadorSalidaActual,
    this.contadorEntradaPrev,
    this.contadorSalidaPrev,
    this.deltaEntrada,
    this.deltaSalida,
    this.montoEstimadoContadores,
    this.causaIrregularidadId,
    this.causaIrregularidadNombre,
    this.notaIrregularidad,
    this.eventoContadorId,
    this.eventoContadorNombre,
    this.notaEventoContador,
    this.motivoOmisionId,
    this.motivoOmisionNombre,
    this.notaOmision,
    this.syncStatus = 'synced',
  });

  bool get isCapturada => estadoMaquina == 'CAPTURADA';
  bool get isOmitida => estadoMaquina == 'OMITIDA';

  factory CorteDetalle.fromJson(Map<String, dynamic> json) => CorteDetalle(
        uuid: json['uuid'] as String,
        corteId: json['corte_id'] as String,
        maquinaId: json['maquina_id'] as String,
        maquinaCodigo: json['maquina_codigo'] as String?,
        estadoMaquina: json['estado_maquina'] as String,
        scoreTarjeta: (json['score_tarjeta'] as num?)?.toDouble(),
        efectivoTotal: (json['efectivo_total'] as num?)?.toDouble(),
        fondo: (json['fondo'] as num?)?.toDouble(),
        recaudable: (json['recaudable'] as num?)?.toDouble(),
        diferenciaScore: (json['diferencia_score'] as num?)?.toDouble(),
        contadorEntradaActual: json['contador_entrada_actual'] as int?,
        contadorSalidaActual: json['contador_salida_actual'] as int?,
        contadorEntradaPrev: json['contador_entrada_prev'] as int?,
        contadorSalidaPrev: json['contador_salida_prev'] as int?,
        deltaEntrada: json['delta_entrada'] as int?,
        deltaSalida: json['delta_salida'] as int?,
        montoEstimadoContadores:
            (json['monto_estimado_contadores'] as num?)?.toDouble(),
        causaIrregularidadId: json['causa_irregularidad_id'] as String?,
        causaIrregularidadNombre:
            json['causa_irregularidad_nombre'] as String?,
        notaIrregularidad: json['nota_irregularidad'] as String?,
        eventoContadorId: json['evento_contador_id'] as String?,
        eventoContadorNombre: json['evento_contador_nombre'] as String?,
        notaEventoContador: json['nota_evento_contador'] as String?,
        motivoOmisionId: json['motivo_omision_id'] as String?,
        motivoOmisionNombre: json['motivo_omision_nombre'] as String?,
        notaOmision: json['nota_omision'] as String?,
      );

  Map<String, dynamic> toDb() => {
        'uuid': uuid,
        'corte_id': corteId,
        'maquina_id': maquinaId,
        'estado_maquina': estadoMaquina,
        'score_tarjeta': scoreTarjeta,
        'efectivo_total': efectivoTotal,
        'fondo': fondo,
        'recaudable': recaudable,
        'diferencia_score': diferenciaScore,
        'contador_entrada_actual': contadorEntradaActual,
        'contador_salida_actual': contadorSalidaActual,
        'contador_entrada_prev': contadorEntradaPrev,
        'contador_salida_prev': contadorSalidaPrev,
        'delta_entrada': deltaEntrada,
        'delta_salida': deltaSalida,
        'monto_estimado_contadores': montoEstimadoContadores,
        'causa_irregularidad_id': causaIrregularidadId,
        'nota_irregularidad': notaIrregularidad,
        'evento_contador_id': eventoContadorId,
        'nota_evento_contador': notaEventoContador,
        'motivo_omision_id': motivoOmisionId,
        'nota_omision': notaOmision,
        'sync_status': syncStatus,
      };

  factory CorteDetalle.fromDb(Map<String, dynamic> row) => CorteDetalle(
        uuid: row['uuid'] as String,
        corteId: row['corte_id'] as String,
        maquinaId: row['maquina_id'] as String,
        estadoMaquina: row['estado_maquina'] as String,
        scoreTarjeta: (row['score_tarjeta'] as num?)?.toDouble(),
        efectivoTotal: (row['efectivo_total'] as num?)?.toDouble(),
        fondo: (row['fondo'] as num?)?.toDouble(),
        recaudable: (row['recaudable'] as num?)?.toDouble(),
        diferenciaScore: (row['diferencia_score'] as num?)?.toDouble(),
        contadorEntradaActual: row['contador_entrada_actual'] as int?,
        contadorSalidaActual: row['contador_salida_actual'] as int?,
        contadorEntradaPrev: row['contador_entrada_prev'] as int?,
        contadorSalidaPrev: row['contador_salida_prev'] as int?,
        deltaEntrada: row['delta_entrada'] as int?,
        deltaSalida: row['delta_salida'] as int?,
        montoEstimadoContadores:
            (row['monto_estimado_contadores'] as num?)?.toDouble(),
        causaIrregularidadId: row['causa_irregularidad_id'] as String?,
        notaIrregularidad: row['nota_irregularidad'] as String?,
        eventoContadorId: row['evento_contador_id'] as String?,
        notaEventoContador: row['nota_evento_contador'] as String?,
        motivoOmisionId: row['motivo_omision_id'] as String?,
        notaOmision: row['nota_omision'] as String?,
        syncStatus: row['sync_status'] as String? ?? 'synced',
      );
}
