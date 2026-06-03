from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

from app.services.users import UserService
from app.db.crud.users import UserCRUD
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    
    user_service = UserService(db=db, crud=UserCRUD(db))
    
    user = await user_service.get_user_by_email(email=form_data.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    is_password_correct = verify_password(plain_password=form_data.password, hashed_password=user.hashed_password)
   
    if not is_password_correct:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    
    token = create_access_token(data={"sub": str(user.id)})
    
    return {"access_token": token, "token_type": "bearer"}
