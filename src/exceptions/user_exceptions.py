class UserException(Exception):
    pass


class DuplicateFieldError(UserException):
    def __init__(self, field_name: str):
        self.field_name = field_name
        super().__init__(f"Duplicate field {field_name}")


class EntityNotFoundError(UserException):
    def __init__(self, entity_name: str):
        self.entity_name = entity_name
        super().__init__(f"{entity_name} not found")
