
import uuid
from sqlalchemy import Column, TIMESTAMP, ForeignKey, func, String
from sqlalchemy.dialects.postgresql import JSONB
from db import Base

class UserActivityData(Base):
    __tablename__ = 'user_activity'

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = Column("user_id", String, primary_key=True, nullable=False)
    record_id = Column("record_id", String, ForeignKey("record.record_id"), nullable=True) #foriegn key to record table record_id
    project_id = Column("project_id", String,ForeignKey("project.project_system_id"), nullable=True) #foriegn key to project table project_id
    location_id = Column("location_id", String,ForeignKey("location.location_id"), nullable=True) #foriegn key to location table location_id
    action = Column("action", String, nullable=False)
    created = Column(TIMESTAMP, default=func.now(), nullable=False)
    
