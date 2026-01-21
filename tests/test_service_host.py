from eventide_python.service_host import ServiceHost


class CounterService:
    def __init__(self) -> None:
        self.calls = 0

    def run_once(self) -> None:
        self.calls += 1


class FlakyService:
    def __init__(self) -> None:
        self.calls = 0

    def run_once(self) -> None:
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("boom")


def test_service_host_runs_services() -> None:
    host = ServiceHost(poll_interval=0)
    service = CounterService()
    host.register(service)
    host.run(max_iterations=2)
    assert service.calls == 2


def test_service_host_handles_errors() -> None:
    host = ServiceHost(poll_interval=0)
    service = FlakyService()
    host.register(service)
    host.run(max_iterations=2)
    assert service.calls == 2
