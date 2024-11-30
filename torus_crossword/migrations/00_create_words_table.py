from sqlalchemy import inspect
from schema import Base, engine, Word


def table_exists(engine, table_name):
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def main():
    table_name = Word.__tablename__

    # Check if the table already exists
    if table_exists(engine, table_name):
        print(f"Table '{table_name}' already exists. Exiting...")
        return

    # Create the table
    Base.metadata.create_all(engine)
    print(f"Table '{table_name}' created successfully.")


if __name__ == "__main__":
    main()
