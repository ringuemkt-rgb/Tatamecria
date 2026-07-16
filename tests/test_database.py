from datetime import UTC, datetime

import pytest

from neurojitsu.storage.database import Database
from neurojitsu.synthetic.generator import dataframe_to_windows, generate_session_dataframe


def test_database_roundtrip(tmp_path) -> None:
    database = Database(tmp_path / "demo.db")
    database.register_participant("C001", synthetic=True)
    dataframe = generate_session_dataframe(windows_per_phase=1)
    windows = dataframe_to_windows(dataframe)
    database.create_session("NJ-DEMO-001", "C001", windows[0].timestamp_start)
    assert database.store_windows(windows) == 4
    loaded = database.load_windows("NJ-DEMO-001")
    assert len(loaded) == 4
    assert loaded[0].participant_id == "C001"


def test_plain_database_rejects_real_participant(tmp_path) -> None:
    database = Database(tmp_path / "demo.db")
    with pytest.raises(PermissionError):
        database.register_participant("C002", synthetic=False)


def test_missing_session_state_update_fails(tmp_path) -> None:
    database = Database(tmp_path / "demo.db")
    with pytest.raises(KeyError):
        database.set_session_state("missing", "review", datetime.now(UTC))
