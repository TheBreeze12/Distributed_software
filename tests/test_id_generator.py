from app.services.id_generator import SnowflakeGenerator


def test_snowflake_id_unique_and_increasing():
    generator = SnowflakeGenerator(worker_id=1, datacenter_id=1)
    ids = [generator.next_id() for _ in range(2000)]

    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)
