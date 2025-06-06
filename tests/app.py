from question_pipeline.data.storage.database_manager import DataBaseManager

if __name__ == "__main__":
    db = DataBaseManager("test.db")

    db.initialize()
    print(db.get_migration_info())
    print(db.get_database_info())