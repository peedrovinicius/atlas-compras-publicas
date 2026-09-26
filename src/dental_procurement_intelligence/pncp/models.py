from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PNCPBaseModel(BaseModel):
    model_config = ConfigDict(extra="allow", populate_by_name=True)


class PNCPOrganization(PNCPBaseModel):
    cnpj: str | None = None
    legal_name: str | None = Field(default=None, alias="razaoSocial")
    branch: str | None = Field(default=None, alias="poderId")
    sphere: str | None = Field(default=None, alias="esferaId")


class PNCPOrganizationUnit(PNCPBaseModel):
    unit_code: str | None = Field(default=None, alias="codigoUnidade")
    unit_name: str | None = Field(default=None, alias="nomeUnidade")
    municipality_id: int | None = Field(default=None, alias="municipioId")
    municipality_name: str | None = Field(default=None, alias="municipioNome")
    state_code: str | None = Field(default=None, alias="ufSigla")
    state_name: str | None = Field(default=None, alias="ufNome")


class PNCPContract(PNCPBaseModel):
    """Subset of procurement metadata used for geographic and temporal analysis."""

    control_number: str | None = Field(default=None, alias="numeroControlePNCP")
    purchase_year: int | None = Field(default=None, alias="anoCompra")
    sequence: int | None = Field(default=None, alias="sequencialCompra")
    modality_name: str | None = Field(default=None, alias="modalidadeNome")
    status_name: str | None = Field(default=None, alias="situacaoCompraNome")
    publication_date: date | None = Field(default=None, alias="dataPublicacaoPncp")
    total_estimated_value: Decimal | None = Field(default=None, alias="valorTotalEstimado")
    total_awarded_value: Decimal | None = Field(default=None, alias="valorTotalHomologado")
    organization: PNCPOrganization | None = Field(default=None, alias="orgaoEntidade")
    organization_unit: PNCPOrganizationUnit | None = Field(default=None, alias="unidadeOrgao")


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
    awarded_total_value: Decimal | None = Field(default=None, alias="valorTotalHomologado")
    discount_percentage: Decimal | None = Field(default=None, alias="percentualDesconto")
    supplier_name: str | None = Field(default=None, alias="nomeRazaoSocialFornecedor")
    supplier_document: str | None = Field(default=None, alias="niFornecedor")
    brand: str | None = Field(default=None, alias="marca")
    result_date: date | None = Field(default=None, alias="dataResultado")
    cancellation_date: datetime | None = Field(default=None, alias="dataCancelamento")
    status_id: int | None = Field(default=None, alias="situacaoCompraItemResultadoId")
    status_name: str | None = Field(default=None, alias="situacaoCompraItemResultadoNome")
