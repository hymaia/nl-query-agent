from prometheus_fastapi_instrumentator import Instrumentator, metrics


instrumentator = Instrumentator(
    should_group_status_codes=True,
    should_ignore_untemplated=True,
    should_respect_env_var=False,
    excluded_handlers=["/metrics", "/health"],
)

instrumentator.add(metrics.latency())
instrumentator.add(metrics.requests())
instrumentator.add(metrics.request_size())
instrumentator.add(metrics.response_size())
