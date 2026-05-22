from taskiq import SimpleRetryMiddleware
from taskiq_aio_pika import AioPikaBroker
from taskiq_fastapi import init as taskiq_fastapi_init

broker = AioPikaBroker(url="amqp://guest:guest@localhost:5672//").with_middlewares(
    SimpleRetryMiddleware(default_retry_count=3),
)

taskiq_fastapi_init(broker, "main:app")