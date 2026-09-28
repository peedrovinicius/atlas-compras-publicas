import unicodedata

from dental_procurement_intelligence.identity.models import ProductCategory

_CATEGORY_LABELS = {
    ProductCategory.COMPOSITE_RESIN: "Resina composta",
    ProductCategory.FLOWABLE_RESIN: "Resina flow",
    ProductCategory.ADHESIVE: "Adesivo odontológico",
    ProductCategory.GLASS_IONOMER: "Ionômero de vidro",
    ProductCategory.PHOSPHORIC_ACID: "Ácido fosfórico",
    ProductCategory.ALGINATE: "Alginato",
    ProductCategory.FLUORIDE_GEL: "Gel fluoretado",
    ProductCategory.PROPHYLAXIS_PASTE: "Pasta profilática",
    ProductCategory.CALCIUM_HYDROXIDE: "Hidróxido de cálcio",
    ProductCategory.ZINC_OXIDE: "Óxido de zinco",
    ProductCategory.EUGENOL: "Eugenol",
    ProductCategory.RADIOGRAPHIC_FIXER: "Fixador radiográfico",
    ProductCategory.RADIOGRAPHIC_DEVELOPER: "Revelador radiográfico",
    ProductCategory.LOCAL_ANESTHETIC: "Anestésico local",
    ProductCategory.UNKNOWN: "Não reconhecido",
}


def parser_categories() -> list[dict[str, str | bool]]:
    return [
        {
            "id": category.value,
            "label": _CATEGORY_LABELS[category],
            "fallback": category is ProductCategory.UNKNOWN,
        }
        for category in ProductCategory
    ]


def parser_category_label(category_id: str) -> str:
    for category, label in _CATEGORY_LABELS.items():
        if category.value == category_id:
            return label
    return category_id.replace("_", " ").strip().title()


_CATEGORY_SEARCH_ALIASES = {
    ProductCategory.COMPOSITE_RESIN: (
        "resina composta",
        "composite resin",
    ),
    ProductCategory.FLOWABLE_RESIN: (
        "resina flow",
        "resina fluida",
        "flowable",
        "flow",
    ),
    ProductCategory.ADHESIVE: (
        "adesivo odontologico",
        "adesivo dental",
        "adesivo",
        "bond",
    ),
    ProductCategory.GLASS_IONOMER: (
        "ionomero de vidro",
        "cimento ionomero",
        "ionomero",
    ),
    ProductCategory.PHOSPHORIC_ACID: (
        "acido fosforico",
        "condicionador acido",
    ),
    ProductCategory.ALGINATE: (
        "alginato",
    ),
    ProductCategory.FLUORIDE_GEL: (
        "gel fluoretado",
        "gel de fluor",
        "fluor gel",
        "fluoreto",
    ),
    ProductCategory.PROPHYLAXIS_PASTE: (
        "pasta profilatica",
        "pasta de profilaxia",
    ),
    ProductCategory.CALCIUM_HYDROXIDE: (
        "hidroxido de calcio",
        "calcium hydroxide",
    ),
    ProductCategory.ZINC_OXIDE: (
        "oxido de zinco",
    ),
    ProductCategory.EUGENOL: (
        "eugenol",
    ),
    ProductCategory.RADIOGRAPHIC_FIXER: (
        "fixador radiografico",
        "fixador raio x",
        "fixador rx",
    ),
    ProductCategory.RADIOGRAPHIC_DEVELOPER: (
        "revelador radiografico",
        "revelador raio x",
        "revelador rx",
    ),
    ProductCategory.LOCAL_ANESTHETIC: (
        "anestesico local",
        "anestesico odontologico",
        "anestesico",
    ),
}


def _normalize_search_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    without_accents = "".join(
        character
        for character in decomposed
        if not unicodedata.combining(character)
    )
    return " ".join(without_accents.casefold().split())


def resolve_product_search_query(
    query: str,
) -> tuple[str | None, list[str], str | None]:
    normalized = _normalize_search_text(query)
    if not normalized:
        return None, [], None

    best_match: tuple[ProductCategory, str] | None = None
    for category, aliases in _CATEGORY_SEARCH_ALIASES.items():
        for alias in aliases:
            normalized_alias = _normalize_search_text(alias)
            padded_query = f" {normalized} "
            padded_alias = f" {normalized_alias} "
            if padded_alias in padded_query:
                if best_match is None or len(normalized_alias) > len(best_match[1]):
                    best_match = (category, normalized_alias)

    if best_match is None:
        return None, normalized.split(), None

    category, alias = best_match
    residual = " ".join(f" {normalized} ".replace(f" {alias} ", " ").split())
    return category.value, residual.split(), _CATEGORY_LABELS[category]


def product_search_shortcuts() -> list[dict[str, str]]:
    shortcuts: list[dict[str, str]] = []
    for category, aliases in _CATEGORY_SEARCH_ALIASES.items():
        shortcuts.append(
            {
                "category": category.value,
                "label": _CATEGORY_LABELS[category],
                "query": aliases[0],
            }
        )
    return shortcuts
