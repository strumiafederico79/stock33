from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
class LoginRequest(BaseModel):
    username: str
    password: str
class UserRead(BaseModel):
    id: int; username: str; full_name: str; role: str; is_active: bool
    class Config: from_attributes = True
class UserCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: str = "operator"
class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class ClientCreate(BaseModel):
    name: str; company_name: Optional[str]=None; phone: Optional[str]=None; email: Optional[str]=None; address: Optional[str]=None; notes: Optional[str]=None
class ClientUpdate(BaseModel):
    name: Optional[str]=None; company_name: Optional[str]=None; phone: Optional[str]=None; email: Optional[str]=None; address: Optional[str]=None; notes: Optional[str]=None
class ClientRead(ClientCreate):
    id: int; created_at: datetime
    class Config: from_attributes = True

class ItemCreate(BaseModel):
    code: str; qr_code: Optional[str]=None; barcode: Optional[str]=None; name: str; category: Optional[str]=None; status: str="AVAILABLE"; location: Optional[str]=None; replacement_value: Optional[float]=None; notes: Optional[str]=None
class ItemUpdate(BaseModel):
    code: Optional[str]=None; qr_code: Optional[str]=None; barcode: Optional[str]=None; name: Optional[str]=None; category: Optional[str]=None; status: Optional[str]=None; location: Optional[str]=None; replacement_value: Optional[float]=None; notes: Optional[str]=None
class ItemRead(ItemCreate):
    id: int; created_at: datetime
    class Config: from_attributes = True

class EventCreate(BaseModel):
    name: str; client_id: Optional[int]=None; location: Optional[str]=None; start_date: date; end_date: date; status: str="PLANNED"; operator_name: Optional[str]=None; notes: Optional[str]=None
class EventUpdate(BaseModel):
    name: Optional[str]=None; client_id: Optional[int]=None; location: Optional[str]=None; start_date: Optional[date]=None; end_date: Optional[date]=None; status: Optional[str]=None; operator_name: Optional[str]=None; notes: Optional[str]=None
class EventRead(EventCreate):
    id: int; created_at: datetime
    class Config: from_attributes = True

class ChecklistCreate(BaseModel):
    item_id: Optional[int]=None; event_id: Optional[int]=None; title: str; status: str="PENDING"; performed_by: Optional[str]=None; notes: Optional[str]=None
class ChecklistUpdate(BaseModel):
    item_id: Optional[int]=None; event_id: Optional[int]=None; title: Optional[str]=None; status: Optional[str]=None; performed_by: Optional[str]=None; notes: Optional[str]=None
class ChecklistRead(ChecklistCreate):
    id: int; checks_json: str; created_at: datetime
    class Config: from_attributes = True

class ContractCreate(BaseModel):
    title: str; client_id: Optional[int]=None; event_id: Optional[int]=None; status: str="DRAFT"; terms: Optional[str]=None
class ContractUpdate(BaseModel):
    title: Optional[str]=None; client_id: Optional[int]=None; event_id: Optional[int]=None; status: Optional[str]=None; terms: Optional[str]=None
class ContractRead(BaseModel):
    id: int; document_number: str; title: str; client_id: Optional[int]; event_id: Optional[int]; status: str; file_path: Optional[str]; public_url: Optional[str]; terms: Optional[str]; created_by: Optional[str]; created_at: datetime
    class Config: from_attributes = True

class BackupRead(BaseModel):
    id: int; file_name: str; file_path: str; status: str; triggered_by: Optional[str]; created_at: datetime
    class Config: from_attributes = True

class HistoryRead(BaseModel):
    id: int; item_id: int; source: str; description: str; created_by: Optional[str]; created_at: datetime
    class Config: from_attributes = True
