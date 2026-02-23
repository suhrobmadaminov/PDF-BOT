"""
Locales paketi — ko'p tilli qo'llab-quvvatlash moduli.
Qo'llab-quvvatlanadigan tillar: O'zbek (uz), Rus (ru), Ingliz (en)
"""

from locales.uz import UZ_TEXTS
from locales.ru import RU_TEXTS
from locales.en import EN_TEXTS

# Barcha tillar bir lug'atda
ALL_TEXTS: dict[str, dict] = {
    "uz": UZ_TEXTS,
    "ru": RU_TEXTS,
    "en": EN_TEXTS,
}


def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """
    Berilgan kalit va til bo'yicha matn olish.

    Args:
        key:    Matn kaliti
        lang:   Til kodi ('uz', 'ru', 'en')
        **kwargs: Formatlash uchun parametrlar

    Returns:
        Formatlangan matn satri
    """
    # Agar til mavjud bo'lmasa, o'zbek tiliga qaytish
    texts = ALL_TEXTS.get(lang, ALL_TEXTS["uz"])

    # Kalit topilmasa, o'zbek tilidan qidirish
    text = texts.get(key, ALL_TEXTS["uz"].get(key, f"[{key}]"))

    # Parametrlar bilan formatlash
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass

    return text
