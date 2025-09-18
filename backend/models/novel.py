from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Novel(Base):

    __tablename__ = "novels"

 
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    genre = Column(String, nullable=True)
    status = Column(String, default="draft")  # draft, published, completed
    is_public = Column(Boolean, default=False)
    cover_image_url = Column(String, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    word_count = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)

    # Связи
    author = relationship("User", back_populates="novels")
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan", lazy="dynamic") 