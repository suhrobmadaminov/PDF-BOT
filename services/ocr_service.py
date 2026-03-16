"""
OCR (Optical Character Recognition) Servisi.
pytesseract va easyocr kutubxonalarini birgalikda ishlatadi.
Natija: qidiriladigan (searchable) PDF fayl.
"""

import asyncio
import tempfile
from pathlib import Path
from loguru import logger

from config import TEMP_DIR, OCR_LANGUAGES


class OCRService:
    """
    Rasm ichidagi matnni aniqlash va qidiriladigan PDF yaratish.
    Birinchi pytesseract ishlatiladi, u ishlamasa easyocr ga o'tadi.
    """

    # easyocr reader ni cache qilish (har safar yuklab olmaslik uchun)
    _easyocr_readers: dict = {}
    _tesseract_available: bool | None = None

    @classmethod
    def _check_tesseract(cls) -> bool:
        """Tesseract o'rnatilgan-o'rnatilmaganligini tekshirish."""
        if cls._tesseract_available is not None:
            return cls._tesseract_available
        try:
            import pytesseract
            pytesseract.get_tesseract_version()
            cls._tesseract_available = True
            logger.info("Tesseract mavjud")
        except Exception:
            cls._tesseract_available = False
            logger.warning("Tesseract mavjud emas — easyocr ishlatiladi")
        return cls._tesseract_available

    @classmethod
    def _get_easyocr_reader(cls, lang_code: str):
        """
        easyocr reader ni olish (cache dan yoki yangi yaratish).

        Args:
            lang_code: Til kodi ('uz', 'ru', 'en', 'ar')
        """
        if lang_code not in cls._easyocr_readers:
            try:
                import easyocr
                ocr_langs = OCR_LANGUAGES.get(lang_code, {}).get("easyocr", ["en"])
                # Ingliz tilini har doim qo'shish (aniqroq natija uchun)
                if "en" not in ocr_langs:
                    ocr_langs = ocr_langs + ["en"]
                reader = easyocr.Reader(ocr_langs, gpu=False, verbose=False)
                cls._easyocr_readers[lang_code] = reader
                logger.info(f"easyocr reader yaratildi: {ocr_langs}")
            except Exception as e:
                logger.debug(f"easyocr mavjud emas, faqat tesseract ishlatiladi: {e}")
                return None
        return cls._easyocr_readers.get(lang_code)

    @classmethod
    async def extract_text(cls, image_path: str | Path, lang: str = "en") -> str:
        """
        Rasmdan matn ajratib olish.

        Args:
            image_path: Rasm fayl yo'li
            lang:       Til kodi ('uz', 'ru', 'en', 'ar')

        Returns:
            Aniqlangan matn satri (bo'sh bo'lishi mumkin)
        """
        image_path = Path(image_path)

        # Avval pytesseract sinab ko'rish
        if cls._check_tesseract():
            text = await asyncio.get_event_loop().run_in_executor(
                None, cls._tesseract_extract, image_path, lang
            )
            if text and text.strip():
                return text.strip()

        # pytesseract ishlamasa yoki matn topilmasa — easyocr
        text = await asyncio.get_event_loop().run_in_executor(
            None, cls._easyocr_extract, image_path, lang
        )
        return text.strip() if text else ""

    @classmethod
    def _tesseract_extract(cls, image_path: Path, lang: str) -> str:
        """Pytesseract orqali matn ajratish (sinxron)."""
        try:
            import pytesseract
            from PIL import Image

            tesseract_lang = OCR_LANGUAGES.get(lang, {}).get("tesseract", "eng")

            with Image.open(image_path) as img:
                # Rasm sifatini oshirish (OCR uchun)
                img = cls._preprocess_for_ocr(img)
                text = pytesseract.image_to_string(
                    img,
                    lang=tesseract_lang,
                    config="--psm 3 --oem 3",
                )
                return text
        except Exception as e:
            logger.debug(f"Tesseract xatosi: {e}")
            return ""

    @classmethod
    def _easyocr_extract(cls, image_path: Path, lang: str) -> str:
        """easyocr orqali matn ajratish (sinxron)."""
        try:
            reader = cls._get_easyocr_reader(lang)
            if not reader:
                return ""

            results = reader.readtext(str(image_path), detail=0, paragraph=True)
            text = "\n".join(str(r) for r in results if r)
            return text
        except Exception as e:
            logger.debug(f"easyocr xatosi: {e}")
            return ""

    @classmethod
    def _preprocess_for_ocr(cls, img):
        """
        OCR uchun rasmni oldindan qayta ishlash.
        Kontrast va o'tkir chegaralarni oshirish.
        """
        try:
            from PIL import ImageEnhance, ImageFilter

            # Grayscale ga aylantirish
            if img.mode != "L":
                img = img.convert("L")

            # Kontrast oshirish
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.5)

            # O'tkir chegaralar
            img = img.filter(ImageFilter.SHARPEN)

            return img
        except Exception:
            return img

    @classmethod
    async def create_searchable_pdf(
        cls,
        image_path: str | Path,
        output_path: str | Path,
        lang: str = "en",
    ) -> tuple[bool, int]:
        """
        Qidiriladigan (searchable) PDF yaratish.
        pytesseract ning image_to_pdf_or_hocr funksiyasi ishlatiladi.

        Args:
            image_path:  Rasm fayl yo'li
            output_path: Chiquvchi PDF yo'li
            lang:        OCR tili

        Returns:
            (muvaffaqiyat, aniqlangan_belgilar_soni)
        """
        image_path = Path(image_path)
        output_path = Path(output_path)

        # Avval matnni aniqlash
        extracted_text = await cls.extract_text(image_path, lang)
        char_count = len(extracted_text.replace(" ", "").replace("\n", ""))

        if char_count == 0:
            logger.info("OCR: Matn topilmadi")
            # Matn topilmasa oddiy PDF yaratish
            try:
                from services.pdf_converter import PDFConverter
                settings = {"quality": "high", "pagesize": "A4",
                            "orientation": "portrait", "margin": "small"}
                success, err = await PDFConverter.convert_single_image(
                    image_path, output_path, settings
                )
                return success, 0
            except Exception as e:
                logger.error(f"OCR fallback PDF xatosi: {e}")
                return False, 0

        # Pytesseract bilan qidiriladigan PDF yaratish
        if cls._check_tesseract():
            result = await asyncio.get_event_loop().run_in_executor(
                None, cls._create_pdf_with_tesseract, image_path, output_path, lang
            )
            if result:
                logger.info(f"Searchable PDF yaratildi: {char_count} belgi aniqlandi")
                return True, char_count

        # Tesseract ishlamasa — oddiy PDF + matn fayli
        try:
            from services.pdf_converter import PDFConverter
            settings = {"quality": "high", "pagesize": "A4",
                        "orientation": "portrait", "margin": "small"}
            success, err = await PDFConverter.convert_single_image(
                image_path, output_path, settings
            )
            return success, char_count
        except Exception as e:
            logger.error(f"OCR fallback xatosi: {e}")
            return False, 0

    @classmethod
    def _create_pdf_with_tesseract(
        cls,
        image_path: Path,
        output_path: Path,
        lang: str,
    ) -> bool:
        """
        Pytesseract bilan qidiriladigan PDF yaratish (sinxron).

        Returns:
            Muvaffaqiyat True/False
        """
        try:
            import pytesseract
            from PIL import Image

            tesseract_lang = OCR_LANGUAGES.get(lang, {}).get("tesseract", "eng")

            with Image.open(image_path) as img:
                # OCR uchun tayyorlash
                processed = cls._preprocess_for_ocr(img.copy())

                # Qidiriladigan PDF yaratish
                pdf_bytes = pytesseract.image_to_pdf_or_hocr(
                    processed,
                    extension="pdf",
                    lang=tesseract_lang,
                    config="--psm 3",
                )

                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(pdf_bytes)

            return True
        except Exception as e:
            logger.error(f"_create_pdf_with_tesseract xatosi: {e}")
            return False

    @classmethod
    async def create_searchable_pdf_multi(
        cls,
        image_paths: list[str | Path],
        output_path: str | Path,
        lang: str = "en",
        progress_callback=None,
    ) -> tuple[bool, int]:
        """
        Bir nechta rasmdan qidiriladigan PDF yaratish.

        Args:
            image_paths:       Rasm yo'llari ro'yxati
            output_path:       Chiquvchi PDF yo'li
            lang:              OCR tili
            progress_callback: Progress yangilash funksiyasi

        Returns:
            (muvaffaqiyat, jami_aniqlangan_belgilar)
        """
        if not image_paths:
            return False, 0

        try:
            import fitz  # PyMuPDF

            output_path = Path(output_path)
            total_chars = 0
            temp_pdfs = []
            total = len(image_paths)

            # Har bir rasm uchun alohida PDF yaratish
            for i, img_path in enumerate(image_paths):
                temp_pdf = TEMP_DIR / f"ocr_page_{i}_{id(img_path)}.pdf"
                success, chars = await cls.create_searchable_pdf(
                    img_path, temp_pdf, lang
                )
                if success:
                    temp_pdfs.append(str(temp_pdf))
                    total_chars += chars

                if progress_callback:
                    await progress_callback(i + 1, total)

            if not temp_pdfs:
                return False, 0

            # Barcha PDF larni birlashtirish
            def _merge_pdfs():
                merged = fitz.open()
                for pdf_path in temp_pdfs:
                    try:
                        doc = fitz.open(pdf_path)
                        merged.insert_pdf(doc)
                        doc.close()
                    except Exception as e:
                        logger.warning(f"PDF birlashtirish xatosi ({pdf_path}): {e}")
                merged.save(str(output_path), garbage=4, deflate=True)
                merged.close()

            await asyncio.get_event_loop().run_in_executor(None, _merge_pdfs)

            return True, total_chars

        except Exception as e:
            logger.error(f"create_searchable_pdf_multi xatosi: {e}")
            return False, 0
        finally:
            # Vaqtinchalik fayllarni tozalash
            for temp_pdf in (temp_pdfs if 'temp_pdfs' in locals() else []):
                try:
                    Path(temp_pdf).unlink(missing_ok=True)
                except Exception:
                    pass
