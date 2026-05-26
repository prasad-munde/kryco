
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Structured connection details — completely safe from character bugs
db_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password="prasad",  
    host="localhost",
    port=5432,              # Fresh install default port
    database="mydb"         # The database you just created in pgAdmin
)

try:
    engine = create_engine(db_url)
    
    # Try connecting to see if everything works
    with engine.connect() as connection:
        print("🚀 Success! Clean connection established with PostgreSQL 18.")
        
except Exception as e:
    print("❌ Something went wrong:")
    print(e)