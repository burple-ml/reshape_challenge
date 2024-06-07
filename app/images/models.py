# Mostly used for static Pydantic request bodies or custom body definitions.

from pydantic import BaseModel
from fastapi import Depends
from fastapi import UploadFile, \
             File
from ..config import Base, IMAGE_OPS_SCHEMA
from sqlalchemy import Column, Integer, Text, text
from sqlalchemy.dialects.postgresql import UUID, NUMERIC
from .services import Session

# just an example, not used anywhere, because of problems with openapi.json spec.
class MultiFormData(BaseModel):
    image1: UploadFile = File(...)
    image2: UploadFile = File(...)


class ImageCrop(Base):
    __tablename__ = "crop"
    __table_args__ = {'schema': 'image_ops'}

    id = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), nullable=False)
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    data = Column(Text, nullable=False, primary_key=True)

    def add(self, db: Session):
        db.add(self)
        return db
    
    def commit(self, db: Session):
        db.commit()
        return db
    
    def refresh(self, db: Session):
        db.refresh(self)
        return db

class ImageDiff(Base, ImageCrop):
    __tablename__ = "diff"
    __table_args__ = {'schema': 'image_ops'}

    id = Column(UUID(as_uuid=True), server_default=text('uuid_generate_v4()'), nullable=False)
    score = Column(NUMERIC, nullable=False)
    image1 = Column(Text, nullable=False, primary_key=True)
    image2 = Column(Text, nullable=False, primary_key=True)