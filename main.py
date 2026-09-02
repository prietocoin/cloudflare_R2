import os
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import RedirectResponse
import boto3
from botocore.config import Config

app = FastAPI(title="Cloudflare R2 Uploader & Link Shortener")

R2_ACCOUNT_ID = os.getenv("R2_ACCOUNT_ID", "19e79842547693ffe34fbd1d311d25dc")
R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME", "remesas-img")
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID", "f3a93d65fe3ddaaff42dcbbd81f4f774")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY", "b29f83288b12cf4b17a638f343d574daf2093a89a31dd72b8417191ca786668d")

# Dominio público real asignado por Cloudflare
R2_PUBLIC_DOMAIN = "https://pub-49b9c87f6e6a418ba42de5ba36ddc73e.r2.dev"
ENDPOINT_URL = f"https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com"

s3_client = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    region_name="auto",
    config=Config(signature_version="s3v4", s3={"addressing_style": "path"})
)

@app.get("/")
def root():
    return {"status": "online", "service": "Cloudflare R2 Uploader & Shortener"}

@app.post("/upload")
def upload_image(file: UploadFile = File(...), filename: str = Form(None)):
    try:
        final_filename = filename if filename else file.filename
        file_bytes = file.file.read()
        
        s3_client.put_object(
            Bucket=R2_BUCKET_NAME,
            Key=final_filename,
            Body=file_bytes,
            ContentType=file.content_type or "image/jpeg"
        )
        
        clean_hash = final_filename.replace(".jpg", "").replace(".png", "").replace(".jpeg", "")
        
        return {
            "status": "success",
            "filename": final_filename,
            "short_url": f"https://api.jairokov.com/i/{clean_hash}",
            "r2_url": f"{R2_PUBLIC_DOMAIN}/{final_filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir a R2: {str(e)}")

@app.get("/i/{image_hash}")
def redirect_to_image(image_hash: str):
    file_key = image_hash if image_hash.endswith((".jpg", ".png", ".jpeg")) else f"{image_hash}.jpg"
    r2_url = f"{R2_PUBLIC_DOMAIN}/{file_key}"
    return RedirectResponse(url=r2_url, status_code=307)
