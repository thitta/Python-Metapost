import json
from metapost import MetaPostReader, MTPReaderError, MetaPost, MetaPostError
from pathlib import Path
from unittest import TestCase


class TestMetapostReader(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_raise_check_markdown_file(self):
        with self.assertRaises(MTPReaderError):
            null_path = Path.cwd().joinpath("invalidFile.txt")
            MetaPostReader._check_markdown_file(null_path)
        with self.assertRaises(MTPReaderError):
            null_path = Path.cwd().joinpath("null_path.py")
            MetaPostReader._check_markdown_file(null_path)

    def test_ok_list_markdown_files(self):
        dirpath = Path.cwd().joinpath("mocks")
        # ok walk = False
        exp = [str(Path.cwd().joinpath("mocks/post_1.md")),
               str(Path.cwd().joinpath("mocks/post_2.md"))]
        act = MetaPostReader._list_markdown_files(dirpath)
        self.assertEqual(exp, act)
        # walk = True
        dirpath = Path.cwd().joinpath("mocks")
        exp = [str(Path.cwd().joinpath("mocks/post_1.md")),
               str(Path.cwd().joinpath("mocks/post_2.md")),
               str(Path.cwd().joinpath("mocks/bad_format/post_99.md"))]
        act = MetaPostReader._list_markdown_files(dirpath, walk=True)
        self.assertEqual(exp, act)

    def test_raise_list_markdown_files(self):
        with self.assertRaises(MetaPostError):
            null_dirpath = Path.cwd().joinpath("null_dirpath")
            MetaPostReader._list_markdown_files(null_dirpath)

    def test_ok_reset_mtp_list(self):
        mtpr = MetaPostReader()
        # reserve = 0
        mtpr.read_text("```key:val``` some content")
        mtpr.read_text("```key:val``` some content")
        mtpr._reset_mtp_list(reserve_latest=0)
        exp = 0
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)
        # reserve = 2
        mtpr.read_text("```key:val``` some content")
        mtpr.read_text("```key:val``` some content")
        mtpr.read_text("```key:val``` some content")
        mtpr._reset_mtp_list(reserve_latest=2)
        exp = 2
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)

    def test_ok_setters(self):
        mtpr = MetaPostReader()
        mtpr.set_markdown_extensions([])
        exp = 0
        act = len(mtpr.md_exts)
        self.assertEqual(exp, act)
        mtpr.set_strict_mode(False)
        exp = False
        act = mtpr.strict_mode
        self.assertEqual(exp, act)

    def test_ok_add_meta_cfg(self):
        mtpr = MetaPostReader()
        mtpr.add_meta_cfg("title", "str", True, "Undefined Post")
        exp = [{"key": "title", "datatype": "str", "required": True, "df_val": "Undefined Post"}]
        act = mtpr.meta_configs
        self.assertEqual(exp, act)

    def test_raise_to_meta(self):
        path = Path.cwd().joinpath("mocks/post_1.md")
        mtpr = MetaPostReader()
        # Key not exist in source file
        mtpr.add_meta_cfg("missing_key", "str", True)
        mtpr.read_file(path)
        with self.assertRaises(MTPReaderError):
            mtpr.to_meta()

    def test_ok_export_to_meta_dict_json(self):
        path = Path.cwd().joinpath("mocks/post_1.md")
        mtpr = MetaPostReader()
        mtpr.add_meta_cfg("title", "str", True)
        mtpr.read_file(path)
        # to meta
        exp1 = [{"title": "A mock post", "_filepath_": str(path), "_filename_": "post_1",
                 "_last_update_": mtpr.mtp_list[0]._get_last_update_dt(path)}]
        act1 = mtpr.to_meta()
        self.assertEqual(exp1, act1)
        # to html
        exp2 = ["<p>some content</p>"]
        act2 = mtpr.to_html()
        self.assertEqual(exp2, act2)
        # to dict
        exp3 = [{"meta": exp1[0], "html": exp2[0]}]
        act3 = mtpr.to_dict()
        self.assertEqual(exp3, act3)
        # to json
        exp4 = json.loads(mtpr.to_json())
        act4 = mtpr.to_dict()
        self.assertEqual(exp4, act4)

    def test_ok_reset_target_mtp_list(self):
        mtpr = MetaPostReader()
        mtpr.read_text("```key:val``` some content", reset=False)
        mtpr.read_text("```key:val``` some content", reset=False)
        exp = 2
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)
        mtpr.read_text("```key:val``` some content", reset=True)
        exp = 1
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)

    def test_ok_read_flie_and_text(self):
        path = Path.cwd().joinpath("mocks/post_1.md")
        mtpr = MetaPostReader()
        # read_file
        mtpr.read_file(path)
        mtpr.read_file(path)
        mtpr.read_file(path)
        exp = 3
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)
        mtpr.read_file(path, reset=True)
        exp = 1
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)
        # read_text
        mtpr._reset_mtp_list()
        mtpr.read_text("```key:val``` some content")
        mtpr.read_text("```key:val``` some content")
        mtpr.read_text("```key:val``` some content", reset=True)
        exp = 1
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)

    def test_ok_read_dir(self):
        path = Path.cwd().joinpath("mocks")
        mtpr = MetaPostReader()
        mtpr.read_text("```key:val``` some content")
        mtpr.read_text("```key:val``` some content")
        # read dir
        mtpr.read_dir(path)
        exp = 4
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)
        # read dir with reset = True
        mtpr.read_dir(path, reset=True)
        exp = 2
        act = len(mtpr.mtp_list)
        self.assertEqual(exp, act)

    def test_raise_read_dir(self):
        mtpr = MetaPostReader()
        null_dirpath = Path.cwd().joinpath("null_dirpath")
        with self.assertRaises(MetaPostError):
            mtpr.read_dir(null_dirpath)

    def test_raise_check_markdown_file(self):
        # null file path
        mtpr = MetaPostReader()
        null_path = Path.cwd().joinpath("null_dirpath")
        with self.assertRaises(MTPReaderError):
            mtpr._check_markdown_file(null_path)
        # not .md file
        mtpr = MetaPostReader()
        null_path = Path.cwd().joinpath("__init__.py")
        with self.assertRaises(MTPReaderError):
            mtpr._check_markdown_file(null_path)
