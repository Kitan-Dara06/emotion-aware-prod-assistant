
from emotion_aware_assistant.service.database import SessionLocal
from emotion_aware_assistant.service.user_token import UserToken
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
import os, pathlib, json
router = APIRouter()

SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = os.getenv("https://emotion-aware-prod-assistant.onrender.com/oauth2callback")  

BASE_DIR = pathlib.Path(__file__).resolve().parent
CLIENT_SECRET_FILE = os.path.join(BASE_DIR, 'client_secret.json')

with open(CLIENT_SECRET_FILE, 'w') as f:
    f.write(os.getenv("GOOGLE_CLIENT_SECRET_JSON"))

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline', include_granted_scopes='true')
    return RedirectResponse(auth_url)

@router.get("/oauth2callback")
def oauth2callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get('code')
    if not code:
        return JSONResponse(status_code=400, content={"error": "Missing authorization code"})

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    credentials = flow.credentials
    email = "default_user@example.com"

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
        db.delete(existing)
    db.add(token_data)
    db.commit()

    return JSONResponse(content={"message": f"{email} authorized successfully 🎉"})

