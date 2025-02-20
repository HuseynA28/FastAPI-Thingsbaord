
import httpx
from urllib.parse import urljoin
from dotenv import load_dotenv
from fastapi import HTTPException
from auth import oauth2_scheme  
import os 
import json
import numpy as np
devices={}
load_dotenv()
base_url = os.getenv('BASE_URL')
if not base_url:
    raise ValueError("BASE_URL environment variable is not set")
async def get_device_names(
    customerId: str,
    token: str,
    pageSize:int,
    page:int,
    active:bool,
    includeCustomers :bool
    ):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            tenant_url = urljoin(base_url, f'/api/customer/{customerId}/deviceInfos')
            params = {
            "pageSize": pageSize,
            "page": page,
            "includeCustomers": includeCustomers,
            "active":active
        }

            response = await client.get(tenant_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()   
            if not data:
                raise HTTPException(status_code=404, detail="Device not found")  
            else:
                devices.update(map(lambda i: (i.get("name"), i.get("id", {}).get("id")), data["data"])) 
                return  devices
            
        except HTTPException as e:
            detail_message = str(e) if str(e).strip() else "No element(s) found"
            raise HTTPException(status_code=404, detail=detail_message)

