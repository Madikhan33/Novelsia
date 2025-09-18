from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class AISuggestion(Base):
 
    __tablename__ = "ai_suggestions"

    id = Column(Integer, primary_key=True, index=True)
    suggestion_type = Column(String, index=True, default="continuation")  # continuation, plot_idea, character_development, etc.
    content = Column(Text)
    context = Column(Text, nullable=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"), nullable=True)
    novel_id = Column(Integer, ForeignKey("novels.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_used = Column(Boolean, default=False)
    rating = Column(Integer, default=0,  nullable=True)  # 1-5
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    model_used = Column(String, default="gpt-4o-mini", nullable=True)
    tokens_used = Column(Integer, default=0, nullable=True)
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    chapter = relationship("Chapter")
    novel = relationship("Novel")
    user = relationship("User") 