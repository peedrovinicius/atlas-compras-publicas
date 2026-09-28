from dental_procurement_intelligence.identity.domains import (
    DomainStatus,
    IdentityDomain,
    active_domains,
    available_domains,
    get_domain,
)
from dental_procurement_intelligence.identity.rules.medications import (
    MEDICATION_CATEGORY_SPECS,
    MEDICATIONS_DOMAIN,
)


def test_multidomain_registry_exposes_dental_and_medications() -> None:
    domains = available_domains()

    assert [domain.domain for domain in domains] == [
        IdentityDomain.DENTAL,
        IdentityDomain.MEDICATIONS,
    ]


def test_dental_is_active_and_medications_are_experimental() -> None:
    dental = get_domain(IdentityDomain.DENTAL)
    medications = get_domain(IdentityDomain.MEDICATIONS)

    assert dental.status == DomainStatus.ACTIVE
    assert dental.benchmark_required is False

    assert medications.status == DomainStatus.EXPERIMENTAL
    assert medications.benchmark_required is False
    assert MEDICATIONS_DOMAIN.status == DomainStatus.EXPERIMENTAL
    assert MEDICATION_CATEGORY_SPECS == ()


def test_only_validated_domains_are_active() -> None:
    assert [domain.domain for domain in active_domains()] == [
        IdentityDomain.DENTAL
    ]
