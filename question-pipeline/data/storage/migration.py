import re
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional
import logging
import sqlite3

from ...utils.exceptions import (
    MigrationError,
    MigrationFileError,
    MigrationVersionError,
    ValidationError,
    SchemaError,
    DatabaseError,
    DatabaseConnectionError,
    MigrationRollbackError,
    MigrationSequenceError,
    MigrationDirectoryError,
    MigrationStateError,
    MigrationExecutionError,
    ConfigurationError,
    QueryError,
)

@dataclass
class Migration:
    """Represents a single database migration"""
    version: int
    name: str
    file_path: Path
    
    @classmethod
    def from_file(cls, file_path: Path) -> 'Migration':
        """Create Migration from filename like '001_initial.sql'"""
        try:
            # Validate file exists
            if not file_path.exists():
                raise MigrationFileError(
                    f"Migration file does not exist",
                    context={
                        'file_path': str(file_path),
                        'operation': 'from_file'
                    }
                )
            
            # Validate file is readable
            if not file_path.is_file():
                raise MigrationFileError(
                    f"Path is not a file",
                    context={
                        'file_path': str(file_path),
                        'path_type': 'directory' if file_path.is_dir() else 'other'
                    }
                )
            
            filename = file_path.stem
            
            # Validate filename format
            match = re.match(r'^(\d+)_(.+)$', filename)
            if not match:
                raise ValidationError(
                    f"Invalid migration filename format",
                    context={
                        'filename': filename,
                        'expected_format': 'NNN_description.sql',
                        'examples': ['001_initial.sql', '002_add_users.sql']
                    }
                )
            
            # Extract version and name
            try:
                version = int(match.group(1))
            except ValueError as e:
                raise ValidationError(
                    f"Invalid version number in migration filename",
                    context={
                        'filename': filename,
                        'version_string': match.group(1),
                        'error': str(e)
                    }
                ) from e
            
            name = match.group(2)
            
            # Validate version is positive
            if version <= 0:
                raise MigrationVersionError(
                    f"Migration version must be positive",
                    context={
                        'filename': filename,
                        'version': version
                    }
                )
            
            # Validate name is not empty
            if not name.strip():
                raise ValidationError(
                    f"Migration name cannot be empty",
                    context={
                        'filename': filename,
                        'version': version
                    }
                )
            
            # Validate file extension
            if file_path.suffix.lower() != '.sql':
                raise MigrationFileError(
                    f"Migration file must have .sql extension",
                    context={
                        'filename': filename,
                        'actual_extension': file_path.suffix,
                        'expected_extension': '.sql'
                    }
                )
            
            # Validate file is not empty
            try:
                if file_path.stat().st_size == 0:
                    raise MigrationFileError(
                        f"Migration file is empty",
                        context={
                            'filename': filename,
                            'file_path': str(file_path)
                        }
                    )
            except OSError as e:
                raise MigrationFileError(
                    f"Cannot read migration file",
                    context={
                        'filename': filename,
                        'file_path': str(file_path),
                        'os_error': str(e)
                    }
                ) from e
            
            # Validate SQL content (basic check)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    
                if not content:
                    raise MigrationFileError(
                        f"Migration file contains no SQL content",
                        context={
                            'filename': filename,
                            'file_path': str(file_path)
                        }
                    )
                    
                # Basic SQL validation (look for dangerous patterns)
                dangerous_patterns = ['DROP DATABASE', 'DROP SCHEMA', '--', '/*']
                for pattern in dangerous_patterns:
                    if pattern in content.upper():
                        logging.warning(f"Migration {filename} contains potentially dangerous SQL: {pattern}")
                        
            except UnicodeDecodeError as e:
                raise MigrationFileError(
                    f"Migration file encoding error",
                    context={
                        'filename': filename,
                        'file_path': str(file_path),
                        'encoding_error': str(e)
                    }
                ) from e
            except OSError as e:
                raise MigrationFileError(
                    f"Cannot read migration file content",
                    context={
                        'filename': filename,
                        'file_path': str(file_path),
                        'os_error': str(e)
                    }
                ) from e
           
            return cls(version=version, name=name, file_path=file_path)
            
        except (MigrationError, ValidationError):
            # Re-raise our custom errors
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise MigrationFileError(
                f"Unexpected error processing migration file",
                context={
                    'file_path': str(file_path),
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }
            ) from e

    def validate_content(self) -> bool:
        """Validate the SQL content of the migration file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for required SQL patterns
            content_upper = content.upper()
            
            # Migrations should typically have CREATE, ALTER, or INSERT statements
            sql_keywords = ['CREATE', 'ALTER', 'INSERT', 'UPDATE', 'DROP']
            if not any(keyword in content_upper for keyword in sql_keywords):
                raise SchemaError(
                    f"Migration does not contain expected SQL statements",
                    context={
                        'migration': f"{self.version}_{self.name}",
                        'file_path': str(self.file_path),
                        'expected_keywords': sql_keywords
                    }
                )
            
            # Check for transaction statements (migrations should be atomic)
            if 'BEGIN' in content_upper and 'COMMIT' not in content_upper:
                raise SchemaError(
                    f"Migration contains BEGIN without COMMIT",
                    context={
                        'migration': f"{self.version}_{self.name}",
                        'file_path': str(self.file_path)
                    }
                )
            
            return True
            
        except SchemaError:
            raise
        except Exception as e:
            raise MigrationFileError(
                f"Error validating migration content",
                context={
                    'migration': f"{self.version}_{self.name}",
                    'file_path': str(self.file_path),
                    'error': str(e)
                }
            ) from e
    
    def __post_init__(self):
        """Validate migration after creation."""
        # Additional validation after object creation
        if self.version < 1:
            raise MigrationVersionError(
                f"Migration version must be at least 1",
                context={
                    'version': self.version,
                    'name': self.name
                }
            )
        
        if len(self.name) > 100:  # Reasonable name length limit
            raise ValidationError(
                f"Migration name too long",
                context={
                    'name': self.name,
                    'length': len(self.name),
                    'max_length': 100
                }
            )
        
class MigrationRunner:
    """Handles database schema migrations with comprehensive error handling"""
    
    def __init__(self, storage):
        self.storage = storage
        self.migration_dir = storage.migration_dir
        self.logger = logging.getLogger(__name__)
        self._validate_initialization()
    
    def _validate_initialization(self):
        """Validate that migration runner is properly initialized."""
        try:
            if not self.storage:
                raise ConfigurationError(
                    "Storage instance is required for migration runner",
                    context={'storage': None}
                )
            
            if not hasattr(self.storage, 'connection'):
                raise ConfigurationError(
                    "Storage must have a connection attribute",
                    context={'storage_type': type(self.storage).__name__}
                )
            
            if not self.migration_dir:
                raise ConfigurationError(
                    "Migration directory path is required",
                    context={'migration_dir': None}
                )
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                "Failed to initialize migration runner",
                context={'error': str(e), 'error_type': type(e).__name__}
            ) from e
    
    def _validate_migration_directory(self):
        """Validate migration directory exists and is accessible."""
        try:
            if not self.migration_dir.exists():
                raise MigrationDirectoryError(
                    "Migration directory does not exist",
                    context={
                        'migration_dir': str(self.migration_dir),
                        'parent_exists': self.migration_dir.parent.exists()
                    }
                )
            
            if not self.migration_dir.is_dir():
                raise MigrationDirectoryError(
                    "Migration path is not a directory",
                    context={
                        'migration_dir': str(self.migration_dir),
                        'path_type': 'file' if self.migration_dir.is_file() else 'other'
                    }
                )
            
            # Check if directory is readable
            try:
                list(self.migration_dir.iterdir())
            except PermissionError as e:
                raise MigrationDirectoryError(
                    "Cannot read migration directory - permission denied",
                    context={
                        'migration_dir': str(self.migration_dir),
                        'permission_error': str(e)
                    }
                ) from e
                
        except MigrationDirectoryError:
            raise
        except Exception as e:
            raise MigrationDirectoryError(
                "Unexpected error accessing migration directory",
                context={
                    'migration_dir': str(self.migration_dir),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def ensure_migration_table(self):
        """Create migrations tracking table if it doesn't exist"""
        try:
            if not self.storage.connection:
                raise DatabaseConnectionError(
                    "No database connection available for migration table creation",
                    context={'operation': 'ensure_migration_table'}
                )
            
            query = """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT
            )
            """
            
            self.storage.execute_query(query)
            self.storage.connection.commit()
            
            self.logger.debug("Migration tracking table ensured")
            
        except sqlite3.OperationalError as e:
            raise QueryError(
                "Failed to create migration tracking table",
                context={
                    'sqlite_error': str(e),
                    'operation': 'create_migration_table'
                }
            ) from e
        except Exception as e:
            raise DatabaseError(
                "Unexpected error creating migration tracking table",
                context={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def get_current_version(self) -> int:
        """Get the highest applied migration version"""
        try:
            self.ensure_migration_table()
            
            result = self.storage.fetch_one(
                "SELECT MAX(version) as version FROM schema_migrations"
            )
            
            current_version = result['version'] if result['version'] is not None else 0
            
            self.logger.debug(f"Current migration version: {current_version}")
            
            return current_version
            
        except (QueryError, DatabaseError):
            # Re-raise database errors
            raise
        except Exception as e:
            raise DatabaseError(
                "Failed to get current migration version",
                context={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def get_applied_migrations(self) -> List[int]:
        """Get list of all applied migration versions"""
        try:
            self.ensure_migration_table()
            
            results = self.storage.fetch_all(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
            
            versions = [row['version'] for row in results]
            
            self.logger.debug(f"Applied migrations: {versions}")
            
            return versions
            
        except (QueryError, DatabaseError):
            raise
        except Exception as e:
            raise DatabaseError(
                "Failed to get applied migrations list",
                context={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def scan_migration_files(self) -> List[Migration]:
        """Scan migration directory for migration files"""
        try:
            self._validate_migration_directory()
            
            migrations = []
            migration_files = list(self.migration_dir.glob("*.sql"))
            
            if not migration_files:
                self.logger.warning(f"No migration files found in {self.migration_dir}")
                return []
            
            # Track versions to detect duplicates
            seen_versions: set[int] = set()
            
            for file_path in migration_files:
                try:
                    migration = Migration.from_file(file_path)
                    
                    # Check for duplicate versions
                    if migration.version in seen_versions:
                        raise MigrationVersionError(
                            f"Duplicate migration version found",
                            context={
                                'version': migration.version,
                                'file_path': str(file_path),
                                'migration_dir': str(self.migration_dir)
                            }
                        )
                    
                    seen_versions.add(migration.version)
                    migrations.append(migration)
                    
                except (MigrationFileError, ValidationError, MigrationVersionError) as e:
                    # Add file context to existing error
                    e.context.update({
                        'migration_dir': str(self.migration_dir),
                        'scanning_operation': True
                    })
                    self.logger.warning(f"Skipping invalid migration file {file_path}: {e.message}")
                    # Don't raise here - continue scanning other files
                    continue
            
            # Sort by version number
            migrations.sort(key=lambda m: m.version)
            
            # Validate sequence continuity
            self._validate_migration_sequence(migrations)
            
            self.logger.info(f"Found {len(migrations)} valid migration files")
            
            return migrations
            
        except MigrationDirectoryError:
            raise
        except (MigrationVersionError, MigrationSequenceError):
            raise
        except Exception as e:
            raise MigrationDirectoryError(
                "Unexpected error scanning migration files",
                context={
                    'migration_dir': str(self.migration_dir),
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def _validate_migration_sequence(self, migrations: List[Migration]):
        """Validate that migration versions form a proper sequence."""
        if not migrations:
            return
        
        versions = [m.version for m in migrations]
        
        # Check for gaps in sequence (optional - some teams allow gaps)
        if len(set(versions)) != len(versions):
            # This should have been caught in scan_migration_files, but double-check
            duplicates = [v for v in versions if versions.count(v) > 1]
            raise MigrationVersionError(
                "Duplicate migration versions detected",
                context={
                    'duplicate_versions': list(set(duplicates)),
                    'all_versions': versions
                }
            )
        
        # Check for reasonable version numbers (no massive jumps)
        sorted_versions = sorted(versions)
        for i in range(1, len(sorted_versions)):
            gap = sorted_versions[i] - sorted_versions[i-1]
            if gap > 100:  # Configurable threshold
                self.logger.warning(
                    f"Large gap in migration versions: {sorted_versions[i-1]} -> {sorted_versions[i]}"
                )
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get migrations that haven't been applied yet"""
        try:
            applied_versions = set(self.get_applied_migrations())
            all_migrations = self.scan_migration_files()
            
            pending = [m for m in all_migrations if m.version not in applied_versions]
            
            self.logger.info(f"Found {len(pending)} pending migrations")
            
            return pending
            
        except (DatabaseError, MigrationDirectoryError, MigrationVersionError):
            raise
        except Exception as e:
            raise MigrationError(
                "Failed to determine pending migrations",
                context={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def _validate_migration_state(self, migration: Migration):
        """Validate migration state before applying."""
        try:
            # Check if migration was already applied
            applied_versions = self.get_applied_migrations()
            if migration.version in applied_versions:
                raise MigrationStateError(
                    f"Migration {migration.version} is already applied",
                    context={
                        'migration_version': migration.version,
                        'migration_name': migration.name,
                        'applied_versions': applied_versions
                    }
                )
            
            # Check for missing prerequisite migrations
            current_version = self.get_current_version()
            if migration.version != current_version + 1:
                # Allow non-sequential if explicitly configured
                missing_versions = []
                for v in range(current_version + 1, migration.version):
                    if v not in applied_versions:
                        missing_versions.append(v)
                
                if missing_versions:
                    raise MigrationSequenceError(
                        f"Cannot apply migration {migration.version} - missing prerequisite migrations",
                        context={
                            'migration_version': migration.version,
                            'current_version': current_version,
                            'missing_versions': missing_versions
                        }
                    )
            
            # Validate file still exists and is readable
            if not migration.file_path.exists():
                raise MigrationFileError(
                    f"Migration file no longer exists",
                    context={
                        'migration_version': migration.version,
                        'file_path': str(migration.file_path)
                    }
                )
                
        except (MigrationStateError, MigrationSequenceError, MigrationFileError):
            raise
        except Exception as e:
            raise MigrationError(
                "Failed to validate migration state",
                context={
                    'migration_version': migration.version,
                    'error': str(e)
                }
            ) from e
    
    def apply_migration(self, migration: Migration):
        """Apply a single migration with comprehensive error handling"""
        self.logger.info(f"Applying migration {migration.version}: {migration.name}")
        
        try:
            # Pre-flight validation
            self._validate_migration_state(migration)
            
            # Read migration file
            try:
                with open(migration.file_path, 'r', encoding='utf-8') as f:
                    sql_content = f.read().strip()
            except UnicodeDecodeError as e:
                raise MigrationFileError(
                    f"Migration file encoding error",
                    context={
                        'migration_version': migration.version,
                        'file_path': str(migration.file_path),
                        'encoding_error': str(e)
                    }
                ) from e
            except OSError as e:
                raise MigrationFileError(
                    f"Cannot read migration file",
                    context={
                        'migration_version': migration.version,
                        'file_path': str(migration.file_path),
                        'os_error': str(e)
                    }
                ) from e
            
            if not sql_content:
                raise MigrationFileError(
                    f"Migration file is empty",
                    context={
                        'migration_version': migration.version,
                        'file_path': str(migration.file_path)
                    }
                )
            
            # Execute migration in a transaction
            try:
                self.storage.connection.execute("BEGIN")
                
                # Execute the migration SQL
                self.storage.execute_script(sql_content)
                
                # Record that migration was applied
                self.storage.execute_query(
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                    (migration.version, migration.name)
                )
                
                # Commit transaction
                self.storage.connection.commit()
                
                self.logger.info(f"Migration {migration.version} applied successfully")
                
            except sqlite3.OperationalError as e:
                # Rollback on SQL error
                try:
                    self.storage.connection.rollback()
                except:
                    pass  # Rollback might fail if connection is broken
                
                raise MigrationExecutionError(
                    f"SQL error during migration {migration.version}",
                    context={
                        'migration_version': migration.version,
                        'migration_name': migration.name,
                        'sql_error': str(e),
                        'file_path': str(migration.file_path)
                    }
                ) from e
                
            except sqlite3.IntegrityError as e:
                try:
                    self.storage.connection.rollback()
                except:
                    pass
                
                raise MigrationExecutionError(
                    f"Data integrity error during migration {migration.version}",
                    context={
                        'migration_version': migration.version,
                        'migration_name': migration.name,
                        'integrity_error': str(e),
                        'file_path': str(migration.file_path)
                    }
                ) from e
                
            except Exception as e:
                try:
                    self.storage.connection.rollback()
                except:
                    pass
                
                raise MigrationExecutionError(
                    f"Unexpected error during migration {migration.version}",
                    context={
                        'migration_version': migration.version,
                        'migration_name': migration.name,
                        'error': str(e),
                        'error_type': type(e).__name__,
                        'file_path': str(migration.file_path)
                    }
                ) from e
            
        except (MigrationFileError, MigrationStateError, MigrationSequenceError, MigrationExecutionError):
            # Re-raise migration-specific errors
            raise
        except Exception as e:
            # Catch any other unexpected errors
            raise MigrationError(
                f"Failed to apply migration {migration.version}",
                context={
                    'migration_version': migration.version,
                    'migration_name': migration.name,
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def migrate_to_latest(self):
        """Apply all pending migrations"""
        try:
            pending = self.get_pending_migrations()
            
            if not pending:
                self.logger.info("Database is up to date")
                return
            
            self.logger.info(f"Applying {len(pending)} pending migrations")
            
            for migration in pending:
                try:
                    self.apply_migration(migration)
                except MigrationExecutionError as e:
                    # Add context about batch operation
                    e.context.update({
                        'batch_operation': True,
                        'total_pending': len(pending),
                        'failed_at_migration': migration.version
                    })
                    raise
            
            self.logger.info("All migrations applied successfully")
            
        except (MigrationError, DatabaseError):
            raise
        except Exception as e:
            raise MigrationError(
                "Failed to migrate to latest version",
                context={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            ) from e
    
    def migrate_to_version(self, target_version: int):
        """Migrate to a specific version"""
        try:
            if target_version < 0:
                raise ValidationError(
                    "Target version cannot be negative",
                    context={'target_version': target_version}
                )
            
            current_version = self.get_current_version()
            
            if target_version == current_version:
                self.logger.info(f"Already at version {target_version}")
                return
            
            if target_version < current_version:
                raise MigrationRollbackError(
                    "Downgrade migrations not implemented",
                    context={
                        'current_version': current_version,
                        'target_version': target_version
                    }
                )
            
            all_migrations = self.scan_migration_files()
            migrations_to_apply = [
                m for m in all_migrations 
                if current_version < m.version <= target_version
            ]
            
            if not migrations_to_apply:
                raise MigrationSequenceError(
                    f"No migrations found between version {current_version} and {target_version}",
                    context={
                        'current_version': current_version,
                        'target_version': target_version,
                        'available_versions': [m.version for m in all_migrations]
                    }
                )
            
            # Check if target version exists
            target_exists = any(m.version == target_version for m in all_migrations)
            if not target_exists:
                raise MigrationVersionError(
                    f"Target version {target_version} not found",
                    context={
                        'target_version': target_version,
                        'available_versions': [m.version for m in all_migrations]
                    }
                )
            
            self.logger.info(f"Migrating from version {current_version} to {target_version}")
            
            for migration in migrations_to_apply:
                self.apply_migration(migration)
                
        except (ValidationError, MigrationError, DatabaseError):
            raise
        except Exception as e:
            raise MigrationError(
                f"Failed to migrate to version {target_version}",
                context={
                    'target_version': target_version,
                    'current_version': current_version,
                    'error': str(e)
                }
            ) from e