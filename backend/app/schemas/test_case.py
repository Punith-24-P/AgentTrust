from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RequiredFactSchema(BaseModel):
    id: str
    type: str  # "section", "date", "authority", "number", "deadline", "entity"
    expected: str
    description: Optional[str] = ""


class SourceDocumentRef(BaseModel):
    document_id: str
    section_id: Optional[str] = None


class TestCaseBase(BaseModel):
    external_id: str
    language: str
    category: str = "general"
    question: str
    expected_answer: str
    source_documents: List[SourceDocumentRef] = Field(default_factory=list)
    required_facts: List[RequiredFactSchema] = Field(default_factory=list)
    potential_traps: List[str] = Field(default_factory=list)


class TestCaseCreate(TestCaseBase):
    dataset_id: Optional[str] = None


class TestCaseResponse(TestCaseBase):
    id: str
    dataset_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = ""
    version: str = "1.0.0"


class DatasetCreate(DatasetBase):
    project_id: str


class DatasetResponse(DatasetBase):
    id: str
    project_id: str
    test_cases_count: Optional[int] = 0
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
