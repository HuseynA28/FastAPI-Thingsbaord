
import httpx
from urllib.parse import urljoin
from dotenv import load_dotenv
from fastapi import HTTPException
from auth import oauth2_scheme  
import os 
import datetime
import json
import numpy as np
import warnings
import polars as pl
import time 

devices_child={}
devices={}
load_dotenv()
base_url = os.getenv('BASE_URL')
if not base_url:
    raise ValueError("BASE_URL environment variable is not set")
async def get_device_details(
    customerId: str,
    token: str,
    pageSize:int,
    page:int,
    active:bool,
    includeCustomers :bool, 
    asChild: bool, 
    SaveDataFrame:bool
    
    
    
    ):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            tenant_url = urljoin(base_url, f'/api/customer/{customerId}/deviceInfos')
            params = {
            "pageSize": pageSize,
            "page": page,
            "includeCustomers": includeCustomers,
            "active":active,
             "asChild":asChild, 
             "SaveDataFrame":SaveDataFrame
            
        }

            response = await client.get(tenant_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json() 
           
            if not data:
                raise HTTPException(status_code=404, detail="Device not found")  
            else:
                if asChild is False:
                   
                    if SaveDataFrame is False :
                        try:
                            devices = pl.DataFrame(data["data"])
                            devices = devices.with_columns(pl.col("id").struct["id"].alias("id"), pl.col("customerId").struct["id"].alias("customerId")).select(["name", "id", "type", "label", "customerId"])
                            devices= devices.to_dicts()
                    
                        
                        except:
                            devices=f"No device is found as parent to show . Try to chnage the params "
                            warnings.warn("No devies is found , It will seach as  asChild . Make sure that  asChild is True")
                        
                    else:
                        try:
                            now = datetime.datetime.now()
                            devices = pl.DataFrame(data["data"])
                            devices = devices.with_columns(pl.col("id").struct["id"].alias("id"), pl.col("customerId").struct["id"].alias("customerId")).select(["name", "id", "type", "label", "customerId"])
                            devices.write_csv(f"/root/kafka-fastapi/dataFrame/{customerId}-{now}.csv")
                            return f"You save the data as /root/kafka-fastapi/dataFrame/{customerId}-{now}.csv"
                        except:
                            devices=f"No device is found as parent to save . Try to chnage the params "
                        return devices
                        
                  
                else:
                    try:
                        tenant_url = urljoin(base_url, f'/api/customer/info/{customerId}/')
                        response = await client.get(tenant_url, headers=headers)
                        response.raise_for_status()
                        data = response.json()     
                        name = data.get("name")
                        try:
                            parent_customer_data = data.get("parentCustomerId")
                            parent_customer_id = parent_customer_data.get("id")
                            # result_message = f'The customer "{name}" is a child of the customer with ID {parent_customer_id}.'
                            # print("result_message ")
                            if parent_customer_id:
                                try:
                                    tenant_url = urljoin(base_url, f'/api/customer/{parent_customer_id}/deviceInfos')
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
                                            
                                        if SaveDataFrame is False:
                                            try:
                                                devices = pl.DataFrame(data["data"])
                                                devices = devices.with_columns(pl.col("id").struct["id"].alias("id"), pl.col("customerId").struct["id"].alias("customerId")).select(["name", "id", "type", "label", "customerId"])
                                                return  devices.to_dicts()
                                        
                                                
                                            except:
                                                devices=[]
                                                warnings.warn("No devies is found , It will seach as  asChild . Make sure that  asChild is True")
                                                
                                        else:
                                            try:
                                                now = datetime.datetime.now()
                                                devices = pl.DataFrame(data["data"])
                                                devices = devices.with_columns(pl.col("id").struct["id"].alias("id"), pl.col("customerId").struct["id"].alias("customerId")).select(["name", "id", "type", "label", "customerId"])
                                                devices.write_csv(f"/root/kafka-fastapi/dataFrame/{customerId}-{now}.csv")
                                                return f"You save the data as /root/kafka-fastapi/dataFrame/{customerId}-{now}.csv"
                                            except:
                                                devices=f"No device is found to save "
                                        
                                except HTTPException as e:
                                    detail_message = str(e) if str(e).strip() else "No element(s) found"
                                    raise HTTPException(status_code=404, detail=detail_message)
                                
                        except:
                            result_message = f'The customer "{name}" does not have a parent customer.' 
                        return result_message
                    except HTTPException as es:
                        detail_message = str(es) if str(es).strip() else "No element(s) found"
                        raise HTTPException(status_code=404, detail=detail_message)

        except HTTPException as he:
            raise he
        except Exception as e:
            detail_message = str(e) if str(e).strip() else "No element(s) found"
            raise HTTPException(status_code=404, detail=detail_message)
        
            
        except HTTPException as e:
            detail_message = str(e) if str(e).strip() else "No element(s) found"
            raise HTTPException(status_code=404, detail=detail_message)
