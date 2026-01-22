from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.models import Batch, BatchStatus, get_db
from backend.routers.auth import get_current_admin


router = APIRouter(prefix="/api/admin/batches", tags=["admin-batches"])


class BatchBase(BaseModel):
  batch_id: str
  product_name: str
  origin_info: Optional[str] = None
  process_info: Optional[str] = None
  logistics_static: Optional[str] = None
  quality_report: Optional[str] = None
  status: BatchStatus = BatchStatus.NORMAL


class BatchCreate(BatchBase):
  pass


class BatchUpdate(BaseModel):
  product_name: Optional[str] = None
  origin_info: Optional[str] = None
  process_info: Optional[str] = None
  logistics_static: Optional[str] = None
  quality_report: Optional[str] = None
  status: Optional[BatchStatus] = None


class BatchOut(BatchBase):
  scan_count: int
  created_at: Optional[datetime] = None

  class Config:
    orm_mode = True


@router.get("/", response_model=List[BatchOut])
def list_batches(
  batch_id: Optional[str] = Query(default=None),
  product_name: Optional[str] = Query(default=None),
  status_filter: Optional[BatchStatus] = Query(default=None, alias="status"),
  skip: int = 0,
  limit: int = 50,
  db: Session = Depends(get_db),
  _: object = Depends(get_current_admin),
):
  query = db.query(Batch)

  if batch_id:
    query = query.filter(Batch.batch_id.contains(batch_id))
  if product_name:
    query = query.filter(Batch.product_name.contains(product_name))
  if status_filter is not None:
    query = query.filter(Batch.status == status_filter)

  items = query.order_by(Batch.created_at.desc()).offset(skip).limit(limit).all()
  return items


@router.get("/{batch_id}/", response_model=BatchOut)
def get_batch(
  batch_id: str,
  db: Session = Depends(get_db),
  _: object = Depends(get_current_admin),
):
  batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
  if not batch:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")
  return batch


@router.post("/", response_model=BatchOut, status_code=status.HTTP_201_CREATED)
def create_batch(
  payload: BatchCreate,
  db: Session = Depends(get_db),
  _: object = Depends(get_current_admin),
):
  exists = db.query(Batch).filter(Batch.batch_id == payload.batch_id).first()
  if exists:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="batch_id already exists")

  batch = Batch(
    batch_id=payload.batch_id,
    product_name=payload.product_name,
    origin_info=payload.origin_info,
    process_info=payload.process_info,
    logistics_static=payload.logistics_static,
    quality_report=payload.quality_report,
    status=payload.status,
    scan_count=0,
  )
  db.add(batch)
  db.commit()
  db.refresh(batch)
  return batch


@router.put("/{batch_id}/", response_model=BatchOut)
def update_batch(
  batch_id: str,
  payload: BatchUpdate,
  db: Session = Depends(get_db),
  _: object = Depends(get_current_admin),
):
  batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
  if not batch:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

  data = payload.dict(exclude_unset=True)
  for field, value in data.items():
    setattr(batch, field, value)

  db.add(batch)
  db.commit()
  db.refresh(batch)
  return batch


@router.delete("/{batch_id}/", status_code=status.HTTP_204_NO_CONTENT)
def delete_batch(
  batch_id: str,
  db: Session = Depends(get_db),
  _: object = Depends(get_current_admin),
):
  batch = db.query(Batch).filter(Batch.batch_id == batch_id).first()
  if not batch:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Batch not found")

  db.delete(batch)
  db.commit()
  return None
