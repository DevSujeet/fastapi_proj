# import logging
# import base64
# import zlib
# import os
# from datetime import datetime, timedelta
# from fastapi import FastAPI, HTTPException, Depends, Security
# from fastapi.responses import JSONResponse
# import xmlsec
# from lxml import etree
# import jwt
# from onelogin.saml2.auth import OneLogin_Saml2_Auth
# from onelogin.saml2.utils import OneLogin_Saml2_Utils
# from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
# from pydantic_settings import BaseSettings
# from src.config.configs import SAML_Settings
# from src.config.log_config import logger

# # Configuration for JWT
# SECRET_KEY = "your-secret-key"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# # Initialize settings
# settings = SAML_Settings()

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


# # OAuth2 Password Bearer for JWT token handling
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# # Function to validate the JWT token
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     expired_token_exception = HTTPException(
#         status_code=401,
#         detail="Token has expired",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         # assumption that the roles are stored in the JWT token
#         roles = payload.get("roles")
#         if username is None or roles is None:
#             raise credentials_exception
#         return {"username": username, "roles": roles}
#     except jwt.ExpiredSignatureError:
#         # Decode without verifying expiration to extract user info
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"verify_exp": False})
#         username = payload.get("sub")
#         roles = payload.get("roles")
#         # Log the expired token information
#         if username:
#             print(f"Expired token for user: {username}, roles: {roles}")
#         raise expired_token_exception
#         "Note:- Capture user session ending here."
#         raise expired_token_exception
#     except jwt.PyJWTError:
#         raise credentials_exception

# # another way Security scheme for Authorization header
# api_key_header = APIKeyHeader(name="Authorization", auto_error=True)
# def get_current_user_header(api_key: str = Security(api_key_header)):
#     # Validate JWT token
#     credentials_exception = HTTPException(
#         status_code=401,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     try:
#         payload = jwt.decode(api_key.split("Bearer ")[1], SECRET_KEY, algorithms=[ALGORITHM])
#         username = payload.get("sub")
#         roles = payload.get("roles")
#         if username is None or roles is None:
#             raise credentials_exception
#         return {"username": username, "roles": roles}
#     except Exception:
#         raise credentials_exception
    
# # Function to directly extract user details from the SAML response (without signature verification)
# def extract_user_details_from_saml(saml_response: str):
#     try:
#         # Decode and decompress the SAML response
#         decoded_response = base64.b64decode(saml_response)
#         inflated_response = zlib.decompress(decoded_response, -15)

#         # Parse the SAML XML
#         tree = etree.fromstring(inflated_response)

#         # Extract expiration time
#         expiration = tree.find(".//Assertion//Conditions").get("NotOnOrAfter")
#         expiration_time = datetime.strptime(expiration, "%Y-%m-%dT%H:%M:%S.%fZ")
#         if expiration_time < datetime.now():
#             raise HTTPException(status_code=401, detail="Session expired")

#         # Extract roles and username (userPrincipalName)
#         roles = [role.text for role in tree.findall(".//Attribute[@Name='Role']")]
#         username = tree.find(".//Attribute[@Name='userPrincipalName']").text

#         logger.info("SAML response extracted successfully for user: %s", username)

#         return {
#             "username": username,
#             "roles": roles
#         }
#     except Exception as e:
#         logger.error("Error extracting user details from SAML response: %s", str(e))
#         raise HTTPException(status_code=400, detail="Invalid SAML response")

# # Function to validate the SAML response using signature (using python3-saml)
# def validate_saml_response_with_signature(saml_response: str):
#     try:
#         # Initialize the SAML authentication object
#         saml_settings = {
#             "strict": True,
#             "sp": {
#                 "entityId": settings.saml_entity_id,
#                 "assertionConsumerService": {
#                     "url": "your-assertion-consumer-service-url"
#                 },
#                 "singleLogoutService": {
#                     "url": "your-logout-url"
#                 },
#             },
#             "idp": {
#                 "entityId": settings.saml_idp_entity_id,
#                 "singleSignOnService": {
#                     "url": settings.saml_sso_url
#                 },
#                 "x509cert": open(settings.saml_public_cert_path).read(),
#             }
#         }

#         # Create an instance of OneLogin_Saml2_Auth to handle the SAML response
#         auth = OneLogin_Saml2_Auth({}, saml_settings)
        
#         # Process the SAML response and validate it
#         saml_data = {
#             "SAMLResponse": saml_response
#         }
#         auth.process_response(saml_data)
        
#         # Check if the response is valid
#         if not auth.is_authenticated():
#             raise HTTPException(status_code=401, detail="Invalid SAML Response")

#         # Extract user attributes from the SAML response
#         username = auth.get_nameid()
#         roles = auth.get_attributes().get("Role", [])

#         logger.info("SAML validation successful for user: %s", username)

#         return {
#             "username": username,
#             "roles": roles
#         }

#     except Exception as e:
#         logger.error("Invalid SAML response or signature: %s", str(e))
#         raise HTTPException(status_code=401, detail="Invalid SAML response or signature")


