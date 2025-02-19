from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import httpx
import os 
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security
from typing import Annotated, Literal
from pydantic import BaseModel
from typing import List
from enum import Enum
from getDevicesNames import *
from auth import oauth2_scheme  
load_dotenv()
base_url = os.getenv('BASE_URL', "https://emea5.ebmpapstneo.io")

if not base_url:
    raise ValueError("BASE_URL environment variable is not set")

login_url = f"{base_url}/api/auth/login"

app = FastAPI()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

async def get_token(form_data: OAuth2PasswordRequestForm):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                login_url,
                json={"username": form_data.username, "password": form_data.password}
            )
            response.raise_for_status()
            data = response.json()
            return TokenResponse(access_token=data.get("token"), token_type="bearer")
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=exc.response.status_code if exc.response else 500,
            detail="Login failed",
        ) from exc

@app.post("/token12", response_model=TokenResponse , include_in_schema=False)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    return await get_token(form_data)

@app.get("/checkConnection")
async def protected_route(token: Annotated[str, Depends(oauth2_scheme)]):
    return {"message": "You have accessed a protected route!", "token": token}


@app.get("/getCustomerDeviceNames/")
async def getCustomerDevice(
    token: Annotated[str, Depends(oauth2_scheme)], 
    customerId : str =Query(...,description= "A string value representing the customer id. For example:784f394c-42b6-435a-983c-b7beff2784f9"), 
    pageSize : int = Query (1000,description= "Maximum amount of entities in a one page The defaut value is 1000" ), 
    page : int = Query(0,description="Sequence number of page starting from 0"), 
    includeCustomers : bool=True, 
    active: bool =False
):

    return await get_device_names(token=token, customerId=customerId, pageSize=pageSize, page=page, includeCustomers=includeCustomers, active=active)
    # return {"message": "You have accessed a protected route!", "token": customerId}


# https://emea5.ebmpapstneo.io/swagger-ui/#/device-controller/getCustomerDeviceInfosUsingGET