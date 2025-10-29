"""
Database Router para modo SOLO LECTURA
"""

class ReadOnlyRouter:
    """
    Router que permite solo operaciones de lectura.
    """
    
    def db_for_read(self, model, **hints):
        """Permite todas las operaciones de lectura"""
        return 'default'
    
    def db_for_write(self, model, **hints):
        """BLOQUEA todas las operaciones de escritura"""
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Permite relaciones entre objetos"""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """BLOQUEA todas las migraciones"""
        return False