from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..auth import get_password_hash, create_access_token, get_current_user, get_db, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models.user import User
from ..models.user_preferences import UserPreferences
from ..schemas.user import UserCreate, UserOut
from ..schemas.user_preferences import UserPreferencesCreate, UserPreferencesOut
from datetime import timedelta

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Crear el nuevo usuario
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Verificar las credenciales del usuario
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generar un token JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/preferences", response_model=UserPreferencesOut)
def create_preferences(preferences: UserPreferencesCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verificar si el usuario ya tiene preferencias
    existing_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if existing_preferences:
        raise HTTPException(status_code=400, detail="User already has preferences")

    db_preferences = UserPreferences(
        user_id=current_user.id,
        favorite_photography_type=preferences.favorite_photography_type,
        preferred_format=preferences.preferred_format,
        color_preference=preferences.color_preference,
        preferred_camera_type=preferences.preferred_camera_type,
        preferred_focal_length=preferences.preferred_focal_length,
        favourite_look=preferences.favourite_look
    )
    db.add(db_preferences)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

@router.put("/preferences", response_model=UserPreferencesOut)
def update_preferences(preferences: UserPreferencesCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not db_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")

    for key, value in preferences.dict(exclude_unset=True).items():
        setattr(db_preferences, key, value)
    db.commit()
    db.refresh(db_preferences)
    return db_preferences

@router.get("/preferences", response_model=UserPreferencesOut)
def get_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not db_preferences:
        raise HTTPException(status_code=404, detail="User preferences not found")
    return db_preferences