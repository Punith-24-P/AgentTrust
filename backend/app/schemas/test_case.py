from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class RequiredFactSchema(BaseModel):
    id: str
    type: str  # "section", "date", "duration", "authority", "number", "named_entity", "condition", "exception", "keyword", "custom"
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
    expected_retrieval: bool = True
    expected_tools: List[str] = Field(default_factory=list)


class TestCaseCreate(TestCaseBase):
    dataset_id: Optional[str] = None
    version: Optional[str] = "1.0.0"


class TestCaseResponse(TestCaseBase):
    id: str
    dataset_id: str
    version: Optional[str] = "1.0.0"
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetVersionCreate(BaseModel):
    version: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")
    changelog: Optional[str] = ""


class DatasetVersionResponse(BaseModel):
    id: str
    dataset_id: str
    version: str
    is_published: bool
    test_cases_count: int
    changelog: Optional[str]
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
    versions: List[DatasetVersionResponse] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DatasetValidationIssue(BaseModel):
    test_case_id: Optional[str] = None
    level: str  # "ERROR", "WARNING"
    field: str
    message: str


class DatasetValidationReport(BaseModel):
    dataset_id: str
    is_valid: bool
    total_test_cases: int
    errors_count: int
    warnings_count: int
    issues: List[DatasetValidationIssue] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
