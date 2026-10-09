"""Unbound integration boundary for M3's WaterloggingRiskService.

This module deliberately avoids assuming a service constructor, method name or
result shape. Bind the final tested M3 implementation here in a later change.
"""


class RiskServiceAdapter:
    """Hold an optional M3 service implementation without recreating its logic."""

    def __init__(self, implementation: object | None = None) -> None:
        self._implementation = implementation

    @property
    def is_configured(self) -> bool:
        return self._implementation is not None

    def get_implementation(self) -> object:
        if self._implementation is None:
            raise RuntimeError(
                "M3 WaterloggingRiskService is not bound. Define its public interface before integration."
            )
        return self._implementation
