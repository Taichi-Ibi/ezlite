import json
import os
import pathlib
import platform
import pyperclip
import re

INSTALL_CMD = "pip install git+https://github.com/Taichi-Ibi/ezlite --upgrade"


TEMPLATE = """
import glob
import os
from datetime import datetime
from dateutil import relativedelta
from pprint import pprint

import numpy as np
import pandas as pd

import japanize_matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
"""


def print_2dlist(big_li):
    for lines in big_li:
        for line in lines:
            print(line)
    return None


def check_itr(itr, file_count):
    for tpl in enumerate(itr):
        if tpl[0] == file_count:
            print(f"検索対象ファイル数が{file_count}を超えています。\n")
            break
    return None


def escape_brackets(path):
    # globは[]を正規表現パターンとして認識してしまうためエスケープする
    replace_list = [["[", "[[[", "[[]"], ["]", "]]]", "[]]"]]
    path = path.replace(replace_list[0][0], replace_list[0][1])
    path = path.replace(replace_list[1][0], replace_list[1][1])
    path = path.replace(replace_list[0][1], replace_list[0][2])
    path = path.replace(replace_list[1][1], replace_list[1][2])
    return path


def ref2abs(path):
    # 相対パスを絶対パスに変換する
    path = pathlib.Path(path)
    abs_path = str(path.resolve())
    return abs_path


def print_copy(code, *, pp=True):
    code = code.strip()
    print(code)
    if pp is True:
        try:
            pyperclip.copy(code)
        except:
            pass
    return None


def fix_sep(path):
    # /と\の数を数える
    slash_cnt = path.count("/")
    bslash_cnt = path.count("\\")

    # 多い方を区切り文字として採用する
    if slash_cnt > bslash_cnt:
        sep = "/"
    elif bslash_cnt > slash_cnt:
        sep = "\\"
    return sep


def get_upper_dir(environ):
    if environ is None:
        # 引数なしの場合
        if platform.system() == "Windows":
            # Windowsの場合
            environ = "HOMEPATH"
        else:
            # MacやLinuxの場合
            environ = "HOME"
    else:
        # 引数ありの場合はそのまま使う
        pass
    upper_dir = os.getenv(environ)
    return upper_dir


def get_lines(path):
    if path.endswith("ipynb"):
        lines = parse_ipynb(path)
    else:
        lines = parse_text(path)
    return lines


def parse_ipynb(path):
    with open(path, encoding="utf-8") as f:
        try:
            jsn = json.load(f)
            # セルの情報をリストに格納
            cells = jsn["cells"]
            # セルからコード部分のみ取得
            cell_codes = [c["source"] for c in cells]
            # 1行ごとにリストに追加
            lines = []
            for codes in cell_codes:
                for c in codes:
                    lines.append(c)
            # 末尾の改行文字を削除
            lines = [l[:-1] if l.endswith("\n") else l for l in lines]
        except:
            return None
    return lines


def parse_text(path):
    with open(path, "r", encoding="utf-8") as f:
        try:
            lines = re.split("[\n|\r|\r\n]", f.read())
        except:
            return []
    return lines


def get_matched_idxs(lines, word):
    """サーチする文字列が含まれるリストの番号を返す"""
    idxs_matched = []
    for idx, line in enumerate(lines):
        if word in line:
            idxs_matched.append(idx)
        else:
            pass
    return idxs_matched


def collect_neighbor(num_list, n_neighbors):
    """リストの各数値の前後nの範囲の数値を追加して重複を除外する
    >>> collect_neighbor([2, 10], 1, 2)
    [1, 2, 3, 4, 9, 10, 11, 12]
    """
    collected_list = []
    for num in num_list:
        for diff in range(-n_neighbors, n_neighbors + 1):
            collected_list.append(num + diff)
    collected_list = sorted(list(set(collected_list)))
    return collected_list
