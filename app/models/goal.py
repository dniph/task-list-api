from sqlalchemy.orm import Mapped, mapped_column, relationship
from ..db import db
from typing import List, Optional

from typing import TYPE_CHECKING
if TYPE_CHECKING: from .task import Task

class Goal(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str]
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="goal")  
    
    @classmethod
    def from_dict(cls, goal_data):
        new_goal = Goal(title=goal_data["title"])
        return new_goal

    def to_dict(self, include_tasks=False, include_task_ids=False):
        goal_dict = {
            "id": self.id,
            "title": self.title
        }
        if include_tasks:
            goal_dict["tasks"] = [task.to_dict() for task in self.tasks]
        if include_task_ids:  
            goal_dict["task_ids"] = [task.id for task in self.tasks]
        return goal_dict