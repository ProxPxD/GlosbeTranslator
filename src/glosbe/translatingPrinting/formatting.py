from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from typing import Iterable, Callable, Any

from more_itertools import bucket

from ..translating.parsing.parser import Record
from ..translating.translator import TranslationResult, TranslationTypes


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


class AbstractIntoPrintableIterableFormatter:
	sep = ' '
	pre_all = ''
	pre_one = ''
	post_all = '\n'
	post_one = ''
	pre_group = ''
	post_group = ''

	@classmethod
	def _gen_if(cls, to_yield: str):
		if to_yield:
			yield to_yield

	@classmethod
	def _get_pre_all(cls, **kwargs) -> str:
		return cls.pre_all

	@classmethod
	def _get_pre_one(cls, one: Any, **kwargs) -> str:
		return cls.pre_one

	@classmethod
	def format_into_printable_iterable(cls, to_format: Any, **kwargs) -> Iterable[str]:
		yield from cls._gen_if(cls._get_pre_one(to_format, **kwargs))
		yield from cls._format_core_into_printable_iterable(to_format, **kwargs)
		yield from cls._gen_if(cls.post_one)

	@classmethod
	def _format_core_into_printable_iterable(cls, to_format: Any, **kwargs) -> Iterable[str]:
		yield to_format

	@classmethod
	def format_many_into_printable_iterable(cls, to_formats: Iterable[Any], *, level=0, **kwargs) -> Iterable[str]:
		yield from cls._gen_if(cls._get_pre_all(**kwargs))
		yield from cls._format_many_into_printable_iterable_core(to_formats, level=level, **kwargs)
		yield from cls._gen_if(cls.post_all)

	@classmethod
	def _is_grouped(cls, **kwargs) -> bool:
		return False

	@classmethod
	def _format_many_into_printable_iterable_core(cls, to_formats: Iterable[Any], level, **kwargs):
		if not level == 0 and cls._is_grouped(**kwargs):
			yield from cls._format_with_groups(to_formats, level, **kwargs)
		else:
			yield from cls._format_without_groups(to_formats, **kwargs)

	@classmethod
	def _format_without_groups(cls, to_formats: Iterable[Any], **kwargs) -> Iterable[str]:
		is_not_first = False
		for to_format in to_formats:
			if is_not_first:
				yield cls.sep
			yield from cls.format_into_printable_iterable(to_format, **kwargs)
			is_not_first = True

	@classmethod
	def _get_grouping_key(cls, **kwargs) -> Callable:
		return lambda a: False

	@classmethod
	def _format_with_groups(cls, to_formats: Iterable[Any], level: int, **kwargs) -> Iterable[str]:
		key = cls._get_grouping_key(**kwargs)
		groups = bucket(to_formats, key)
		for group in groups:
			yield from cls._gen_if(cls._get_pre_group(group, **kwargs))
			# TODO: check level of recursion to decide if there are groups
			yield from cls._format_many_into_printable_iterable_core(groups[group], level=level-1, **kwargs)

	@classmethod
	def _get_pre_group(cls, group: Any, **kwargs) -> str:
		return cls.pre_group


class GenderFormatter(AbstractFormatter, AbstractIntoPrintableIterableFormatter):

	pre_one = ' ['
	post_one = ']'

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


class PartOfSpeechFormatter(AbstractFormatter, AbstractIntoPrintableIterableFormatter):

	pre_one = ' ('
	post_one = ')'

	@classmethod
	def format(cls, part_of_speech: str) -> str:
		if part_of_speech == 'adverb':
			part_of_speech = 'adv.'
		if part_of_speech == 'adjective':
			part_of_speech = 'adj.'
		return part_of_speech


class RecordFormatter(AbstractFormatter, AbstractIntoStringFormatter, AbstractIntoPrintableIterableFormatter):

	sep = '; '
	post_all = ''

	@classmethod
	def format(cls, record: Record):
		record = replace(record)
		record.gender = GenderFormatter.format(record.gender)
		record.part_of_speech = PartOfSpeechFormatter.format(record.part_of_speech)
		return record

	@classmethod
	def format_into_string(cls, record: Record, **kwargs) -> str:
		return ''.join(cls.format_into_printable_iterable(record))

	@classmethod
	def format_many_into_string(cls, to_formats: Iterable, sep: str = '; ', **kwargs) -> str:
		return ''.join(cls.format_many_into_printable_iterable(to_formats))

	@classmethod
	def format_into_printable_iterable(cls, record: Record, **kwargs) -> Iterable[str]:
		yield record.translation
		if record.gender:
			yield from GenderFormatter.format_into_printable_iterable(record.gender, **kwargs)
		if record.part_of_speech:
			yield from PartOfSpeechFormatter.format_into_printable_iterable(record.part_of_speech, **kwargs)


class TranslationFormatter(AbstractFormatter, AbstractIntoStringFormatter, AbstractIntoPrintableIterableFormatter):
	_post_sep_length = 64
	_pre_sep_length = 4
	group_dash = '-'

	sep = ''
	post_one = '\n'
	post_all = '\n'

	@classmethod
	def format(cls, translation: TranslationResult) -> TranslationResult:
		translation.records = RecordFormatter.format_many(translation.records)
		return translation

	@classmethod
	def format_into_string(cls, translation: TranslationResult, **kwargs) -> str:
		return ''.join(cls.format_into_printable_iterable(**kwargs))

	@classmethod
	def format_many_into_string(cls, translations: Iterable[TranslationResult], main_division: TranslationTypes = None, prefix_style: TranslationTypes = None, level=0) -> str:
		return ''.join(cls.format_many_into_printable_iterable(translations, main_division=main_division, prefix_style=prefix_style, level=level))

	@classmethod
	def _get_pre_one(cls, translation: TranslationResult, prefix_style=None, **kwargs) -> str:
		match prefix_style:
			case TranslationTypes.LANG:
				prefix = translation.trans_args.to_lang
			case TranslationTypes.WORD:
				prefix = translation.trans_args.word
			case TranslationTypes.DOUBLE:
				prefix = f'{translation.trans_args.to_lang}-{translation.trans_args.word}'
			case _:
				prefix = ''
		return f'{prefix}: ' if prefix else prefix

	@classmethod
	def _get_pre_group(cls, group: Any, **kwargs) -> str:
		group_str = str(group)
		if not group_str:
			return ''
		pre_dash = cls.group_dash * cls._pre_sep_length
		post_dash = cls.group_dash * cls._post_sep_length
		return f'{pre_dash} {group_str} {post_dash}\n'

	@classmethod
	def _get_grouping_key(cls, main_division: TranslationTypes, **kwargs) -> Callable:
		match main_division:
			case TranslationTypes.WORD:
				return lambda tr: tr.trans_args.word
			case TranslationTypes.LANG:
				return lambda tr: tr.trans_args.to_lang
			case _:
				return lambda tr: ''

	@classmethod
	def _is_grouped(cls, main_division: TranslationTypes, **kwargs) -> bool:
		return bool(main_division)

	@classmethod
	def _format_core_into_printable_iterable(cls, translation: TranslationResult, **kwargs) -> Iterable[str]:
		yield from RecordFormatter.format_many_into_printable_iterable(translation.records, **kwargs)

	@classmethod
	def format_into_printable_iterable(cls, translation: TranslationResult, **kwargs) -> Iterable[str]:
		yield ''.join(super().format_into_printable_iterable(translation, **kwargs))
