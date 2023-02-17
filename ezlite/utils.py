import json
import os
import pathlib
import platform
import pyperclip
import re


def escape_brackets(path):
    # globは[]を正規表現パターンとして認識してしまうためエスケープする
    replace_list = [["[", "[[[", "[[]"], ["]", "]]]", "[]]"]]
    path = path.replace(replace_list[0][0], replace_list[0][1])
    path = path.replace(replace_list[1][0], replace_list[1][1])
    path = path.replace(replace_list[0][1], replace_list[0][2])
    path = path.replace(replace_list[1][1], replace_list[1][2])
    return path


def ref2abs(path):
    path = pathlib.Path(path)
    abs_path = str(path.resolve())
    return abs_path


def print_copy(code, pp):
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


def lsplit(text):
    # 改行文字で分割
    li = text.split("\n")
    # 0文字のものは除外
    li = [l for l in li if len(l) != 0]
    pyperclip.copy(repr(li))
    return li


def parse_ipynb(path):
    with open(path, encoding="utf-8") as f:
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
    return lines


def parse_text(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = re.split("[\n|\r|\r\n]", f.read())
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
