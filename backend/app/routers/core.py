from datetime import datetime
from pathlib import Path
import shutil
from fastapi import APIRouter, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from app.config import get_settings
from app.db import get_db
from app.models import Client, Item, ItemHistory, Event, TechnicalChecklist, ContractDocument, BackupRecord
from app.schemas import *
from app.deps import get_current_user, require_admin
from app.services.pdf_service import generate_contract_pdf

router = APIRouter()
settings = get_settings()

@router.get("/dashboard/admin")
def dashboard(db: Session = Depends(get_db), user = Depends(require_admin)):
    return {
      "clients": db.query(Client).count(),
      "items": db.query(Item).count(),
      "available_items": db.query(Item).filter(Item.status=="AVAILABLE").count(),
      "in_use_items": db.query(Item).filter(Item.status.in_(["IN_USE","RESERVED"])).count(),
      "maintenance_items": db.query(Item).filter(Item.status=="MAINTENANCE").count(),
      "events": db.query(Event).count(),
      "active_events": db.query(Event).filter(Event.status.in_(["PLANNED","READY","IN_PROGRESS"])).count(),
      "checklists_pending": db.query(TechnicalChecklist).filter(TechnicalChecklist.status=="PENDING").count(),
      "contracts": db.query(ContractDocument).count(),
      "backups": db.query(BackupRecord).count(),
      "latest_events": [{"id":x.id,"name":x.name,"status":x.status} for x in db.query(Event).order_by(Event.created_at.desc()).limit(5).all()],
      "latest_items": [{"id":x.id,"code":x.code,"name":x.name} for x in db.query(Item).order_by(Item.created_at.desc()).limit(5).all()],
    }

@router.get("/clients", response_model=list[ClientRead])
def clients(db: Session=Depends(get_db), user=Depends(get_current_user)): return db.query(Client).order_by(Client.name).all()
@router.post("/clients", response_model=ClientRead)
def create_client(p: ClientCreate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=Client(**p.model_dump()); db.add(o); db.commit(); db.refresh(o); return o
@router.put("/clients/{client_id}", response_model=ClientRead)
def update_client(client_id:int, p: ClientUpdate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(Client).filter(Client.id==client_id).first()
    if not o: raise HTTPException(status_code=404, detail="Cliente no encontrado")
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(o,k,v)
    db.commit(); db.refresh(o); return o
@router.delete("/clients/{client_id}")
def delete_client(client_id:int, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(Client).filter(Client.id==client_id).first()
    if not o: raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(o); db.commit(); return {"ok":True}

@router.get("/items", response_model=list[ItemRead])
def items(q: str|None=None, db: Session=Depends(get_db), user=Depends(get_current_user)):
    query=db.query(Item)
    if q:
        like=f"%{q}%"; query=query.filter((Item.code.like(like)) | (Item.qr_code.like(like)) | (Item.barcode.like(like)) | (Item.name.like(like)))
    return query.order_by(Item.name).all()
@router.post("/items", response_model=ItemRead)
def create_item(p: ItemCreate, db: Session=Depends(get_db), user=Depends(require_admin)):
    data=p.model_dump(); data["qr_code"]=data.get("qr_code") or data["code"]; o=Item(**data); db.add(o); db.commit(); db.refresh(o)
    db.add(ItemHistory(item_id=o.id, source="ITEM", description=f"Alta de equipo {o.name}", created_by=user.username)); db.commit(); return o
@router.put("/items/{item_id}", response_model=ItemRead)
def update_item(item_id:int, p: ItemUpdate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(Item).filter(Item.id==item_id).first()
    if not o: raise HTTPException(status_code=404, detail="Equipo no encontrado")
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(o,k,v)
    db.commit(); db.refresh(o)
    db.add(ItemHistory(item_id=o.id, source="ITEM", description=f"Edición de equipo {o.name}", created_by=user.username)); db.commit()
    return o
@router.delete("/items/{item_id}")
def delete_item(item_id:int, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(Item).filter(Item.id==item_id).first()
    if not o: raise HTTPException(status_code=404, detail="Equipo no encontrado")
    db.delete(o); db.commit(); return {"ok":True}
@router.get("/items/scan/{code}", response_model=ItemRead)
def scan(code: str, db: Session=Depends(get_db), user=Depends(get_current_user)):
    o=db.query(Item).filter((Item.code==code)|(Item.qr_code==code)|(Item.barcode==code)).first()
    if not o: raise HTTPException(status_code=404, detail="Equipo no encontrado")
    db.add(ItemHistory(item_id=o.id, source="SCAN", description=f"Escaneo: {code}", created_by=user.username)); db.commit(); return o
@router.get("/items/{item_id}/history", response_model=list[HistoryRead])
def history(item_id:int, db: Session=Depends(get_db), user=Depends(get_current_user)): return db.query(ItemHistory).filter(ItemHistory.item_id==item_id).order_by(ItemHistory.created_at.desc()).all()

@router.get("/events", response_model=list[EventRead])
def events(db: Session=Depends(get_db), user=Depends(get_current_user)): return db.query(Event).order_by(Event.start_date.desc()).all()
@router.post("/events", response_model=EventRead)
def create_event(p: EventCreate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=Event(**p.model_dump()); db.add(o); db.commit(); db.refresh(o); return o
@router.put("/events/{event_id}", response_model=EventRead)
def update_event(event_id:int, p: EventUpdate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(Event).filter(Event.id==event_id).first()
    if not o: raise HTTPException(status_code=404, detail="Evento no encontrado")
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(o,k,v)
    db.commit(); db.refresh(o); return o
@router.delete("/events/{event_id}")
def delete_event(event_id:int, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(Event).filter(Event.id==event_id).first()
    if not o: raise HTTPException(status_code=404, detail="Evento no encontrado")
    db.delete(o); db.commit(); return {"ok":True}

@router.get("/checklists", response_model=list[ChecklistRead])
def checklists(db: Session=Depends(get_db), user=Depends(get_current_user)): return db.query(TechnicalChecklist).order_by(TechnicalChecklist.created_at.desc()).all()
@router.post("/checklists", response_model=ChecklistRead)
def create_checklist(p: ChecklistCreate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=TechnicalChecklist(**p.model_dump(), checks_json="[]"); db.add(o); db.commit(); db.refresh(o)
    if o.item_id: db.add(ItemHistory(item_id=o.item_id, source="CHECKLIST", description=f"Checklist: {o.title}", created_by=user.username)); db.commit()
    return o
@router.put("/checklists/{checklist_id}", response_model=ChecklistRead)
def update_checklist(checklist_id:int, p: ChecklistUpdate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(TechnicalChecklist).filter(TechnicalChecklist.id==checklist_id).first()
    if not o: raise HTTPException(status_code=404, detail="Checklist no encontrado")
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(o,k,v)
    db.commit(); db.refresh(o); return o
@router.delete("/checklists/{checklist_id}")
def delete_checklist(checklist_id:int, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(TechnicalChecklist).filter(TechnicalChecklist.id==checklist_id).first()
    if not o: raise HTTPException(status_code=404, detail="Checklist no encontrado")
    db.delete(o); db.commit(); return {"ok":True}

@router.get("/contracts", response_model=list[ContractRead])
def contracts(db: Session=Depends(get_db), user=Depends(get_current_user)): return db.query(ContractDocument).order_by(ContractDocument.created_at.desc()).all()
@router.post("/contracts", response_model=ContractRead)
def create_contract(p: ContractCreate, db: Session=Depends(get_db), user=Depends(require_admin)):
    number=datetime.utcnow().strftime("CTR-%Y%m%d-%H%M%S"); path=f"/data/contracts/{number}.pdf"; url=f"{settings.public_base_url}:8000/static/contracts/{number}.pdf"
    client=db.query(Client).filter(Client.id==p.client_id).first() if p.client_id else None
    event=db.query(Event).filter(Event.id==p.event_id).first() if p.event_id else None
    meta={"Documento":number,"Cliente":client.name if client else "-","Evento":event.name if event else "-","Lugar":event.location if event else "-","Operador":event.operator_name if event else user.username}
    generate_contract_pdf(path, p.title, meta, p.terms)
    o=ContractDocument(document_number=number,title=p.title,client_id=p.client_id,event_id=p.event_id,status=p.status,file_path=path,public_url=url,terms=p.terms,created_by=user.username)
    db.add(o); db.commit(); db.refresh(o); return o
@router.put("/contracts/{contract_id}", response_model=ContractRead)
def update_contract(contract_id:int, p: ContractUpdate, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(ContractDocument).filter(ContractDocument.id==contract_id).first()
    if not o: raise HTTPException(status_code=404, detail="Contrato no encontrado")
    for k,v in p.model_dump(exclude_unset=True).items(): setattr(o,k,v)
    db.commit(); db.refresh(o); return o
@router.delete("/contracts/{contract_id}")
def delete_contract(contract_id:int, db: Session=Depends(get_db), user=Depends(require_admin)):
    o=db.query(ContractDocument).filter(ContractDocument.id==contract_id).first()
    if not o: raise HTTPException(status_code=404, detail="Contrato no encontrado")
    db.delete(o); db.commit(); return {"ok":True}

@router.get("/backups", response_model=list[BackupRead])
def backups(db: Session=Depends(get_db), user=Depends(require_admin)): return db.query(BackupRecord).order_by(BackupRecord.created_at.desc()).all()
@router.post("/backups/run", response_model=BackupRead)
def run_backup(db: Session=Depends(get_db), user=Depends(require_admin)):
    Path("/data/backups").mkdir(parents=True, exist_ok=True)
    name=datetime.utcnow().strftime("backup_%Y%m%d_%H%M%S.db"); target=f"/data/backups/{name}"; shutil.copy2("/data/stock_control.db", target)
    o=BackupRecord(file_name=name,file_path=target,status="CREATED",triggered_by=user.username); db.add(o); db.commit(); db.refresh(o); return o
