import sqlite3
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging
import threading

from question_pipeline.utils.exceptions import (
    DatabaseError,
    QueryError,
    IntegrityError,
    ValidationError
)

class SQLiteStorage:
    """Base class for NoSQL storage systems."""

    def __init__(self, db_path: str):
        """Initializes the SQLite storage with the given database path."""
        self.db_path = Path(db_path)
        self.migration_dir = Path(__file__).parent / "migrations"
        self.schema_dir = Path(__file__).parent / "schemas"
        self.logger = logging.getLogger(__name__)
        self._thread_local = threading.local()

    def connect(self):
        """Connect to the SQLite database (thread-safe)."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create thread-local connection
            connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False  # Allow cross-thread usage
            )
            connection.row_factory = sqlite3.Row
            
            # Enable foreign key constraints
            connection.execute("PRAGMA foreign_keys = ON")
            
            # Store in thread-local storage
            self._thread_local.connection = connection
            
            self.logger.info(f"Connected to SQLite database at {self.db_path}")
            
            return connection
            
        except sqlite3.OperationalError as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise ConnectionError(
                f"Cannot connect to database at {self.db_path}",
                context={'db_path': str(self.db_path), 'sqlite_error': str(e)}
            ) from e
            
        except Exception as e:
            self.logger.error(f"Unexpected error connecting to database: {e}")
            raise ConnectionError(
                f"Unexpected database connection error",
                context={'db_path': str(self.db_path), 'error_type': type(e).__name__}
            ) from e
    
    def close(self):
        """Close the SQLite database connection (thread-safe)."""
        try:
            connection = getattr(self._thread_local, 'connection', None)
            if connection:
                connection.close()
                self._thread_local.connection = None
                self.logger.info(f"Closed SQLite database connection")
                
        except Exception as e:
            self.logger.warning(f"Error closing database connection: {e}")
            # Don't raise here - closing should be fail-safe

    @property
    def connection(self):
        """Get the thread-local database connection."""
        return getattr(self._thread_local, 'connection', None)

    def execute_query(self, query: str, params: tuple = None) -> sqlite3.Cursor:
        """Execute a query on the SQLite database."""
        try:
            self._ensure_connection()
            
            cursor = self.connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            return cursor
            
        except sqlite3.OperationalError as e:
            self.logger.error(f"SQL operational error: {e}")
            raise QueryError(
                f"Failed to execute query",
                context={
                    'query': query,
                    'params': params,
                    'sqlite_error': str(e)
                }
            ) from e
            
        except sqlite3.DatabaseError as e:
            self.logger.error(f"Database error executing query: {e}")
            raise QueryError(
                f"Database error during query execution",
                context={
                    'query': query,
                    'params': params,
                    'sqlite_error': str(e)
                }
            ) from e

    def execute_script(self, script: str):
        """Execute a script on the SQLite database."""
        try:
            self._ensure_connection()
            
            cursor = self.connection.cursor()
            cursor.executescript(script)
            self.connection.commit()
            
            self.logger.debug("Script executed successfully")
            
        except sqlite3.OperationalError as e:
            self.logger.error(f"Error executing script: {e}")
            raise QueryError(
                f"Failed to execute SQL script",
                context={'script_length': len(script), 'sqlite_error': str(e)}
            ) from e

    def fetch_one(self, query: str, params: tuple = None) -> Optional[sqlite3.Row]:
        """Fetch one record from the database."""
        try:
            cursor = self.execute_query(query, params)
            result = cursor.fetchone()
            
            self.logger.debug(f"Fetched one record: {'found' if result else 'not found'}")
            
            return result
            
        except QueryError:
            # Re-raise QueryError from execute_query
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching record: {e}")
            raise DatabaseError(
                "Unexpected error fetching record",
                context={'query': query, 'params': params}
            ) from e
    
    def fetch_all(self, query: str, params: tuple = None) -> List[sqlite3.Row]:
        """Fetch all records from the database."""
        try:
            cursor = self.execute_query(query, params)
            results = cursor.fetchall()
            
            self.logger.debug(f"Fetched {len(results)} records")
            
            return results
            
        except QueryError:
            # Re-raise QueryError from execute_query
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching records: {e}")
            raise DatabaseError(
                "Unexpected error fetching records",
                context={'query': query, 'params': params}
            ) from e
    
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record into the specified table."""
        try:
            # Validation
            self._validate_table_name(table)
            self._validate_insert_data(table, data)
            self._ensure_connection()

            # Build query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            self.logger.debug(f"Inserting into {table}", extra={
                'table': table,
                'columns': list(data.keys()),
                'query': query
            })

            # Execute insert
            cursor = self.execute_query(query, tuple(data.values()))
            self.connection.commit()

            inserted_id = cursor.lastrowid
            
            self.logger.info(f"Successfully inserted record", extra={
                'table': table,
                'inserted_id': inserted_id,
                'operation': 'insert'
            })
            
            return inserted_id
            
        except ValidationError:
            # Re-raise validation errors
            raise
            
        except sqlite3.IntegrityError as e:
            self.logger.error(f"Integrity constraint violation", extra={
                'table': table,
                'data': data,
                'sqlite_error': str(e)
            })
            
            # Convert to friendly error message
            friendly_msg = self._get_friendly_integrity_error(str(e))
            
            raise IntegrityError(
                f"Cannot insert into {table}: {friendly_msg}",
                context={
                    'table': table,
                    'data': data,
                    'constraint_type': self._get_constraint_type(str(e)),
                    'sqlite_error': str(e)
                }
            ) from e
            
        except sqlite3.OperationalError as e:
            self.logger.error(f"Operational error during insert", extra={
                'table': table,
                'query': query,
                'sqlite_error': str(e)
            })
            
            raise QueryError(
                f"Insert operation failed for table {table}",
                context={
                    'table': table,
                    'query': query,
                    'data': data,
                    'sqlite_error': str(e)
                }
            ) from e
            
        except Exception as e:
            self.logger.error(f"Unexpected error during insert", extra={
                'table': table,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            
            raise DatabaseError(
                f"Unexpected error inserting into {table}",
                context={
                    'table': table,
                    'data': data,
                    'error_type': type(e).__name__
                }
            ) from e
    
    def bulk_insert(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """Insert multiple records into the specified table."""
        try:
            # Validation
            self._validate_table_name(table)
            
            if not data_list:
                self.logger.debug(f"Skipping bulk insert: empty data list")
                return 0
            
            if not isinstance(data_list, list):
                raise ValidationError(
                    "Bulk insert data must be a list",
                    context={'table': table, 'data_type': type(data_list).__name__}
                )
            
            # Validate each record and ensure consistent structure
            first_record_cols = set(data_list[0].keys())
            for i, record in enumerate(data_list):
                self._validate_insert_data(table, record)
                
                if set(record.keys()) != first_record_cols:
                    raise ValidationError(
                        f"Record {i} has different columns than first record",
                        context={
                            'table': table,
                            'record_index': i,
                            'expected_columns': list(first_record_cols),
                            'actual_columns': list(record.keys())
                        }
                    )
            
            self._ensure_connection()
            
            # Build query
            columns = list(data_list[0].keys())
            placeholders = ', '.join(['?' for _ in columns])
            column_names = ', '.join(columns)
            query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
            
            # Convert to tuple format
            values = [tuple(record[col] for col in columns) for record in data_list]
            
            self.logger.debug(f"Bulk inserting {len(data_list)} records into {table}")
            
            # Execute bulk insert
            cursor = self.connection.cursor()
            cursor.executemany(query, values)
            self.connection.commit()
            
            rows_affected = cursor.rowcount
            
            self.logger.info(f"Successfully bulk inserted records", extra={
                'table': table,
                'records_inserted': rows_affected,
                'operation': 'bulk_insert'
            })
            
            return rows_affected
            
        except ValidationError:
            # Re-raise validation errors
            raise
            
        except sqlite3.IntegrityError as e:
            self.connection.rollback()
            self.logger.error(f"Integrity constraint violation during bulk insert", extra={
                'table': table,
                'record_count': len(data_list),
                'sqlite_error': str(e)
            })
            
            friendly_msg = self._get_friendly_integrity_error(str(e))
            
            raise IntegrityError(
                f"Bulk insert into {table} failed: {friendly_msg}",
                context={
                    'table': table,
                    'record_count': len(data_list),
                    'constraint_type': self._get_constraint_type(str(e)),
                    'sqlite_error': str(e)
                }
            ) from e
            
        except sqlite3.OperationalError as e:
            self.connection.rollback()
            self.logger.error(f"Operational error during bulk insert", extra={
                'table': table,
                'query': query,
                'sqlite_error': str(e)
            })
            
            raise QueryError(
                f"Bulk insert operation failed for table {table}",
                context={
                    'table': table,
                    'query': query,
                    'record_count': len(data_list),
                    'sqlite_error': str(e)
                }
            ) from e
            
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Unexpected error during bulk insert", extra={
                'table': table,
                'error_type': type(e).__name__,
                'error_message': str(e)
            })
            
            raise DatabaseError(
                f"Unexpected error during bulk insert into {table}",
                context={
                    'table': table,
                    'record_count': len(data_list),
                    'error_type': type(e).__name__
                }
            ) from e
        
    def get_table_columns(self, table: str) -> List[str]:
        """Get the column names for a given table."""
        try:
            self._ensure_connection()
            self._validate_table_name(table)
            
            query = f"PRAGMA table_info({table})"
            cursor = self.execute_query(query)
            columns = [row['name'] for row in cursor.fetchall()]
            
            self.logger.debug(f"Columns in {table}: {columns}")
            
            return columns
            
        except sqlite3.OperationalError as e:
            self.logger.error(f"Error fetching columns for {table}", extra={
                'table': table,
                'sqlite_error': str(e)
            })
            raise QueryError(
                f"Failed to fetch columns for table {table}",
                context={'table': table, 'sqlite_error': str(e)}
            ) from e
        
    def get_tables(self) -> List[str]:
        """Get a list of all tables in the database."""
        try:
            self._ensure_connection()
            
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            cursor = self.execute_query(query)
            tables = [row['name'] for row in cursor.fetchall()]
            
            self.logger.debug(f"Tables in database: {tables}")
            
            return tables
            
        except sqlite3.OperationalError as e:
            self.logger.error(f"Error fetching tables", extra={
                'sqlite_error': str(e)
            })
            raise QueryError(
                "Failed to fetch tables from database",
                context={'sqlite_error': str(e)}
            ) from e
        
    def _validate_insert_data(self, table: str, data: Dict[str, Any]):
        """Validate data before insert."""
        if not data:
            raise ValidationError(
                "Cannot insert empty data",
                context={'table': table}
            )
        
        if not isinstance(data, dict):
            raise ValidationError(
                "Insert data must be a dictionary",
                context={'table': table, 'data_type': type(data).__name__}
            )
        
        # Check for None keys
        if None in data.keys():
            raise ValidationError(
                "Column names cannot be None",
                context={'table': table, 'data': data}
            )
        
        # Check for empty column names
        empty_cols = [k for k in data.keys() if not str(k).strip()]
        if empty_cols:
            raise ValidationError(
                "Column names cannot be empty",
                context={'table': table, 'empty_columns': empty_cols}
            )
        
    def _validate_table_name(self, table: str):
        """Validate table name for security."""
        if not table or not table.strip():
            raise ValidationError("Table name cannot be empty")
        
        # Basic SQL injection protection
        if any(char in table for char in [';', '--', '/*', '*/', 'DROP', 'DELETE']):
            raise ValidationError(
                "Invalid table name - contains potentially dangerous characters",
                context={'table': table}
            )
        
    def _get_friendly_integrity_error(self, error_msg: str) -> str:
        """Convert SQLite integrity errors to user-friendly messages."""
        error_lower = error_msg.lower()
        
        if 'unique constraint failed' in error_lower:
            return "A record with this data already exists"
        elif 'foreign key constraint failed' in error_lower:
            return "Referenced record does not exist"
        elif 'not null constraint failed' in error_lower:
            return "Required field is missing"
        elif 'check constraint failed' in error_lower:
            return "Data validation rule violated"
        else:
            return "Data constraint violation"
        
    def _get_constraint_type(self, error_msg: str) -> str:
        """Extract constraint type from error message."""
        error_lower = error_msg.lower()
        
        if 'unique' in error_lower:
            return 'unique'
        elif 'foreign key' in error_lower:
            return 'foreign_key'
        elif 'not null' in error_lower:
            return 'not_null'
        elif 'check' in error_lower:
            return 'check'
        else:
            return 'unknown'

    def _ensure_connection(self):
        """Ensure database connection exists."""
        if not self.connection:
            self.logger.debug("No database connection, attempting to connect...")
            self.connect()
