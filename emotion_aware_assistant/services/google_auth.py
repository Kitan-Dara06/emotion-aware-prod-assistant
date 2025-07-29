from emotion_aware_assistant.services.database import SessionLocal
from emotion_aware_assistant.services.user_token import UserToken
from emotion_aware_assistant.gloabal_import import *

router = APIRouter()

SCOPES = ['https://www.googleapis.com/auth/calendar']

REDIRECT_URI = os.getenv("REDIRECT_URI", "https://emotion-aware-prod-assistant.onrender.com/oauth2callback")

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
        # Fixed: Proper method call for authorization URL
        auth_url, _ = flow.authorization_url(
            prompt='consent', 
            access_type='offline', 
            include_granted_scopes='true'
        )
        return RedirectResponse(auth_url)
    except Exception as e:
        print(f"❌ Authorization error: {e}")
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
        
        # Check if user already exists
        existing = db.query(UserToken).filter_by(email=email).first()
        if existing:
            # Update existing token
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
        print(f"❌ OAuth callback error: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": f"OAuth callback failed: {str(e)}"}
        )
