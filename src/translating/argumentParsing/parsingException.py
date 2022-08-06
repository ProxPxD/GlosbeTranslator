class ParsingException(ConnectionError):
    def __init__(self, validation_messages: list[str], *args):
        super().__init__(*args)
        self.validation_messages = validation_messages