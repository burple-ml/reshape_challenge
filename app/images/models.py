# Mostly used for static Pydantic request bodies or custom body definitions.

from pydantic import BaseModel
from fastapi import Depends
from fastapi import UploadFile, \
             File
from ..config import Base, IMAGE_OPS_SCHEMA
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID, TEXT

# just an example, not used anywhere, because of problems with openapi.json spec.
class MultiFormData(BaseModel):
    image1: UploadFile = File(...)
    image2: UploadFile = File(...)



class ImageCrop(Base):
    __tablename__ = "crop"
    __table_args__ = {'schema': 'image_ops'}

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=TEXT('uuid_generate_v4()'))
    name = Column(String, index=True)
    url = Column(String)
    data = Column(String)