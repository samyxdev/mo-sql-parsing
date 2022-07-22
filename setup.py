# encoding: utf-8
# THIS FILE IS AUTOGENERATED!
from __future__ import unicode_literals
from setuptools import setup
setup(
    author='Kyle Lahnakoski',
    author_email='kyle@lahnakoski.com',
    classifiers=["Development Status :: 3 - Alpha","Topic :: Software Development :: Libraries","Topic :: Software Development :: Libraries :: Python Modules","Programming Language :: SQL","Programming Language :: Python :: 3.7","Programming Language :: Python :: 3.8","Programming Language :: Python :: 3.9","License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)"],
    description='More SQL Parsing! Parse SQL into JSON parse tree',
    extras_require={"dev":[],"tests":["mo-testing","mo-threads","mo-files"]},
    include_package_data=True,
    install_requires=["mo-dots==9.189.22201","mo-future==6.2.21303","mo-imports==7.187.22201","mo-parsing==8.189.22201"],
    license='MPL 2.0',
    long_description='# More SQL Parsing!\n\n[![PyPI Latest Release](https://img.shields.io/pypi/v/mo-sql-parsing.svg)](https://pypi.org/project/mo-sql-parsing/)\n[![Build Status](https://app.travis-ci.com/klahnakoski/mo-sql-parsing.svg?branch=master)](https://travis-ci.com/github/klahnakoski/mo-sql-parsing)\n\n\nParse SQL into JSON so we can translate it for other datastores!\n\n[See changes](https://github.com/klahnakoski/mo-sql-parsing#version-changes)\n\n\n## Problem Statement\n\nSQL is a familiar language used to access databases. Although, each database vendor has its quirky implementation, there is enough standardization that the average developer does not need to know of those quirks. This familiar core SQL (lowest common denominator, if you will) is useful enough to explore data in primitive ways. It is hoped that, once programmers have reviewed a datastore with basic SQL queries, and they see the value of that data, and they will be motivated to use the datastore\'s native query format.\n\n## Objectives\n\nThe objective is to convert SQL queries to JSON-izable parse trees. This originally targeted MySQL, but has grown to include other database engines. *Please [paste some SQL into a new issue](https://github.com/klahnakoski/mo-sql-parsing/issues) if it does not work for you*\n\n\n## Project Status\n\nJune 2022 - There has been some work on improving the error reporting alongside resolving any bug reports.  There are [over 900 tests](https://app.travis-ci.com/github/klahnakoski/mo-sql-parsing), that covers most SQL for most databases, with limited DML support, including:\n\n  * inner queries, \n  * with clauses, \n  * window functions\n  * create/drop tables and views\n  * insert/update/delete statements\n  * lambda (`->`) functions\n\n## Install\n\n    pip install mo-sql-parsing\n\n## Parsing SQL\n\n    >>> from mo_sql_parsing import parse\n    >>> parse("select count(1) from jobs")\n    {\'select\': {\'value\': {\'count\': 1}}, \'from\': \'jobs\'}\n    \nEach SQL query is parsed to an object: Each clause is assigned to an object property of the same name. \n\n    >>> parse("select a as hello, b as world from jobs")\n    {\'select\': [{\'value\': \'a\', \'name\': \'hello\'}, {\'value\': \'b\', \'name\': \'world\'}], \'from\': \'jobs\'}\n\nThe `SELECT` clause is an array of objects containing `name` and `value` properties. \n\n\n### SQL Flavours \n\nThere are a few parsing modes you may be interested in:\n\n\n#### SQLServer Identifiers (`[]`)\n\nSQLServer uses square brackets to delimit identifiers. For example\n\n    SELECT [Timestamp] FROM [table]\n    \nwhich conflicts with BigQuery array constructor (eg `[1, 2, 3, 4]`). You may use the SqlServer flavour with \n    \n    from mo_sql_parsing import parse_sqlserver as parse\n\n\n#### NULL is None\n\nThe default output for this parser is to emit a null function `{"null":{}}` wherever `NULL` is encountered in the SQL.  If you would like something different, you can replace nulls with `None` (or anything else for that matter):\n\n    result = parse(sql, null=None)\n    \nthis has been implemented with a post-parse rewriting of the parse tree.\n\n\n#### Normalized function call form\n\nThe default behaviour of the parser is to output function calls in `simple_op` format: The operator being a key in the object; `{op: params}`.  This form can be difficult to work with because the object must be scanned for known operators, or possible optional arguments, or at least distinguished from a query object.\n\nYou can have the parser emit function calls in `normal_op` format\n\n    >>> from mo_sql_parsing import parse, normal_op\n    >>> parse("select trim(\' \' from b+c)", calls=normal_op)\n    \nwhich produces calls in a normalized format\n\n    {"op": op, "args": args, "kwargs": kwargs}\n\nhere is the pretty-printed JSON from the example above:\n\n```\n{\'select\': {\'value\': {\n    \'op\': \'trim\', \n    \'args\': [{\'op\': \'add\', \'args\': [\'b\', \'c\']}], \n    \'kwargs\': {\'characters\': {\'literal\': \' \'}}\n}}}\n```\n\n#### MySQL literal strings\n\nMySQL uses both double quotes and single quotes to declare literal strings.  This is not ansi behaviour, but it is more forgiving for programmers coming from other languages. A specific parse function is provided: \n\n    result = parse_mysql(sql)\n\n\n## Generating SQL\n\nYou may also generate SQL from the a given JSON document. This is done by the formatter, which is in Alpha state (Oct2021).\n\n    >>> from mo_sql_parsing import format\n    >>> format({"from":"test", "select":["a.b", "c"]})\n    \'SELECT a.b, c FROM test\'\n\n## Contributing\n\nIn the event that the parser is not working for you, you can help make this better but simply pasting your sql (or JSON) into a new issue. Extra points if you describe the problem. Even more points if you submit a PR with a test.  If you also submit a fix, then you also have my gratitude. \n\n\n### Run Tests\n\nSee [the tests directory](https://github.com/klahnakoski/mo-sql-parsing/tree/dev/tests) for instructions running tests, or writing new ones.\n\n## More about implementation\n\nSQL queries are translated to JSON objects: Each clause is assigned to an object property of the same name.\n\n    \n    # SELECT * FROM dual WHERE a>b ORDER BY a+b\n    {\n        "select": "*", \n        "from": "dual", \n        "where": {"gt": ["a", "b"]}, \n        "orderby": {"value": {"add": ["a", "b"]}}\n    }\n        \nExpressions are also objects, but with only one property: The name of the operation, and the value holding (an array of) parameters for that operation. \n\n    {op: parameters}\n\nand you can see this pattern in the previous example:\n\n    {"gt": ["a","b"]}\n    \n## Array Programming\n\nThe `mo-sql-parsing.scrub()` method is used liberally throughout the code, and it "simplifies" the JSON.  You may find this form a bit tedious to work with because the JSON property values can be values, lists of values, or missing.  Please consider converting everything to arrays: \n\n\n```\ndef listwrap(value):\n    if value is None:\n        return []\n    elif isinstance(value, list)\n        return value\n    else:\n        return [value]\n```  \n\nthen you may avoid all the is-it-a-list checks :\n\n```\nfor select in listwrap(parsed_result.get(\'select\')):\n    do_something(select)\n```\n\n## Version Changes\n\n\n\n### Version 8\n \n*November 2021*\n\n* Prefer BigQuery `[]` (create array) over SQLServer `[]` (identity) \n* Added basic DML (`INSERT`/`UPDATE`/`DELETE`)              \n* flatter `CREATE TABLE` structures. The `option` list in column definition has been flattened:<br>\n    **Old column format**\n    \n        {"create table": {\n            "columns": {\n                "name": "name",\n                "type": {"decimal": [2, 3]},\n                "option": [\n                    "not null",\n                    "check": {"lt": [{"length": "name"}, 10]}\n                ]\n            }\n        }}\n        \n    **New column format**\n                \n        {"create table": {\n            "columns": {\n                "name": "name", \n                "type": {"decimal": [2, 3]}\n                "nullable": False,\n                "check": {"lt": [{"length": "name"}, 10]} \n            }\n        }}\n\n### Version 7 \n\n*October 2021*\n\n* changed error reporting; still terrible\n* upgraded mo-parsing library which forced version change\n\n### Version 6 \n\n*October 2021*\n\n* fixed `SELECT DISTINCT` parsing\n* added `DISTINCT ON` parsing\n\n### Version 5 \n\n*August 2021*\n\n* remove inline module `mo-parsing`\n* support `CREATE TABLE`, add SQL "flavours" emit `{null:{}}` for None\n\n### Version 4\n\n*November 2021*\n\n* changed parse result of `SELECT DISTINCT`\n* simpler `ORDER BY` clause in window functions\n\n\n\n\n\n',
    long_description_content_type='text/markdown',
    name='mo-sql-parsing',
    packages=["mo_sql_parsing"],
    url='https://github.com/klahnakoski/mo-sql-parsing',
    version='8.190.22203',
    zip_safe=True
)