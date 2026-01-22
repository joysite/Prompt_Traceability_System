from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models import Batch, ScanLog, get_db
from backend.routers.auth import get_current_admin


router = APIRouter(prefix="/api", tags=["trace"])


class TraceResponse(BaseModel):
    batch_id: str
    product_name: str
    origin_info: Optional[str] = None
    process_info: Optional[str] = None
    logistics_static: Optional[str] = None
    quality_report: Optional[str] = None
    scan_count: int
    status: str

    class Config:
        orm_mode = True


class CloneRequest(BaseModel):
    old_batch_id: str
    new_batch_id: Optional[str] = None


class CloneResponse(BaseModel):
    batch_id: str
    created_at: datetime


@router.get("/trace/{batch_id}", response_model=TraceResponse)
def trace_batch(batch_id: str, request: Request, db: Session = Depends(get_db)):
    batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

    batch.scan_count = (batch.scan_count or 0) + 1

    client_ip = request.client.host if request.client else None
    log = ScanLog(batch_id=batch.batch_id, ip_address=client_ip)
    db.add(log)
    db.add(batch)
    db.commit()
    db.refresh(batch)

    return batch


@router.post("/admin/batch/clone", response_model=CloneResponse)
def clone_batch(
    payload: CloneRequest,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_admin),
):
    old = db.query(Batch).filter(Batch.batch_id == payload.old_batch_id).first()
    if not old:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source batch not found")

    if payload.new_batch_id is None:
        # simple new id generation rule for MVP; can be replaced by a more robust ID generator
        suffix = int(datetime.utcnow().timestamp())
        new_batch_id = f"{old.batch_id}-{suffix}"
    else:
        new_batch_id = payload.new_batch_id

    exists = db.query(Batch).filter(Batch.batch_id == new_batch_id).first()
    if exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="new_batch_id already exists")

    new_batch = Batch(
        batch_id=new_batch_id,
        product_name=old.product_name,
        origin_info=old.origin_info,
        process_info=old.process_info,
        logistics_static=old.logistics_static,
        quality_report=old.quality_report,
        scan_count=0,
        status=old.status,
    )

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)

    return CloneResponse(batch_id=new_batch.batch_id, created_at=new_batch.created_at)
