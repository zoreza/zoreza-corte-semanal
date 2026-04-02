/// Catalog item (irregularidad, omisión, evento_contador).
class CatalogItem {
  final String uuid;
  final String nombre;
  final bool requiereNota;
  final bool activo;

  const CatalogItem({
    required this.uuid,
    required this.nombre,
    required this.requiereNota,
    required this.activo,
  });

  factory CatalogItem.fromJson(Map<String, dynamic> json) => CatalogItem(
        uuid: json['uuid'] as String,
        nombre: json['nombre'] as String,
        requiereNota: json['requiere_nota'] as bool,
        activo: json['activo'] as bool,
      );

  Map<String, dynamic> toDb(String catalogType) => {
        'uuid': uuid,
        'catalog_type': catalogType,
        'nombre': nombre,
        'requiere_nota': requiereNota ? 1 : 0,
        'activo': activo ? 1 : 0,
        'sync_status': 'synced',
      };

  factory CatalogItem.fromDb(Map<String, dynamic> row) => CatalogItem(
        uuid: row['uuid'] as String,
        nombre: row['nombre'] as String,
        requiereNota: (row['requiere_nota'] as int) == 1,
        activo: (row['activo'] as int) == 1,
      );
}
