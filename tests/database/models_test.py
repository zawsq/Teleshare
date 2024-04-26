from bot.database.models import FltId, PipeMatch, UpdSet


def test_pipe_match() -> None:
    pipe_match = PipeMatch(match={"_id": "69420"})
    dumped = pipe_match.model_dump()
    assert dumped == {"$match": {"_id": "69420"}}

def test_flt_id() -> None:
    flt_id = FltId(_id="id")
    dumped = flt_id.model_dump()
    assert dumped == {"_id": "id"}

def test_upd_set() -> None:
    upd_set = UpdSet(_set={"id here": "69420"})
    dumped = upd_set.model_dump()
    assert dumped == {"$set": {"id here": "69420"}}
