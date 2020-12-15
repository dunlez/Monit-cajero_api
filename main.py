from db.user_db import UserInDB
from db.user_db import update_user, get_user
from db.transaction_db import TransactionInDB
from db.transaction_db import save_transaction, get_transactions
from models.user_models import UserIn, UserOut
from models.transaction_models import TransactionIn, TransactionOut

import datetime
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

mi_app = FastAPI()

origins = [
    "http://localhost.tiangolo.com", "https://localhost.tiangolo.com",
    "http://localhost", "http://localhost:8080", "https://cajero-app-frontend-123.herokuapp.com"
]
mi_app.add_middleware(
    CORSMiddleware, allow_origins=origins,
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@mi_app.get("/")
async def root():
    return {"message" : "Hola mundo desde Heroku"}

@mi_app.get("/user/transactions/{username}")
async def list_transactions(username: str):
    transactions_in_db = get_transactions(username)
    transactions_out = []
    for t in transactions_in_db:
        t_out = TransactionOut(**t.dict())
        transactions_out.append(t_out)
    
    return transactions_out
    

@mi_app.post("/user/auth/")
async def auth_user(user_in: UserIn):
    user_in_db = get_user(user_in.username)
    if user_in_db == None:
        raise HTTPException(status_code=404,detail="El usuario no existe")
    if user_in_db.password != user_in.password:
        raise HTTPException(status_code=401,detail="Error en la autenticación")        
    return {"Autenticado": True}

@mi_app.get("/user/balance/{usuario}")
async def get_balance(usuario: str):
    user_in_db = get_user(usuario)
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    user_out = UserOut(**user_in_db.dict())
    return user_out

@mi_app.put("/user/transaction/")
async def make_transaction(transaction_in: TransactionIn):    
    user_in_db = get_user(transaction_in.username)
    if user_in_db == None:
        raise HTTPException(status_code=404, detail="El usuario no existe")
    if user_in_db.balance < transaction_in.value:
        raise HTTPException(status_code=400, detail="Sin fondos suficientes")

    user_in_db.balance = user_in_db.balance - transaction_in.value
    update_user(user_in_db)

    transaction_in_db = TransactionInDB(**transaction_in.dict(), actual_balance = user_in_db.balance)
    
    transaction_in_db = save_transaction(transaction_in_db)
    transaction_out = TransactionOut(**transaction_in_db.dict())
    return transaction_out


