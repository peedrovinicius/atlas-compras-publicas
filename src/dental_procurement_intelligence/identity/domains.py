from dataclasses import dataclass
from enum import StrEnum


class IdentityDomain(StrEnum):
    DENTAL = "dental"
    MEDICATIONS = "medications"


class DomainStatus(StrEnum):
    ACTIVE = "active"
    BENCHMARK_REQUIRED = "benchmark_required"


@dataclass(frozen=True, slots=True)
class DomainDescriptor:
    domain: IdentityDomain
    label: str
    rule_namespace: str
    status: DomainStatus
    benchmark_required: bool
    notes: str


_DENTAL = DomainDescriptor(
    domain=IdentityDomain.DENTAL,
    label="Odontologia",
    rule_namespace="dental",
    status=DomainStatus.ACTIVE,
    benchmark_required=False,
    notes="Domínio validado pelos benchmarks técnicos versionados.",
)

_MEDICATIONS = DomainDescriptor(
    domain=IdentityDomain.MEDICATIONS,
    label="Medicamentos",
    rule_namespace="medications",
    status=DomainStatus.BENCHMARK_REQUIRED,
    benchmark_required=True,
    notes=(
        "Próximo domínio planejado. Nenhuma regra de classificação é ativada "
        "antes de taxonomia e benchmark independentes."
    ),
)

DOMAIN_REGISTRY: dict[IdentityDomain, DomainDescriptor] = {
    _DENTAL.domain: _DENTAL,
    _MEDICATIONS.domain: _MEDICATIONS,
}


def get_domain(domain: IdentityDomain | str) -> DomainDescriptor:
    domain_id = IdentityDomain(domain)
    return DOMAIN_REGISTRY[domain_id]


def available_domains() -> tuple[DomainDescriptor, ...]:
    return tuple(DOMAIN_REGISTRY[domain] for domain in IdentityDomain)


def active_domains() -> tuple[DomainDescriptor, ...]:
    return tuple(
        descriptor
        for descriptor in available_domains()
        if descriptor.status == DomainStatus.ACTIVE
    )
