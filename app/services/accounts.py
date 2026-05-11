from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Depends
from app.db.session import get_db
from app.db.crud.accounts import AccountCRUD
from app.db.models.accounts import Account
from app.schemas.accounts import AccountCreate


class AccountService:
    def __init__(
        self, 
        db: AsyncSession = Depends(get_db), 
        crud: AccountCRUD = Depends(AccountCRUD)
    ):
        self.db = db
        self.crud = crud

    async def create_account(self, account_in: AccountCreate) -> Account:
        create_data = account_in.model_dump()
        account = await self.crud.account_create(create_data)
        await self.db.refresh(account)
        return account