from fastapi import HTTPException, Request
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict

rate_limit_store: Dict[str, list] = defaultdict(list)

async def rate_limit_middleware(request: Request, call_next):
    """
    Simple rate limiting: 10 requests per minute per IP
    """
    # Get client IP
    client_ip = request.client.host
    
    # Only rate limit report generation endpoint
    if request.url.path == "/reports/generate" and request.method == "POST":
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Clean old requests
        rate_limit_store[client_ip] = [
            req_time for req_time in rate_limit_store[client_ip]
            if req_time > one_minute_ago
        ]
        
        # Check limit
        if len(rate_limit_store[client_ip]) >= 10:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Maximum 10 report generations per minute."
            )
        
        # Add current request
        rate_limit_store[client_ip].append(now)
    
    response = await call_next(request)
    return response