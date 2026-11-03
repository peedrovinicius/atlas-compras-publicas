"""Garantias de cota e consumo limitado de memoria do rate limiter."""

import pytest

from dental_procurement_intelligence.api.rate_limit import SlidingWindowRateLimiter


def test_limit_is_per_client_and_renews_after_window() -> None:
    now = [100.0]
    limiter = SlidingWindowRateLimiter(
        limit=2, window_seconds=60, max_clients=4, clock=lambda: now[0]
    )

    assert limiter.allow("a")
    assert limiter.allow("a")
    assert not limiter.allow("a")
    assert limiter.allow("b")

    now[0] = 159.0
    assert not limiter.allow("a")
    now[0] = 160.0
    assert limiter.allow("a")
    assert limiter.allow("b")


def test_capacity_denies_new_clients_and_expires_inactive_buckets() -> None:
    now = [100.0]
    limiter = SlidingWindowRateLimiter(
        limit=2, window_seconds=60, max_clients=2, clock=lambda: now[0]
    )

    assert limiter.allow("first")
    now[0] = 130.0
    assert limiter.allow("second")
    assert not limiter.allow("third")
    assert len(limiter._requests) == 2

    now[0] = 160.0
    assert limiter.allow("third")
    assert set(limiter._requests) == {"second", "third"}
    assert not limiter.allow("first")
    assert len(limiter._requests) == 2

    now[0] = 191.0
    assert limiter.allow("first")
    assert len(limiter._requests) == 2


def test_distinct_client_flood_cannot_expand_bucket_dictionary() -> None:
    now = [100.0]
    limiter = SlidingWindowRateLimiter(
        limit=1, window_seconds=60, max_clients=3, clock=lambda: now[0]
    )

    for number in range(1000):
        accepted = limiter.allow(f"client-{number}")
        assert accepted is (number < 3)
    assert len(limiter._requests) == 3

    now[0] = 161.0
    assert limiter.allow("new-client")
    assert len(limiter._requests) == 1


@pytest.mark.parametrize(
    ("limit", "window", "max_clients"),
    [(0, 60, 3), (1, 0, 3), (1, 60, 0)],
)
def test_reject_invalid_rate_limiter_configuration(
    limit: int, window: float, max_clients: int
) -> None:
    with pytest.raises(ValueError):
        SlidingWindowRateLimiter(
            limit=limit, window_seconds=window, max_clients=max_clients
        )
