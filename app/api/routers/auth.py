from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.users import UserService
from app.db.crud.users import UserCRUD
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token

router = APIRouter()

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    
    user_service = UserService(db=db, crud=UserCRUD(db))    
    user = await user_service.get_user_by_email(email=form_data.username)

    if not user or not verify_password(
        plain_password=form_data.password,
        hashed_password=user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
            )
  
    token = create_access_token(data={"sub": str(user.id)})  
    return {"access_token": token, "token_type": "bearer"}
