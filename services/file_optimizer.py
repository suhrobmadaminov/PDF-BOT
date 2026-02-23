"""
Fayl Optimizatsiya Servisi — PDF → Rasm konvertatsiyasi va ZIP yaratish.
PyMuPDF (fitz) yordamida PDF sahifalarini rasmlarga aylantirish.
"""

import io
import asyncio
import zipfile
from pathlib import Path
from loguru import logger

from config import TEMP_DIR
from utils.helpers import get_timestamp, get_file_size_from_path


class FileOptimizer:
    """
    PDF fayllarni rasmlarga aylantirish va ZIP arxiv yaratish.
    Reverse funksiyasi uchun asosiy servis.
    """

    @staticmethod
    async def pdf_to_images(
        pdf_path: str | Path,
        output_format: str = "jpg",
        dpi: int = 150,
        page_indices: list[int] | None = None,
        progress_callback=None,
    ) -> list[Path]:
        """
        PDF faylni alohida rasmlar ro'yxatiga aylantirish.

        Args:
            pdf_path:          PDF fayl yo'li
            output_format:     Chiqish formati ('jpg' yoki 'png')
            dpi:               Rasm sifati (DPI)
            page_indices:      Qaysi sahifalar (None = barchasi, 0-indexed)
            progress_callback: Progress yangilash funksiyasi

        Returns:
            Yaratilgan rasm fayllari yo'llari ro'yxati
        """
        pdf_path = Path(pdf_path)
        output_paths = []

        def _convert_sync() -> list[str]:
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(str(pdf_path))
                total_pages = doc.page_count

                # Konvertatsiya qilinadigan sahifalarni aniqlash
                if page_indices is None:
                    pages_to_convert = list(range(total_pages))
                else:
                    pages_to_convert = [
                        p for p in page_indices if 0 <= p < total_pages
                    ]

                if not pages_to_convert:
                    doc.close()
                    return []

                results = []
                mat = fitz.Matrix(dpi / 72, dpi / 72)

                for i, page_num in enumerate(pages_to_convert):
                    page = doc[page_num]
                    pix = page.get_pixmap(matrix=mat, alpha=False)

                    # Fayl nomi
                    ext = output_format.lower()
                    if ext not in ("jpg", "jpeg", "png"):
                        ext = "jpg"

                    out_filename = f"page_{page_num + 1:03d}_{get_timestamp()}.{ext}"
                    out_path = TEMP_DIR / out_filename

                    if ext in ("jpg", "jpeg"):
                        pix.save(str(out_path), "jpeg")
                    else:
                        pix.save(str(out_path), "png")

                    results.append(str(out_path))

                doc.close()
                return results

            except Exception as e:
                logger.error(f"PDF→Rasm konvertatsiya xatosi: {e}")
                return []

        try:
            paths = await asyncio.get_event_loop().run_in_executor(None, _convert_sync)
            output_paths = [Path(p) for p in paths]
            logger.info(f"PDF→Rasm: {len(output_paths)} ta rasm yaratildi")
            return output_paths
        except Exception as e:
            logger.error(f"pdf_to_images xatosi: {e}")
            return []

    @staticmethod
    async def create_zip_from_images(
        image_paths: list[Path],
        output_path: str | Path,
    ) -> bool:
        """
        Rasmlardan ZIP arxiv yaratish.

        Args:
            image_paths: Rasm fayllari yo'llari
            output_path: ZIP fayl yo'li

        Returns:
            Muvaffaqiyat True/False
        """
        output_path = Path(output_path)

        def _create_zip_sync():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for img_path in image_paths:
                    img_path = Path(img_path)
                    if img_path.exists():
                        zf.write(img_path, img_path.name)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _create_zip_sync)
            zip_size = get_file_size_from_path(output_path)
            logger.info(f"ZIP yaratildi: {output_path.name}, {zip_size:,} bayt")
            return result
        except Exception as e:
            logger.error(f"create_zip_from_images xatosi: {e}")
            return False

    @staticmethod
    async def get_pdf_info(pdf_path: str | Path) -> dict:
        """
        PDF fayl haqida ma'lumot olish.

        Args:
            pdf_path: PDF fayl yo'li

        Returns:
            {page_count, file_size, metadata}
        """
        def _sync():
            try:
                import fitz
                pdf_path_obj = Path(pdf_path)
                doc = fitz.open(str(pdf_path_obj))
                info = {
                    "page_count": doc.page_count,
                    "file_size":  pdf_path_obj.stat().st_size,
                    "title":      doc.metadata.get("title", ""),
                    "author":     doc.metadata.get("author", ""),
                }
                doc.close()
                return info
            except Exception as e:
                logger.error(f"get_pdf_info xatosi: {e}")
                return {"page_count": 0, "file_size": 0, "title": "", "author": ""}

        return await asyncio.get_event_loop().run_in_executor(None, _sync)

    @staticmethod
    async def optimize_image_for_web(
        image_path: str | Path,
        output_path: str | Path,
        max_size: tuple[int, int] = (1920, 1920),
        quality: int = 85,
    ) -> tuple[bool, int, int]:
        """
        Rasmni web uchun optimallashtirish (hajmni kamaytirish).

        Args:
            image_path:  Kiruvchi rasm yo'li
            output_path: Chiquvchi rasm yo'li
            max_size:    Maksimal o'lcham (kenglik, balandlik)
            quality:     JPEG sifati (1-95)

        Returns:
            (muvaffaqiyat, asl_hajm, yangi_hajm)
        """
        def _sync():
            from PIL import Image
            original = Path(image_path)
            output = Path(output_path)
            original_size = original.stat().st_size

            with Image.open(original) as img:
                if img.mode in ("RGBA", "P", "LA"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode in ("RGBA", "LA"):
                        bg.paste(img, mask=img.split()[-1])
                    else:
                        bg.paste(img)
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # O'lchamni kamaytirish
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                output.parent.mkdir(parents=True, exist_ok=True)
                img.save(str(output), format="JPEG", quality=quality, optimize=True)

            new_size = output.stat().st_size
            return True, original_size, new_size

        try:
            return await asyncio.get_event_loop().run_in_executor(None, _sync)
        except Exception as e:
            logger.error(f"optimize_image_for_web xatosi: {e}")
            return False, 0, 0

    @staticmethod
    async def cleanup_temp_files(older_than_minutes: int = 60) -> int:
        """
        TEMP_DIR papkasidagi eski fayllarni tozalash.

        Args:
            older_than_minutes: Necha daqiqadan eski fayllar o'chirilsin

        Returns:
            O'chirilgan fayllar soni
        """
        import time
        cutoff = time.time() - (older_than_minutes * 60)
        count = 0

        try:
            for file_path in TEMP_DIR.iterdir():
                if file_path.is_file():
                    try:
                        if file_path.stat().st_mtime < cutoff:
                            file_path.unlink()
                            count += 1
                    except Exception as e:
                        logger.debug(f"Fayl o'chirishda xato: {e}")
        except Exception as e:
            logger.error(f"cleanup_temp_files xatosi: {e}")

        if count:
            logger.info(f"Temp tozalandi: {count} ta fayl")
        return count

    @staticmethod
    async def compress_image(
        image_path: str | Path,
        output_path: str | Path,
        quality: str = "medium",
    ) -> tuple[bool, int, int]:
        """
        Rasmni belgilangan sifat darajasida siqish.

        Args:
            quality: 'low', 'medium', 'high', 'ultra'

        Returns:
            (muvaffaqiyat, asl_hajm, siqilgan_hajm)
        """
        from config import QUALITY_SETTINGS
        q_cfg = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS["medium"])
        return await FileOptimizer.optimize_image_for_web(
            image_path,
            output_path,
            max_size=q_cfg.get("max_size", (1920, 1920)),
            quality=q_cfg.get("quality", 70),
        )
