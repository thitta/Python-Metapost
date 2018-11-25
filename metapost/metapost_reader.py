from __future__ import absolute_import
from __future__ import unicode_literals
from .metapost import MetaPost, MetaPostError
from markdown.extensions.extra import ExtraExtension
from typing import Any, List
import json
import os


class MetaPostReader(object):

    def __init__(self):
        self.mtp_list = []
        self.meta_configs = []
        self.strict_mode = True
        self.md_exts = [ExtraExtension()]

    def read_dir(self, dirpath: str, reset: bool = False, walk: bool = False) -> None:
        filepaths = self._list_markdown_files(dirpath, walk)
        for filepath in filepaths:
            self.read_file(filepath, reset=False)
        if reset is True:
            self._reset_mtp_list(reserve_latest=len(filepaths))
        return self

    def read_text(self, source_text: str, reset: bool = False) -> None:
        self.mtp_list.append(MetaPost.from_text(source_text))
        if reset is True:
            self._reset_mtp_list(reserve_latest=1)
        return self

    def read_file(self, filepath: str, reset: bool = False) -> None:
        self._check_markdown_file(filepath)
        self.mtp_list.append(MetaPost.from_file(filepath))
        if reset is True:
            self._reset_mtp_list(reserve_latest=1)
        return self

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    def to_dict(self) -> List[dict]:
        result = []
        for meta, html in zip(self.to_meta(), self.to_html()):
            result.append({"meta": meta, "html": html})
        return result

    def to_html(self) -> List[str]:
        return [mtp.to_html(self.md_exts) for mtp in self.mtp_list]

    def to_meta(self) -> List[dict]:
        result = []
        try:
            for mtp in self.mtp_list:
                result.append(mtp.to_meta(self.meta_configs, self.strict_mode))
        except MetaPostError:
            raise MetaPostReaderError("Fail to parse MetaPost, filepath:{}".format(mtp.filepath))
        return result

    def add_meta_cfg(self, key: str, datatype: str = "str", required: bool = True, df_val: Any = None) -> None:
        datatype = datatype if datatype in ("bool", "int", "float", "str") else "str"
        to_append = {"key": str(key), "datatype": datatype, "required": bool(required), "df_val": df_val}
        self.meta_configs.append(to_append)

    def set_strict_mode(self, strict_mode: bool) -> None:
        self.strict_mode = bool(strict_mode)

    def set_markdown_extensions(self, extensions: list) -> None:
        self.md_exts = extensions

    def _reset_mtp_list(self, reserve_latest: int = 0) -> None:
        if reserve_latest == 0:
            self.mtp_list = []
        else:
            self.mtp_list = self.mtp_list[-reserve_latest:]

    @staticmethod
    def _list_markdown_files(dirpath: str, walk: bool = False) -> list:
        if os.path.isdir(dirpath) is False:
            raise MetaPostError("MTPReaderError: directory does not exist.")
        # search one directory only
        if walk is False:
            filepaths = [os.path.join(dirpath, filename)
                         for filename in os.listdir(dirpath) if filename.endswith(".md")]
            return filepaths
        # search multiple directories
        result = []
        for root, dirs, files in os.walk(dirpath):
            for basename in files:
                if basename.endswith(".md"):
                    result.append(os.path.join(root, basename))
        return result

    @staticmethod
    def _check_markdown_file(filepath: str) -> None:
        if os.path.isfile(filepath) is False:
            raise MetaPostReaderError("MTPReaderError: file path does not exist")
        if os.path.splitext(filepath)[1].lower() != ".md":
            raise MetaPostReaderError("MTPReaderError: expect .md extension")


class MetaPostReaderError(Exception):
    pass
