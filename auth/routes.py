from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import User
from auth.schemas import UserCreate, UserLogin, Token, UserResponse, UserUpdate
from auth.utils import verify_password, get_password_hash, create_access_token
from auth.dependencies import get_current_user
from datetime import timedelta
from config import get_settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user, with validatino
    
    - email: Valid email address (must be unique)
    - username: Username (must be unique)
    - password: Password (min 8 characters recommended)
    """

    # Validate email format
    if "@" not in user_data.email or "." not in user_data.email:
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    
    # Validate username length
    if len(user_data.username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must be at least 3 characters"
        )
    
    # Validate password strength
    if len(user_data.password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with email and password to get JWT token.
    
    - **email**: Your registered email
    - **password**: Your password
    
    Returns a JWT token to use for authenticated requests.
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Create access token
    settings = get_settings()
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Requires: Authorization header with Bearer token
    """
    return current_user

@router.put("/api-keys", response_model=UserResponse)
def update_api_keys(
    api_keys: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user's API keys (Groq and Tavily).
    
    - **groq_api_key**: Your Groq API key (optional)
    - **tavily_api_key**: Your Tavily API key (optional)
    
    Note: Keys are stored encrypted and only used for your report generation.
    """
    if api_keys.groq_api_key is not None:
        current_user.groq_api_key = api_keys.groq_api_key
    
    if api_keys.tavily_api_key is not None:
        current_user.tavily_api_key = api_keys.tavily_api_key
    
    db.commit()
    db.refresh(current_user)
    
    return current_user

@router.get("/check-api-keys")
def check_api_keys(current_user: User = Depends(get_current_user)):
    """
    Check if user has configured API keys.
    
    Returns boolean flags indicating which keys are set.
    """
    return {
        "groq_key_set": bool(current_user.groq_api_key),
        "tavily_key_set": bool(current_user.tavily_api_key),
        "ready_to_generate": bool(current_user.groq_api_key and current_user.tavily_api_key)
    }