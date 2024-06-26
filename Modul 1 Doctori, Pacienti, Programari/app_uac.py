from typing import Optional, Annotated
from peewee import *
from fastapi import FastAPI, HTTPException, Depends, Header, Response, status
from fastapi_hypermodel import HyperModel, UrlFor, LinkSet
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime, timedelta, date
import requests
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from grpc import insecure_channel, _channel
from user_pb2_grpc import AuthServiceStub
from user_pb2 import AuthRequest, TokenRequest
from jose import JWTError, jwt
import re
app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET","POST","DELETE","PUT","PATCH"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  
def get_auth_service_stub():
    channel = insecure_channel('localhost:50051')
    return AuthServiceStub(channel)

