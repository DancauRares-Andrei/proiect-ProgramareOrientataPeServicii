from db import *
from server import *
import threading
import uvicorn
from grpc import insecure_channel, _channel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Response, Depends, Response, HTTPException, status
from typing import Annotated
from jose import JWTError
app = FastAPI()

origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST","GET","PUT"],
    allow_headers=["*"],
)
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
grpc_channel = insecure_channel('localhost:50051')
auth_stub = AuthServiceStub(grpc_channel)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  
def get_auth_service_stub():
    channel = insecure_channel('localhost:50051')
    return AuthServiceStub(channel)
@app.post("/token")
async def generate_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Nu am putut valida credențialele.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        grpc_auth_request = AuthRequest(username=form_data.username, password=form_data.password)
        auth_response = auth_service.Authenticate(grpc_auth_request)

        if not auth_response.token:
            raise credentials_exception

        payload = jwt.decode(auth_response.token, SECRET_KEY, algorithms=[ALGORITHM])

        return {"access_token": auth_response.token, "token_type": "bearer", "sub": payload.get("sub")}

    except JWTError:
        raise credentials_exception
    except _channel._InactiveRpcError:
        raise credentials_exception
@app.get("/api/medical_office_user")
async def find_user(response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),uid:bool=None,username:str=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if uid==True:
            user = User.get(User.uid==token_response.sub)
            #if str(uid)!=token_response.sub:
            #   grpc_token_request = TokenRequest(token=current_user)
            #   auth_response= auth_service.DestroyToken(grpc_token_request)
            #   raise HTTPException(status_code=403, detail="Accesare a unui alt user.") 
            user_hateoas=UserHATEOAS( #Nu expun parola
            uid=user.uid,
            username=user.username,   
            role=user.role.name,
            links={
            "self":{"href":"/api/medical_office_user/"+str(uid)},
            "parent":{"href":"/api/medical_office_user/"},
            "update_user":{"href":"/api/medical_office_user/"+str(uid),"type":"PUT"}
            }
            )
            return user_hateoas
        elif username is not None:
            user = User.get(User.username==username)
            if str(user.uid)!=token_response.sub:
               grpc_token_request = TokenRequest(token=current_user)
               auth_response= auth_service.DestroyToken(grpc_token_request)
               raise HTTPException(status_code=403, detail="Accesare a unui alt user.")           
            user_hateoas=UserHATEOAS( #Nu expun parola
            uid=user.uid,
            username=user.username,   
            role=user.role.name,
            links={
            "self":{"href":"/api/medical_office_user/"+str(user.uid)},
            "parent":{"href":"/api/medical_office_user/"},
            "update_user":{"href":"/api/medical_office_user/"+str(user.uid),"type":"PUT"}
            }
            )
            return user_hateoas
        else:
            raise HTTPException(status_code=422, detail="Trebuie introdus ori uid ori username.")
    except User.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office_user/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu s-a putut face validarea.")
@app.post("/api/medical_office_user")
async def create_user(user:UserCreate,response:Response):
    try:
        new_user=User.create(
        username=user.username,
        password=user.password,
        role=Role.get(Role.name=='pacient')
        )
        user_hateoas=UserHATEOAS( #Nu expun parola
        uid=new_user.uid,
        username=user.username,   
        role='pacient',
        links={
        "self":{"href":"/api/medical_office_user/"+str(new_user.uid)},
        "parent":{"href":"/api/medical_office_user/"},
        "update_user":{"href":"/api/medical_office_user/"+str(new_user.uid),"type":"PUT"}
        }
        )
        response.status_code=status.HTTP_201_CREATED
        return user_hateoas        
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Nu s-a putut crea utilizatorul pentru ca username-ul este deja folosit.")
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu s-a putut face validarea identitatii.")
#Uid este necesar aici pentru a respecta structura PUT-ului
@app.put("/api/medical_office_user/{uid}")
async def update_user(uid:int,user:UserCreate,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),doctor:bool=None):
    try:
        if doctor is not None and doctor!=False:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            if token_response.role!='admin':
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Doar admninul poate schimba rolul unui utilizator la doctor.")
            existing_user = User.get(User.uid == uid)
            existing_user.role=Role.get(Role.name=='doctor')
            existing_user.save()
            response.status_code=status.HTTP_204_NO_CONTENT
        else:
            grpc_token_request = TokenRequest(token=current_user)
            token_response = auth_service.ValidateToken(grpc_token_request)
            if not token_response.valid:
                raise HTTPException(status_code=401, detail="Token-ul nu este valid")
            if token_response.sub!=str(uid):
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request)
                raise HTTPException(status_code=403, detail="Nu este permisa modificarea informatiilor unui alt utilizator.")
            existing_user = User.get(User.uid == uid)
            existing_user.username=user.username
            existing_user.password=user.password
            existing_user.save()
            response.status_code=status.HTTP_204_NO_CONTENT
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Nu s-a putut actualiza utilizatorul pentru ca username-ul este deja folosit.")
    except User.DoesNotExist:
        response.status_code=status.HTTP_404_NOT_FOUND
        return {"parent":{"href":"/api/medical_office_user/"}}
    except _channel._InactiveRpcError:
        raise HTTPException(status_code=401, detail="Nu am putut valida token-ul.")
@app.post("/logout")
async def logout_user(response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    grpc_token_request = TokenRequest(token=current_user)
    token_response = auth_service.ValidateToken(grpc_token_request)
    if not token_response.valid:
        raise HTTPException(status_code=401, detail="Token-ul nu este valid")
    grpc_token_request = TokenRequest(token=current_user)
    auth_response= auth_service.DestroyToken(grpc_token_request)
    response.status_code=status.HTTP_204_NO_CONTENT
def run_uvicorn():
    uvicorn.run(app, host="0.0.0.0", port=8002)
uvicorn_thread = threading.Thread(target=run_uvicorn)
uvicorn_thread.start()
serve()
