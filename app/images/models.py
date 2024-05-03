# Mostly used for static Pydantic request bodies or custom body definitions.

from pydantic import BaseModel
from fastapi import Depends
from fastapi import UploadFile, \
             File

# just an example, not used anywhere, because of problems with openapi.json spec.
class MultiFormData(BaseModel):
    image1: UploadFile = File(...)
    image2: UploadFile = File(...)