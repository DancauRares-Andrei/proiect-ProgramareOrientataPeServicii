from fastapi import FastAPI, HTTPException, Response, status, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from bson import ObjectId, errors
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from bson.objectid import ObjectId
from fastapi_hypermodel import HyperModel, UrlFor, LinkSet
from datetime import date,datetime
from typing import Optional, Annotated
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from grpc import insecure_channel, _channel
from user_pb2_grpc import AuthServiceStub
from user_pb2 import AuthRequest, TokenRequest
from jose import JWTError, jwt
import requests
app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET","POST","DELETE","PUT"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  
def get_auth_service_stub():
    channel = insecure_channel('localhost:50051')
    return AuthServiceStub(channel)
client = MongoClient("mongodb://readWrite:pass@localhost:27017")#/?authSource=medical_office_consultation
db = client["medical_office_consultation"]
colectie = db["consultatie"]
class CreateInvestigatie(BaseModel):
    denumire: str
    durata_de_procesare: int   
    rezultat: str
class InvestigatieHATEOAS(HyperModel):
    id:str
    denumire: str
    durata_de_procesare: int   
    rezultat: str
    links:dict
class CreateConsultatie(BaseModel):
    id_pacient: int
    id_doctor: int
    data: date
    diagnostic: str
    investigatii: List[CreateInvestigatie]
    
class ConsultatieModel:
    def __init__(self, id_pacient: str, id_doctor: int, data: date, diagnostic: str,
                 investigatii: Optional[List[dict]] = None):
        self.id_pacient = id_pacient
        self.id_doctor = id_doctor
        self.data = data
        self.diagnostic = diagnostic
        self.investigatii = investigatii or []

class ConsultatieHATEOAS(HyperModel):
    id:str
    id_pacient: int
    id_doctor: int
    data: date
    diagnostic: str
    investigatii: list
    links:dict
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
#CONSULTATII
@app.get("/api/medical_office_consultation")
async def get_consultatii(response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),diagnostic:str=None,id_doctor:int=None,cnp:int=None,data:date=None):
    grpc_token_request = TokenRequest(token=current_user)
    token_response = auth_service.ValidateToken(grpc_token_request)
    if not token_response.valid:
        raise HTTPException(status_code=401, detail="Token-ul nu este valid")
    if token_response.role!="pacient" and token_response.role!="doctor":
        grpc_token_request = TokenRequest(token=current_user)
        auth_response= auth_service.DestroyToken(grpc_token_request) 
        raise HTTPException(status_code=403, detail="Doar pacientul si doctorul pot vedea informatii despre consultatii.")
    if diagnostic is not None:
        consultatii=colectie.find({"diagnostic":diagnostic})
    elif cnp is not None and data is not None and id_doctor is not None:
        try:
            if token_response.role=="pacient":
                url = f"http://localhost:8000/api/medical_office/patients/{cnp}?uid={token_response.sub}"
                print(url)
                response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
                if response1.status_code != 200:
                    raise HTTPException(status_code=403, detail="Nu este permisa cautarea unei consultatii a unui alt pacient.")
            else:
                url = f"http://localhost:8000/api/medical_office/physicians/{id_doctor}?uid={token_response.sub}"
                print(url)
                response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
                if response1.status_code != 200:
                    raise HTTPException(status_code=403, detail="Nu este permisa cautarea unei consultatii a unui alt doctor.")
            consultatie = colectie.find_one({"id_pacient": cnp,"id_doctor":id_doctor,"data":datetime.combine(data, datetime.min.time())})
            if consultatie:
                if token_response.role=="pacient":
                    consultatie_hateoas=ConsultatieHATEOAS(
                        id=str(consultatie["_id"]),
                        id_pacient=consultatie["id_pacient"],
                        id_doctor=consultatie["id_doctor"],
                        data=consultatie["data"],
                        diagnostic=consultatie["diagnostic"],
                        investigatii=consultatie["investigatii"],
                        links=LinkSet({
                                        "self":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])},
                                        "parent":{"href":"/api/medical_office_consultation"}
                                        })
                            )
                else:
                    consultatie_hateoas=ConsultatieHATEOAS(
                        id=str(consultatie["_id"]),
                        id_pacient=consultatie["id_pacient"],
                        id_doctor=consultatie["id_doctor"],
                        data=consultatie["data"],
                        diagnostic=consultatie["diagnostic"],
                        investigatii=consultatie["investigatii"],
                        links=LinkSet({
                                        "self":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])},
                                        "parent":{"href":"/api/medical_office_consultation"},
                                        "investigatii":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])+"/investigations"},
                                        "delete_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"DELETE"},
                                        "create_consultatie":{"href":"/api/medical_office_consultation","type":"POST"},
                                        "update_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"PUT"}
                                        })
                            )
                return consultatie_hateoas
            else:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office_consultation"}}        
        except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}  
    elif id_doctor is not None:
        url = f"http://localhost:8000/api/medical_office/physicians/{id_doctor}?uid={token_response.sub}"
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            raise HTTPException(status_code=403, detail="Nu este permisa cautarea unei consultatii a unui alt doctor.")
        consultatii=colectie.find({"id_doctor":id_doctor})
    else:
        consultatii=colectie.find()
    consultatie_hateoas_list=[]
    for consultatie in consultatii:
        if token_response.role=="pacient":
            url = f"http://localhost:8000/api/medical_office/patients/{consultatie['id_pacient']}?uid={token_response.sub}"
            print(url)
            response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
            if response1.status_code == 200:
                consultatie_hateoas=ConsultatieHATEOAS(
                id=str(consultatie["_id"]),
                id_pacient=consultatie["id_pacient"],
                id_doctor=consultatie["id_doctor"],
                data=consultatie["data"],
                diagnostic=consultatie["diagnostic"],
                investigatii=consultatie["investigatii"],
                links=LinkSet({#Pacientul nu are dreptul sa execute celalte link-uri, asa ca le-am eliminat. Investigatiile vor fi vazute direct de aici
                                "self":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])},
                                "parent":{"href":"/api/medical_office_consultation"}
                                })
                    )
                consultatie_hateoas_list.append(consultatie_hateoas)
            
        else:
            url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /physicians cu uid=true
            print(url)
            response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
            if response1.status_code == 200:
                consultatie_hateoas=ConsultatieHATEOAS(
                id=str(consultatie["_id"]),
                id_pacient=consultatie["id_pacient"],
                id_doctor=consultatie["id_doctor"],
                data=consultatie["data"],
                diagnostic=consultatie["diagnostic"],
                investigatii=consultatie["investigatii"],
                links=LinkSet({
                                "self":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])},
                                "parent":{"href":"/api/medical_office_consultation"},
                                "investigatii":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])+"/investigations"},
                                "get_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"GET"},
                                "delete_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"DELETE"},
                                "create_consultatie":{"href":"/api/medical_office_consultation","type":"POST"},
                                "update_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"PUT"}
                                })
                    )
                consultatie_hateoas_list.append(consultatie_hateoas)
    return consultatie_hateoas_list
    
@app.post("/api/medical_office_consultation")
async def create_consultatie(consultatie: CreateConsultatie,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    grpc_token_request = TokenRequest(token=current_user)
    token_response = auth_service.ValidateToken(grpc_token_request)
    if not token_response.valid:
        raise HTTPException(status_code=401, detail="Token-ul nu este valid")
    if token_response.role!="doctor":
        grpc_token_request = TokenRequest(token=current_user)
        auth_response= auth_service.DestroyToken(grpc_token_request) 
        raise HTTPException(status_code=403, detail="Doar doctorul poate crea consultatii.")
    url = f"http://localhost:8000/api/medical_office/physicians/{consultatie.id_doctor}?uid={token_response.sub}"
    print(url)
    response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
    if response1.status_code != 200:
        grpc_token_request = TokenRequest(token=current_user)
        auth_response= auth_service.DestroyToken(grpc_token_request)
        raise HTTPException(status_code=403, detail="Se incearca adaugarea unei consultatii la un alt medic.")#S-ar putea face si pe /physicians cu uid=true
    url = f"http://localhost:8000/api/medical_office/physicians/{consultatie.id_doctor}/patients/{consultatie.id_pacient}?data={consultatie.data}"
    print(url)
    response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
    if response1.status_code != 200:
        raise HTTPException(status_code=404, detail="Programare negăsită")
    #Verificarea ca nu se insereaza mai mult de o consultatie pentru o singura programare
    consultatie_ex=colectie.find_one({"id_pacient":consultatie.id_pacient ,"id_doctor":consultatie.id_doctor,"data":datetime.combine(consultatie.data, datetime.min.time())})
    if consultatie_ex:
        raise HTTPException(status_code=409, detail="Deja exista o consultatie pentru aceasta programare.")
    if consultatie.diagnostic not in ['sanatos','bolnav']:
        raise HTTPException(status_code=422, detail="Diagnosticul nu este valid.")
    investigatii_model=[]
    for investigatie in consultatie.investigatii:
        investigatie_model={"id":str(ObjectId()),"denumire":investigatie.denumire,"durata_de_procesare":investigatie.durata_de_procesare,"rezultat":investigatie.rezultat}
        investigatii_model.append(investigatie_model)
    consultatie_model=ConsultatieModel(
    id_pacient=consultatie.id_pacient,
    id_doctor=consultatie.id_doctor,
    data=datetime.combine(consultatie.data, datetime.min.time()),
    diagnostic=consultatie.diagnostic,
    investigatii=investigatii_model
    )
    result = colectie.insert_one(consultatie_model.__dict__)
    consultatie_hateoas=ConsultatieHATEOAS(
        id=str(result.inserted_id),
        id_pacient=consultatie.id_pacient,
        id_doctor=consultatie.id_doctor,
        data=consultatie.data,
        diagnostic=consultatie.diagnostic,
        investigatii=investigatii_model,
        links=LinkSet({
                        "self":{"href":"/api/medical_office_consultation/"+str(result.inserted_id),},
                        "parent":{"href":"/api/medical_office_consultation"},
                        "investigatii":{"href":"/api/medical_office_consultation/"+str(result.inserted_id)+"/investigations"},
                        "delete_consultatie":{"href":"/api/medical_office_consultation/"+str(result.inserted_id),"type":"DELETE"},
                        "create_consultatie":{"href":"/api/medical_office_consultation","type":"POST"},
                        "update_consultatie":{"href":"/api/medical_office_consultation/"+str(result.inserted_id),"type":"PUT"}
                        })
            )
    response.status_code=status.HTTP_201_CREATED
    return consultatie_hateoas
    
@app.get("/api/medical_office_consultation/{id}")
async def get_consultatie(id:str,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        if consultatie:
            if token_response.role=="admin":
                grpc_token_request = TokenRequest(token=current_user)
                auth_response= auth_service.DestroyToken(grpc_token_request) 
                raise HTTPException(status_code=403, detail="Adminul nu poate vedea consultatii.")
            if token_response.role=="pacient":
                url = f"http://localhost:8000/api/medical_office/patients/{consultatie['id_pacient']}?uid={token_response.sub}"#S-ar putea face si pe /patients cu uid=true
                print(url)
                response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
                if response1.status_code == 200:
                    consultatie_hateoas=ConsultatieHATEOAS(
                        id=str(consultatie["_id"]),
                        id_pacient=consultatie["id_pacient"],
                        id_doctor=consultatie["id_doctor"],
                        data=consultatie["data"],
                        diagnostic=consultatie["diagnostic"],
                        investigatii=consultatie["investigatii"],
                        links=LinkSet({
                                        "self":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])},
                                        "parent":{"href":"/api/medical_office_consultation"},
                                        "investigatii":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])+"/investigations"},
                                        "get_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"GET"},
                                        "delete_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"DELETE"},
                                        "create_consultatie":{"href":"/api/medical_office_consultation","type":"POST"},
                                        "update_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"PUT"}
                                        })
                            )
                    return consultatie_hateoas
                else:
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request) 
                    raise HTTPException(status_code=403, detail="S-a incercat accesarea unei consultatii nepersonale.")   
            elif token_response.role=="doctor":
                url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /patients cu uid=true
                print(url)
                response1 = requests1.get(url,headers={'Authorization':f"Bearer {current_user}"})
                if response.status_code == 200:
                    consultatie_hateoas=ConsultatieHATEOAS(
                        id=str(consultatie["_id"]),
                        id_pacient=consultatie["id_pacient"],
                        id_doctor=consultatie["id_doctor"],
                        data=consultatie["data"],
                        diagnostic=consultatie["diagnostic"],
                        investigatii=consultatie["investigatii"],
                        links=LinkSet({
                                        "self":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])},
                                        "parent":{"href":"/api/medical_office_consultation"},
                                        "investigatii":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"])+"/investigations"},
                                        "get_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"GET"},
                                        "delete_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"DELETE"},
                                        "create_consultatie":{"href":"/api/medical_office_consultation","type":"POST"},
                                        "update_consultatie":{"href":"/api/medical_office_consultation/"+str(consultatie["_id"]),"type":"PUT"}
                                        })
                            )
                    return consultatie_hateoas
                else:
                    grpc_token_request = TokenRequest(token=current_user)
                    auth_response= auth_service.DestroyToken(grpc_token_request) 
                    raise HTTPException(status_code=403, detail="S-a incercat accesarea unei consultatii nepersonale.")           
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}} 
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}         
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid")
           
@app.put("/api/medical_office_consultation/{id}")
async def update_consultatie(id:str,consultatie: CreateConsultatie,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate modifica consultatii.")
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie.id_doctor}?uid={token_response.sub}"#S-ar putea face si pe /phyisicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca modificarea consultatiei unui alt medic.")
        if consultatie.diagnostic not in ['sanatos','bolnav']:
            raise HTTPException(status_code=422, detail="Diagnosticul nu este valid.")
        consultatie1 = colectie.find_one({"_id": ObjectId(id)})
        investigatii_model=[]
        for investigatie in consultatie.investigatii:
            investigatie_model={"id":str(ObjectId()),"denumire":investigatie.denumire,"durata_de_procesare":investigatie.durata_de_procesare,"rezultat":investigatie.rezultat}
            investigatii_model.append(investigatie_model)
        consultatie_model=ConsultatieModel(
            id_pacient=consultatie.id_pacient,
            id_doctor=consultatie.id_doctor,
            data=datetime.combine(consultatie.data, datetime.min.time()),
            diagnostic=consultatie.diagnostic,
            investigatii=investigatii_model
        )
        result = colectie.update_one({"_id": ObjectId(id)}, {"$set": consultatie_model.__dict__})
        if result.matched_count > 0:
            response.status_code=status.HTTP_204_NO_CONTENT
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}} #Nu pot alege eu la ce id se face inserarea, deci nu se poate crea un nou obiect in PUT
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}         
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid")

@app.delete("/api/medical_office_consultation/{id}")
async def delete_consultatie(id: str,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate sterge consultatii.")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /physicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca stergerea consultatiei unui alt medic.")
        result = colectie.delete_one({"_id": ObjectId(id)})
        if result.deleted_count > 0:
            response.status_code=status.HTTP_204_NO_CONTENT
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid")
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}    










#INVESTIGATII

@app.get("/api/medical_office_consultation/{id}/investigations")
async def get_investigatii(id: str,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub),denumire:str=None):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate vedea lista de investigatii spre a le modifica.")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /phyisicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca accesarea listei de investigatii de la consultatia unui alt medic.")
        
        if denumire is not None:
            try:
                investigatii=consultatie["investigatii"]
                investigatii=[inv for inv in investigatii if inv['denumire']==denumire]
            except TypeError:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office_consultation"}}
        else:
            try:
                investigatii=consultatie["investigatii"]
            except TypeError:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office_consultation"}}
        investigatii_hateoas=[]
        for investigatie in investigatii:
            investigatie_hateoas=InvestigatieHATEOAS(
            id=investigatie['id'],
            denumire=investigatie['denumire'],
            durata_de_procesare=investigatie['durata_de_procesare'],
            rezultat=investigatie['rezultat'],
            links=LinkSet({
                            "self":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id'])},
                            "parent":{"href":"/api/medical_office_consultation/"+str(id)},
                            "get_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id']),"type":"GET"},
                            "delete_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id']),"type":"DELETE"},
                            "create_investigatie":{"href":"/api/medical_office_consultation/"+str(id),"type":"POST"},
                            "update_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id']),"type":"PUT"}
                            })
            )
            investigatii_hateoas.append(investigatie_hateoas)
        return investigatii_hateoas
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}} 
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid")

@app.get("/api/medical_office_consultation/{id}/investigations/{idi}")
async def get_investigatie(id:str,idi:str,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate vedea lista de investigatii spre a le modifica.")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /phyisicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca accesarea listei de investigatii de la consultatia unui alt medic.")        
        if consultatie:
            investigatii=consultatie["investigatii"]
            investigatie=next(inv for inv in investigatii if inv['id']==idi)
            if investigatie:
                investigatie_hateoas=InvestigatieHATEOAS(
                    id=investigatie['id'],
                    denumire=investigatie['denumire'],
                    durata_de_procesare=investigatie['durata_de_procesare'],
                    rezultat=investigatie['rezultat'],
                    links=LinkSet({
                            "self":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id'])},
                            "parent":{"href":"/api/medical_office_consultation/"+str(id)},
                            "get_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id']),"type":"GET"},
                            "delete_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id']),"type":"DELETE"},
                            "create_investigatie":{"href":"/api/medical_office_consultation/"+str(id),"type":"POST"},
                            "update_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie['id']),"type":"PUT"}
                            })
                    )
                return investigatie_hateoas
            else:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office_consultation/"+str(id)}} 
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}} 
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid la consultatie")
    except StopIteration:
           response.status_code=status.HTTP_404_NOT_FOUND
           return {"parent":{"href":"/api/medical_office_consultation/"+str(id)}}
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}   
           
@app.post("/api/medical_office_consultation/{id}/investigations")
async def create_investigatie(id:str,investigatie:CreateInvestigatie,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate adauga noi investigatii la consultatiile sale.")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /phyisicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca adaugarea la lista de consultatii a unui alt medic.")
        if consultatie:
            investigatie_model={"id":str(ObjectId()),"denumire":investigatie.denumire,"durata_de_procesare":investigatie.durata_de_procesare,"rezultat":investigatie.rezultat}
            investigatie_hateoas=InvestigatieHATEOAS(
                    id=investigatie_model['id'],
                    denumire=investigatie_model['denumire'],
                    durata_de_procesare=investigatie_model['durata_de_procesare'],
                    rezultat=investigatie_model['rezultat'],
                    links=LinkSet({
                            "self":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie_model['id'])},
                            "parent":{"href":"/api/medical_office_consultation/"+str(id)},
                            "get_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie_model['id']),"type":"GET"},
                            "delete_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie_model['id']),"type":"DELETE"},
                            "create_investigatie":{"href":"/api/medical_office_consultation/"+str(id),"type":"POST"},
                            "update_investigatie":{"href":"/api/medical_office_consultation/"+str(id)+"/investigations/"+str(investigatie_model['id']),"type":"PUT"}
                            })
                    )
            consultatie["investigatii"].append(investigatie_model)
            result = colectie.update_one({"_id": ObjectId(id)}, {"$set": consultatie})
            response.status_code=status.HTTP_201_CREATED
            return investigatie_hateoas
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid la consultatie") 
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}} 
@app.put("/api/medical_office_consultation/{id}/investigations/{idi}")
async def update_investigatie(id:str,idi:str,investigatie:CreateInvestigatie,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):
    try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate modifica investigatiile din consultatii.")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /physicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca modificarea unei investigatii din lista continuta in consultatia altui medic.")        
        if consultatie:
            investigatii=consultatie["investigatii"]
            investigatie_ex=next(inv for inv in investigatii if inv['id']==idi)
            if investigatie_ex:
               investigatie_ex["denumire"]=investigatie.denumire
               investigatie_ex["durata_de_procesare"]=investigatie.durata_de_procesare
               investigatie_ex["rezultat"]=investigatie.rezultat
               result = colectie.update_one({"_id": ObjectId(id)}, {"$set": consultatie})
               response.status_code=status.HTTP_204_NO_CONTENT 
            else:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office_consultation/"+str(id)}}
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}
    except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid la consultatie")
    except StopIteration:
           response.status_code=status.HTTP_404_NOT_FOUND
           return {"parent":{"href":"/api/medical_office_consultation/"+str(id)}}#Nu permit crearea unei noi investigatii din PUT, oblig doar la actualizarea celor existente
    except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}} 

@app.delete("/api/medical_office_consultation/{id}/investigations/{idi}")
async def delete_investigatie(id:str,idi:str,response:Response,current_user: str = Depends(oauth2_scheme),auth_service: AuthServiceStub = Depends(get_auth_service_stub)):  
     try:
        grpc_token_request = TokenRequest(token=current_user)
        token_response = auth_service.ValidateToken(grpc_token_request)
        if not token_response.valid:
            raise HTTPException(status_code=401, detail="Token-ul nu este valid")
        if token_response.role!="doctor":
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request) 
            raise HTTPException(status_code=403, detail="Doar doctorul poate sterge investigatiile din consultatii.")
        consultatie = colectie.find_one({"_id": ObjectId(id)})
        url = f"http://localhost:8000/api/medical_office/physicians/{consultatie['id_doctor']}?uid={token_response.sub}"#S-ar putea face si pe /phyisicians cu uid=true
        print(url)
        response1 = requests.get(url,headers={'Authorization':f"Bearer {current_user}"})
        if response1.status_code != 200:
            grpc_token_request = TokenRequest(token=current_user)
            auth_response= auth_service.DestroyToken(grpc_token_request)
            raise HTTPException(status_code=403, detail="Se incearca stergerea unei investigatii din consultatia altui medic.")     
        if consultatie:
            investigatii=consultatie["investigatii"]
            investigatie=next(inv for inv in investigatii if inv['id']==idi)
            if investigatie:
               consultatie["investigatii"].remove(investigatie)
               result = colectie.update_one({"_id": ObjectId(id)}, {"$set": consultatie})
               response.status_code=status.HTTP_204_NO_CONTENT 
            else:
                response.status_code=status.HTTP_404_NOT_FOUND
                return {"parent":{"href":"/api/medical_office_consultation/"+str(id)}}
        else:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}
     except errors.InvalidId:
           raise HTTPException(status_code=422, detail="Id invalid la consultatie")
     except StopIteration:
           response.status_code=status.HTTP_404_NOT_FOUND
           return {"parent":{"href":"/api/medical_office_consultation/"+str(id)}}
     except TypeError:
            response.status_code=status.HTTP_404_NOT_FOUND
            return {"parent":{"href":"/api/medical_office_consultation"}}          
           
