"""
PDF Konvertatsiya Servisi — rasmlarni PDF ga aylantirish.
img2pdf va Pillow kutubxonalaridan foydalaniladi.
"""

import io
import asyncio
from pathlib import Path
from datetime import datetime

import img2pdf
from PIL import Image
from loguru import logger

from config import (
    TEMP_DIR,
    QUALITY_SETTINGS,
    PAGE_SIZES,
    MARGIN_SIZES,
    HISTORY_DIR,
)
from utils.helpers import get_timestamp, get_file_size_from_path


class PDFConverter:
    """
    Rasmlarni PDF ga aylantiruvchi asosiy sinf.
    Bitta yoki ko'p rasmni PDF ga birlashtirish imkoniyati mavjud.
    """

    @staticmethod
    async def convert_single_image(
        image_path: str | Path,
        output_path: str | Path,
        settings: dict,
    ) -> tuple[bool, str]:
        """
        Bitta rasmni PDF ga aylantirish.

        Args:
            image_path:  Kiruvchi rasm fayl yo'li
            output_path: Chiquvchi PDF fayl yo'li
            settings:    Foydalanuvchi sozlamalari (quality, pagesize, orientation, margin)

        Returns:
            (muvaffaqiyat, xato_xabari)
        """
        try:
            image_path = Path(image_path)
            output_path = Path(output_path)

            # Rasmni Pillow bilan ochish va tayyorlash
            processed_path = await asyncio.get_event_loop().run_in_executor(
                None,
                PDFConverter._prepare_image_sync,
                image_path,
                settings,
            )

            if not processed_path:
                return False, "Rasm qayta ishlashda xato"

            # img2pdf bilan PDF yaratish
            await asyncio.get_event_loop().run_in_executor(
                None,
                PDFConverter._create_pdf_sync,
                [processed_path],
                output_path,
                settings,
            )

            # Vaqtinchalik qayta ishlangan faylni o'chirish
            if processed_path != image_path:
                try:
                    Path(processed_path).unlink(missing_ok=True)
                except Exception:
                    pass

            logger.info(f"PDF yaratildi: {output_path.name}")
            return True, ""

        except Exception as e:
            logger.error(f"convert_single_image xatosi: {e}")
            return False, str(e)

    @staticmethod
    async def convert_multiple_images(
        image_paths: list[str | Path],
        output_path: str | Path,
        settings: dict,
        progress_callback=None,
    ) -> tuple[bool, str]:
        """
        Bir nechta rasmni bitta PDF ga birlashtirish.

        Args:
            image_paths:       Rasm fayl yo'llari ro'yxati
            output_path:       Chiquvchi PDF fayl yo'li
            settings:          Foydalanuvchi sozlamalari
            progress_callback: Progress yangilash funksiyasi (ixtiyoriy)

        Returns:
            (muvaffaqiyat, xato_xabari)
        """
        if not image_paths:
            return False, "Rasmlar ro'yxati bo'sh"

        processed_paths = []
        try:
            total = len(image_paths)

            # Har bir rasmni tayyorlash
            for i, img_path in enumerate(image_paths):
                processed = await asyncio.get_event_loop().run_in_executor(
                    None,
                    PDFConverter._prepare_image_sync,
                    Path(img_path),
                    settings,
                )
                if processed:
                    processed_paths.append(processed)
                else:
                    logger.warning(f"Rasm qayta ishlanmadi: {img_path}")

                # Progress yangilash
                if progress_callback:
                    await progress_callback(i + 1, total)

            if not processed_paths:
                return False, "Hech qaysi rasm qayta ishlanmadi"

            # Barcha rasmlarni bitta PDF ga birlashtirish
            output_path = Path(output_path)
            await asyncio.get_event_loop().run_in_executor(
                None,
                PDFConverter._create_pdf_sync,
                processed_paths,
                output_path,
                settings,
            )

            logger.info(f"Ko'p rasmli PDF yaratildi: {output_path.name}, {len(processed_paths)} sahifa")
            return True, ""

        except Exception as e:
            logger.error(f"convert_multiple_images xatosi: {e}")
            return False, str(e)
        finally:
            # Vaqtinchalik fayllarni tozalash
            for path in processed_paths:
                if path not in [str(p) for p in image_paths]:
                    try:
                        Path(path).unlink(missing_ok=True)
                    except Exception:
                        pass

    @staticmethod
    def _prepare_image_sync(
        image_path: Path,
        settings: dict,
    ) -> str | None:
        """
        Rasmni PDF uchun tayyorlash (sinxron).
        Sifat, o'lcham, yo'nalish va chegaralarni qo'llash.

        Args:
            image_path: Rasm yo'li
            settings:   Sozlamalar

        Returns:
            Tayyorlangan rasm yo'li (o'zgartirilmagan bo'lsa asl yo'l)
        """
        try:
            quality_key = settings.get("quality", "high")
            quality_cfg = QUALITY_SETTINGS.get(quality_key, QUALITY_SETTINGS["high"])

            pagesize = settings.get("pagesize", "A4")
            orientation = settings.get("orientation", "portrait")
            margin_key = settings.get("margin", "small")
            margin_px = MARGIN_SIZES.get(margin_key, 10)

            with Image.open(image_path) as img:
                # EXIF orientatsiyani to'g'rilash
                img = PDFConverter._fix_exif_orientation(img)

                # RGBA → RGB (PDF JPEG uchun zarur)
                if img.mode in ("RGBA", "P", "LA"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode in ("RGBA", "LA"):
                        background.paste(img, mask=img.split()[-1])
                    else:
                        background.paste(img)
                    img = background
                elif img.mode != "RGB":
                    img = img.convert("RGB")

                # Maksimal o'lchamga moslashtirish
                max_size = quality_cfg.get("max_size", (2560, 2560))
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Sahifa o'lchamiga moslashtirish
                if pagesize != "Original" and pagesize in PAGE_SIZES and PAGE_SIZES[pagesize]:
                    img = PDFConverter._fit_to_page(img, pagesize, orientation, margin_px)

                # Yo'nalishni avtomatik tekshirish
                if orientation == "auto":
                    # Keng rasm → landscape sahifaga moslashtirish
                    pass

                # Saqlash
                output_path = TEMP_DIR / f"prep_{image_path.stem}_{id(img)}.jpg"
                quality = quality_cfg.get("quality", 85)
                optimize = quality_cfg.get("optimize", False)
                img.save(
                    output_path,
                    format="JPEG",
                    quality=quality,
                    optimize=optimize,
                    progressive=True,
                )
                return str(output_path)

        except Exception as e:
            logger.error(f"_prepare_image_sync xatosi ({image_path}): {e}")
            return str(image_path)  # Asl faylni qaytarish

    @staticmethod
    def _fix_exif_orientation(img: Image.Image) -> Image.Image:
        """EXIF ma'lumotlariga asosan rasmni to'g'ri yo'nalishda o'rnatish."""
        try:
            exif = img._getexif()
            if exif:
                orientation_key = 274  # EXIF orientation tag
                orientation_val = exif.get(orientation_key, 1)
                rotations = {3: 180, 6: 270, 8: 90}
                if orientation_val in rotations:
                    img = img.rotate(rotations[orientation_val], expand=True)
        except (AttributeError, Exception):
            pass
        return img

    @staticmethod
    def _fit_to_page(
        img: Image.Image,
        pagesize: str,
        orientation: str,
        margin_px: int,
    ) -> Image.Image:
        """
        Rasmni sahifa o'lchamiga moslashtirish (nisbatni saqlab).

        Args:
            img:        Pillow Image
            pagesize:   Sahifa o'lchami ('A4', 'A3', va h.k.)
            orientation: Yo'nalish ('portrait', 'landscape', 'auto')
            margin_px:  Chegara o'lchami pikselda
        """
        page_mm = PAGE_SIZES.get(pagesize)
        if not page_mm:
            return img

        pw_mm, ph_mm = page_mm

        # Landscape bo'lsa, kenglik va balandlikni almashtirish
        if orientation == "landscape" or (
            orientation == "auto" and img.width > img.height
        ):
            pw_mm, ph_mm = ph_mm, pw_mm

        # mm dan pikselga o'tkazish (96 DPI)
        dpi = 96
        pw_px = int(pw_mm / 25.4 * dpi)
        ph_px = int(ph_mm / 25.4 * dpi)

        # Chegara qo'shish
        content_w = pw_px - 2 * margin_px
        content_h = ph_px - 2 * margin_px

        if content_w <= 0 or content_h <= 0:
            return img

        # Nisbatni saqlab o'lchamni moslashtirish
        ratio = min(content_w / img.width, content_h / img.height)
        new_w = max(1, int(img.width * ratio))
        new_h = max(1, int(img.height * ratio))

        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # Oq sahifaga joylashtirish (markazda)
        if margin_px > 0:
            page_img = Image.new("RGB", (pw_px, ph_px), (255, 255, 255))
            x = (pw_px - new_w) // 2
            y = (ph_px - new_h) // 2
            page_img.paste(img_resized, (x, y))
            return page_img

        return img_resized

    @staticmethod
    def _create_pdf_sync(
        image_paths: list[str],
        output_path: Path,
        settings: dict,
    ) -> None:
        """
        Tayyorlangan rasmlardan PDF yaratish (sinxron, img2pdf yordamida).

        Args:
            image_paths: Tayyorlangan rasm yo'llari
            output_path: Chiquvchi PDF yo'li
            settings:    Sozlamalar
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # img2pdf sahifa o'lchami sozlamasi
        pagesize = settings.get("pagesize", "A4")
        orientation = settings.get("orientation", "portrait")

        layout_fun = None
        if pagesize != "Original" and pagesize in PAGE_SIZES and PAGE_SIZES[pagesize]:
            pw_mm, ph_mm = PAGE_SIZES[pagesize]
            if orientation == "landscape":
                pw_mm, ph_mm = ph_mm, pw_mm

            # img2pdf mm → points (1 inch = 72 points, 1 mm = 2.8346 points)
            pw_pt = img2pdf.mm_to_pt(pw_mm)
            ph_pt = img2pdf.mm_to_pt(ph_mm)
            layout_fun = img2pdf.get_layout_fun((pw_pt, ph_pt))

        # PDF yaratish
        with open(output_path, "wb") as f:
            if layout_fun:
                pdf_bytes = img2pdf.convert(image_paths, layout_fun=layout_fun)
            else:
                pdf_bytes = img2pdf.convert(image_paths)
            f.write(pdf_bytes)

    @staticmethod
    async def compress_pdf(
        input_path: str | Path,
        output_path: str | Path,
        quality: str = "medium",
    ) -> tuple[bool, int, int]:
        """
        PDF faylni siqish (rasmlarni qayta siqib yaratish orqali).

        Args:
            input_path:  Kiruvchi PDF yo'li
            output_path: Siqilgan PDF yo'li
            quality:     Sifat darajasi

        Returns:
            (muvaffaqiyat, asl_hajm, siqilgan_hajm)
        """
        try:
            import fitz  # PyMuPDF

            input_path = Path(input_path)
            output_path = Path(output_path)
            original_size = input_path.stat().st_size

            quality_cfg = QUALITY_SETTINGS.get(quality, QUALITY_SETTINGS["medium"])
            dpi = quality_cfg.get("dpi", 150)
            jpeg_quality = quality_cfg.get("quality", 70)

            def _compress_sync() -> None:
                doc = fitz.open(str(input_path))
                new_doc = fitz.open()

                for page_num in range(doc.page_count):
                    page = doc[page_num]
                    # Sahifani rasmga aylantirish
                    mat = fitz.Matrix(dpi / 72, dpi / 72)
                    pix = page.get_pixmap(matrix=mat, alpha=False)

                    # JPEG sifatida siqish
                    img_bytes = pix.tobytes("jpeg", jpg_quality=jpeg_quality)
                    img = Image.open(io.BytesIO(img_bytes))

                    # Yangi PDF sahifaga qo'shish
                    img_pdf_bytes = img2pdf.convert(io.BytesIO(img_bytes).read())
                    img_doc = fitz.open("pdf", img_pdf_bytes)
                    new_doc.insert_pdf(img_doc)
                    img_doc.close()

                new_doc.save(str(output_path), garbage=4, deflate=True)
                new_doc.close()
                doc.close()

            await asyncio.get_event_loop().run_in_executor(None, _compress_sync)

            compressed_size = output_path.stat().st_size
            logger.info(
                f"PDF siqildi: {original_size:,} → {compressed_size:,} bayt"
            )
            return True, original_size, compressed_size

        except Exception as e:
            logger.error(f"compress_pdf xatosi: {e}")
            return False, 0, 0

    @staticmethod
    async def get_pdf_page_count(pdf_path: str | Path) -> int:
        """
        PDF fayldagi sahifalar sonini olish.

        Args:
            pdf_path: PDF fayl yo'li

        Returns:
            Sahifalar soni (xato bo'lsa 0)
        """
        try:
            import fitz
            doc = fitz.open(str(pdf_path))
            count = doc.page_count
            doc.close()
            return count
        except Exception as e:
            logger.error(f"get_pdf_page_count xatosi: {e}")
            return 0

    @staticmethod
    def generate_output_path(prefix: str = "converted") -> Path:
        """
        Yangi PDF fayl yo'lini generatsiya qilish (HISTORY_DIR papkasida).

        Args:
            prefix: Prefiks ('converted', 'ocr', 'merged')

        Returns:
            Path obyekti
        """
        filename = f"{prefix}_{get_timestamp()}.pdf"
        return HISTORY_DIR / filename
