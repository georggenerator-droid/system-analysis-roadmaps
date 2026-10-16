# M06 Спроектируй обработку событий

[← Маршрут](../README.md) · [Назад: M05](m05-api-evolution.md) · [Дальше: M07 →](m07-reliability.md)

**Результат:** ты описываешь отправку и обработку сообщений, включая дубликаты и изменение порядка. Ориентир — 28 часов.

Изучи событие и команду, producer/consumer, очередь и pub/sub, partition key, consumer group, offset, acknowledgement, повторную доставку, lag, DLQ и replay. Kafka и RabbitMQ решают пересекающиеся задачи, но не являются взаимозаменяемыми коробками с одинаковой моделью поведения.

Разбирай гарантии по границам: запись в БД, публикация, доставка и внешний эффект. At-least-once требует обработки повторов. Обещание exactly-once в одном механизме не означает ровно один внешний HTTP-вызов или одну запись в любой чужой БД. Publisher confirm и consumer acknowledgement тоже подтверждают разные участки пути.

**Обязательно:**

- [V07 Kafka 101 Events](https://developer.confluent.io/courses/apache-kafka/events/) · EN. Разбери событие и устройство Kafka на уровне идеи.
- [V08 Kafka 101 Partitions](https://developer.confluent.io/courses/apache-kafka/partitions/) · EN. Изучи partitions и роль ключа для выбранного порядка.
- [V09 Kafka 101 Consumers](https://developer.confluent.io/courses/apache-kafka/consumers/) · EN. Разбери consumer groups и чтение событий.
- [S55 Consumer Acknowledgements and Publisher Confirms](https://www.rabbitmq.com/docs/confirms) · EN. Прочитай отдельно publisher confirms и consumer acknowledgements. Нарисуй границы их гарантий.
- [S50 Transactional Outbox](https://microservices.io/patterns/data/transactional-outbox.html) · EN. Изучи, какую проблему dual write решает Outbox и почему публикация всё равно может повторяться.

**Расширение:**

- [S56 Apache Kafka Documentation](https://kafka.apache.org/documentation/) · EN. Выбери документацию своей версии Kafka и проверь детали порядка, групп и доставки.
- [S57 AsyncAPI Document](https://www.asyncapi.com/docs/concepts/asyncapi-document) · EN. Посмотри описание channel, operation и message в используемой версии AsyncAPI. Не смешивай синтаксис разных версий.

**Сделай:** спроектируй BookingConfirmed и BookingCancelled для внешней платформы. Опиши eventId, bookingId, версию события, occurredAt, correlationId и данные предметной области. Выбери partition key и объясни, какой порядок сохраняется и где он не обещан. Назначь владельца схемы и правила совместимости.

Подготовь алгоритм публикации через Outbox и обработки через дедупликацию/Inbox или другой обоснованный механизм. Отметка eventId и локальный эффект должны быть согласованы транзакционно. Если consumer вызывает внешний API, одной локальной таблицы недостаточно для атомарности с чужой системой: нужны её идемпотентность и сверка результата.

Опиши сбои до/после коммита, после отправки до отметки Outbox, после локальной обработки до ack. Покажи повтор старого BookingConfirmed после BookingCancelled: бизнес-модель не должна возвращаться назад только из-за поздней доставки. Реши, использовать ли версию агрегата, проверку состояния или другой механизм.

**Самопроверка:** когда подтверждать обработку? Что доказывает offset? Где порядок существует, а где нет? Когда допустим replay? Почему DLQ не является решением проблемы без владельца и процедуры разбора? Где сломается наивная «ровно одна доставка»?

**Контрольная точка 1:** проведи 60-минутный разбор контракта и событий с «тимлидом». Проверяется новая вариация: consumer падает после внешнего успешного вызова. Ты показываешь точку неопределённости, восстановление и недостающие гарантии партнёра.

---

## Перед сдачей

- [ ] Выполнена практика из блока.
- [ ] Могу объяснить решение и ответить на вопросы самопроверки.
- [ ] Обновлены связанные работы проекта.
- [ ] Замечания ментора исправлены.

[Отметить прогресс](../../../templates/progress.md) · [Шаблон постановки](../../../templates/spec-template.md)

[← Маршрут](../README.md) · [Назад: M05](m05-api-evolution.md) · [Дальше: M07 →](m07-reliability.md)
