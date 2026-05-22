from app.db.session import engine, Base
import app.db.base  # noqa: F401

def init_db() -> None:
    """
    Create all tables in the database.
    Useful for development or testing database setups.
    """
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Creating database tables...")
    init_db()
    print("Database tables created successfully!")
