from sqlalchemy import create_engine
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from dotenv import load_dotenv
import os

load_dotenv()

#don't change this codes
#nothing much usefull here really just connecting to supabase 
app = FastAPI()
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Construct the SQLAlchemy connection string
DATABASE_URL = f"postgresql+psycopg2://postgres.aqhdcxmyugudovprznwi:yVNc3rnjFgh3PuKx@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require"


# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)
# If using Transaction Pooler or Session Pooler, we want to ensure we disable SQLAlchemy client side pooling -
# https://docs.sqlalchemy.org/en/20/core/pooling.html#switching-pool-implementations
# engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Test the connection
try:
    with engine.connect() as connection:
        print("Connection successful!")
except Exception as e:
    print(f"Failed to connect: {e}")
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with specific frontend origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
