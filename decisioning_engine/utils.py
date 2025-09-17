import logging
from types import SimpleNamespace
from typing import Any, Dict, Optional, Union


def get_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Return a configured logger that writes to stdout. Safe to call multiple times.
    """
    logger = logging.getLogger(name or "decisioning")
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    logger.setLevel(level)
    return logger


# class ConstantAdapter:
#     """
#     Adapter that abstracts access to configuration from either:
#     - a Django model instance (e.g., ConstantVariable), or
#     - a plain dict for raw Python testing
#     """

#     def __init__(self, source: Union[Dict[str, Any], Any]):
#         self._source = source

#     # Percentage ranges used to compute reward percentages
#     def percentage_range(self) -> Dict[int, Dict[str, int]]:
#         if hasattr(self._source, "wysecash_percentage_range"):
#             return self._source.wysecash_percentage_range()
#         return self._source.get("wysecash_percentage_range", {})

#     # RTO/RTP percentages
#     def rto_rtp(self) -> Dict[str, float]:
#         if hasattr(self._source, "rto_rtp"):
#             return self._source.rto_rtp()
#         return self._source.get("rto_rtp", {"rto": 0.0, "rtp": 0.0})

#     # Win factor per band
#     def reward_factors(self) -> Dict[str, float]:
#         if hasattr(self._source, "wyse_cash_win_factor"):
#             return getattr(self._source, "wyse_cash_win_factor")
#         return self._source.get("wyse_cash_win_factor", {})

#     # Running balance accessors
#     def get_running_balance(self) -> float:
#         if hasattr(self._source, "wyse_cash_running_balance"):
#             return float(getattr(self._source, "wyse_cash_running_balance", 0.0))
#         return float(self._source.get("wyse_cash_running_balance", 0.0))

#     def set_running_balance(self, value: float) -> None:
#         if hasattr(self._source, "wyse_cash_running_balance"):
#             setattr(self._source, "wyse_cash_running_balance", value)
#             if hasattr(self._source, "save"):
#                 self._source.save()
#         else:
#             self._source["wyse_cash_running_balance"] = value


# def resolve_constant_adapter(
#     source: Optional[Union[Dict[str, Any], Any]],
# ) -> ConstantAdapter:
#     """
#     Create a ConstantAdapter from a dict or a Django model instance.
#     If source is None, caller should provide its own fallback (e.g., fetch model).
#     """
#     if source is None:
#         raise ValueError("source is required to resolve ConstantAdapter")
#     return ConstantAdapter(source)


def as_object(data: Dict[str, Any]) -> SimpleNamespace:
    """Convert a dict to a SimpleNamespace for attribute access during tests."""
    return SimpleNamespace(**data)


def log_table(logger: logging.Logger, title: str, rows: Dict[str, Any]) -> None:
    """
    Log a simple key/value table for clarity.
    rows: mapping of label -> value
    """
    if not rows:
        logger.info(f"{title}: (no data)")
        return

    key_width = max(len(str(k)) for k in rows.keys())
    logger.info(title)
    logger.info("-" * (len(title)))
    for key, value in rows.items():
        logger.info(f"{str(key).ljust(key_width)} : {value}")
