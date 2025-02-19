from fastapi.security import OAuth2PasswordBearer

# Define the OAuth2 scheme in a shared module
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token12")
