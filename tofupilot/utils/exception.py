class RunCreationError(Exception):
    def __init__(self, message: str, warnings: list = None, status_code: int = None):
        self.message = message
        self.warnings = warnings
        self.status_code = status_code
        super().__init__(message)
