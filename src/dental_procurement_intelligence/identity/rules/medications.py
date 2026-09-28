from dental_procurement_intelligence.identity.domains import (
    DomainDescriptor,
    DomainStatus,
    IdentityDomain,
)

MEDICATIONS_DOMAIN = DomainDescriptor(
    domain=IdentityDomain.MEDICATIONS,
    label="Medicamentos",
    rule_namespace="medications",
    status=DomainStatus.EXPERIMENTAL,
    benchmark_required=False,
    notes=(
        "Parser farmacêutico possui benchmarks independentes v1-v4. "
        "As regras permanecem isoladas do classificador odontológico principal."
    ),
)

MEDICATION_CATEGORY_SPECS: tuple[()] = ()
