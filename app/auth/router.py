from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, Token
from .utils import (
    authenticate_user, 
    create_access_token, 
    get_password_hash,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.responses import JSONResponse
from fastapi import Form

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@router.post("/token")
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    print("\n" + "="*50)
    print("INICIO DEL PROCESO DE LOGIN")
    print(f"Método de la petición: {request.method}")
    
    try:
        # Log de headers
        print("\nHeaders recibidos:")
        for name, value in request.headers.items():
            print(f"{name}: {value}")
        
        # Obtener y loguear el form data
        form_data = await request.form()
        print("\nForm data recibido:")
        for key, value in form_data.items():
            if key == 'password':
                print(f"{key}: ********")
            else:
                print(f"{key}: {value}")
        
        username = form_data.get('username')
        password = form_data.get('password')
        
        if not username or not password:
            print("\nFaltan credenciales")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Por favor ingrese email y contraseña"
                },
                status_code=400
            )

        print(f"\nIntentando autenticar usuario: {username}")
        user = authenticate_user(db, username, password)
        
        if not user:
            print("Autenticación fallida")
            return templates.TemplateResponse(
                "auth/login.html",
                {
                    "request": request,
                    "error": "Credenciales inválidas"
                },
                status_code=401
            )

        print(f"Usuario autenticado: {user.email}")
        access_token = create_access_token(data={"sub": user.email})
        
        response = RedirectResponse(
            url="/",
            status_code=303
        )
        
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=1800,
            path="/"
        )
        
        print("Cookie establecida correctamente")
        print("Redirigiendo al dashboard")
        print("="*50)
        return response
        
    except Exception as e:
        print("\nError en login:")
        print(str(e))
        import traceback
        print("\nTraceback:")
        print(traceback.format_exc())
        print("="*50)
        return templates.TemplateResponse(
            "auth/login.html",
            {
                "request": request,
                "error": "Error del servidor, por favor intente más tarde"
            },
            status_code=500
        )
@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(
        "auth/login.html",
        {"request": request}
    )

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            password=hashed_password,
            name=user.name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar usuario: {str(e)}"
        )

@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/auth/login", status_code=302)
    response.delete_cookie(
        key="access_token",
        path="/",
        secure=True,
        httponly=True,
        samesite="lax"
    )
    return response