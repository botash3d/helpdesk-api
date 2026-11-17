import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine

@pytest.fixture
def query_counter():
    count = {"n":0}

    def _count(conn,cursor,statement,parameters,context,executemany):
        count["n"]+=1

    event.listen(Engine,"after_cursor_execute",_count)
    yield count
    event.remove(Engine,"after_cursor_execute",_count)

    