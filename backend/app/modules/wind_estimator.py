"""Wind estimator (smoothing and gust detection).

Pure-Python, dependency-free module for smoothing apparent wind angle (AWA)
with circular mean, smoothing apparent wind speed (AWS), and computing a gust
value over a sliding time window or EWMA. Designed for unit testing now and
integration later.

Inputs are samples of (AWA deg in [-180, 180], AWS knots, timestamp seconds).
Outputs provide smoothed AWA/AWS and a gust estimate.
"""

from __future__ import annotations

import bisect
import math
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Optional

from ..core.config import settings


@dataclass
class WindSample:
    t: float
    awa_deg: float
    aws_kn: float


def _normalize_angle_deg(angle: float) -> float:
    a = ((angle + 180.0) % 360.0) - 180.0
    if a <= -180.0:
        a = 180.0
    return a


def _circular_mean_deg(degrees: list[float]) -> float:
    if not degrees:
        return 0.0
    sx = 0.0
    sy = 0.0
    for d in degrees:
        r = math.radians(_normalize_angle_deg(d))
        sx += math.cos(r)
        sy += math.sin(r)
    if sx == 0.0 and sy == 0.0:
        # Undefined; pick 180 as stable default for opposing values
        return 180.0
    ang = math.degrees(math.atan2(sy, sx))
    return _normalize_angle_deg(ang)


class WindEstimator:
    def __init__(
        self,
        *,
        method: Optional[str] = None,
        ewma_alpha: Optional[float] = None,
        window_seconds: Optional[float] = None,
        gust_percentile: Optional[float] = None,
    ) -> None:
        self.method = (method or settings.WIND_ESTIMATOR_METHOD).lower()
        self.alpha = float(ewma_alpha if ewma_alpha is not None else settings.WIND_EWMA_ALPHA)
        self.window_seconds = float(window_seconds if window_seconds is not None else settings.WIND_WINDOW_SECONDS)
        self.gust_percentile = float(
            gust_percentile if gust_percentile is not None else settings.WIND_GUST_PERCENTILE
        )
        if self.method not in {"ewma", "window"}:
            raise ValueError(f"Unsupported wind estimator method: {self.method}")

        # State for EWMA
        self._ewa_awa_sin = None  # type: Optional[float]
        self._ewa_awa_cos = None  # type: Optional[float]
        self._ewa_aws = None  # type: Optional[float]

        # State for window
        self._win_samples: Deque[WindSample] = deque()
        self._win_aws_sorted: list[float] = []  # keep a separate sorted list for percentile

    def add_sample(self, awa_deg: float, aws_kn: float, *, timestamp: Optional[float] = None) -> None:
        t = time.time() if timestamp is None else float(timestamp)
        awa = _normalize_angle_deg(float(awa_deg))
        aws = max(0.0, float(aws_kn))

        if self.method == "ewma":
            # EWMA for AWS
            self._ewa_aws = aws if self._ewa_aws is None else (self.alpha * aws + (1 - self.alpha) * self._ewa_aws)
            # Circular EWMA: maintain EWMA of sin/cos components
            s = math.sin(math.radians(awa))
            c = math.cos(math.radians(awa))
            self._ewa_awa_sin = s if self._ewa_awa_sin is None else (self.alpha * s + (1 - self.alpha) * self._ewa_awa_sin)
            self._ewa_awa_cos = c if self._ewa_awa_cos is None else (self.alpha * c + (1 - self.alpha) * self._ewa_awa_cos)
            # For gust with EWMA, we approximate as the max of last window
            self._append_window_sample(WindSample(t, awa, aws))
            self._prune_window(t)
        else:
            # window
            self._append_window_sample(WindSample(t, awa, aws))
            self._prune_window(t)

    def _append_window_sample(self, sample: WindSample) -> None:
        self._win_samples.append(sample)
        # keep sorted AWS list in sync
        bisect.insort(self._win_aws_sorted, sample.aws_kn)

    def _prune_window(self, now_t: float) -> None:
        cutoff = now_t - self.window_seconds
        while self._win_samples and self._win_samples[0].t < cutoff:
            old = self._win_samples.popleft()
            # remove from sorted list
            idx = bisect.bisect_left(self._win_aws_sorted, old.aws_kn)
            if 0 <= idx < len(self._win_aws_sorted) and self._win_aws_sorted[idx] == old.aws_kn:
                self._win_aws_sorted.pop(idx)
            else:
                # fallback linear remove
                try:
                    self._win_aws_sorted.remove(old.aws_kn)
                except ValueError:
                    pass

    def get_state(self) -> dict:
        """Return current estimator outputs as a dict.

        Keys:
        - awa_deg: smoothed AWA
        - aws_kn: smoothed AWS
        - gust_kn: gust estimate (percentile or max in window)
        - method: estimator method
        - window_size: number of samples in the window buffer
        """
        if self.method == "ewma":
            if self._ewa_awa_cos is None or self._ewa_awa_sin is None or self._ewa_aws is None:
                return {"awa_deg": 0.0, "aws_kn": 0.0, "gust_kn": 0.0, "method": self.method, "window_size": 0}
            awa = math.degrees(math.atan2(self._ewa_awa_sin, self._ewa_awa_cos))
            awa = _normalize_angle_deg(awa)
            gust = max(self._win_aws_sorted) if self._win_aws_sorted else 0.0
            return {
                "awa_deg": awa,
                "aws_kn": float(self._ewa_aws),
                "gust_kn": float(gust),
                "method": self.method,
                "window_size": len(self._win_samples),
            }

        # window method: compute circular mean of AWA and mean AWS; gust as percentile
        if not self._win_samples:
            return {"awa_deg": 0.0, "aws_kn": 0.0, "gust_kn": 0.0, "method": self.method, "window_size": 0}
        awa_vals = [s.awa_deg for s in self._win_samples]
        aws_vals = [s.aws_kn for s in self._win_samples]
        awa = _circular_mean_deg(awa_vals)
        aws_mean = sum(aws_vals) / len(aws_vals)
        if self._win_aws_sorted:
            k = self.gust_percentile * (len(self._win_aws_sorted) - 1)
            lo = int(math.floor(k))
            hi = int(math.ceil(k))
            if lo == hi:
                gust = self._win_aws_sorted[lo]
            else:
                w = k - lo
                gust = (1 - w) * self._win_aws_sorted[lo] + w * self._win_aws_sorted[hi]
        else:
            gust = 0.0
        return {"awa_deg": awa, "aws_kn": aws_mean, "gust_kn": float(gust), "method": self.method, "window_size": len(self._win_samples)}
