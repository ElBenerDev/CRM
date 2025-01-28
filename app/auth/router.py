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
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    print("\n" + "="*50)
    print("INICIO DEL PROCESO DE LOGIN")
    print(f"Método de la petición: {request.method}")
    print(f"Headers de la petición:")
    for header, value in request.headers.items():
        print(f"{header}: {value}")
    print(f"Email recibido: {username}")
    print("="*50)

    try:
        # Verificar conexión a la base de datos
        try:
            db.execute("SELECT 1")
            print("Conexión a la base de datos verificada")
        except Exception as e:
            print(f"Error de conexión a la base de datos: {e}")
            raise HTTPException(status_code=500, detail="Error de conexión a la base de datos")

        # Intentar autenticar
        print("Intentando autenticar usuario...")
        user = authenticate_user(db, username, password)
        
        if not user:
            print("Autenticación fallida - Usuario no encontrado o contraseña incorrecta")
            return JSONResponse(
                status_code=401,
                content={"error": "Credenciales inválidas"}
            )

        print(f"Usuario autenticado exitosamente: {user.email}")
        
        # Crear token
        try:
            access_token = create_access_token(
                data={"sub": user.email},
                expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            print("Token de acceso creado correctamente")
        except Exception as e:
            print(f"Error creando token: {e}")
            raise HTTPException(status_code=500, detail="Error creando token de acceso")

        # Crear respuesta
        response = JSONResponse(
            content={
                "access_token": access_token,
                "token_type": "bearer",
                "user": {
                    "email": user.email,
                    "name": user.name
                }
            }
        )
        
        # Establecer cookie
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            path="/"
        )
        
        print("Cookie establecida correctamente")
        print("LOGIN EXITOSO")
        print("="*50 + "\n")
        
        return response
        
    except Exception as e:
        print("\nERROR EN EL PROCESO DE LOGIN")
        print(f"Tipo de error: {type(e).__name__}")
        print(f"Mensaje de error: {str(e)}")
        import traceback
        print("Traceback completo:")
        print(traceback.format_exc())
        print("="*50 + "\n")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error del servidor: {str(e)}"}
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
        path="/"
    )
    return response