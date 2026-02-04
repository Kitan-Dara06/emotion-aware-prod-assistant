import logging
import os
import pathlib
from dotenv import load_dotenv
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

# Load environment variables FIRST
load_dotenv()

from emotion_aware_assistant.services.database import SessionLocal
from emotion_aware_assistant.services.user_token import UserToken

logger = logging.getLogger(__name__)

router = APIRouter()

# Include all scopes that Google may add (userinfo is added automatically for OAuth)
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]

# Get redirect URI from environment (defaults to localhost for development)
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/api/v2/auth/oauth2callback")

BASE_DIR = pathlib.Path(__file__).resolve().parent
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret.json')

client_secret_json = os.getenv("GOOGLE_CLIENT_SECRET_JSON")
if client_secret_json:
    with open(CLIENT_SECRET_FILE, 'w') as f:
        f.write(client_secret_json)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/authorize")
def authorize():
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
       
        auth_url, _ = flow.authorization_url(
            prompt='consent', 
            access_type='offline', 
            include_granted_scopes='true'
        )
        return RedirectResponse(auth_url)
    except Exception as e:
        logger.error("Authorization error: {e}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Authorization failed: {str(e)}"}
        )

@router.get("/oauth2callback")
def oauth2callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get('code')
    if not code:
        return JSONResponse(
            status_code=400, 
            content={"error": "Missing authorization code"}
        )
    
    try:
        flow = Flow.from_client_secrets_file(
            CLIENT_SECRET_FILE,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        flow.fetch_token(code=code)
        credentials = flow.credentials
        idinfo = id_token.verify_oauth2_token(
        flow.credentials._id_token,
        google_requests.Request(),
        flow.client_config['client_id'])
        email = idinfo.get("email")  
      
        
        
        token_data = UserToken(
            email=email,
            token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_uri=credentials.token_uri,
            client_id=credentials.client_id,
            client_secret=credentials.client_secret,
            scopes=",".join(credentials.scopes)
        )
        
        
        existing = db.query(UserToken).filter_by(email=email).first()
        if existing:
            
            existing.token = credentials.token
            existing.refresh_token = credentials.refresh_token
            existing.token_uri = credentials.token_uri
            existing.client_id = credentials.client_id
            existing.client_secret = credentials.client_secret
            existing.scopes = ",".join(credentials.scopes)
        else:
   
            db.add(token_data)
        
        db.commit()
        return JSONResponse(content={"message": f"{email} authorized successfully 🎉"})
        
    except Exception as e:
        logger.error("OAuth callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"OAuth callback failed: {str(e)}"}
        )
