class Parser:

    def __init__(self, text=""):
        self._text: str = text

    def set_page_text(self, text: str):
        self._text = text

