from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import csv
import io
import logging

from database import get_db
import models

router = APIRouter(prefix="/api/export", tags=["export"])

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import csv, io
from urllib.parse import quote

@router.get("/projects/{project_id}/selectedrequirements/csv")
async def export_selected_requirements_csv(
    project_id: UUID,
    db: Session = Depends(get_db)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    selected_requirements = (
        db.query(models.SelectedRequirement)
        .filter(models.SelectedRequirement.project_id == project_id)
        .order_by(models.SelectedRequirement.req_id)
        .all()
    )

    if not selected_requirements:
        raise HTTPException(status_code=404, detail="No selected requirements found")

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["req_id", "module", "requirement"])

    for req in selected_requirements:
        writer.writerow([
            req.req_id,
            req.module or "",
            req.requirement
        ])

    output.seek(0)

    # 🔑 แก้ตรงนี้
    filename = f"{project.title}_selected_requirements.csv"
    filename_encoded = quote(filename)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": (
                "attachment; "
                f"filename*=UTF-8''{filename_encoded}"
            )
        }
    )


