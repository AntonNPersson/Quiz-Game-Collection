from question_pipeline.data.storage.sqlite_storage import SQLiteStorage
from question_pipeline.data.storage.migration import MigrationRunner
from typing import Dict, Any
import logging

class DataBaseManager:
    def __init__(self, db_path: str):
        self.storage = SQLiteStorage(db_path)
        self.migration_runner = MigrationRunner(self.storage)
        self.logger = logging.getLogger(__name__)

    def initialize(self):
        """Initialize the database and run migrations if necessary."""
        self.logger.info("Inititalizing database...")

        self.storage.connect()

        if self.is_fresh():
            self.logger.info("Fresh database detected. Creating from schema...")
            self.create_from_schema()
        else:
            self.logger.info("Existing database detected. Running migrations...")
            self.migrate_to_latest()

    def is_fresh(self) -> bool:
        """Check if the database is fresh (i.e., no tables exist)."""
        try:
            result = self.storage.fetch_one("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
            return result is None
        except:
            return True
        
    def create_from_schema(self):
        """Create the database schema from the initial schema file."""
        self.logger.info("Creating fresh database from schema")

        schema_files = self.storage.schema_dir.glob("*.sql")

        for schema_file in schema_files:
            self.logger.info(f"Executing schema file: {schema_file.name}")
            with open(schema_file, 'r') as file:
                sql_script = file.read()

            self.storage.execute_script(sql_script)

        migrations = self.migration_runner.scan_migration_files()
        if migrations:
            self.logger.info(f"Found {len(migrations)} migration files to run.")
            self.migration_runner.ensure_migration_table()

            for migration in migrations:
                self.storage.execute_script(f"INSERT INTO schema_migrations (version, name) VALUES ('{migration.version}', '{migration.name}')")

            self.storage.connection.commit()
        
        self.logger.info("Database schema created successfully.")

    def migrate_to_latest(self):
        """Run migrations to bring the database schema up to date."""
        self.logger.info("Updating database to latest version")
        self.migration_runner.migrate_to_latest()

    def get_migration_info(self) -> Dict[str, Any]:
        """Get database status information"""
        current_version = self.migration_runner.get_current_version()
        pending_migrations = self.migration_runner.get_pending_migrations()
        
        return {
            'current_version': current_version,
            'pending_migrations': len(pending_migrations),
            'database_file': str(self.storage.db_path),
            'database_exists': self.storage.db_path.exists()
        }
    
    def get_database_info(self) ->Dict[str, Any]:
        """Get database information."""
        info = {
            'database_file': str(self.storage.db_path),
            'database_exists': self.storage.db_path.exists(),
            'tables': [],
            'columns': {}
        }
        tables = self.storage.get_tables()
        info['tables'] = [table for table in tables]
        info['columns'] = {table : self.storage.get_table_columns(table) for table in tables}
        return info
        