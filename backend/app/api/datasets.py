from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.dataset import Dataset, TestCase
from app.schemas.test_case import DatasetCreate, DatasetResponse, TestCaseCreate, TestCaseResponse
import json

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("", response_model=DatasetResponse)
async def create_dataset(data: DatasetCreate, db: AsyncSession = Depends(get_db)):
    dataset = Dataset(
        project_id=data.project_id,
        name=data.name,
        description=data.description,
        version=data.version
    )
    db.add(dataset)
    await db.commit()
    await db.refresh(dataset)
    return dataset


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(project_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Dataset)
    if project_id:
        q = q.where(Dataset.project_id == project_id)
    q = q.order_by(Dataset.created_at.desc())
    res = await db.execute(q)
    datasets = res.scalars().all()

    # Count test cases for each
    results = []
    for d in datasets:
        cnt_q = select(func.count(TestCase.id)).where(TestCase.dataset_id == d.id)
        cnt_res = await db.execute(cnt_q)
        cnt = cnt_res.scalar() or 0
        d_dict = {
            "id": d.id,
            "project_id": d.project_id,
            "name": d.name,
            "description": d.description,
            "version": d.version,
            "test_cases_count": cnt,
            "created_at": d.created_at
        }
        results.append(DatasetResponse(**d_dict))
    return results


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(q)
    d = res.scalars().first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")
    cnt_q = select(func.count(TestCase.id)).where(TestCase.dataset_id == d.id)
    cnt_res = await db.execute(cnt_q)
    cnt = cnt_res.scalar() or 0
    return DatasetResponse(
        id=d.id,
        project_id=d.project_id,
        name=d.name,
        description=d.description,
        version=d.version,
        test_cases_count=cnt,
        created_at=d.created_at
    )


@router.get("/{dataset_id}/test-cases", response_model=List[TestCaseResponse])
async def list_test_cases(dataset_id: str, language: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(TestCase).where(TestCase.dataset_id == dataset_id)
    if language:
        q = q.where(TestCase.language == language.lower())
    q = q.order_by(TestCase.external_id)
    res = await db.execute(q)
    return res.scalars().all()


@router.post("/{dataset_id}/test-cases", response_model=TestCaseResponse)
async def create_test_case(dataset_id: str, data: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    tc = TestCase(
        dataset_id=dataset_id,
        external_id=data.external_id,
        language=data.language,
        category=data.category,
        question=data.question,
        expected_answer=data.expected_answer,
        source_documents=[d.model_dump() for d in data.source_documents],
        required_facts=[f.model_dump() for f in data.required_facts],
        potential_traps=data.potential_traps
    )
    db.add(tc)
    await db.commit()
    await db.refresh(tc)
    return tc


@router.post("/{dataset_id}/import-json")
async def import_json_test_cases(dataset_id: str, cases: List[Dict[str, Any]], db: AsyncSession = Depends(get_db)):
    count = 0
    for c in cases:
        tc = TestCase(
            dataset_id=dataset_id,
            external_id=c.get("id", f"TC-{count+1}"),
            language=c.get("language", "en"),
            category=c.get("category", "general"),
            question=c.get("question", ""),
            expected_answer=c.get("expected_answer", ""),
            source_documents=c.get("source_documents", []),
            required_facts=c.get("required_facts", []),
            potential_traps=c.get("potential_traps", [])
        )
        db.add(tc)
        count += 1
    await db.commit()
    return {"status": "SUCCESS", "imported_count": count}
