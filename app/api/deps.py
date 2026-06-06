from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import jwt
from jwt.exceptions import InvalidTokenError
from app.db.session import get_db
from app.core.settings import settings
from app.services.users import UserService
from app.db.crud.users import UserCRUD


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        key = settings.SECRET_KEY
        if key is None:
            raise credentials_exception
        payload = jwt.decode(token, key, algorithms=[settings.ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        try:
            user_uuid = uuid.UUID(user_id_str)
        except ValueError:
              raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception
    
    user_service = UserService(db=db, crud=UserCRUD(db))
    user = await user_service.get_user_by_id(user_uuid)

    
    if user is None:
        raise credentials_exception       
    return user
