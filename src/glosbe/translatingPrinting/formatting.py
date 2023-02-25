from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace
from itertools import product, islice, count, chain
from typing import Iterable, Callable, Any

import numpy as np
import pandas as pd
from more_itertools import bucket, split_when
from numpy import ndarray
from pandas import DataFrame, RangeIndex, MultiIndex, Series
from pandas.core.indexes.numeric import Int64Index, NumericIndex
from tabulate import tabulate

from ..translating.parsing.parsing import Record
from ..translating.scrapping import TranslationResult, TranslationTypes


class AbstractFormatter(ABC):

	invisibles = '',  ' ', '\u00A0', '\u2000', '\u2001', '\u2002', '\u2003', '\u2004', '\u2005' '\u2006', '\u2007', '\u2008', '\u2009',

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


class AbstractToManyFormatter(ABC):

	@classmethod
	@abstractmethod
	def format_to_many(cls, to_format):
		raise NotImplementedError

	@classmethod
	def format_many_to_many(cls, to_formats: Iterable):
		for to_format in to_formats:
			yield from cls.format_to_many(to_format)


class AbstractFromManyToManyFormatter(ABC):

	@classmethod
	@abstractmethod
	def format_from_many(cls, to_formats: Iterable) -> Iterable:
		raise NotImplementedError


class AbstractIntoPrintableIterableFormatter:
	sep = ' '
	pre_all = ''
	pre_one = ''
	post_all = '\n'
	post_one = ''
	pre_group = ''
	post_group = ''
	no_value = None

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
	def format_many_into_printable_iterable(cls, to_formats: Iterable[Any], *, level=None, **kwargs) -> Iterable[str]:
		if level is None:
			level = cls._get_starting_group_level(**kwargs)
		yield from cls._gen_if(cls._get_pre_all(**kwargs))
		yield from cls._format_many_into_printable_iterable_core(to_formats, level=level, **kwargs)
		yield from cls._gen_if(cls.post_all)

	@classmethod
	def _is_grouped(cls, **kwargs) -> bool:
		return False

	@classmethod
	def _get_starting_group_level(cls, **kwargs) -> int:
		return 0

	@classmethod
	def _format_many_into_printable_iterable_core(cls, to_formats: Iterable[Any], level, **kwargs):
		if level != 0 and cls._is_grouped(**kwargs):
			yield from cls._format_with_groups(to_formats, level, **kwargs)
		else:
			yield from cls._format_without_groups(to_formats, **kwargs)

	@classmethod
	def _format_without_groups(cls, to_formats: Iterable[Any], **kwargs) -> Iterable[str]:
		is_first = True
		for to_format in to_formats:
			if not is_first and cls.sep:
				yield cls.sep
			yield from cls.format_into_printable_iterable(to_format, **kwargs)
			is_first = False
		if is_first:
			yield from cls._get_no_value_string(**kwargs)

	@classmethod
	def _get_no_value_string(cls, **kwargs) -> Iterable[str]:
		if cls.no_value is not None:
			yield cls.no_value

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

	NO_RECORDS_MESSAGE = 'No translation has been found!'

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

	@classmethod
	def format_many_into_printable_iterable(cls, records: Iterable, **kwargs):
		records = list(records)
		if not records:
			records = [Record(cls.NO_RECORDS_MESSAGE)]
		yield from super().format_many_into_printable_iterable(records, **kwargs)


class TranslationFormatter(AbstractFormatter, AbstractIntoStringFormatter, AbstractIntoPrintableIterableFormatter):
	_post_sep_length = 64
	_pre_sep_length = 4
	group_dash = '-'

	sep = ''
	post_one = '\n'
	post_all = ''

	@classmethod
	def format(cls, translation: TranslationResult) -> TranslationResult:
		translation.records = RecordFormatter.format_many(translation.records)
		return translation

	@classmethod
	def format_into_string(cls, translation: TranslationResult, **kwargs) -> str:
		return ''.join(cls.format_into_printable_iterable(**kwargs))

	@classmethod
	def format_many_into_string(cls, translations: Iterable[TranslationResult], main_division: TranslationTypes = None, prefix_style: TranslationTypes = None, level: int =None) -> str:
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
		return main_division in (TranslationTypes.WORD, TranslationTypes.LANG)

	@classmethod
	def _get_starting_group_level(cls, main_division: TranslationTypes, **kwargs) -> int:
		return 1 if cls._is_grouped(main_division) else 0

	@classmethod
	def _format_core_into_printable_iterable(cls, translation: TranslationResult, **kwargs) -> Iterable[str]:
		yield from RecordFormatter.format_many_into_printable_iterable(translation.records, **kwargs)

	@classmethod
	def format_into_printable_iterable(cls, translation: TranslationResult, **kwargs) -> Iterable[str]:
		yield ''.join(super().format_into_printable_iterable(translation, **kwargs))


class TableFormatter(AbstractFormatter, AbstractIntoStringFormatter):
	@classmethod
	def format_into_string(cls, table, **kwargs) -> str:
		return tabulate(table, tablefmt='rounded_outline')

	@classmethod
	def format(cls, table: DataFrame) -> Iterable[DataFrame]:
		table = HeaderToDefaultFormatter.format(table)
		table = DataTableFormatter.format(table)
		tables = TableSplitter.format_to_many(table)
		tables = TableMerger.format_from_many(tables)
		tables = TableSizeAdjusterFormatter.format_many(tables)
		tables = RowNamesTableFormatter.format_many(tables)
		yield from tables

	@classmethod
	def format_many(cls, tables) -> Iterable:
		for table in tables:
			yield from cls.format(table)


class HeaderToDefaultFormatter(AbstractFormatter):
	@classmethod
	def format(cls, table: DataFrame):
		if str(table.iloc[0, 0]) + str(table.iloc[0, 1]) == '01' or isinstance(table.columns, MultiIndex):
			table = pd.concat([table.columns.to_frame().T, table], ignore_index=True)
			table.columns = range(len(table.columns))
		return table


class DataTableFormatter(AbstractFormatter):
	@classmethod
	def format(cls, table: DataFrame) -> DataFrame:
		table = TrashRemovingFormatter.format(table)
		table = DuplicateRemoverTableFormatter.format(table)
		return table


class TrashRemovingFormatter(AbstractFormatter):

	_unnamed = 'Unnamed:'

	@classmethod
	def format(cls, table: DataFrame) -> DataFrame:
		for row, col in product(table.index, islice(table.columns, 3)):
			if cls._is_trash(table.at[row, col]):
				table.at[row, col] = list(islice(chain(cls.invisibles, count()), col + 1))[-1]

		table.columns = list(map(lambda c: '' if cls._is_trash(c) else c, iter(table.columns)))

		return table

	@classmethod
	def _is_trash(cls, val):
		return str(val).startswith(cls._unnamed)


class DuplicateRemoverTableFormatter(AbstractFormatter):
	_replacing_value = ''

	@classmethod
	def format(cls, table: DataFrame) -> DataFrame:
		last = None
		for row, col in product(table.index, table.columns):
			curr = table.at[row, col]
			if curr == last:
				table.at[row, col] = cls._replacing_value
			else:
				last = curr
		return table


class TableSplitter(AbstractToManyFormatter):
	@classmethod
	def format_to_many(cls, table: DataFrame):
		by_empties = EmptyRowSplitter.format_to_many(table.values.tolist())
		by_types = TypeSplitter.format_many_to_many(by_empties)
		for by_type in by_types:
			yield pd.DataFrame(by_type, columns=range(len(by_type[0])))

	@classmethod
	def get_presence_list(cls, row: list[str]) -> list[bool]:
		return list(map(lambda v: v not in cls.invisibles, row))


class EmptyRowSplitter(AbstractToManyFormatter):
	@classmethod
	def format_to_many(cls, table: list) -> Iterable[ndarray]:
		curr_table = []
		for row in table:
			if any(row):
				curr_table.append(row)
			else:
				yield curr_table
				curr_table = []
		yield curr_table


class TypeSplitter(AbstractToManyFormatter):

	@classmethod
	def format_to_many(cls, table: ndarray) -> Iterable[list]:
		return split_when(table, cls._should_split)

	@classmethod
	def _should_split(cls, row1, row2) -> bool:
		return row1[0] and row1[0] != row2[0]


class TableSizeAdjusterFormatter(AbstractFormatter):
	@classmethod
	def format(cls, table: DataFrame) -> DataFrame:
		df = pd.DataFrame(table, columns=table.columns)
		df.replace('', np.nan, inplace=True)
		df.dropna(how='all', axis=1, inplace=True)
		df.replace(np.nan, '', inplace=True)
		return df


class TableMerger(AbstractFromManyToManyFormatter):

	@classmethod
	def format_from_many(cls, tables: Iterable) -> Iterable:
		merged = None
		for table in tables:
			if (len([v for v in table.iloc[:, 0] if v]) == 1) and (merged is None or len(table.columns) == len(merged.columns)):
				merged = table if merged is None else pd.concat([merged, table], ignore_index=True)
			else:
				if merged is not None:
					yield merged
				merged = None
				yield table
		if merged is not None:
			yield merged


class HeaderTableFormatter(AbstractFormatter):
	@classmethod
	def format(cls, table: DataFrame) -> DataFrame:
		if isinstance(table.columns, (RangeIndex, Int64Index, NumericIndex)):
			table, table.columns = table[1:], table.iloc[0]
		return table


class RowNamesTableFormatter(AbstractFormatter):
	@classmethod
	def format(cls, table: DataFrame) -> DataFrame:
		if isinstance(table.index, (RangeIndex, Int64Index, NumericIndex)):
			table = table.set_index(table.columns.array[0])
		return table