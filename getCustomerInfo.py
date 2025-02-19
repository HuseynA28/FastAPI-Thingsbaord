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
async def getCustomerInfo(
    customerId: str,
    token: str,
    ):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            tenant_url = urljoin(base_url, f'/api/customer/info/{customerId}/')
            response = await client.get(tenant_url, headers=headers)
            response.raise_for_status()
            data = response.json()     
            # devices.update(map(lambda i: (i.get("name"), i.get("id", {}).get("id")), data["data"]))
            name = data.get("name")
            try:
                parent_customer_data = data.get("parentCustomerId")
                parent_customer_id = parent_customer_data.get("id")
                result_message = f'The customer "{name}" is a child of the customer with ID {parent_customer_id}.'
            except:
                result_message = f'The customer "{name}" does not have a parent customer.' 
            return result_message


        except HTTPException as he:
            raise he
        except Exception as e:
            detail_message = str(e) if str(e).strip() else "No element(s) found"
            raise HTTPException(status_code=404, detail=detail_message)