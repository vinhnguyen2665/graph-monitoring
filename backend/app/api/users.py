from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from uuid import UUID

from app.db.postgres import get_db
from app.models.postgres_models import User
from app.api import deps

router = APIRouter()

def require_admin(current_user: User = Depends(deps.get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

class UserRoleUpdate(BaseModel):
    role: str

@router.get("")
async def get_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Any:
    stmt = select(User)
    res = await db.execute(stmt)
    users = res.scalars().all()
    # Filter sensitive data
    return [
        {
            "id": u.id,
            "email": u.email,
            "username": u.username,
            "full_name": u.full_name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at
        }
        for u in users
    ]

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role_in: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Any:
    if role_in.role not in ["admin", "operator", "viewer"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.role = role_in.role
    await db.commit()
    return {"message": "User role updated successfully", "role": user.role}

@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin)
) -> Any:
    stmt = select(User).where(User.id == user_id)
    res = await db.execute(stmt)
    user = res.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    await db.delete(user)
    await db.commit()
    return {"message": "User deleted successfully"}
