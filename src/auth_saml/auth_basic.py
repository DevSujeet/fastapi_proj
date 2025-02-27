# import logging
# import jwt
# from fastapi import FastAPI, Depends, HTTPException, Request
# from fastapi.responses import JSONResponse
# from datetime import datetime, timedelta
# import xml.etree.ElementTree as ET
# from fastapi.security import OAuth2PasswordBearer
# import base64
# import zlib

# from src.auth_oauth.auth_config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY



# # Initialize FastAPI app
# app = FastAPI()

# # Logging setup
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # In-memory session store (simulating database)
# session_store = {}

# # OAuth2 Password Bearer for JWT token handling
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# # Function to generate JWT token
# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.now() + expires_delta
#     else:
#         expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# # Function to validate and decode the JWT token
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         roles = payload.get("roles")
#         if username is None or roles is None:
#             raise credentials_exception
#         return {"username": username, "roles": roles}
#     except jwt.PyJWTError:
#         raise credentials_exception

# # Function to validate the SAML response and extract roles and user details
# def validate_saml_response(saml_response: str):
#     try:
#         # Decode and inflate the response if it’s base64 and compressed (standard in SAML)
#         decoded_response = base64.b64decode(saml_response)
#         inflated_response = zlib.decompress(decoded_response, -15)

#         # Parse XML and extract necessary info
#         tree = ET.ElementTree(ET.fromstring(inflated_response))
#         root = tree.getroot()

#         # Extract expiration time
#         expiration = root.find(".//Assertion//Conditions").get("NotOnOrAfter")
#         expiration_time = datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%S.%fZ")
#         if expiration_time < datetime.now():
#             raise HTTPException(status_code=401, detail="Session expired")

#         # Extract user roles from the SAML response
#         roles = [role.text for role in root.findall(".//Attribute[@Name='Role']")]
#         username = root.find(".//Attribute[@Name='userPrincipalName']").text

#         logger.info("SAML validation successful for user: %s", username)

#         return {
#             "username": username,
#             "roles": roles
#         }
#     except Exception as e:
#         logger.error("Invalid SAML response: %s", str(e))
#         raise HTTPException(status_code=401, detail="Invalid SAML response")

# # Endpoint to receive the SAML response from the frontend and generate JWT
# @app.post("/saml/response")
# async def saml_response(saml_response: str):
#     """
#     Endpoint to receive the SAML response from the frontend after the user has authenticated via IDP.
#     """
#     # Validate the SAML response and extract user information
#     user_info = validate_saml_response(saml_response)

#     # Create a JWT token with user information
#     access_token_expires = timedelta(minutes=30)  # Token expiration time
#     access_token = create_access_token(
#         data={"sub": user_info["username"], "roles": user_info["roles"]},
#         expires_delta=access_token_expires,
#     )

#     return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

# # Example protected route requiring a valid JWT token
# @app.get("/protected")
# async def protected_route(current_user: dict = Depends(get_current_user)):
#     # Check if user has 'user' role
#     if "user" not in current_user["roles"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
#     return {"message": "Access granted", "user": current_user}

# # Admin route requiring 'admin' role
# @app.get("/admin")
# async def admin_route(current_user: dict = Depends(get_current_user)):
#     # Check if user has 'admin' role
#     if "admin" not in current_user["roles"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
#     return {"message": "Admin access granted", "user": current_user}

# # Logout route (optional, for demonstration purposes)
# @app.get("/logout")
# async def logout():
#     return {"message": "Logged out successfully"}
