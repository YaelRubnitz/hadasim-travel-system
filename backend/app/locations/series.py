"""Load ordered movement tracks from the append-only location table."""
from datetime import datetime, timezone

from sqlmodel import Session, desc, select

from app.models.location import LocationUpdate
from app.models.student import Student
from app.locations.types import StudentTrack, TrackPoint


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _row_to_point(person_tz: str, row: LocationUpdate) -> TrackPoint | None:
    if row.timestamp is None:
        return None
    return TrackPoint(
        person_tz=person_tz,
        latitude=row.latitude,
        longitude=row.longitude,
        recorded_at=_ensure_utc(row.timestamp),
    )


def _rows_to_track(person_tz: str, rows: list[LocationUpdate]) -> StudentTrack:
    points: list[TrackPoint] = []
    for row in rows:
        point = _row_to_point(person_tz, row)
        if point is not None:
            points.append(point)
    points.sort(key=lambda p: (p.recorded_at, p.latitude, p.longitude))
    return StudentTrack(person_tz=person_tz, points=tuple(points))


def fetch_track(
    session: Session,
    person_tz: str,
    *,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int | None = None,
) -> StudentTrack:
    """
    Load one person's location history, ascending by ``timestamp`` then ``id``.

    - ``since`` / ``until``: inclusive window filters.
    - ``since > until``: empty track.
    - ``limit``: last N rows matching filters, still returned ascending.
    """
    if since is not None and until is not None and since > until:
        return StudentTrack(person_tz=person_tz, points=())

    conditions = [LocationUpdate.student_tz == person_tz]
    if since is not None:
        conditions.append(LocationUpdate.timestamp >= since)
    if until is not None:
        conditions.append(LocationUpdate.timestamp <= until)

    statement = select(LocationUpdate).where(*conditions)

    if limit is not None:
        statement = statement.order_by(
            desc(LocationUpdate.timestamp), desc(LocationUpdate.id)
        ).limit(limit)
        rows = list(session.exec(statement).all())
        rows.sort(key=lambda r: (_ensure_utc(r.timestamp), r.id or 0))
    else:
        statement = statement.order_by(
            LocationUpdate.timestamp.asc(), LocationUpdate.id.asc()
        )
        rows = list(session.exec(statement).all())

    return _rows_to_track(person_tz, rows)


def fetch_class_tracks(
    session: Session,
    class_name: str,
    *,
    since: datetime | None = None,
    until: datetime | None = None,
    limit_per_student: int | None = None,
) -> dict[str, StudentTrack]:
    """One track per student in ``class_name``; omits students with no points."""
    student_tzs = session.exec(
        select(Student.tz).where(Student.class_name == class_name)
    ).all()
    tracks: dict[str, StudentTrack] = {}
    for tz in student_tzs:
        track = fetch_track(
            session,
            tz,
            since=since,
            until=until,
            limit=limit_per_student,
        )
        if track.points:
            tracks[tz] = track
    return tracks
