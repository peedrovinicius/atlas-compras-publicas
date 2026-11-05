"""Limitador de janela deslizante com memoria limitada por instancia."""

from collections import deque
from collections.abc import Callable
from threading import Lock
from time import monotonic


class SlidingWindowRateLimiter:
    """Cota por cliente com remocao de buckets inativos e limite de cardinalidade.

    O identificador do cliente deve vir de uma camada de proxy confiavel.
    Esta classe nao interpreta nem valida cabecalhos HTTP.
    """

    def __init__(
        self,
        *,
        limit: int,
        window_seconds: float,
        max_clients: int,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if limit < 1 or window_seconds <= 0 or max_clients < 1:
            raise ValueError("Limites e duracao devem ser positivos.")
        self._limit = limit
        self._window_seconds = window_seconds
        self._max_clients = max_clients
        self._clock = clock
        self._requests: dict[str, deque[float]] = {}
        self._lock = Lock()
        self._last_cleanup = clock()

    def allow(self, client_id: str) -> bool:
        with self._lock:
            now = self._clock()
            at_capacity = len(self._requests) >= self._max_clients
            # Evita revarrer milhares de chaves a cada rejeicao sob carga.
            cleanup_due = now - self._last_cleanup >= self._window_seconds
            cleanup_at_capacity = at_capacity and now - self._last_cleanup >= 1.0
            if cleanup_due or cleanup_at_capacity:
                stale = [
                    key
                    for key, requests in self._requests.items()
                    if not requests or now - requests[-1] >= self._window_seconds
                ]
                for key in stale:
                    del self._requests[key]
                self._last_cleanup = now

            if client_id not in self._requests:
                if len(self._requests) >= self._max_clients:
                    # Rejeita novos identificadores em vez de crescer sem limite.
                    return False
                self._requests[client_id] = deque()

            requests = self._requests[client_id]
            while requests and now - requests[0] >= self._window_seconds:
                requests.popleft()
            if len(requests) >= self._limit:
                return False
            requests.append(now)
            return True
