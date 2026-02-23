"""
Rasm Tahrirlash Servisi — Pillow yordamida rasmlarni o'zgartirish.
Yorqinlik, kontrast, qora-oq, aylantirish, keskinlashtirish, A4 moslashtirish.
"""

import asyncio
import shutil
from pathlib import Path
from loguru import logger

from config import TEMP_DIR


class ImageEditor:
    """
    Pillow kutubxonasi orqali rasmlarni tahrirlash.
    Har bir o'zgartirish joriy ish nusxasiga qo'llanadi.
    """

    @staticmethod
    def _get_work_copy(original_path: str | Path) -> Path:
        """
        Asl rasmdan ish nusxasi yaratish.

        Args:
            original_path: Asl rasm yo'li

        Returns:
            Ish nusxasi yo'li (TEMP_DIR da)
        """
        original = Path(original_path)
        work_path = TEMP_DIR / f"edit_{original.stem}_{id(original_path)}.jpg"
        try:
            shutil.copy2(original, work_path)
        except Exception as e:
            logger.error(f"Ish nusxa yaratishda xato: {e}")
        return work_path

    @staticmethod
    async def adjust_brightness(
        image_path: str | Path,
        output_path: str | Path,
        factor: float,
    ) -> bool:
        """
        Rasmning yorqinligini o'zgartirish.

        Args:
            image_path:  Kiruvchi rasm yo'li
            output_path: Chiquvchi rasm yo'li
            factor:      Yorqinlik koeffitsienti
                         (0.5 = -50%, 0.75 = -25%, 1.0 = normal, 1.25 = +25%, 1.5 = +50%)

        Returns:
            Muvaffaqiyat True/False
        """
        def _sync():
            from PIL import Image, ImageEnhance
            with Image.open(image_path) as img:
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                enhancer = ImageEnhance.Brightness(img)
                enhanced = enhancer.enhance(factor)
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                enhanced.save(str(output), format="JPEG", quality=90)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _sync)
            logger.debug(f"Yorqinlik o'zgartirildi: {factor}")
            return result
        except Exception as e:
            logger.error(f"adjust_brightness xatosi: {e}")
            return False

    @staticmethod
    async def adjust_contrast(
        image_path: str | Path,
        output_path: str | Path,
        factor: float,
    ) -> bool:
        """
        Rasmning kontrastini o'zgartirish.

        Args:
            factor: Kontrast koeffitsienti
                    (0.5=past, 1.0=normal, 1.5=o'rta, 2.0=yuqori, 3.0=juda yuqori)
        """
        def _sync():
            from PIL import Image, ImageEnhance
            with Image.open(image_path) as img:
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                enhancer = ImageEnhance.Contrast(img)
                enhanced = enhancer.enhance(factor)
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                enhanced.save(str(output), format="JPEG", quality=90)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _sync)
            logger.debug(f"Kontrast o'zgartirildi: {factor}")
            return result
        except Exception as e:
            logger.error(f"adjust_contrast xatosi: {e}")
            return False

    @staticmethod
    async def convert_to_grayscale(
        image_path: str | Path,
        output_path: str | Path,
    ) -> bool:
        """
        Rasmni qora-oq formatga aylantirish.

        Args:
            image_path:  Kiruvchi rasm yo'li
            output_path: Chiquvchi rasm yo'li
        """
        def _sync():
            from PIL import Image
            with Image.open(image_path) as img:
                gray = img.convert("L")
                # JPEG uchun L → RGB ga qaytarish
                gray_rgb = gray.convert("RGB")
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                gray_rgb.save(str(output), format="JPEG", quality=90)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _sync)
            logger.debug("Qora-oq formatga aylantildi")
            return result
        except Exception as e:
            logger.error(f"convert_to_grayscale xatosi: {e}")
            return False

    @staticmethod
    async def rotate_image(
        image_path: str | Path,
        output_path: str | Path,
        degrees: int,
    ) -> bool:
        """
        Rasmni aylantirish.

        Args:
            degrees: Aylantirish burchagi (90, 180, 270)
        """
        def _sync():
            from PIL import Image
            with Image.open(image_path) as img:
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGB")
                # expand=True — yangi o'lcham to'g'ri bo'lishi uchun
                rotated = img.rotate(-degrees, expand=True)
                if rotated.mode == "RGBA":
                    bg = Image.new("RGB", rotated.size, (255, 255, 255))
                    bg.paste(rotated, mask=rotated.split()[3])
                    rotated = bg
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                rotated.save(str(output), format="JPEG", quality=90)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _sync)
            logger.debug(f"Rasm {degrees}° aylantirildi")
            return result
        except Exception as e:
            logger.error(f"rotate_image xatosi: {e}")
            return False

    @staticmethod
    async def sharpen_image(
        image_path: str | Path,
        output_path: str | Path,
        factor: float = 2.0,
    ) -> bool:
        """
        Rasmni keskinlashtirish (sharpen).

        Args:
            factor: Keskinlik darajasi (1.0=normal, 2.0=o'rta, 3.0=kuchli)
        """
        def _sync():
            from PIL import Image, ImageEnhance, ImageFilter
            with Image.open(image_path) as img:
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                # Avval unsharp mask
                sharpened = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
                # So'ng ImageEnhance.Sharpness
                enhancer = ImageEnhance.Sharpness(sharpened)
                final = enhancer.enhance(factor)
                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                final.save(str(output), format="JPEG", quality=90)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _sync)
            logger.debug(f"Rasm keskinlashtirildi: {factor}")
            return result
        except Exception as e:
            logger.error(f"sharpen_image xatosi: {e}")
            return False

    @staticmethod
    async def fit_to_a4(
        image_path: str | Path,
        output_path: str | Path,
        orientation: str = "portrait",
    ) -> bool:
        """
        Rasmni A4 sahifasiga to'liq moslashtirish.

        Args:
            orientation: 'portrait' yoki 'landscape'
        """
        def _sync():
            from PIL import Image

            # A4 o'lchami 96 DPI da
            if orientation == "landscape":
                target_w, target_h = 1123, 794   # landscape A4
            else:
                target_w, target_h = 794, 1123    # portrait A4

            with Image.open(image_path) as img:
                if img.mode not in ("RGB",):
                    img = img.convert("RGB")

                # O'lchamni hisoblash (nisbatni saqlab)
                ratio = min(target_w / img.width, target_h / img.height)
                new_w = max(1, int(img.width * ratio))
                new_h = max(1, int(img.height * ratio))

                resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                # Oq fonli A4 sahifasiga joylashtirish
                page = Image.new("RGB", (target_w, target_h), (255, 255, 255))
                x = (target_w - new_w) // 2
                y = (target_h - new_h) // 2
                page.paste(resized, (x, y))

                output = Path(output_path)
                output.parent.mkdir(parents=True, exist_ok=True)
                page.save(str(output), format="JPEG", quality=90)
            return True

        try:
            result = await asyncio.get_event_loop().run_in_executor(None, _sync)
            logger.debug("A4 ga moslashtildi")
            return result
        except Exception as e:
            logger.error(f"fit_to_a4 xatosi: {e}")
            return False

    @staticmethod
    async def reset_to_original(
        original_path: str | Path,
        work_path: str | Path,
    ) -> bool:
        """
        Ish nusxasini asl nusxaga qaytarish.

        Args:
            original_path: Asl rasm yo'li
            work_path:     Ish nusxasi yo'li
        """
        try:
            shutil.copy2(str(original_path), str(work_path))
            logger.debug("Rasm asl holatiga qaytarildi")
            return True
        except Exception as e:
            logger.error(f"reset_to_original xatosi: {e}")
            return False

    @staticmethod
    async def apply_edit(
        work_path: str | Path,
        action: str,
    ) -> bool:
        """
        Ish nusxasiga amal qo'llash (in-place o'zgartirish).

        Args:
            work_path: Ish nusxasi yo'li
            action:    Amal kodi (masalan: 'ed_bri_p25', 'ed_gray')

        Returns:
            Muvaffaqiyat True/False
        """
        work_path = Path(work_path)

        # Vaqtinchalik output fayl
        temp_out = work_path.parent / f"tmp_{work_path.name}"

        success = False

        # Brightness
        if action == "ed_bri_m50":
            success = await ImageEditor.adjust_brightness(work_path, temp_out, 0.5)
        elif action == "ed_bri_m25":
            success = await ImageEditor.adjust_brightness(work_path, temp_out, 0.75)
        elif action == "ed_bri_nor":
            success = await ImageEditor.adjust_brightness(work_path, temp_out, 1.0)
        elif action == "ed_bri_p25":
            success = await ImageEditor.adjust_brightness(work_path, temp_out, 1.25)
        elif action == "ed_bri_p50":
            success = await ImageEditor.adjust_brightness(work_path, temp_out, 1.5)

        # Contrast
        elif action == "ed_con_low":
            success = await ImageEditor.adjust_contrast(work_path, temp_out, 0.6)
        elif action == "ed_con_med":
            success = await ImageEditor.adjust_contrast(work_path, temp_out, 1.0)
        elif action == "ed_con_hi":
            success = await ImageEditor.adjust_contrast(work_path, temp_out, 1.5)
        elif action == "ed_con_vhi":
            success = await ImageEditor.adjust_contrast(work_path, temp_out, 2.5)

        # Grayscale
        elif action == "ed_gray":
            success = await ImageEditor.convert_to_grayscale(work_path, temp_out)

        # Rotation
        elif action == "ed_rot_90":
            success = await ImageEditor.rotate_image(work_path, temp_out, 90)
        elif action == "ed_rot_180":
            success = await ImageEditor.rotate_image(work_path, temp_out, 180)
        elif action == "ed_rot_270":
            success = await ImageEditor.rotate_image(work_path, temp_out, 270)

        # Sharpen
        elif action == "ed_sharp":
            success = await ImageEditor.sharpen_image(work_path, temp_out, 2.0)

        # A4 moslashtirish
        elif action == "ed_a4":
            success = await ImageEditor.fit_to_a4(work_path, temp_out)

        else:
            logger.warning(f"Noma'lum amal: {action}")
            return False

        # Muvaffaqiyatli bo'lsa, vaqtinchalik nusxani ish nusxasiga ko'chirish
        if success and temp_out.exists():
            try:
                shutil.move(str(temp_out), str(work_path))
            except Exception as e:
                logger.error(f"Fayl ko'chirishda xato: {e}")
                return False

        return success

    @staticmethod
    def create_work_session(original_path: str | Path) -> dict:
        """
        Tahrirlash sessiyasini yaratish.

        Args:
            original_path: Asl rasm yo'li

        Returns:
            Sessiya ma'lumotlari lug'ati
        """
        original = Path(original_path)
        work_path = TEMP_DIR / f"work_{original.stem}_{id(original_path)}.jpg"

        try:
            shutil.copy2(str(original), str(work_path))
        except Exception as e:
            logger.error(f"Ish sessiyasi yaratishda xato: {e}")
            work_path = original

        return {
            "original_path": str(original),
            "work_path": str(work_path),
            "edits_applied": [],
        }

    @staticmethod
    async def get_image_info(image_path: str | Path) -> dict:
        """
        Rasm haqida ma'lumot olish.

        Returns:
            {width, height, mode, format, size_bytes}
        """
        def _sync():
            from PIL import Image
            from pathlib import Path as P
            p = P(image_path)
            with Image.open(p) as img:
                return {
                    "width":      img.width,
                    "height":     img.height,
                    "mode":       img.mode,
                    "format":     img.format or "JPEG",
                    "size_bytes": p.stat().st_size,
                }

        try:
            return await asyncio.get_event_loop().run_in_executor(None, _sync)
        except Exception as e:
            logger.error(f"get_image_info xatosi: {e}")
            return {}
