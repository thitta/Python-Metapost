This Python package helps developers parse `Metapost` file.

Metapost allows meta data to be appended to markdown files, such as `title` for a post; or `on_index` which denotes whether the post should be placed on the index page -- in a most human `readable` and `manageable` way.

# Use Case

Metapost is meant to help developers efficiently manipulate mock data when building CMS service.
You can put a bunch of markdown files (with meta info) in a folder,
then use `MetaPostReader` to parse them into a list of dictionaries, 
which can easily be imported into database via ORM modules.

# How Metapost Works

- `Metapost` file is a standard `Markdown` file with `.md` extension. 
- Except one thing - `Metapost` is expected to star with a `code block`, which will be parsed as metas of the file.
- The content of the `code block` should be neither json nor YAML, it's a special but easy to learn format, which is meant to optimize the readability and manageability.
- This package provides necessary tools for manipulating Metapost files, such as reading and exporting.
- The markdown parser in this project is based on John Gruber's [Markdown](https://github.com/Python-Markdown/markdown)

Metapost is extremely simple and powerful. The examples below will demonstrate how to implement it.

# Examples

## Quickstart

In this section, we are going to demonstrate how to parse a Metapost(markdown) file into useful formats that can interact with our application. Be aware that the meta content is neither json nor YAML, it's a key-value pair separated by a colon.

First things first, install the package via PyPI

```
pip install metapost
```

Assuming we have a MetaPost(.md file) article like this. The file starts with a code block containing metas, which is embraced by triple consecutive backtick(\`\`\`).

```
` ` `
title: Example post
ranking: 999
on_top: true
keywords: ["markdown", "meta", "microblog"]
work_hours: 35.6
` ` `

--- ↑↑↑    Meta Block    ↑↑↑ ---
--- ↓↓↓ Markdown Content ↓↓↓ ---

Be careful we use ` ` ` here just because we can't escape backtick in the code block of github. 

You should always use ``` in your markdown file.
```

Now, we are going to parse the file with `MetaPostReader` in our package:

``` python
# import package
from metapost import MetaPostReader

# set file path
path = ".\myMetaPostFilepath.md"

# instantiate MetaPostReader
mtpr = MetaPostReader()
mtpr.set_strict_mode(False)

# read and export to python dict
result = mtpr.read_file(path).to_dict()
print(result)
```

The out put will be:

```
[{
    "meta":{"title":"Example post",
            "rank":"999",
            "on_top":"true",
            "keywords":'["markdown", "meta", "microblog"]',
            "work_hours": "35.6"}
    "html":"<p>......</p>"
}]
```

Well, it's not that impressive, right? All values are parsed as string instead of boolean, integer or other useful datatype.

## Set Meta Configs

Set `meta_configs` on the `MetaPostReader` can help us parse value precisely. We can also set `required` and `df_val` on it to declare whether a meta is required or have default value.

The five lines of meta in the source markdown file are mapping to five acceptable datatype in the meta, they are string(`str`), boolean(`bool`), integer(`int`),  float(`float`) and json(`json`).

Let's set meta configs and parse it again

``` python
from metapost import MetaPostReader

path = "./ExampleMetaPost.md"
mtpr = MetaPostReaser()

# add_meta_config()
# key: str, datatype: str = "str", required: bool = True, df_val: Any = None
mtpr.add_meta_config("title",      "str",   True        )
mtpr.add_meta_config("ranking",    "int",   False, 0    )
mtpr.add_meta_config("on_top",     "bool",  False, False)
mtpr.add_meta_config("keywords",   "json",  False       )
mtpr.add_meta_config("work_hours", "float", True        )

result = mtpr.to_dict()
print(result)
```

Now, we can get the content of the file in the format of python `dict`:

```
[{
    "meta":{"title":"Example post",
            "rank":999,
            "on_top":true,
            "keywords":["markdown", "meta", "microblog"],
            "work_hours":35.6,
            ......}
    "html":"<p>......</p>"
}]
```

If the parameter `required` is `True` while your file does not contain that meta key, 
the reader will report error. 

We can compare these three lines of code which clearly demonstrate how `required` and `df_val` works

```python
from metapost import MetaPostReader
mtpr = MetaPostReader()

# meta required, default value not necessary
mtpr.add_meta_config("title",      "str",   True       )

# meta not required, it is defaulted to be 999 if not provided
mtpr.add_meta_config("ranking",    "int",   False, 999 )

# meta not required, no default value
mtpr.add_meta_config("keywords",   "json",  False      )
```

Another thing worth mention is that `MetaPostReader` adopt elastic approach to parse `bool` meta. That's to say, values like `False`, `false`, `No`, `n`, `0`, etc., will be parsed to `False` as long as the meta config expects a boolean. The rule is __case insensitive__ and is also applies to `True` parsing.

## Set Strict Mode

We can set the property `strict_mode` on `MetaPostReader`. The defaulted value is `True`, which means the reader won't parse metas that are not defined in configs. Set it to `False` if you wish to parse as many valid metas as possible.

```python
from metapost import MetaPostReader
mtpr = MetaPostReader()

# strict mode on 
MetaPostReader().set_strict_mode(True)

# strict mode off
MetaPostReader().set_strict_mode(False)
```

## Default Meta

Except for metas we have defined in config, you can find some default ones. They are `_content_markdown_`,`_filepath_`, `_filename_` and `_last_update_`. These are meant to provide more information about the source file.

## Read Multiple Files & Read from Directory

`MetaPostReader` can also read and stack multiple files, then export them all at once.
All the files loaded will be stored in `MetaPostReader.mtp_list`.

```python
from metapost import MetaPostReader

# read three files into MetaPostReader
mtpr = MetaPostReader()
mtpr.read_file("/mocks/file1.md")
mtpr.read_file("/mocks/file2.md")
mtpr.read_file("/mocks/file3.md")

# now, the length will be 3
print(len(mtpr.mtp_list))

# parse all the posts, this returns a list of dictionary
my_metas = mtpr.to_dict()

# set reset to True if you wish to reset list before read
mtpr.read_file("/mocks/file4.md", reset=True)

# now, the length will be 1
print(len(mtpr.mtp_list))
```

You can also read all files under a specific directory. 
`MetaPostReader.read_dir()` will automatically load all files with `.md` extensions.
If you wish to load all `.md` files in the directory tree, just set `walk` to `True`.

This feature is especially useful when importing mock data via migrations in web development.

```python
from metapost import MetaPostReader

# Read .md from directory
my_mock_dirpath = "./mocks"
mtpr = MetaPostReader()
mtpr.read_file(my_mock_dirpath, walk=True)

# get all parsed data
posts = mtpr.to_dict()
```

That's all! If you have any advice, feel free to contact me via email(thittalee@gmail.com) or github.
The following API document provides some short description of all the (expected) public methods. 
Happy coding! 

## API Document

### Init
- `MetaPostReader.__init__(self)`

Create a MetaPostReader

### Add Meta Configs
- `.add_meta_cfg(self, key: str, datatype: str = "str", required: bool = True, df_val: Any = None)`

Add meta config. `datatype` can be `str`, `bool`, `int`, `float` and `json`.

### Methods of Read
- `.read_dir(self, dirpath: str, reset: bool = False, walk: bool = False)`

Read all the `.md` files under `dirpath` into reader. Set `reset` to `True` if you wish to clean the former loading. Set `walk` to `True` if you wish to read all the `.md` files in the directory tree.

- `.read_file(self, filepath: str, reset: bool = False)`

Read one single file from `filepath`. Set `reset` to `True` if you wish to clean the former loading.

- `.read_text(self, source_text: str, reset: bool = False)`

Read from a string. Set `reset` to `True` if you wish to clean the former loading.

### Methods of Output

- `.to_dict(self) -> List[dict]`

Export a list of dict from data read . Use `dict["meta"]` and `dict["html"]` to fetch values.

- `.to_json(self) -> str`

Export a string of json from data read.

- `.to_meta(self) -> List[dict]`

Export a list of dict of meta from data read.s

- `.to_html(self) -> List[str]`

Export a list of string of html from data read.

### Methods of Setter

- `.set_strict_mode(self, strict_mode: bool)`

Set `.strict_mode` to `True` if you wish to parse metas defined in configs only.

- `.set_markdown_extensions(self, extensions: list)`

Customize your markdown extensions. Visit [Markdown](https://github.com/Python-Markdown/markdown) for more information.
