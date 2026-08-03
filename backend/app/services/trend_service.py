"""Lab value trend detection - pure Python/scipy, no LLM involved. Matches
the frontend's LabTrend contract: {test_name, trend, points:[{date,value,unit}]}."""
from scipy import stats
from sqlalchemy.orm import Session

from app.models.lab_result import LabResult
from app.models.visit import Visit

MIN_POINTS = 3
# Threshold on the *total* modeled change over the observed period, relative
# to the mean value (not a per-day rate - lab values often move slowly over
# months, so a tiny per-day slope can still be a real trend over the window).
RELATIVE_CHANGE_THRESHOLD = 0.10


def compute_trend(points: list[tuple]) -> str:
    """points: list of (date, value) tuples, already sorted by date ascending."""
    if len(points) < MIN_POINTS:
        return "insufficient_data"

    x = [(d - points[0][0]).days for d, _ in points]
    y = [v for _, v in points]
    mean_y = (sum(y) / len(y)) or 1.0

    if len(set(x)) < 2:
        relative_change = (max(y) - min(y)) / abs(mean_y)
        relative_change *= 1 if y[-1] >= y[0] else -1
    else:
        slope, *_ = stats.linregress(x, y)
        relative_change = (slope * (x[-1] - x[0])) / abs(mean_y)

    if relative_change > RELATIVE_CHANGE_THRESHOLD:
        return "increasing"
    if relative_change < -RELATIVE_CHANGE_THRESHOLD:
        return "decreasing"
    return "stable"


def get_lab_trend(db: Session, patient_id, test_name: str) -> dict:
    rows = (
        db.query(LabResult)
        .join(Visit, LabResult.visit_id == Visit.id)
        .filter(Visit.patient_id == patient_id, LabResult.test_name.ilike(f"%{test_name}%"))
        .filter(LabResult.test_date.isnot(None), LabResult.value.isnot(None))
        .order_by(LabResult.test_date.asc())
        .all()
    )

    points = [{"date": r.test_date, "value": r.value, "unit": r.unit} for r in rows]
    trend = compute_trend([(r.test_date, r.value) for r in rows])
    display_name = rows[0].test_name if rows else test_name

    return {"test_name": display_name, "trend": trend, "points": points}
