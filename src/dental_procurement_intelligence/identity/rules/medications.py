from dental_procurement_intelligence.identity.domains import (
    DomainDescriptor,
    DomainStatus,
    IdentityDomain,
)

MEDICATIONS_DOMAIN = DomainDescriptor(
    domain=IdentityDomain.MEDICATIONS,
    label="Medicamentos",
    rule_namespace="medications",
    status=DomainStatus.BENCHMARK_REQUIRED,
    benchmark_required=True,
    notes=(
        "Namespace reservado para a taxonomia de medicamentos. "
        "Não contém aliases de classificação até que um dataset independente "
        "seja congelado e revisado."
    ),
)

MEDICATION_CATEGORY_SPECS: tuple[()] = ()
