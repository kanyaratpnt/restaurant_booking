import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึงค่าออกมาใช้
# user = os.getenv("DB_USER")
# password = os.getenv("DB_PASSWORD")
# host = os.getenv("DB_HOST")
# db_name = os.getenv("DB_NAME")

# รวมร่างเป็น URL
# SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}/{db_name}"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:beam123@192.168.1.41:3307/restaurant_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()