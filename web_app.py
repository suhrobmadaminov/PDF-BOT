import os
import shutil
import uuid
import asyncio
from pathlib import Path
from typing import List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from config import TEMP_DIR, HISTORY_DIR, DEFAULT_SETTINGS, QUALITY_SETTINGS
from services.pdf_converter import PDFConverter
from services.ocr_service import OCRService
from services.file_optimizer import FileOptimizer

app = FastAPI(title="Image to PDF Pro Web API")

# CORS rejimi (agar frontend boshqa domenda bo'lsa kerak bo'ladi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statik fayllar (CSS, JS, Images)
# website papkasi ichidagi hamma narsani / havolasi ostida ko'rsatish
app.mount("/css", StaticFiles(directory="website/css"), name="css")
app.mount("/js", StaticFiles(directory="website/js"), name="js")
# Agar images papkasi bo'lsa:
if os.path.exists("website/images"):
    app.mount("/images", StaticFiles(directory="website/images"), name="images")

@app.get("/")
async def read_index():
    return FileResponse("website/index.html")

# ── API Endpoints ────────────────────────────────────────────────────────────

def cleanup_file(path: str):
    """Faylni o'chirish (background task uchun)."""
    try:
        if os.path.exists(path):
            os.remove(path)
            logger.debug(f"Vaqtinchalik fayl o'chirildi: {path}")
    except Exception as e:
        logger.error(f"Cleanup hatosi: {e}")

@app.post("/api/convert")
async def api_convert(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    quality: str = Form("high"),
    pagesize: str = Form("A4"),
    orientation: str = Form("portrait"),
    margin: str = Form("small")
):
    """Rasmlarni PDF ga aylantirish API."""
    if not files:
        raise HTTPException(status_code=400, detail="Fayllar topilmadi")

    session_id = str(uuid.uuid4())
    temp_paths = []
    
    try:
        # Fayllarni temp papkaga saqlash
        for file in files:
            temp_ext = os.path.splitext(file.filename)[1] or ".jpg"
            temp_path = TEMP_DIR / f"web_{session_id}_{uuid.uuid4().hex}{temp_ext}"
            temp_paths.append(temp_path)
            
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # PDF yaratish
        output_pdf = PDFConverter.generate_output_path("web_converted")
        settings = {
            "quality": quality,
            "pagesize": pagesize,
            "orientation": orientation,
            "margin": margin
        }

        if len(temp_paths) == 1:
            success, error = await PDFConverter.convert_single_image(temp_paths[0], output_pdf, settings)
        else:
            success, error = await PDFConverter.convert_multiple_images(temp_paths, output_pdf, settings)

        if not success:
            raise HTTPException(status_code=500, detail=f"Konvertatsiya hatosi: {error}")

        # Natijani qaytarish va keyinroq o'chirishni rejalashtirish
        # (Eslatma: Haqiqiy productionda fayllarni uzoqroq saqlash yoki S3 ishlatish ma'qul)
        # Hozircha HISTORY_DIR da qolaveradi, config dagi scheduler uni o'chiradi.
        
        return {
            "success": True,
            "filename": output_pdf.name,
            "download_url": f"/api/download/{output_pdf.name}",
            "pages": len(temp_paths)
        }

    except Exception as e:
        logger.error(f"Web API Convert hatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Kiruvchi rasmlarni o'chirish
        for p in temp_paths:
            background_tasks.add_task(cleanup_file, str(p))

@app.post("/api/ocr")
async def api_ocr(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    lang: str = Form("en")
):
    """OCR matn aniqlash API."""
    session_id = str(uuid.uuid4())
    temp_ext = os.path.splitext(file.filename)[1] or ".jpg"
    temp_path = TEMP_DIR / f"web_ocr_{session_id}{temp_ext}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_pdf = PDFConverter.generate_output_path("web_ocr")
        success, char_count = await OCRService.create_searchable_pdf(temp_path, output_pdf, lang)

        if not success:
            raise HTTPException(status_code=500, detail="OCR jarayonida hato yuz berdi")

        return {
            "success": True,
            "filename": output_pdf.name,
            "download_url": f"/api/download/{output_pdf.name}",
            "chars_detected": char_count
        }

    except Exception as e:
        logger.error(f"Web API OCR hatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        background_tasks.add_task(cleanup_file, str(temp_path))

@app.post("/api/compress")
async def api_compress(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    quality: str = Form("medium")
):
    """PDF siqish API."""
    session_id = str(uuid.uuid4())
    temp_path = TEMP_DIR / f"web_comp_{session_id}.pdf"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_pdf = PDFConverter.generate_output_path("web_compressed")
        success, old_size, new_size = await PDFConverter.compress_pdf(temp_path, output_pdf, quality)

        if not success:
            raise HTTPException(status_code=500, detail="Siqish jarayonida hato yuz berdi")

        return {
            "success": True,
            "filename": output_pdf.name,
            "download_url": f"/api/download/{output_pdf.name}",
            "original_size": old_size,
            "compressed_size": new_size,
            "ratio": round((1 - new_size/old_size) * 100, 1) if old_size > 0 else 0
        }

    except Exception as e:
        logger.error(f"Web API Compress hatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        background_tasks.add_task(cleanup_file, str(temp_path))

@app.post("/api/edit")
async def api_edit(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    action: str = Form(...)
):
    """Rasm tahrirlash API."""
    session_id = str(uuid.uuid4())
    temp_ext = os.path.splitext(file.filename)[1] or ".jpg"
    temp_path = TEMP_DIR / f"web_edit_{session_id}{temp_ext}"
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        output_path = TEMP_DIR / f"res_{session_id}{temp_ext}"
        # Copy to output first so we can edit in-place or use as result
        shutil.copy2(str(temp_path), str(output_path))
        
        success = await ImageEditor.apply_edit(output_path, action)

        if not success:
            raise HTTPException(status_code=500, detail="Tahrirlashda hato")

        # Natijani yuklab olish uchun web_download endpointiga moslash
        # (Lekin rasm JPEG bo'lishi mumkin, shuning uchun download endpointini kengaytiramiz)
        return {
            "success": True,
            "filename": output_path.name,
            "download_url": f"/api/download/{output_path.name}?type=image"
        }

    except Exception as e:
        logger.error(f"Web API Edit hatosi: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        background_tasks.add_task(cleanup_file, str(temp_path))

@app.get("/api/download/{filename}")
async def download_file(filename: str, type: str = "pdf"):
    """Tayyor faylni yuklab olish."""
    # TEMP_DIR yoki HISTORY_DIR dan qidirish
    file_path = HISTORY_DIR / filename
    if not file_path.exists():
        file_path = TEMP_DIR / filename
        
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fayl topilmadi yoki o'chirilgan")
    
    media_type = "application/pdf" if type == "pdf" else "image/jpeg"
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type=media_type
    )

@app.get("/api/stats")
async def get_stats():
    """Vebsayt uchun statistik ma'lumotlar."""
    # Bot database dan statistika olish (ixtiyoriy)
    return {
        "users": "1000+",
        "pdfs": "50,000+",
        "status": "online"
    }

if __name__ == "__main__":
    import uvicorn
    # Terminal orqali ishga tushirish uchun:
    # uvicorn web_app:app --host 0.0.0.0 --port 8000
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
