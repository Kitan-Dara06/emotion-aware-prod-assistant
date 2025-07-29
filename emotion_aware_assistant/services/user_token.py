from emotion_aware_assistant.services.database import Base

class UserToken(Base):
    __tablename__ = "user_tokens"

    email = Column(String, primary_key=True, index=True)
    token = Column(String)
    refresh_token = Column(String)
    token_uri = Column(String)
    client_id = Column(String)
    client_secret = Column(String)
    scopes = Column(String)
