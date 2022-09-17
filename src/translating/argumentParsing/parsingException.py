class ParsingException(ConnectionError):
    def __init__(self, validation_messages: list[str] = None, *args):
        super().__init__(*args)
        self.validation_messages = validation_messages if validation_messages else []