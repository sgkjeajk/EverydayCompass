
import importlib.util
from datetime import date
from pathlib import Path
import pytest
P=Path(__file__).resolve().parents[1]/"scripts"/"update_events.py"
spec=importlib.util.spec_from_file_location("u2",P); u=importlib.util.module_from_spec(spec); spec.loader.exec_module(u)
@pytest.mark.parametrize("key", list(u.SOURCES))
def test_fixture_for_each_source(key):
    html=(Path(__file__).parent/"fixtures"/f"{key}.html").read_text(encoding="utf-8")
    got=u.parse_source_html(html,key,date(2026,9,25))
    assert len(got)==1
    assert got[0]["source_key"]==key
    assert got[0]["title"]=="Fixture Event"
