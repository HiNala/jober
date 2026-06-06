from jober_worker.tasks import ping


def test_ping_task_returns_pong() -> None:
    result = ping.run()
    assert result == "pong"
