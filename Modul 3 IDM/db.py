from peewee import *
from fastapi_hypermodel import HyperModel, UrlFor, LinkSet
import pydantic
db = MySQLDatabase('medical_office_user', user='rares', password='rares', host='localhost', port=3306)
db_user=MySQLDatabase(database='medical_office_user',user='user',password='pass',host='localhost',port=3306)
class BaseModel(Model):
    class Meta:
        database = db_user

class Role(BaseModel):
    name = CharField(primary_key=True)

class User(BaseModel):
    uid = AutoField(primary_key=True)
    username = CharField(unique=True)
    password = CharField()
    role = ForeignKeyField(Role, backref='users')
class UserHATEOAS(HyperModel):
    uid:int
    username: str   
    role: str
    links:dict
class UserCreate(pydantic.BaseModel):
    username:str
    password:str
# Creează tabelele în baza de date
db.connect()
db.create_tables([Role,User])
try:
    admin_model= Role.get(Role.name=='admin')
except Role.DoesNotExist:
    admin = Role.create(name='admin')
    admin_model= Role.get(Role.name=='admin')
try:
    doctor_model= Role.get(Role.name=='doctor')
except Role.DoesNotExist:
    doctor = Role.create(name='doctor')
    doctor_model= Role.get(Role.name=='doctor')
try:
    pacient_model= Role.get(Role.name=='pacient')
except Role.DoesNotExist:
    pacient = Role.create(name='pacient')
    pacient_model= Role.get(Role.name=='pacient')
try:
    pacient1=User.get(User.username=='pacient1')
except User.DoesNotExist:
    pacient = User.create(
    #uid=1,
    username='pacient1',
    password='parola1',#de hash-uit
    role=pacient_model
    )
try:
    doctor1=User.get(User.username=='doctor1')
except User.DoesNotExist:
    doctor = User.create(
    #uid=2,
    username='doctor1',
    password='parola1',#de hash-uit
    role=doctor_model
    )
try:
    admin1=User.get(User.username=='admin1')
except User.DoesNotExist:
    admin = User.create(
    #uid=3,
    username='admin1',
    password='parola1',#de hash-uit
    role=admin_model
    )
try:
    pacient2=User.get(User.username=='pacient2')
except User.DoesNotExist:
    pacient = User.create(
    #uid=4,
    username='pacient2',
    password='parola2',#de hash-uit
    role=pacient_model
    )
try:
    doctor2=User.get(User.username=='doctor2')
except User.DoesNotExist:
    doctor = User.create(
    #uid=5,
    username='doctor2',
    password='parola2',#de hash-uit
    role=doctor_model
    )

