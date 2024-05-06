from typing import Dict, Optional

import pandas as pd


class AverageForecaster:
    def __init__(self):
        self.means: Optional[Dict[str, float]] = None

    def fit(self, daily_df: pd.DataFrame) -> "AverageForecaster":
        out = {}
        mean_data = daily_df.mean()
        for name in daily_df.mean().index:
            if name == "Date":
                continue
            out[name] = mean_data[name]
        self.means = out
        return self

    def predict(self, days: float) -> Optional[Dict[str, float]]:
        if self.means is None:
            return None
        out = {}
        for n, v in self.means.items():
            out[n] = v * days
        out["All"] = sum(out.values())
        return out
