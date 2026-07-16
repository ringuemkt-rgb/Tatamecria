from neurojitsu.vision.zone_events import ZoneEventEngine, ZoneEventKind


def test_zone_engine_emits_single_dwell_and_exit_duration() -> None:
    engine = ZoneEventEngine({"sensory_pause": 2_000})

    entered = engine.update(1_000, {"sensory_pause": {7}})
    assert len(entered) == 1
    assert entered[0].kind == ZoneEventKind.ENTER

    dwell = engine.update(3_100, {"sensory_pause": {7}})
    assert len(dwell) == 1
    assert dwell[0].kind == ZoneEventKind.DWELL
    assert dwell[0].dwell_ms == 2_100

    assert engine.update(4_000, {"sensory_pause": {7}}) == ()

    exited = engine.update(5_500, {"sensory_pause": set()})
    assert len(exited) == 1
    assert exited[0].kind == ZoneEventKind.EXIT
    assert exited[0].dwell_ms == 4_500


def test_zone_engine_handles_multiple_tracks_and_reset() -> None:
    engine = ZoneEventEngine()
    events = engine.update(100, {"tatame": {1, 2}})
    assert {(event.track_id, event.kind) for event in events} == {
        (1, ZoneEventKind.ENTER),
        (2, ZoneEventKind.ENTER),
    }

    engine.reset()
    events_after_reset = engine.update(200, {"tatame": {1}})
    assert len(events_after_reset) == 1
    assert events_after_reset[0].kind == ZoneEventKind.ENTER
