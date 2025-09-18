from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional

from database import get_db
from schemas.user import UserCreate, UserResponse, UserLogin, Token
from services.auth import AuthService
from services.user import UserService
from services.google_oauth import GoogleOAuthService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        return UserService.create_user(db, user_data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Login attempt for username: {form_data.username}")
        user = AuthService.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Authentication failed for username: {form_data.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        access_token = AuthService.create_access_token(data={"sub": str(user.id)})
        logger.info(f"User {user.username} logged in successfully")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):

    payload = AuthService.verify_token(current_token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    access_token = AuthService.create_access_token(data={"sub": payload.get("sub")})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(
    current_token: str = Depends(oauth2_scheme)
):

    try:
        payload = AuthService.verify_token(current_token)
        if not payload:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        return {"message": "Logged out successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    


@router.post("/forgot-password")
async def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):

    user = UserService.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    reset_token = AuthService.create_reset_token(user.id)
    # TODO: Отправить email с токеном
    return {"message": "Password reset instructions sent to email"}

@router.post("/reset-password")
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):

    payload = AuthService.verify_reset_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = UserService.get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.hashed_password = AuthService.get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Password reset successfully"}

@router.post("/verify-email")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):

    payload = AuthService.verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = UserService.get_user_by_id(db, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user.is_verified = True
    db.commit()
    db.refresh(user)
    return {"message": "Email verified successfully"}


# Google OAuth2 routes
@router.get("/google")
async def google_login():
    """Redirect to Google OAuth2 authorization with JWT state"""
    # Create JWT state token for CSRF protection
    state_token = GoogleOAuthService.create_oauth_state()
    authorization_url = GoogleOAuthService.get_authorization_url(jwt_state=state_token)
    return RedirectResponse(url=authorization_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    state: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth2 callback with JWT state verification"""
    from config import settings
    import logging
    
    logger = logging.getLogger(__name__)
    logger.info(f"Google OAuth callback received with code: {code[:20]}... and state: {state[:20]}...")
    
    try:
        result = GoogleOAuthService.handle_google_callback(code, state, db)
        logger.info("Google OAuth callback processed successfully")
        
        # Redirect to frontend with token
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={result['access_token']}"
        logger.info(f"Redirecting to: {redirect_url}")
        
        return RedirectResponse(url=redirect_url)
        
    except HTTPException as e:
        logger.error(f"Google OAuth callback error: {e.detail}")
        # Redirect to frontend with error
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?error={e.detail}"
        return RedirectResponse(url=redirect_url)
    except Exception as e:
        logger.error(f"Unexpected error in Google OAuth callback: {str(e)}")
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?error=Unexpected error occurred"
        return RedirectResponse(url=redirect_url)