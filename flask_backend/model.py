import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def monthly_linear_regression(rows, months_to_predict=1):

    if not rows:
        return None

    df = pd.DataFrame(rows)
    df["dispatch_date_time"] = pd.to_datetime(df["dispatch_date_time"])

    # Aggregate monthly totals
    monthly = (
        df
        .groupby(pd.Grouper(key="dispatch_date_time", freq="M"))
        .size()
        .reset_index(name="count")
    )

    monthly = monthly.sort_values("dispatch_date_time").reset_index(drop=True)

    if len(monthly) < 2:
        return None

    # Create numeric time index
    monthly["time_index"] = np.arange(len(monthly))

    X = monthly[["time_index"]]
    y = monthly["count"]

    model = LinearRegression()
    model.fit(X, y)

    last_index = monthly["time_index"].iloc[-1]

    future_indexes = np.arange(
        last_index + 1,
        last_index + 1 + months_to_predict
    ).reshape(-1, 1)

    predictions = model.predict(future_indexes)

    predictions = [max(0, int(p)) for p in predictions]

    return {
        "historical": monthly.tail(12).to_dict(orient="records"),
        "forecast": predictions
    }