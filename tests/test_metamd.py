from metapost import MetaPost, MetaPostError
from pathlib import Path
from unittest import TestCase
import json
import os

MOCKS_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mocks")


class TestMetaMD(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_ok_type_cast(self):
        # int
        exp = 999
        act = MetaPost._type_cast("999", "int")
        self.assertEqual(exp, act)
        # float
        exp = 9.9
        act = MetaPost._type_cast("9.9", "float")
        self.assertEqual(exp, act)
        # bool_1
        exp = True
        act = MetaPost._type_cast("true", "bool")
        self.assertEqual(exp, act)
        # bool_2
        exp = False
        act = MetaPost._type_cast("n", "bool")
        self.assertEqual(exp, act)
        # str
        exp = "999"
        act = MetaPost._type_cast("999", "str")
        self.assertEqual(exp, act)
        # json_1
        exp = [True, 1, "123", []]
        act = MetaPost._type_cast(json.dumps(exp), "json")
        self.assertEqual(exp, act)
        # json_2
        exp = ["apple", "orange"]
        act = MetaPost._type_cast('["apple","orange"]', "json")
        self.assertEqual(exp, act)

    def test_raise_type_cast(self):
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("abcd", "int")
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("abcd", "float")
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("abcd", "bool")
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("abcd", "noSuchType")
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("abcd", "json")
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("abcd", "json")
        with self.assertRaises(MetaPostError):
            MetaPost._type_cast("[1,2,abcd]", "json")

    def test_raise_parse_meta_value(self):
        with self.assertRaises(MetaPostError):
            val = "[apple, orange]"
            datatype = "int"
            exp = ["apple", "orange"]
            act = MetaPost._type_cast(val, datatype)
            self.assertEqual(exp, act)

    def test_ok_append_target_equals_blank(self):
        html = 'prefix<a href="http://google.com">Go</a>suffix'
        exp = 'prefix<a target="_blank" href="http://google.com">Go</a>suffix'
        act = MetaPost._append_target_equals_blank(html)
        self.assertEqual(exp, act)

    def test_raise_extract_block(self):
        # invalid parameter
        with self.assertRaises(MetaPostError):
            MetaPost._extract_block(source_text="", block_type="wrong_type")
        # invalid file content
        with self.assertRaises(MetaPostError):
            MetaPost._extract_block(source_text="invalid source text", block_type="meta")

    def test_ok_extract_block(self):
        text = " ```meta block   ``` content block```code block in content```"
        exp1, exp2 = "meta block", "content block```code block in content```"
        act1, act2 = MetaPost._extract_block(text, "meta"), MetaPost._extract_block(text, "content")
        self.assertEqual(exp1, act1)
        self.assertEqual(exp2, act2)

    def test_ok_get_meta(self):
        filepath = os.path.join(MOCKS_ROOT, "post_1.md")
        meta_configs = [{"key": "title", "datatype": "str", "required": True, "df_val": ""},
                        {"key": "on_index", "datatype": "bool", "required": True, "df_val": ""},
                        {"key": "index", "datatype": "int", "required": True, "df_val": ""},
                        {"key": "author", "datatype": "str", "required": False, "df_val": "John"}]
        mmd = MetaPost.from_file(filepath)
        # strict_mode = True
        exp = {"on_index": True, "index": 99, "title": "A mock post", "_filename_": "post_1",
               "author": "John"}
        act = mmd.to_meta(meta_configs, strict_mode=True)
        for key in exp.keys():
            self.assertEqual(exp[key], act[key])
        self.assertFalse("subtitle" in act)
        # strict_mode = False
        act = mmd.to_meta(meta_configs, strict_mode=False)
        self.assertTrue("subtitle" in act)

    def test_raise_get_meta(self):
        filepath = Path.cwd().joinpath("mocks/post_1.md")
        mmd = MetaPost.from_file(filepath)
        # required meta key missing
        with self.assertRaises(MetaPostError):
            meta_configs = [{"key": "required_but_missing", "datatype": "str", "required": True, "df_val": ""}]
            mmd.to_meta(meta_configs, strict_mode=True)
        # can't parse int
        with self.assertRaises(MetaPostError):
            meta_configs = [{"key": "title", "datatype": "int", "required": True, "df_val": ""}]
            mmd.to_meta(meta_configs, strict_mode=True)
        # can't parse float
        with self.assertRaises(MetaPostError):
            meta_configs = [{"key": "title", "datatype": "float", "required": True, "df_val": ""}]
            mmd.to_meta(meta_configs, strict_mode=True)

    def test_ok_get_html(self):
        # html conversion
        filepath = os.path.join(MOCKS_ROOT, "post_1.md")
        mmd = MetaPost.from_file(filepath)
        exp = "<p>some content</p>"
        act = mmd.to_html()
        self.assertEqual(exp, act)

    def test_ok_get_dict(self):
        filepath = os.path.join(MOCKS_ROOT, "post_1.md")
        mmd = MetaPost.from_file(filepath)
        exp = {
            "meta": {
                "on_index": "true",
                "index": "99",
                "title": "A mock post",
                "subtitle": "Gossips-01",
                '_filename_': 'post_1',
                '_filepath_': os.path.join(MOCKS_ROOT, "post_1.md"),
                '_last_update_': mmd._get_last_update_dt(filepath),
                '_content_markdown_': 'some content',
            },
            "html": "<p>some content</p>"
        }
        act = mmd.to_dict(meta_configs=[], strict_mode=False)
        self.assertEqual(exp, act)

    def test_ok_get_json(self):
        try:
            filepath = os.path.join(MOCKS_ROOT, "post_1.md")
            mmd = MetaPost.from_file(filepath)
            mmd.to_json(meta_configs=[], strict_mode=True)
        except Exception:
            self.fail()

    def test_raise_from_file(self):
        with self.assertRaises(MetaPostError):
            null_path = Path.cwd().joinpath("NoSuchFile.md")
            MetaPost.from_file(null_path)
        with self.assertRaises(MetaPostError):
            null_path = Path.cwd().joinpath("requirements.txt")
            MetaPost.from_file(null_path)
        with self.assertRaises(MetaPostError):
            null_path = Path.cwd().joinpath("mocks/bad_format/post_99.md")
            MetaPost.from_file(null_path)

    def test_raise_from_text(self):
        with self.assertRaises(MetaPostError):
            bad_text = "Some Invalid Text"
            MetaPost.from_text(bad_text)
