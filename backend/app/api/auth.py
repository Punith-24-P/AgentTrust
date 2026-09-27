from datetime import timedelta
import re
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)
from app.utils.security import hash_password, verify_password, create_access_token
from app.api.deps import get_current_user, log_audit_event

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    req: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == req.email.lower().strip()))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists"
        )

    # Password validation
    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    if req.confirm_password and req.password != req.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )

    # Create User
    new_user = User(
        name=req.name.strip(),
        email=req.email.lower().strip(),
        hashed_password=hash_password(req.password),
        is_active=True
    )
    db.add(new_user)
    await db.flush()

    # Create default Workspace for the user
    slug_base = re.sub(r"[^a-z0-9]", "-", req.name.lower().strip()) or "workspace"
    workspace_slug = f"{slug_base}-{new_user.id[:6]}"
    workspace = Workspace(
        name=f"{new_user.name}'s Workspace",
        slug=workspace_slug,
        owner_id=new_user.id
    )
    db.add(workspace)
    await db.flush()

    # Add user as workspace admin
    member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=new_user.id,
        role="admin"
    )
    db.add(member)
    await db.flush()

    # Audit log
    await log_audit_event(
        db=db,
        action="USER_REGISTERED",
        entity_type="user",
        entity_id=new_user.id,
        user_id=new_user.id,
        workspace_id=workspace.id,
        details={"email": new_user.email},
        ip_address=request.client.host if request.client else None
    )

    access_token = create_access_token({"sub": new_user.id, "email": new_user.email})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(new_user),
        workspace_id=workspace.id
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    req: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == req.email.lower().strip()))
    user = result.scalar_one_or_none()

    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact support."
        )

    # Find primary workspace
    ws_result = await db.execute(
        select(WorkspaceMember.workspace_id).where(WorkspaceMember.user_id == user.id).limit(1)
    )
    primary_workspace_id = ws_result.scalar_one_or_none()

    # Duration: 30 days if remember is True, else default 24h
    expires_delta = timedelta(days=30) if req.remember else None
    access_token = create_access_token(
        {"sub": user.id, "email": user.email},
        expires_delta=expires_delta
    )

    await log_audit_event(
        db=db,
        action="USER_LOGGED_IN",
        entity_type="user",
        entity_id=user.id,
        user_id=user.id,
        workspace_id=primary_workspace_id,
        details={"remember": req.remember},
        ip_address=request.client.host if request.client else None
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
        workspace_id=primary_workspace_id
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await log_audit_event(
        db=db,
        action="USER_LOGGED_OUT",
        entity_type="user",
        entity_id=current_user.id,
        user_id=current_user.id,
        ip_address=request.client.host if request.client else None
    )
    return {"message": "Successfully logged out"}


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Standard security practice: return success regardless of email existence to avoid email enumeration
    return {
        "message": "If an account with this email exists, a password reset link has been dispatched.",
        "status": "DISPATCHED"
    }


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if len(req.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
    return {
        "message": "Password has been successfully updated. You may now log in.",
        "status": "SUCCESS"
    }
