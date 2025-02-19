
import os
from urllib.parse import urljoin

import logging
import asyncio
import math
from datetime import datetime
from typing import List, Dict, Any, Set, Any, Tuple
import httpx
from fastapi import HTTPException
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from datetime import datetime, timedelta

from dotenv import load_dotenv
from urllib.parse import urljoin, urlencode




async def fetch_device_name(client: httpx.AsyncClient, headers: Dict[str, str], device_id: str, element_uid: str) -> Set[str]:
    try:
       

        relations_path = '/api/relations/info'
        query_params = {
            'fromId': device_id,
            'fromType': 'DEVICE'
        }

        relations_url = urljoin(base_url, relations_path)
        relations_url = f"{relations_url}?{urlencode(query_params)}"
        
        response = await client.get(relations_url, headers=headers)
        response.raise_for_status()
        relations = response.json()
        if not relations:
            raise HTTPException(status_code=404, detail="No asset relations found for device")
        for rel in relations:
            if rel.get('to', {}).get('entityType') == 'ASSET' and rel.get('toName').split('/')[1] == element_uid:
                operation_mode_1 = rel.get('toName').split('/')[2].split("_")[0]
                operation_mode_3 = rel.get('toName').split('/')[2].split("_")[1]
                asset_id = rel.get('to', {}).get('id')
        return asset_id ,operation_mode_1, operation_mode_3, relations

    except:
        raise HTTPException(status_code=404, detail="No asset relations found for device with the specified element UID")


