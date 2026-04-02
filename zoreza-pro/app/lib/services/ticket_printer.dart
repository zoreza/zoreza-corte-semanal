import 'dart:typed_data';

/// ESC/POS thermal printer service.
/// Generates raw byte commands for 58mm thermal printers.
class TicketPrinter {
  TicketPrinter._();

  // ESC/POS constants
  static const _esc = 0x1B;
  static const _gs = 0x1D;
  static const _lf = 0x0A;

  /// Build a complete ticket as raw bytes.
  static Uint8List buildCorteTicket({
    required String clienteNombre,
    required String weekStart,
    required String weekEnd,
    required List<TicketMaquina> maquinas,
    required double netoCliente,
    required double gananciaDueno,
    required double totalGastos,
    String? operador,
  }) {
    final buf = BytesBuilder();

    // Initialize printer
    buf.add([_esc, 0x40]); // ESC @ – reset

    // Center alignment
    buf.add([_esc, 0x61, 0x01]);

    // Bold on
    buf.add([_esc, 0x45, 0x01]);
    _addLine(buf, 'ZOREZA PRO');
    _addLine(buf, 'CORTE SEMANAL');
    // Bold off
    buf.add([_esc, 0x45, 0x00]);

    _addLine(buf, '================================');

    // Left alignment
    buf.add([_esc, 0x61, 0x00]);

    _addLine(buf, 'Cliente: $clienteNombre');
    _addLine(buf, 'Periodo: $weekStart');
    _addLine(buf, '     a: $weekEnd');
    if (operador != null) {
      _addLine(buf, 'Operador: $operador');
    }

    _addLine(buf, '--------------------------------');
    _addLine(buf, 'DETALLE POR MAQUINA');
    _addLine(buf, '--------------------------------');

    for (final m in maquinas) {
      _addLine(buf, m.nombre);
      if (m.omitida) {
        _addLine(buf, '  ** OMITIDA: ${m.motivoOmision ?? ""}');
      } else {
        _addLine(buf, '  Efectivo: \$${m.efectivo.toStringAsFixed(2)}');
        if (m.scoreTarjeta > 0) {
          _addLine(buf, '  Tarjeta:  \$${m.scoreTarjeta.toStringAsFixed(2)}');
        }
        _addLine(buf, '  Fondo:    \$${m.fondo.toStringAsFixed(2)}');
        _addLine(buf, '  Neto:     \$${m.neto.toStringAsFixed(2)}');
      }
    }

    _addLine(buf, '================================');

    // Bold totals
    buf.add([_esc, 0x45, 0x01]);
    _addPaddedLine(buf, 'NETO CLIENTE', '\$${netoCliente.toStringAsFixed(2)}');
    _addPaddedLine(buf, 'GANANCIA DUENO', '\$${gananciaDueno.toStringAsFixed(2)}');
    if (totalGastos > 0) {
      _addPaddedLine(buf, 'GASTOS', '\$${totalGastos.toStringAsFixed(2)}');
      final ganNeta = gananciaDueno - totalGastos;
      _addPaddedLine(buf, 'GANANCIA NETA', '\$${ganNeta.toStringAsFixed(2)}');
    }
    buf.add([_esc, 0x45, 0x00]);

    _addLine(buf, '================================');

    // Center
    buf.add([_esc, 0x61, 0x01]);
    _addLine(buf, 'Gracias por su preferencia');

    // Feed and cut
    buf.add([_lf, _lf, _lf, _lf]);
    buf.add([_gs, 0x56, 0x00]); // GS V 0 – full cut

    return buf.toBytes();
  }

  static void _addLine(BytesBuilder buf, String text) {
    buf.add(Uint8List.fromList(text.codeUnits));
    buf.addByte(_lf);
  }

  static void _addPaddedLine(BytesBuilder buf, String label, String value) {
    const total = 32; // 58mm ≈ 32 chars
    final pad = total - label.length - value.length;
    final spaces = pad > 0 ? ' ' * pad : ' ';
    _addLine(buf, '$label$spaces$value');
  }
}

class TicketMaquina {
  final String nombre;
  final double efectivo;
  final double scoreTarjeta;
  final double fondo;
  final double neto;
  final bool omitida;
  final String? motivoOmision;

  const TicketMaquina({
    required this.nombre,
    this.efectivo = 0,
    this.scoreTarjeta = 0,
    this.fondo = 0,
    this.neto = 0,
    this.omitida = false,
    this.motivoOmision,
  });
}
