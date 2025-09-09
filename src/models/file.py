from sqlalchemy import event, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)

from ..database import Base

class File(Base):
    __tablename__ = "files"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=True, default="")
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    post_id = Column(Integer, ForeignKey('posts.id'), nullable=False)

    post = relationship("Post", back_populates="files")

# Event listener for after delete
@event.listens_for(File, 'after_delete')
def delete_file_after_delete(mapper, connection, target):
    """Delete the physical file after database record is deleted"""
    if target.file_path and os.path.exists(target.file_path):
        try:
            os.remove(target.file_path)
        except OSError as e:
            logger.error(f"Error deleting file {target.file_path}: {e}")