class AppError(Exception):
    """Base class for domain-level errors handled by the API layer."""


class ItemNotFoundError(AppError):
    def __init__(self, item_id: int) -> None:
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")
