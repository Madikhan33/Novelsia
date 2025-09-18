from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Chapter(Base):
 
    __tablename__ = "chapters"


    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    chapter_number = Column(Integer)
    word_count = Column(Integer, default=0)
    reading_time = Column(Float, default=0.0)  # в минутах
    novel_id = Column(Integer, ForeignKey("novels.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_published = Column(Boolean, default=False)
    views_count = Column(Integer, default=0)

    # Связи
    novel = relationship("Novel", back_populates="chapters") 