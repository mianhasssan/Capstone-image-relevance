from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ImageTags(BaseModel):
    subject: str = Field(description="The primary subject of the image (e.g. 'red fox')")
    category: str = Field(description="The general category (e.g. 'animal', 'landscape')")
    attributes: List[str] = Field(description="A list of attributes describing the image (e.g. ['orange fur', 'wild'])")
    caption: str = Field(description="A short descriptive caption of what is happening in the image")
    confidence: float = Field(description="A confidence score between 0.0 and 1.0 representing how sure the model is")

class ImageResponse(BaseModel):
    id: str
    filename: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class ImageMetadataResponse(BaseModel):
    subject: str
    category: str
    attributes: List[str]
    caption: str
    confidence: float
    api_cost: float

    class Config:
        orm_mode = True

class PostCreate(BaseModel):
    content: str = Field(description="The blog post text")
    expected_category: str = Field(description="The expected image category (e.g. 'animal', 'landscape')")

class PostResponse(BaseModel):
    id: str
    content: str
    expected_category: str
    
    class Config:
        orm_mode = True

class MatchResult(BaseModel):
    status: str
    reason: Optional[str] = None
    image: Optional[ImageResponse] = None
    similarity_score: Optional[float] = None
    suggestion_id: Optional[str] = None

class SuggestionResponse(BaseModel):
    id: str
    post_id: str
    image_id: str
    similarity_score: float
    status: str
    
    class Config:
        orm_mode = True
