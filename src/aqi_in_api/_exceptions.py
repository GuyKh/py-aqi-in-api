class AQIException(Exception):
    def __init__(self, message: str, status_code: int, body: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.body = body
        self.name = "AQIException"

    def __str__(self) -> str:
        if self.body:
            return f"AQIException({self.status_code}): {self.message} - {self.body}"
        return f"AQIException({self.status_code}): {self.message}"
