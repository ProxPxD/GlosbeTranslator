import requests


class WrongStatusCodeError(ConnectionError):
	def __init__(self, page: requests.Response, *args):
		super().__init__(*args)
		self.page = page


class TranslatorArgumentException(ValueError):
	pass  # TODO
