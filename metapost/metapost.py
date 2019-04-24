import json
import markdown
import os
import re
from datetime import datetime
from markdown.extensions.extra import ExtraExtension
from tzlocal import get_localzone


class MetaPostError(Exception):
    pass


class MetaPost(object):

    def __init__(self, source_text: str, filepath: str = None):
        self.source_text = source_text.strip()
        self.predefined_meta = dict()
        self.filepath = filepath if filepath is not None else "None(text as source)"
        if filepath is not None:
            self.predefined_meta["_filepath_"] = self.filepath
            self.predefined_meta["_filename_"] = os.path.basename(filepath).strip(".md")
            self.predefined_meta["_last_update_"] = self._get_last_update_dt(filepath)

    @classmethod
    def from_file(cls, filepath: str):
        # check path
        if os.path.isfile(filepath) is False:
            raise MetaPostError("MataMDError: file does not exist.")
        if os.path.splitext(filepath)[1].lower() != ".md":
            raise MetaPostError("MataMDError: expect a path of a markdown file.")
        # validate format
        with open(filepath, mode="r") as f:
            source_text = f.read().strip()
        try:
            cls._extract_block(source_text, block_type="meta")
            cls._extract_block(source_text, block_type="content")
        except MetaPostError:
            basename = os.path.basename(filepath)
            raise MetaPostError("MataMDError: invalid content in file:{}", format(basename))
        # return
        return cls(source_text, str(filepath))

    @classmethod
    def from_text(cls, source_text: str):
        source_text = source_text.strip()
        # validate format
        try:
            cls._extract_block(source_text, block_type="meta")
            cls._extract_block(source_text, block_type="content")
        except MetaPostError:
            raise MetaPostError("MataMDError: invalid content.")
        return cls(source_text)

    def to_dict(self, meta_configs: list, strict_mode: bool = True, md_exts: list = None) -> dict:
        # meta
        result = dict()
        result["meta"] = dict()
        result["meta"].update(self.to_meta(meta_configs, strict_mode))
        # html
        result["html"] = ""
        result["html"] = self.to_html(md_exts)
        return result

    def to_json(self, meta_configs: list, strict_mode: bool = True, md_exts: list = None) -> str:

        return json.dumps(self.to_dict(meta_configs, strict_mode, md_exts))

    def to_meta(self, meta_configs: list, strict_mode: bool = True) -> dict:
        result = dict()
        # extract lines into meta dict
        meta_txt = self._extract_block(self.source_text, block_type="meta")
        pattern = r"""\s*([\d\w_]+?)\s*\:\s*(.+[^\s])\s*"""
        regex = re.compile(pattern, re.MULTILINE)
        # strict mode only take meta in configs
        key_val_tuples = regex.findall(meta_txt)
        expected_meta_keys = [v["key"] for v in meta_configs]
        if strict_mode is True:
            key_val_tuples = [v for v in key_val_tuples if v[0] in expected_meta_keys]
        result.update(key_val_tuples)
        # Update predefined meta
        self.predefined_meta["_content_markdown_"] = self._extract_block(self.source_text, block_type="content")
        result.update(self.predefined_meta)
        # check missing key and cast type
        for cfg in meta_configs:
            # check missing required key
            key, datatype, required, df_val = cfg["key"], cfg["datatype"], cfg["required"], cfg["df_val"]
            if required is True and key not in result:
                raise MetaPostError("MataMDError: required meta:{} is missing".format(key))
            if required is False and key not in result and df_val is not None:
                result[key] = df_val
                continue
            elif required is False and key not in result and df_val is None:
                continue
            result[key] = self._type_cast(result[key], datatype)
        return result

    def to_html(self, md_exts: list = None) -> str:
        if md_exts is None:
            md_exts = [ExtraExtension()]
        content_txt = self._extract_block(self.source_text, "content")
        html = markdown.markdown(content_txt, extensions=md_exts)
        html = self._append_target_equals_blank(html)
        return html

    @staticmethod
    def _extract_block(source_text: str, block_type="meta") -> str:
        if block_type not in ("meta", "content"):
            raise MetaPostError("MataMDError: block_type can only be 'meta' or 'content'")
        try:
            pattern = r"""```(.*?)```(.*)"""
            regex = re.compile(pattern, re.DOTALL)
            group_id = 1 if block_type == "meta" else 2
            result = regex.match(source_text.strip()).group(group_id).strip()
        except (AttributeError, IndexError):
            raise MetaPostError("MataMDError: unable to extract {}".format(block_type))
        return result

    @staticmethod
    def _append_target_equals_blank(html: str) -> str:
        return re.sub(
            pattern='<a .*href=".*".*>.*?</a>',
            repl=lambda m: m.group()[:3] + 'target="_blank" ' + m.group()[3:],
            string=html
        )

    @staticmethod
    def _get_last_update_dt(filepath: str) -> str:
        local_tz_obj = get_localzone()
        if filepath is None:
            return datetime.now(tz=local_tz_obj).isoformat()
        epoch = os.path.getmtime(filepath)
        return datetime.fromtimestamp(epoch, tz=local_tz_obj).isoformat()

    @staticmethod
    def _type_cast(val: str, datatype: str):
        if datatype not in ("bool", "int", "float", "str", "json"):
            raise MetaPostError("MetaMDError: invalid datatype of meta config")
        val = val.strip()
        try:
            if datatype == "bool":
                result = None
                result = True if val.lower() in ("true", "t", "yes", "y", "1") else result
                result = False if val.lower() in ("false", "f", "no", "n", "0") else result
                if result in (True, False):
                    return result
                else:
                    raise ValueError()
            elif datatype == "int":
                return int(val)
            elif datatype == "float":
                return float(val)
            elif datatype == "json":
                return json.loads(val)
            elif datatype == "str":
                return val
        except ValueError:
            raise MetaPostError("Unable to cast {} to {}".format(val, datatype))
        except (json.decoder.JSONDecodeError, TypeError):
            raise MetaPostError("Unable to cast {} to json".format(val, datatype))
