from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mssql+pyodbc://@localhost,1433/Consultorio?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes&Encrypt=yes&TrustServerCertificate=yes"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e