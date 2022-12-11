from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Iterable, Callable

from more_itertools import split_when

from ..constants import PageCodeMessages
from ..parsing.parser import Record
from ..translator import TranslationResult, TranslationTypes


class AbstractFormatter(ABC):

	@classmethod
	@abstractmethod
	def format(cls, to_format):
		raise NotImplementedError

	@classmethod
	def format_many(cls, to_formats) -> Iterable:
		return (cls.format(to_format) for to_format in to_formats)


class AbstractIntoStringFormatter(ABC):

	@classmethod
	@abstractmethod
	def format_into_string(cls, to_format, **kwargs) -> str:
		raise NotImplementedError

	@classmethod
	def format_many_into_string(cls, to_formats: Iterable, sep: str, **kwargs) -> str:
		formatted = map(lambda to_format: cls.format_into_string(to_format, **kwargs), to_formats)
		string = sep.join(formatted)
		return string

	@classmethod
	def _add_if_exist(cls, to_add: str, brackets: str = '()', sep=' ') -> str:
		return sep + brackets[0] + to_add + brackets[1] if to_add else ''


class GenderFormatter(AbstractFormatter):

	@classmethod
	def format(cls, gender: str) -> str:
		if not gender:
			return gender

		if gender == 'feminine':
			gender = 'fem'
		elif gender == 'masculine':
			gender = 'masc'
		elif gender == 'neuter':
			gender = 'neut'
		return gender


class PartOfSpeechFormatter(AbstractFormatter):

	@classmethod
	def format(cls, part_of_speech: str) -> str:
		if part_of_speech == 'adverb':
			part_of_speech = 'adv.'
		if part_of_speech == 'adjective':
			part_of_speech = 'adj.'
		return part_of_speech


class RecordFormatter(AbstractFormatter, AbstractIntoStringFormatter):

	@classmethod
	def format(cls, record: Record):
		record = replace(record)
		record.gender = GenderFormatter.format(record.gender)
		record.part_of_speech = PartOfSpeechFormatter.format(record.part_of_speech)
		return record

	@classmethod
	def format_into_string(cls, record: Record, **kwargs) -> str:
		string = record.translation
		string += cls._add_if_exist(record.gender, '[]')
		string += cls._add_if_exist(record.part_of_speech, '()')
		return string

	@classmethod
	def format_many_into_string(cls, to_formats: Iterable, sep: str = '; ', **kwargs) -> str:
		return super().format_many_into_string(to_formats, sep, **kwargs)


class TranslationFormatter(AbstractFormatter, AbstractIntoStringFormatter):

	@classmethod
	def format(cls, translation: TranslationResult) -> TranslationResult:
		translation.records = RecordFormatter.format_many(translation.records)
		return translation

	@classmethod
	def format_into_string(cls, translation: TranslationResult, **kwargs) -> str:
		prefix_style = kwargs['prefix_style']
		string = cls._get_prefix(translation, prefix_style)
		string += RecordFormatter.format_many_into_string(translation.records)
		return string

	@classmethod
	def _get_prefix(cls, translation: TranslationResult, prefix_style: TranslationTypes) -> '':
		if prefix_style == TranslationTypes.LANG:
			return translation.trans_args.word
		if prefix_style == TranslationTypes.WORD:
			return translation.trans_args.to_lang
		if prefix_style == TranslationTypes.DOUBLE:
			return f'{translation.trans_args.to_lang}-{translation.trans_args.word}: '
		return ''

	@classmethod  # TODO: Just in case - think of refactor
	def format_many_into_string(cls, translations: Iterable[TranslationResult], sep: str = '\n', main_division: TranslationTypes = None, prefix_style: TranslationTypes = None) -> str:
		main_divisioned = split_when(translations, cls._get_key_function(main_division))
		get_divider = cls._get_main_divider_getter(main_division)
		# print(list(list(main_divisioned)[0][0].records))
		super_format_many_into_string = super().format_many_into_string
		division_to_string = lambda division: super_format_many_into_string(division, sep, prefix_style=prefix_style)
		inner_formatted = list(map(lambda division: (get_divider(division), division_to_string(division)), main_divisioned))
		if len(inner_formatted) > 1:
			pre_dash = '-' * 4
			post_dash = '-' * 64
			result = '\n'.join(f'{pre_dash} {divider} {post_dash}\n{inner}' for divider, inner in inner_formatted)
		else:
			result = inner_formatted[0][1]

		return result

	@classmethod
	def _get_main_divider_getter(cls, main_division: TranslationTypes) -> Callable[[TranslationResult], str]:
		if main_division == TranslationTypes.WORD:
			return lambda tr: tr.trans_args.word
		if main_division == TranslationTypes.LANG:
			return lambda tr: tr.trans_args.to_lang
		return lambda tr: ''

	@classmethod
	def _get_key_function(cls, main_division: TranslationTypes) -> Callable[[TranslationResult, TranslationResult], bool]:
		if main_division == TranslationTypes.WORD:
			return lambda tr1, tr2: tr1.trans_args.word != tr2.trans_args.word
		if main_division == TranslationTypes.LANG:
			return lambda tr1, tr2: tr1.trans_args.to_lang != tr2.trans_args.to_lang
		return lambda tr1, tr2: False

	# TODO: Move to printing
	def _get_page_code_messages(self, code: int):
		if code == 404:
			return PageCodeMessages.PAGE_NOT_FOUND_404
		if code == 303:
			return PageCodeMessages.PAGE_NOT_FOUND_303
		return PageCodeMessages.UNHANDLED_PAGE_FULL_MESSAGE.format(code)
