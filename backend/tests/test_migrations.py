import os
import subprocess
import sys

from sqlalchemy import create_engine, inspect

from app.db.base import Base


def test_migration_matches_models(tmp_path):
    url = f"sqlite:///{tmp_path / 'mig.db'}"
    env = {**os.environ, "DATABASE_URL": url}
    for args in (["upgrade", "head"], ["downgrade", "base"], ["upgrade", "head"]):
        r = subprocess.run([sys.executable, "-m", "alembic", *args], env=env, capture_output=True, text=True)
        assert r.returncode == 0, r.stderr

    insp = inspect(create_engine(url))
    assert set(insp.get_table_names()) - {"alembic_version"} == set(Base.metadata.tables)
    for name, table in Base.metadata.tables.items():
        assert {c["name"] for c in insp.get_columns(name)} == {c.name for c in table.columns}, name
