"""
Servicio de backup automático de la base de datos.
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from zoreza.services.exceptions import BackupError
from zoreza.db.core import db_path


def create_backup(backup_dir: str = "./backups") -> str:
    """
    Crea un backup de la base de datos.
    
    Args:
        backup_dir: Directorio donde guardar los backups
        
    Returns:
        Ruta del archivo de backup creado
        
    Raises:
        BackupError: Si hay error al crear el backup
    """
    try:
        # Crear directorio de backups si no existe
        backup_path = Path(backup_dir)
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Obtener ruta de la BD
        source_db = db_path()
        
        if not os.path.exists(source_db):
            raise BackupError(f"Base de datos no encontrada: {source_db}")
        
        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"zoreza_backup_{timestamp}.db"
        backup_file = backup_path / backup_filename
        
        # Copiar archivo
        shutil.copy2(source_db, backup_file)
        
        return str(backup_file)
        
    except Exception as e:
        raise BackupError(f"Error al crear backup: {str(e)}")


def restore_backup(backup_file: str) -> None:
    """
    Restaura la base de datos desde un backup.
    
    Args:
        backup_file: Ruta del archivo de backup
        
    Raises:
        BackupError: Si hay error al restaurar
    """
    try:
        if not os.path.exists(backup_file):
            raise BackupError(f"Archivo de backup no encontrado: {backup_file}")
        
        # Obtener ruta de la BD actual
        target_db = db_path()
        
        # Crear backup de la BD actual antes de restaurar
        if os.path.exists(target_db):
            pre_restore_backup = f"{target_db}.pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(target_db, pre_restore_backup)
        
        # Restaurar
        shutil.copy2(backup_file, target_db)
        
    except Exception as e:
        raise BackupError(f"Error al restaurar backup: {str(e)}")


def list_backups(backup_dir: str = "./backups") -> list[dict]:
    """
    Lista todos los backups disponibles.
    
    Args:
        backup_dir: Directorio de backups
        
    Returns:
        Lista de diccionarios con información de backups
    """
    try:
        backup_path = Path(backup_dir)
        
        if not backup_path.exists():
            return []
        
        backups = []
        for file in backup_path.glob("zoreza_backup_*.db"):
            stat = file.stat()
            backups.append({
                "filename": file.name,
                "path": str(file),
                "size_mb": stat.st_size / (1024 * 1024),
                "created": datetime.fromtimestamp(stat.st_ctime),
                "modified": datetime.fromtimestamp(stat.st_mtime)
            })
        
        # Ordenar por fecha de creación (más reciente primero)
        backups.sort(key=lambda x: x["created"], reverse=True)
        
        return backups
        
    except Exception as e:
        raise BackupError(f"Error al listar backups: {str(e)}")


def cleanup_old_backups(backup_dir: str = "./backups", keep_count: int = 10) -> int:
    """
    Elimina backups antiguos, manteniendo solo los más recientes.
    
    Args:
        backup_dir: Directorio de backups
        keep_count: Número de backups a mantener
        
    Returns:
        Número de backups eliminados
    """
    try:
        backups = list_backups(backup_dir)
        
        if len(backups) <= keep_count:
            return 0
        
        # Eliminar los más antiguos
        to_delete = backups[keep_count:]
        deleted = 0
        
        for backup in to_delete:
            try:
                os.remove(backup["path"])
                deleted += 1
            except Exception:
                pass  # Continuar con los demás
        
        return deleted
        
    except Exception as e:
        raise BackupError(f"Error al limpiar backups antiguos: {str(e)}")


def get_backup_info() -> dict:
    """
    Obtiene información sobre el estado de los backups.
    
    Returns:
        Diccionario con información de backups
    """
    try:
        backups = list_backups()
        
        total_size = sum(b["size_mb"] for b in backups)
        
        return {
            "count": len(backups),
            "total_size_mb": total_size,
            "latest": backups[0] if backups else None,
            "oldest": backups[-1] if backups else None
        }
        
    except Exception as e:
        raise BackupError(f"Error al obtener información de backups: {str(e)}")

# Made with Bob
