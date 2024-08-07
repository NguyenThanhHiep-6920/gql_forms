import sqlalchemy
import logging
import pytest


@pytest.mark.asyncio
async def test_dataloaded(SQLite, DemoData, DBModels):
    async_session_maker = SQLite

    for DBModel in DBModels:
        tableName = DBModel.__tablename__
        table = DemoData.get(tableName, None)
        assert table is not None, f"demodata does not contain {tableName}"
        assert len(table) > 0, f"demodata has 0 rows in table {tableName}"

        statement = sqlalchemy.text(f"SELECT id, lastchange FROM {tableName}")
        async with async_session_maker() as session:
            rows = await session.execute(statement)
            rows = rows.scalars()
            rows = list(rows)
            assert len(rows) == len(table), f" table {tableName} is not fully loaded in DB"
            # assert row is not None, f" table {tableName} has no rows"
            logging.info(f"{tableName} successfully tested")

