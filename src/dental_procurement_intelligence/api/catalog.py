import unicodedata
from difflib import SequenceMatcher

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
        "bonding",
        "bond",
    ),
    ProductCategory.GLASS_IONOMER: (
        "ionomero de vidro",
        "cimento de ionomero de vidro",
        "cimento ionomero",
        "cimento de vidro",
        "ionomero",
        "civ",
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
        "fluor",
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
        "anestesia local",
        "anestesico",
    ),
}


def normalize_product_search_text(value: str) -> str:
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
    normalized = normalize_product_search_text(query)
    if not normalized:
        return None, [], None

    query_tokens = normalized.split()
    exact_match: tuple[ProductCategory, str] | None = None

    for category, aliases in _CATEGORY_SEARCH_ALIASES.items():
        for alias in aliases:
            normalized_alias = normalize_product_search_text(alias)
            padded_query = f" {normalized} "
            padded_alias = f" {normalized_alias} "
            if (
                padded_alias in padded_query
                and (
                    exact_match is None
                    or len(normalized_alias) > len(exact_match[1])
                )
            ):
                exact_match = (category, normalized_alias)

    exact_size = (
        len(exact_match[1].split())
        if exact_match is not None
        else 0
    )
    fuzzy_match: tuple[ProductCategory, int, int, float, int] | None = None

    for category, aliases in _CATEGORY_SEARCH_ALIASES.items():
        for alias in aliases:
            normalized_alias = normalize_product_search_text(alias)
            alias_tokens = normalized_alias.split()
            size = len(alias_tokens)

            if size == 0 or size > len(query_tokens):
                continue
            if exact_match is not None and size <= exact_size:
                continue

            for start in range(len(query_tokens) - size + 1):
                candidate_tokens = query_tokens[start : start + size]
                candidate = " ".join(candidate_tokens)
                ratio = SequenceMatcher(
                    None,
                    candidate,
                    normalized_alias,
                ).ratio()

                if ratio < 0.88:
                    continue

                if (
                    fuzzy_match is None
                    or size > fuzzy_match[4]
                    or (
                        size == fuzzy_match[4]
                        and ratio > fuzzy_match[3]
                    )
                ):
                    fuzzy_match = (
                        category,
                        start,
                        start + size,
                        ratio,
                        size,
                    )

    if fuzzy_match is not None:
        category, start, end, _, _ = fuzzy_match
        residual_tokens = query_tokens[:start] + query_tokens[end:]
        return category.value, residual_tokens, _CATEGORY_LABELS[category]

    if exact_match is not None:
        category, alias = exact_match
        residual = " ".join(
            f" {normalized} ".replace(f" {alias} ", " ").split()
        )
        return category.value, residual.split(), _CATEGORY_LABELS[category]

    return None, query_tokens, None


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
