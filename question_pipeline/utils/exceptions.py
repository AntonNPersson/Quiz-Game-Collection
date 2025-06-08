class QuestionPipelineError(Exception):
    """Base class for all exceptions in the question pipeline."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context if context is not None else {}
        self.message = message
    
    def __str__(self):
        """String representation with context if available."""
        if self.context:
            return f"{self.message} (Context: {self.context})"
        return self.message
    
    def __repr__(self):
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}('{self.message}', context={self.context})"


# Database-related errors
class DatabaseError(QuestionPipelineError):
    """Exception raised for database-related errors."""
    pass


class DatabaseConnectionError(QuestionPipelineError):
    """Exception raised for database connection errors."""
    pass


class QueryError(QuestionPipelineError):
    """Exception raised for SQL query execution errors."""
    pass


class IntegrityError(QuestionPipelineError):
    """Exception raised for database constraint violations."""
    pass


class MigrationError(QuestionPipelineError):
    """Exception raised for database migration errors."""
    pass


# Data processing errors
class ValidationError(QuestionPipelineError):
    """Exception raised for data validation errors."""
    pass


class SchemaError(QuestionPipelineError):
    """Exception raised for schema-related errors."""
    pass


class ParsingError(QuestionPipelineError):
    """Exception raised for data parsing errors."""
    pass


class LoaderError(QuestionPipelineError):
    """Exception raised for data loading errors."""
    pass


class TransformerError(QuestionPipelineError):
    """Exception raised for data transformation errors."""
    pass


# Configuration errors
class ConfigurationError(QuestionPipelineError):
    """Exception raised for configuration-related errors."""
    pass


class PluginError(QuestionPipelineError):
    """Exception raised for plugin-related errors."""
    pass


class RegistryError(QuestionPipelineError):
    """Exception raised for plugin registry errors."""
    pass

# Migration-related errors
class MigrationFileError(MigrationError):
    """Exception raised for errors related to migration files."""
    pass

class MigrationVersionError(MigrationError):
    """Exception raised for errors related to migration versioning."""
    pass

class MigrationSequenceError(MigrationError):
    """Exception raised for errors related to migration sequence."""
    pass

class MigrationRollbackError(MigrationError):
    """Exception raised for errors during migration rollback."""
    pass

class MigrationDirectoryError(MigrationError):
    """Exception raised for errors related to migration directory."""
    pass

class MigrationStateError(MigrationError):
    """Exception raised for errors related to migration state."""
    pass

class MigrationExecutionError(MigrationError):
    """Exception raised for errors during migration execution."""
    pass


# Game engine errors
class GameEngineError(QuestionPipelineError):
    """Exception raised for game engine-related errors."""
    pass
