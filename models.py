from sqlalchemy import Column, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Image(Base):
    __tablename__ = "images"

    id = Column(String, primary_key=True, default=generate_uuid)
    filename = Column(String, unique=True, index=True)
    filepath = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    metadata_info = relationship("ImageMetadata", back_populates="image", uselist=False)

class ImageMetadata(Base):
    __tablename__ = "image_metadata"

    id = Column(String, primary_key=True, default=generate_uuid)
    image_id = Column(String, ForeignKey("images.id"), unique=True)
    subject = Column(String)
    category = Column(String)
    attributes = Column(JSON)
    caption = Column(String)
    confidence = Column(Float)
    embedding = Column(JSON) # Storing vector as JSON list of floats for SQLite simplicity
    api_cost = Column(Float, default=0.0) # Track AI cost

    image = relationship("Image", back_populates="metadata_info")

class Post(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, default=generate_uuid)
    content = Column(String)
    expected_category = Column(String) # For mismatch guard logic check
    embedding = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class Suggestion(Base):
    __tablename__ = "suggestions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    post_id = Column(String, ForeignKey("posts.id"))
    image_id = Column(String, ForeignKey("images.id"))
    similarity_score = Column(Float)
    status = Column(String, default="pending") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
