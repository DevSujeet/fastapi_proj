# from datetime import timedelta
# from typing import List
# from fastapi import APIRouter, Depends, HTTPException
# from fastapi.responses import JSONResponse
# # from src.auth_saml.auth import create_access_token, extract_user_details_from_saml, get_current_user, validate_saml_response_with_signature
# from src.config.log_config import logger
# from src.dependencies import get_user_id_header
# from src.role_dependency import role_based_authorization_with_optional_permissions_oauth
# from src.schemas.user import User


# router = APIRouter(
#     prefix="/auth_saml",
#     tags=["saml_authentication"],
#     responses={404: {"description": "user is not authorised."}}
# )

# # Endpoint to receive the SAML response from the frontend and generate JWT
# @router.post("/saml/response")
# async def saml_response(saml_response: str, validate_signature: bool = True):
#     """
#     Endpoint to receive the SAML response from the frontend after the user has authenticated via IDP.
#     If validate_signature is True, the signature will be validated using the public certificate.
#     """
#     # Choose whether to validate signature or just extract user details
#     if validate_signature:
#         # Validate the SAML response and extract user information using signature verification
#         user_info = validate_saml_response_with_signature(saml_response)
#     else:
#         # Directly extract user details from the SAML response (without signature verification)
#         user_info = extract_user_details_from_saml(saml_response)

#     # Create a JWT token with user information
#     access_token_expires = timedelta(minutes=30)  # Token expiration time
#     access_token = create_access_token(
#         data={"sub": user_info["username"], "roles": user_info["roles"]},
#         expires_delta=access_token_expires,
#     )

#     return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})

# # Example protected route requiring a valid JWT token
# @router.get("/protected")
# async def protected_route(current_user: dict = Depends(get_current_user)):
#     '''
#     curl -X GET "http://localhost:8000/auth/protected" \
#     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdW5ueSBrdW1hciIsInJvbGVzIjpbImFkbWluIl0sImV4cCI6MTczNzAzODA0MX0.nOFdAc3KL6vlxnn9w4ixPJhPv3jord0FjI-ti8JFN1Q"
#     {"message":"Access granted","user":{"username":"sunny kumar","roles":["admin"]}}
#     '''
#     # Check if user has 'user' role
#     if "admin" not in current_user["roles"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
#     return {"message": "Access granted", "user": current_user}

# # Admin route requiring 'admin' role
# @router.get("/admin")
# async def admin_route(current_user: dict = Depends(get_current_user)):
#     # Check if user has 'admin' role
#     if "admin" not in current_user["roles"]:
#         raise HTTPException(status_code=403, detail="Insufficient permissions")
#     return {"message": "Admin access granted", "user": current_user}

# # Logout route (optional, for demonstration purposes)
# @router.get("/logout")
# async def logout():
#     # logout user session if maintained
#     return {"message": "Logged out successfully"}

# @router.get("/decode_token_permission")
# async def admin_route_test(permissions: dict = Depends(role_based_authorization_with_optional_permissions_oauth(['read']))):
#     '''
#     curl -X GET "http://localhost:8000/auth/decode_token_permission" \
#     -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdW5ueSBrdW1hciIsInJvbGVzIjpbImFkbWluIl0sImV4cCI6MTczNzAzODA0MX0.nOFdAc3KL6vlxnn9w4ixPJhPv3jord0FjI-ti8JFN1Q"
#     {"message":"Admin access granted","user":{"current_user":{"username":"sunny kumar","roles":["admin"]},"permissions_granted":[]}}%  
#     '''
#     return {"message": "Admin access granted", "user": permissions}

# @router.post("/get_token")
# async def get_token(user:User):
#     return create_access_token(data={"sub": user.user_name, "roles": user.user_roles}) #,expires_delta=timedelta(minutes=30))