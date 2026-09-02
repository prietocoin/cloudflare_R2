import os
from fastapi import FastAPI, File, UploadFile, HTTPException
import boto3
from botocore.config import Config

app = FastAPI(title="Cloudflare R2 Uploader")

# Credenciales y variables de entorno (puedes cambiarlas o pasarlas como vars de sistema)
R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "19e79842547693ffe34fbd1d311d25dc")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "remesas-img")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "f3a93d65fe3ddaaff42dcbbd81f4f774")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "b29f83288b12cf4b17a638f343d574daf2093a89a31dd72b8417191ca786668d")

ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

# Inicialización del cliente S3 con direccionamiento por Path estricto
s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
    config=Config(
        signature_version="s3v4",
        s3={"addressing_style": "path"}
    )
)

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Subida directa del stream del archivo a Cloudflare R2
        s3_client.upload_fileobj(
            file.file,
            R2_BUCKET_NAME,
            file.filename,
            ExtraArgs={"ContentType": file.content_type or "image/jpeg"}
        )
        
        file_url = f"{ENDPOINT_URL}/{R2_BUCKET_NAME}/{file.filename}"
        
        return {
            "status": "success",
            "filename": file.filename,
            "url": file_url
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir a R2: {str(e)}")
