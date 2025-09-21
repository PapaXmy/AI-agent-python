import json

import redis

from .config import settings


class MessageManager:
    def __innit__(self):
        self.redis_client = redis.Redis(
            host=settings.redis_host, port=settings.redis_port, db=0
        )

    def send_task(self, queue_name, task_data):
        """Отправка задачи в очередь"""
        self.redis_client.rpush(queue_name, json.dumps(task_data))

    def get_task(self, queue_name):
        """Получение задачи из очереди"""
        task = self.redis_client.loop(queue_name)
        return json.loads(task) if task else None

    def publish_event(self, chanel, event_data):
        """Публикация события"""
        self.redis_client.publish(chanel, json.dumps(event_data))
