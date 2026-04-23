from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.accounts import Account
from app.db.session import get_db
from fastapi import Depends



class AccountCRUD:
	def __init__(self, db: AsyncSession = Depends(get_db)):
		self.db = db
		
	async def account_create(self, obj_in: dict) -> Account:
		db_object = Account(**obj_in)
		self.db.add(db_object)
		await self.db.flush()
		return db_object