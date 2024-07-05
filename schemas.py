from datetime import datetime
from typing import Optional
from pydantic import BaseModel, PositiveFloat
from uuid import UUID

# schema JSON
# model em relação ao SGBD

class SchemaUUID(BaseModel):
    id : UUID

class SchemaBasico(SchemaUUID):
    nome : str
    criado_em : datetime = datetime.now()
    alterado_em : datetime = datetime.now()

class SchemaComplementarStore(BaseModel):
    nome : str
    quantidade : int
    preco : PositiveFloat
    status : bool

class Store(SchemaBasico, SchemaComplementarStore):
    pass

class SchemaStoreUpdate(SchemaUUID):
    nome : Optional[str]
    quantidade : Optional[int]
    preco : Optional[PositiveFloat]
    status : Optional[bool]
    
 