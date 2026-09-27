import csv
import io
import json
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.dataset import Dataset, DatasetVersion, TestCase
from app.models.document import Document
from app.schemas.test_case import (
    DatasetCreate,
    DatasetResponse,
    DatasetVersionCreate,
    DatasetVersionResponse,
    TestCaseCreate,
    TestCaseResponse,
    DatasetValidationReport,
    DatasetValidationIssue,
)
from app.api.deps import get_optional_user, log_audit_event

router = APIRouter(prefix="/datasets", tags=["Datasets"])

VALID_LANGUAGES = {"en", "hi", "kn", "te", "es", "fr", "de", "ja", "zh"}
VALID_FACT_TYPES = {
    "number", "date", "duration", "section", "authority",
    "named_entity", "condition", "exception", "keyword", "custom"
}


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset(
    data: DatasetCreate,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    dataset = Dataset(
        project_id=data.project_id,
        name=data.name.strip(),
        description=data.description or "",
        version=data.version or "1.0.0"
    )
    db.add(dataset)
    await db.flush()

    # Create initial version 1.0.0
    initial_version = DatasetVersion(
        dataset_id=dataset.id,
        version=dataset.version,
        is_published=True,
        test_cases_count=0,
        changelog="Initial dataset creation"
    )
    db.add(initial_version)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="DATASET_CREATED",
            entity_type="dataset",
            entity_id=dataset.id,
            user_id=current_user.id,
            details={"name": dataset.name, "version": dataset.version}
        )

    return DatasetResponse(
        id=dataset.id,
        project_id=dataset.project_id,
        name=dataset.name,
        description=dataset.description,
        version=dataset.version,
        test_cases_count=0,
        versions=[DatasetVersionResponse.model_validate(initial_version)],
        created_at=dataset.created_at
    )


@router.get("", response_model=List[DatasetResponse])
async def list_datasets(project_id: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(Dataset)
    if project_id:
        q = q.where(Dataset.project_id == project_id)
    q = q.order_by(Dataset.created_at.desc())
    res = await db.execute(q)
    datasets = res.scalars().all()

    results = []
    for d in datasets:
        cnt_q = select(func.count(TestCase.id)).where(TestCase.dataset_id == d.id)
        cnt_res = await db.execute(cnt_q)
        cnt = cnt_res.scalar() or 0

        v_q = select(DatasetVersion).where(DatasetVersion.dataset_id == d.id).order_by(DatasetVersion.created_at.desc())
        v_res = await db.execute(v_q)
        versions = [DatasetVersionResponse.model_validate(v) for v in v_res.scalars().all()]

        results.append(
            DatasetResponse(
                id=d.id,
                project_id=d.project_id,
                name=d.name,
                description=d.description,
                version=d.version,
                test_cases_count=cnt,
                versions=versions,
                created_at=d.created_at
            )
        )
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

    v_q = select(DatasetVersion).where(DatasetVersion.dataset_id == d.id).order_by(DatasetVersion.created_at.desc())
    v_res = await db.execute(v_q)
    versions = [DatasetVersionResponse.model_validate(v) for v in v_res.scalars().all()]

    return DatasetResponse(
        id=d.id,
        project_id=d.project_id,
        name=d.name,
        description=d.description,
        version=d.version,
        test_cases_count=cnt,
        versions=versions,
        created_at=d.created_at
    )


@router.put("/{dataset_id}", response_model=DatasetResponse)
async def update_dataset(
    dataset_id: str,
    data: DatasetCreate,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    q = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(q)
    d = res.scalars().first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    d.name = data.name.strip()
    d.description = data.description or ""
    if data.version:
        d.version = data.version
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="DATASET_UPDATED",
            entity_type="dataset",
            entity_id=d.id,
            user_id=current_user.id,
            details={"name": d.name, "version": d.version}
        )

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
        versions=[],
        created_at=d.created_at
    )


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dataset(
    dataset_id: str,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    q = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(q)
    d = res.scalars().first()
    if not d:
        raise HTTPException(status_code=404, detail="Dataset not found")

    await db.delete(d)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="DATASET_DELETED",
            entity_type="dataset",
            entity_id=dataset_id,
            user_id=current_user.id
        )


@router.post("/{dataset_id}/duplicate", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_dataset(
    dataset_id: str,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    q = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(q)
    original = res.scalars().first()
    if not original:
        raise HTTPException(status_code=404, detail="Dataset not found")

    new_dataset = Dataset(
        project_id=original.project_id,
        name=f"{original.name} (Copy)",
        description=original.description,
        version="1.0.0"
    )
    db.add(new_dataset)
    await db.flush()

    # Duplicate test cases
    tc_q = select(TestCase).where(TestCase.dataset_id == original.id)
    tc_res = await db.execute(tc_q)
    original_tcs = tc_res.scalars().all()

    for tc in original_tcs:
        new_tc = TestCase(
            dataset_id=new_dataset.id,
            external_id=tc.external_id,
            language=tc.language,
            category=tc.category,
            question=tc.question,
            expected_answer=tc.expected_answer,
            source_documents=tc.source_documents,
            required_facts=tc.required_facts,
            potential_traps=tc.potential_traps,
            expected_retrieval=tc.expected_retrieval,
            expected_tools=tc.expected_tools,
            version="1.0.0"
        )
        db.add(new_tc)

    # Initial version for duplicate
    new_version = DatasetVersion(
        dataset_id=new_dataset.id,
        version="1.0.0",
        is_published=True,
        test_cases_count=len(original_tcs),
        changelog=f"Cloned from {original.name} v{original.version}"
    )
    db.add(new_version)
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="DATASET_DUPLICATED",
            entity_type="dataset",
            entity_id=new_dataset.id,
            user_id=current_user.id,
            details={"source_id": original.id, "name": new_dataset.name}
        )

    return DatasetResponse(
        id=new_dataset.id,
        project_id=new_dataset.project_id,
        name=new_dataset.name,
        description=new_dataset.description,
        version=new_dataset.version,
        test_cases_count=len(original_tcs),
        versions=[DatasetVersionResponse.model_validate(new_version)],
        created_at=new_dataset.created_at
    )


@router.post("/{dataset_id}/versions", response_model=DatasetVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_dataset_version(
    dataset_id: str,
    data: DatasetVersionCreate,
    current_user=Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    q = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(q)
    dataset = res.scalars().first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Check if version string already exists
    existing_v = await db.execute(
        select(DatasetVersion).where(
            DatasetVersion.dataset_id == dataset_id,
            DatasetVersion.version == data.version
        )
    )
    if existing_v.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Version {data.version} already exists for this dataset")

    cnt_q = select(func.count(TestCase.id)).where(TestCase.dataset_id == dataset_id)
    cnt_res = await db.execute(cnt_q)
    test_count = cnt_res.scalar() or 0

    new_version = DatasetVersion(
        dataset_id=dataset_id,
        version=data.version,
        is_published=True,
        test_cases_count=test_count,
        changelog=data.changelog or f"Published version {data.version}"
    )
    db.add(new_version)

    # Update dataset current version pointer
    dataset.version = data.version
    await db.flush()

    if current_user:
        await log_audit_event(
            db=db,
            action="DATASET_VERSION_PUBLISHED",
            entity_type="dataset_version",
            entity_id=new_version.id,
            user_id=current_user.id,
            details={"dataset_id": dataset_id, "version": data.version}
        )

    return DatasetVersionResponse.model_validate(new_version)


@router.get("/{dataset_id}/validate", response_model=DatasetValidationReport)
async def validate_dataset(dataset_id: str, db: AsyncSession = Depends(get_db)):
    q = select(Dataset).where(Dataset.id == dataset_id)
    res = await db.execute(q)
    dataset = res.scalars().first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    tc_q = select(TestCase).where(TestCase.dataset_id == dataset_id)
    tc_res = await db.execute(tc_q)
    test_cases = tc_res.scalars().all()

    issues: List[DatasetValidationIssue] = []
    seen_ids = set()
    languages_seen = set()

    for tc in test_cases:
        # Check duplicate IDs
        if tc.external_id in seen_ids:
            issues.append(
                DatasetValidationIssue(
                    test_case_id=tc.id,
                    level="ERROR",
                    field="external_id",
                    message=f"Duplicate test case ID '{tc.external_id}' detected."
                )
            )
        else:
            seen_ids.add(tc.external_id)

        # Check question
        if not tc.question or not tc.question.strip():
            issues.append(
                DatasetValidationIssue(
                    test_case_id=tc.id,
                    level="ERROR",
                    field="question",
                    message=f"Test case '{tc.external_id}' is missing a question."
                )
            )

        # Check language
        lang = (tc.language or "").lower().strip()
        languages_seen.add(lang)
        if lang not in VALID_LANGUAGES:
            issues.append(
                DatasetValidationIssue(
                    test_case_id=tc.id,
                    level="WARNING",
                    field="language",
                    message=f"Unrecognized language code '{lang}'. Supported standard codes: {', '.join(sorted(VALID_LANGUAGES))}."
                )
            )

        # Check expected answer
        if not tc.expected_answer or not tc.expected_answer.strip():
            issues.append(
                DatasetValidationIssue(
                    test_case_id=tc.id,
                    level="ERROR",
                    field="expected_answer",
                    message=f"Test case '{tc.external_id}' is missing expected_answer."
                )
            )

        # Check required facts
        facts = tc.required_facts or []
        if not facts:
            issues.append(
                DatasetValidationIssue(
                    test_case_id=tc.id,
                    level="WARNING",
                    field="required_facts",
                    message=f"Test case '{tc.external_id}' has no required_facts defined for deterministic verification."
                )
            )
        else:
            for f in facts:
                f_type = f.get("type", "").lower()
                if f_type not in VALID_FACT_TYPES:
                    issues.append(
                        DatasetValidationIssue(
                            test_case_id=tc.id,
                            level="WARNING",
                            field="required_facts",
                            message=f"Test '{tc.external_id}': fact type '{f_type}' is unconventional. Supported: {', '.join(sorted(VALID_FACT_TYPES))}."
                        )
                    )

        # Non-English translation checks
        if lang != "en" and not facts:
            issues.append(
                DatasetValidationIssue(
                    test_case_id=tc.id,
                    level="WARNING",
                    field="translation",
                    message=f"Non-English test '{tc.external_id}' ({lang}) lacks required facts for strict cross-lingual preservation check."
                )
            )

    errors_count = sum(1 for i in issues if i.level == "ERROR")
    warnings_count = sum(1 for i in issues if i.level == "WARNING")
    is_valid = (errors_count == 0) and (len(test_cases) > 0)

    if len(test_cases) == 0:
        issues.append(
            DatasetValidationIssue(
                test_case_id=None,
                level="ERROR",
                field="test_cases",
                message="Dataset has 0 test cases."
            )
        )
        errors_count += 1
        is_valid = False

    return DatasetValidationReport(
        dataset_id=dataset_id,
        is_valid=is_valid,
        total_test_cases=len(test_cases),
        errors_count=errors_count,
        warnings_count=warnings_count,
        issues=issues,
        languages=sorted(list(languages_seen))
    )


@router.get("/{dataset_id}/test-cases", response_model=List[TestCaseResponse])
async def list_test_cases(dataset_id: str, language: Optional[str] = None, db: AsyncSession = Depends(get_db)):
    q = select(TestCase).where(TestCase.dataset_id == dataset_id)
    if language:
        q = q.where(TestCase.language == language.lower())
    q = q.order_by(TestCase.external_id)
    res = await db.execute(q)
    return res.scalars().all()


@router.post("/{dataset_id}/test-cases", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(dataset_id: str, data: TestCaseCreate, db: AsyncSession = Depends(get_db)):
    tc = TestCase(
        dataset_id=dataset_id,
        external_id=data.external_id.strip(),
        language=data.language.strip().lower(),
        category=data.category or "general",
        question=data.question.strip(),
        expected_answer=data.expected_answer.strip(),
        source_documents=[d.model_dump() for d in data.source_documents],
        required_facts=[f.model_dump() for f in data.required_facts],
        potential_traps=data.potential_traps or [],
        expected_retrieval=data.expected_retrieval,
        expected_tools=data.expected_tools or [],
        version=data.version or "1.0.0"
    )
    db.add(tc)
    await db.flush()
    return tc


@router.put("/{dataset_id}/test-cases/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    dataset_id: str,
    test_case_id: str,
    data: TestCaseCreate,
    db: AsyncSession = Depends(get_db)
):
    q = select(TestCase).where(TestCase.id == test_case_id, TestCase.dataset_id == dataset_id)
    res = await db.execute(q)
    tc = res.scalars().first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")

    tc.external_id = data.external_id.strip()
    tc.language = data.language.strip().lower()
    tc.category = data.category or "general"
    tc.question = data.question.strip()
    tc.expected_answer = data.expected_answer.strip()
    tc.source_documents = [d.model_dump() for d in data.source_documents]
    tc.required_facts = [f.model_dump() for f in data.required_facts]
    tc.potential_traps = data.potential_traps or []
    tc.expected_retrieval = data.expected_retrieval
    tc.expected_tools = data.expected_tools or []
    await db.flush()
    return tc


@router.delete("/{dataset_id}/test-cases/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(dataset_id: str, test_case_id: str, db: AsyncSession = Depends(get_db)):
    q = select(TestCase).where(TestCase.id == test_case_id, TestCase.dataset_id == dataset_id)
    res = await db.execute(q)
    tc = res.scalars().first()
    if not tc:
        raise HTTPException(status_code=404, detail="Test case not found")
    await db.delete(tc)
    await db.flush()


@router.post("/{dataset_id}/import-json")
async def import_json_test_cases(dataset_id: str, cases: List[Dict[str, Any]], db: AsyncSession = Depends(get_db)):
    count = 0
    for c in cases:
        tc = TestCase(
            dataset_id=dataset_id,
            external_id=c.get("id") or c.get("external_id") or f"TC-{count+1}",
            language=c.get("language", "en"),
            category=c.get("category", "general"),
            question=c.get("question", ""),
            expected_answer=c.get("expected_answer", ""),
            source_documents=c.get("source_documents", []),
            required_facts=c.get("required_facts", []),
            potential_traps=c.get("potential_traps", []),
            expected_retrieval=c.get("expected_retrieval", True),
            expected_tools=c.get("expected_tools", [])
        )
        db.add(tc)
        count += 1
    await db.flush()
    return {"status": "SUCCESS", "imported_count": count}


@router.post("/{dataset_id}/import-csv")
async def import_csv_test_cases(
    dataset_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    content = await file.read()
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))

    count = 0
    for row in reader:
        external_id = row.get("id") or row.get("external_id") or f"CSV-{count+1}"
        question = row.get("question") or ""
        expected = row.get("expected_answer") or row.get("answer") or ""
        language = (row.get("language") or "en").lower().strip()
        category = row.get("category") or "general"

        if not question:
            continue

        tc = TestCase(
            dataset_id=dataset_id,
            external_id=external_id,
            language=language,
            category=category,
            question=question,
            expected_answer=expected,
            source_documents=[],
            required_facts=[],
            potential_traps=[]
        )
        db.add(tc)
        count += 1

    await db.flush()
    return {"status": "SUCCESS", "imported_count": count}
