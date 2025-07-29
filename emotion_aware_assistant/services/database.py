from emotion_aware_assistant.gloabal_import import *

DATABASE_URL = os.getenv("DATABASE_URL")  

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


