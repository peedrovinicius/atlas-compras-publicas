from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PNCPBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class PNCPItem(PNCPBaseModel):
    """Subset of PNCP procurement-item fields used by the analytical pipeline."""

    item_number: int = Field(alias="numeroItem")
    description: str = Field(alias="descricao")
    quantity: Decimal | None = Field(default=None, alias="quantidade")
    unit: str | None = Field(default=None, alias="unidadeMedida")
    estimated_unit_value: Decimal | None = Field(default=None, alias="valorUnitarioEstimado")
    total_value: Decimal | None = Field(default=None, alias="valorTotal")


class PNCPItemResult(PNCPBaseModel):
    """Subset of PNCP awarded-result fields used by the analytical pipeline."""

    item_number: int = Field(alias="numeroItem")
    result_sequence: int | None = Field(default=None, alias="sequencialResultado")
    awarded_quantity: Decimal | None = Field(default=None, alias="quantidadeHomologada")
    awarded_unit_value: Decimal | None = Field(default=None, alias="valorUnitarioHomologado")
    supplier_name: str | None = Field(default=None, alias="nomeRazaoSocialFornecedor")
    supplier_document: str | None = Field(default=None, alias="niFornecedor")
    brand: str | None = Field(default=None, alias="marca")
