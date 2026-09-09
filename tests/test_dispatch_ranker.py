from app.services.dispatch_ranker import (
    DispatchRanker,
    RankableIncident,
    RankableResource,
)
from app.services.geo import haversine_km

INCIDENT = RankableIncident(
    incident_type="MEDICAL",
    latitude=-1.95,
    longitude=30.06,
    severity="HIGH",
)


def resource(**overrides) -> RankableResource:
    base = dict(
        id=1,
        name="Unit",
        resource_type="AMBULANCE",
        latitude=-1.95,
        longitude=30.06,
        capacity=4,
        current_load=0,
        status="AVAILABLE",
    )
    base.update(overrides)
    return RankableResource(**base)


def test_haversine_zero_and_symmetric():
    assert haversine_km(-1.95, 30.06, -1.95, 30.06) == 0
    a = haversine_km(-1.95, 30.06, -1.98, 30.10)
    b = haversine_km(-1.98, 30.10, -1.95, 30.06)
    assert abs(a - b) < 1e-9
    # 1° of latitude ≈ 111.2 km
    assert abs(haversine_km(0, 0, 1, 0) - 111.19) < 0.3


def test_type_match_beats_closer_mismatch():
    ranker = DispatchRanker()
    ambulance_far = resource(
        id=1,
        name="Far ambulance",
        resource_type="AMBULANCE",
        latitude=-1.95,
        longitude=30.12,
    )
    bus_close = resource(
        id=2,
        name="Close bus",
        resource_type="BUS",
        latitude=-1.95,
        longitude=30.061,
    )
    ranked = ranker.rank(INCIDENT, [ambulance_far, bus_close])
    assert ranked[0].resource_id == 1
    assert ranked[0].type_match > ranked[1].type_match


def test_closer_same_type_ranks_higher():
    ranker = DispatchRanker()
    near = resource(id=1, name="Near", longitude=30.061)
    far = resource(id=2, name="Far", longitude=30.12)
    ranked = ranker.rank(INCIDENT, [far, near])
    assert ranked[0].resource_id == 1
    assert ranked[0].distance_km < ranked[1].distance_km


def test_busy_ranks_below_available():
    ranker = DispatchRanker()
    busy = resource(id=1, name="Busy ambulance", status="BUSY", current_load=4)
    free = resource(id=2, name="Free clinic", resource_type="CLINIC")
    ranked = ranker.rank(INCIDENT, [busy, free])
    assert ranked[0].resource_id == 2
    assert ranked[1].score < ranked[0].score


def test_offline_excluded_by_default_and_ineligible_when_included():
    ranker = DispatchRanker()
    offline = resource(id=9, name="Offline", status="OFFLINE")
    live = resource(id=1, name="Live")
    assert ranker.rank(INCIDENT, [offline, live])[0].resource_id == 1
    included = ranker.rank(INCIDENT, [offline], include_ineligible=True)
    assert included[0].eligible is False
    assert included[0].score == 0


def test_spare_capacity_improves_score():
    ranker = DispatchRanker()
    full = resource(id=1, name="Full", current_load=4, capacity=4)
    empty = resource(id=2, name="Empty", current_load=0, capacity=4)
    ranked = ranker.rank(INCIDENT, [full, empty])
    assert ranked[0].resource_id == 2
    assert ranked[0].capacity_score > ranked[1].capacity_score


def test_score_is_bounded():
    ranker = DispatchRanker()
    scored = ranker.score_one(
        RankableIncident("FIRE", -1.95, 30.06, "CRITICAL"),
        resource(resource_type="FIRE_UNIT"),
    )
    assert 0 <= scored.score <= 100


def test_fire_prefers_fire_unit():
    ranker = DispatchRanker()
    fire = RankableIncident("FIRE", -1.95, 30.06, "HIGH")
    ranked = ranker.rank(
        fire,
        [
            resource(id=1, name="Volunteers", resource_type="VOLUNTEER_TEAM"),
            resource(id=2, name="Engine", resource_type="FIRE_UNIT"),
        ],
    )
    assert ranked[0].resource_id == 2


def test_flood_prefers_shelter_and_bus_over_clinic():
    ranker = DispatchRanker()
    flood = RankableIncident("FLOOD", -1.95, 30.06, "HIGH")
    ranked = ranker.rank(
        flood,
        [
            resource(id=1, name="Clinic", resource_type="CLINIC"),
            resource(id=2, name="Shelter", resource_type="SHELTER", capacity=100),
            resource(id=3, name="Bus", resource_type="BUS", capacity=40),
        ],
    )
    assert ranked[0].resource_type in {"SHELTER", "BUS"}
    assert ranked[-1].resource_type == "CLINIC"


def test_missing_person_prefers_volunteers():
    ranker = DispatchRanker()
    missing = RankableIncident("MISSING_PERSON", -1.95, 30.06, "MEDIUM")
    ranked = ranker.rank(
        missing,
        [
            resource(id=1, name="Clinic", resource_type="CLINIC"),
            resource(id=2, name="Search", resource_type="VOLUNTEER_TEAM"),
        ],
    )
    assert ranked[0].resource_id == 2


def test_best_returns_none_when_empty():
    assert DispatchRanker().best(INCIDENT, []) is None


def test_reasons_explain_the_score():
    scored = DispatchRanker().score_one(INCIDENT, resource())
    blob = " ".join(scored.reasons).lower()
    assert "type match" in blob
    assert "km" in blob
    assert "available" in blob
