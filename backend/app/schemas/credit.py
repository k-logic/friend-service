from pydantic import BaseModel


class CreditChargeRequest(BaseModel):
    amount: int


class CreditBalanceResponse(BaseModel):
    credit_balance: int
