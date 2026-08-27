from pydantic import BaseModel, validator
from typing import Optional

class ProjectRequest(BaseModel):
    name: str
    description: str
    preferences: Optional[dict] = None
    
    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3 or len(v) > 100:
            raise ValueError('项目名称长度必须在3-100字符之间')
        return v
    
    @validator('description')
    def validate_description(cls, v):
        if len(v) < 10:
            raise ValueError('需求描述至少需要10个字符')
        return v