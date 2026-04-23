from fastapi import APIRouter, Depends, status
from app.schemas.accounts import AccountRead, AccountCreate
from app.services.accounts import AccountService


router = APIRouter()


@router.post("/create", response_model=AccountRead, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_in: AccountCreate, 
    account_service: AccountService = Depends(AccountService)
):
    return await account_service.create_account(account_in)