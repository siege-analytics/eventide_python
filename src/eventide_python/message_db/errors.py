class MessageDBError(RuntimeError):
    pass


class WrongExpectedVersion(MessageDBError):
    pass


class CategoryError(MessageDBError):
    pass


class SqlConditionError(MessageDBError):
    pass


class ConsumerGroupError(MessageDBError):
    pass
