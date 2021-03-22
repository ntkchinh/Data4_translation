"""Back Translation to augment a dataset."""

from __future__ import print_function
from __future__ import division

from tensor2tensor.data_generators import translate_envi
from tensor2tensor.utils import registry


# End-of-sentence marker.
EOS = translate_envi.EOS

# For English-Vietnamese the IWSLT'15 corpus
# from https://nlp.stanford.edu/projects/nmt/ is used.



# For development 1,553 parallel sentences are used.
_VIEN_TEST_DATASETS = [[
    # "https://github.com/stefan-it/nmt-en-vi/raw/master/data/dev-2012-en-vi.tgz",  # pylint: disable=line-too-long
    "",
    ("tst2012.vi", "tst2012.en")
]]

_ENVI_TEST_DATASETS = [[
    # "https://github.com/stefan-it/nmt-en-vi/raw/master/data/dev-2012-en-vi.tgz",  # pylint: disable=line-too-long
    "",
    ("tst2012.en", "tst2012.vi")
]]


_11CLASSES_APPEND_TAG_ENVI_DATASETS = [
    ['', ('train.en.fixed.append128.tag', 'train.vi.fixed.append128.tag')],  # original.
    ['', ('medical.en.fixed.filter.append128.tag', 'medical.vi.fixed.filter.append128.tag')],
    ['', ('Gnome.en.fixed.filter.train.tag', 'Gnome.vi.fixed.filter.train.tag')],
    ['', ('Kde4.en.fixed.filter.train.tag', 'Kde4.vi.fixed.filter.train.tag')],
    ['', ('law.en.fixed.filter.fixed.tag', 'law.vi.fixed.filter.fixed.tag')],
    ['', ('fbwiki.en.fixed.tag', 'fbwiki.vi.fixed.tag')],
    ['', ('qed.en.fixed.filter.append128.tag', 'qed.vi.fixed.filter.append128.tag')],
    ['', ('open_sub.en.fixed.max250k.append128.tag', 'open_sub.vi.fixed.max250k.append128.tag')],
    ['', ('Ubuntu_tp_en.txt.fixed.filter.train.tag', 'Ubuntu_tp_vi.txt.fixed.filter.train.tag')],
    ['', ('ELRC_2922.en-vi.en.fixed.append128.tag', 'ELRC_2922.en-vi.vi.fixed.append128.tag')],
    ['', ('bible_uedin.en.fixed.append128.tag', 'bible_uedin.vi.fixed.append128.tag')],
    ['', ('m21book_add2train.en.fixed.append128.tag', 'm21book_add2train.vi.fixed.append128.tag')],
    ['', ('tatoeba.en.fixed.append128.tag', 'tatoeba.vi.fixed.append128.tag')],
    ['', ('ted2020.en.fixed.filter.fixed.append128.tag', 'ted2020.vi.fixed.filter.fixed.append128.tag')],
    ['', ('vnsn.en.filter.fixed.append128.tag', 'vnsn.vi.filter.fixed.append128.tag')],
    ['', ('youtube.fixed.en.fixed.append128.tag', 'youtube.fixed.vi.fixed.append128.tag')],
    ['', ('youtube.teded.en.fixed.filter.fixed.append128.tag', 'youtube.teded.vi.fixed.filter.fixed.append128.tag')],
]


_11CLASSES_APPEND_TAG_VIEN_DATASETS = [
    [url, (vi, en)] for [url, (en, vi)] in _11CLASSES_APPEND_TAG_ENVI_DATASETS
]


@registry.register_problem
class TranslateClass11AppendtagVienIwslt32k(translate_envi.TranslateEnviIwslt32k):
  """Problem spec for IWSLT'15 En-Vi translation."""

  @property
  def approx_vocab_size(self):
    return 2**15  # 32768

  def source_data_files(self, dataset_split):
    train = dataset_split == translate_envi.problem.DatasetSplit.TRAIN
    return _11CLASSES_APPEND_TAG_VIEN_DATASETS if train else _VIEN_TEST_DATASETS


@registry.register_problem
class TranslateClass11AppendtagEnviIwslt32k(translate_envi.TranslateEnviIwslt32k):
  """Problem spec for IWSLT'15 En-Vi translation."""

  @property
  def approx_vocab_size(self):
    return 2**15  # 32768

  def source_data_files(self, dataset_split):
    train = dataset_split == translate_envi.problem.DatasetSplit.TRAIN
    return _11CLASSES_APPEND_TAG_ENVI_DATASETS if train else _ENVI_TEST_DATASETS
