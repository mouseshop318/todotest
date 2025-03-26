from dataclasses import dataclass, field, asdict
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import uuid

@dataclass
class Task:
    """Task data model for the to-do management system."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sub_task: str = ""
    main_task: str = ""
    priority: str = "Medium"
    status: str = "Not Started"
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    responsible: str = ""
    notes: str = ""
    status_update_time: datetime = field(default_factory=datetime.now)
    is_deleted: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        task_dict = asdict(self)
        # Convert datetime and date objects to strings for JSON serialization
        if self.status_update_time:
            task_dict['status_update_time'] = self.status_update_time.isoformat()
        if self.start_date:
            task_dict['start_date'] = self.start_date.isoformat()
        if self.end_date:
            task_dict['end_date'] = self.end_date.isoformat()
        return task_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create a Task object from a dictionary."""
        # Convert string dates back to date objects
        if 'start_date' in data and data['start_date']:
            if isinstance(data['start_date'], str):
                data['start_date'] = date.fromisoformat(data['start_date'])
        if 'end_date' in data and data['end_date']:
            if isinstance(data['end_date'], str):
                data['end_date'] = date.fromisoformat(data['end_date'])
        if 'status_update_time' in data and data['status_update_time']:
            if isinstance(data['status_update_time'], str):
                data['status_update_time'] = datetime.fromisoformat(data['status_update_time'])
        return cls(**data)

@dataclass
class SystemParameter:
    """System parameter data model."""
    param_type: str
    param_value: str
    
    def to_dict(self) -> Dict[str, str]:
        """Convert parameter to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'SystemParameter':
        """Create a SystemParameter object from a dictionary."""
        return cls(**data)
