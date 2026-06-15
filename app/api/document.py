import io
import uuid

from fastapi import APIRouter, Depends, UploadFile
from app.api.auth import get_current_claims
from app.api.auth import get_tenant_db
from app.rag.storage import minio_client
from sqlalchemy import text
from app.rag.ingest import process_document

d_router = APIRouter(prefix="/documents")


@d_router.post("")
async def upload(
        file: UploadFile,
        claims=Depends(get_current_claims),
        session=Depends(get_tenant_db)
):
    tenant_id = claims["tenant_id"]
    user_id = claims["sub"]
    document_id = str(uuid.uuid4())
    data = await file.read()
    length = len(data)
    up_file = {
        "tenant_id": tenant_id,
        "document_id": document_id,
        "file_name": file.filename,
        "bucket_name": "documents"
    }
    file_path = minio_client.upload_file(
        up_file, io.BytesIO(data), length, file.content_type
    )

    await session.execute(
        text("INSERT INTO document (id,tenant_id,user_id,file_name,path) "
             "VALUES (:id, :tenant_id, :user_id, :file_name, :path)"),
        {"id": document_id, "tenant_id": tenant_id, "user_id": user_id,
         "file_name": file.filename, "path": file_path}
    )

    chunk_count = process_document(data, up_file)

    return {
        "document_id": document_id,
        "file_name": file.filename,
        "file_path": file_path,
        "chunk_count": chunk_count
    }
