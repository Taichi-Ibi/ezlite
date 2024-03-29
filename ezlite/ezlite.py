import glob
import os
from functools import partial
from itertools import tee
import subprocess
import time
from typing import List

import isort
from pandas import DataFrame
import pyperclip

from .utils import *

upgrade = partial(pNc, code=INSTALL_CMD)
template = partial(pNc, code=TEMPLATE)

def history(_locals, word=None, n=20, desc=True) -> str:
    """Jupyterで過去に実行したコードを出力する(カーネル再起動によりログは失われる)"""
    _locals.popitem()
    i_codes = [v for k, v in _locals.items() if re.findall(r'_i[0-9]+', k)]
    if desc:
        i_codes.reverse()
    if word is not None:
        i_codes = [c for c in i_codes[:n] if word in c]
    if not i_codes:
        return
    o_codes = list()
    for code in i_codes:
        if bool(o_codes) & (code in o_codes):
            pass
        else:
            o_codes.append(code)
    o_codes = [">>>\n" + c for c in o_codes]
    code = ("\n\n").join(o_codes)
    print(code)

def df_viewer(
    df: DataFrame,
    *,
    head: int = 100,
    tail: int = None,
    columns: List[str] = None,
):
    # dfをhtmlに出力
    if columns is not None:
        df = df[columns].copy()
    df = df.head(head).copy()
    if tail is not None:
        df = df.tail(tail).copy()
    html_path = "df_viewer.html"
    df.to_html(html_path)

    # htmlをopen
    if platform.system() == "Windows":
        os.startfile(html_path)
    else:
        subprocess.call(["open", html_path])
    time.sleep(5)
    os.remove(html_path)
    return None


def df_write_option(dirname=None, *, prefix="", suffix="", skip=False):
    df_reset_write_option()

    def modify_path_or_buf(func):
        def wrapper(self, path_or_buf, *args, **kwargs):
            if skip is True:
                print("ファイル出力をスキップしました。")
            else:
                # 書き換えたいパスやバッファーを指定
                modified_path_or_buf = modify_path(
                    path_or_buf, dirname=dirname, prefix=prefix, suffix=suffix
                )
                return func(self, modified_path_or_buf, *args, **kwargs)

        return wrapper

    DataFrame.to_csv = modify_path_or_buf(DataFrame.to_csv)
    DataFrame.to_excel = modify_path_or_buf(DataFrame.to_excel)
    return None


def msort(code=None, pp=True) -> None:
    """import文をsortする関数"""
    if code is None:
        code = pyperclip.paste()
    sorted_code = isort.code(code=code)
    pNc(code=sorted_code, pp=pp)
    return None


def lsplit(text: str, *, multiline=True, pp=True) -> None:
    """三連引用符を使った複数行にわたる文字列をリストに変換する

    Args:
        text (str: 文字列
        multiline (bool, optional): リストをカンマ区切りで改行するかどうか Defaults to True.
        pp (bool, optional): クリップボードにコピーするかどうか Defaults to True.

    Returns:
        _type_: None
    """
    # 改行文字で分割
    text_li = text.strip().split("\n")
    # 0文字のものは除外し、クォーテーションを付ける
    text_li = [repr(t) for t in text_li if len(t) != 0]
    # 結合して文字列にする
    obj = (",").join(text_li)
    # codeに変換
    code = shape_code(obj, left="[", right="]", multiline=multiline)
    pNc(code, pp=pp)
    return None


def todt(
    df_name: str,
    /,
    col: str,
    *,
    fmt="ymd",
    sep="-",
    new_col=None,
    error_handling=True,
    pp=True,
) -> None:
    """DataFrameとカラム名を受け取ってdatetime型に変換するコードを生成する

    Args:
        df_name (str): DataFrameの名前 example:'df'
        col (str): カラム名 example: ''年月日'
        fmt (str, optional): ymdやymなど日付形式を指定 Defaults to "ymd".
        sep (str, optional): 変換前のカラム名の区切り文字。ない場合は""とする Defaults to "-".
        new_col (str, optional): 新しくカラムを作るときは入力する Defaults to None.
        error_handling (bool, optional): errors='coerce'のオプションをつけるかどうか Defaults to True.
        pp (bool, optional): クリップボードにコピーするかどうか Defaults to True.

    Returns:
        _type_: None
    """
    # 変換対象のカラム
    old_srs = f"{df_name}['{col}']"
    if new_col is None:
        new_srs = old_srs
    else:
        new_srs = f"{df_name}['{new_col}']"
    # 日付形式
    format = fmt.replace("y", "Y")
    format = sep.join(["%" + s for s in list(format)])
    # エラー対応
    if error_handling is True:
        tail = ", errors='coerce'"
    else:
        tail = ""
    # コード作成
    code = f"{new_srs} = pd.to_datetime({old_srs}, format='{format}'{tail})"
    pNc(code, pp=pp)
    return None


def psplit(path="", *, multiline=True, pp=True) -> None:
    """絶対パスや相対パスを環境変数を使って書き換える

    Args:
        path (str): 変換対象となるパス
        multiline (bool, optional): パスをカンマ区切りで改行するかどうか Defaults to True.
        pp (bool, optional): クリップボードにコピーするかどうか Defaults to True.

    Returns:
        _type_: None
    """
    if path == "":
        # 引数がない場合はクリップボードからコピー
        path = pyperclip.paste()
    # 引用符を削除
    path = path.strip("'").strip('"')
    # 絶対パスに変換
    path = ref2abs(path)
    # 同じ文字を含む環境変数を抽出
    envs = {k: v for k, v in dict(os.environ).items() if v in path}
    if len(envs):
        # 環境変数をパスの文字数で降順にソート
        envs_sorted = dict(sorted(envs.items(), key=lambda x: -len(x[1])))
        # 1番目のキーを取得
        env = next(iter(envs_sorted))

        # 環境変数で置き換える部分は一旦除外
        obj = path.replace(os.getenv(env), "")
        # 区切り文字を取得(Windowsはバックスラッシュ)
        sep_s = fix_sep(path)

        # 環境変数以降のパスをリスト化
        obj_li = obj.strip(sep_s).split(sep_s)
        obj_li = [repr(p) for p in obj_li]
        # 環境変数部分を追加
        obj_li = [f'os.getenv("{env}")'] + obj_li
        # 結合して文字列にする
        obj = (",").join(obj_li)
        # コードに変換
        code = shape_code(obj, left="os.path.join(", right=")", multiline=multiline)
        pNc(code, pp=pp)
    else:
        pass
    return None


def j(code: str, *, min_moji=2, ignore_num=False, ignore_kakko=True, pp=True) -> None:
    """文字列中の日本語を判別してシングルクォーテーションを付ける

    Args:
        code (str): 変換前のコード
        min_moji (int, optional): シングルクォーテーションを付ける対象となる最小文字数 Defaults to 2.
        ignore_num (bool, optional): 数字を無視するかどうか Defaults to False.
        ignore_kakko (bool, optional): 丸括弧を無視するかどうか Defaults to True.
        pp (bool, optional): クリップボードにコピーするかどうか Defaults to True.

    Returns:
        _type_: None
    """
    # 日本語とアンダーバーがマッチする位置を取得
    matched_idxs = search_jp(code, ignore_num=ignore_num, ignore_kakko=ignore_kakko)
    # idxが連続していたら同じリストに追加
    group_idxs = grouping_next(matched_idxs)
    # idxを単語にする
    word_li = []
    for idxs in group_idxs:
        tmp_li = []
        if len(idxs) < min_moji:
            # デフォルトは1文字だけの場合スキップ
            pass
        else:
            for idx in idxs:
                # 1文字ずつ追加
                tmp_li.append(code[idx])
            # 文字を繋げて単語にする
            word = ("").join(tmp_li)
            # 単語をリストに追加
            word_li.append(word)
    # 重複マッチ回避のため、文字数で高順に並べ替え
    word_li = sorted(word_li, key=lambda x: -len(x))
    # 辞書を使って文字列を一度に置換
    replace_di = {}
    for word in word_li:
        replace_di[word] = f"'{word}'"
    code = multi_replace(code, replace_di)
    pNc(code, pp=pp)
    return None


def sniff(
    word: str,
    /,
    pattern: str,
    *,
    environ=None,
    limit=(DEFAULT_LIMIT := 20),
    n_neighbors=2,
    count=True,
    decoration=False,
    show_content=True,
    show_filename=True,
) -> None:
    """正規表現で指定したファイルから指定した文字列を検索し表示する

    Args:
        word (str): 検索する文字列
        pattern (str): 検索するファイルパスの正規表現パターン. **も使用可能
        environ (_type_, optional): ホームパスではなく環境変数でパスを指定するときに使用 Defaults to None.
        limit (tuple, optional): 検索結果を表示するファイル数 Defaults to (DEFAULT_LIMIT := 20).
        n_neighbors (int, optional): 検索がマッチした行の前後n行を表示する Defaults to 2.
        count (bool, optional): ファイルの末尾にマッチした行数を表示する Defaults to True.
        decoration (bool, optional): 検索結果の左端に、行番号とマッチした行の目印を表示する Defaults to False.
        show_content (bool, optional): 検索結果を表示する. Falseの場合、ファイル名のみ表示 Defaults to True.
        show_filename (bool, optional): 検索結果にファイル名を表示する Defaults to True.

    Returns:
        _type_: _description_
    """
    # 環境変数で親ディレクトリを取得
    upper_dir = get_upper_dir(environ)
    # 引数が絶対パスの場合はuppper_dirが重複するので空白に置き換え
    pattern = pattern.replace(upper_dir + "/", "")
    # 親ディレクトリとパターンを結合
    pattern = os.path.join(upper_dir, pattern)
    # パスの[]をglob用にescapeする
    pattern = multi_replace(pattern, {"[": "[[]", "]": "[]]"})
    # サーチするパスのリストをイテレータで取得
    paths = glob.iglob(pattern, recursive=True)

    # イテレータをコピー
    paths, _paths = tee(paths)
    # 検索対象ファイル数を表示
    COUNT_LIMIT = 1000
    file_count = count_itr(_paths, COUNT_LIMIT)
    if file_count == COUNT_LIMIT:
        print(f"検索対象ファイル数が{COUNT_LIMIT}を超えています。")
    else:
        print(f"検索対象ファイル数は{file_count+1}です。")

    # 検索結果を辞書に追加
    result_li = []
    for path in paths:
        # 検索結果を取得
        result_di = get_search_result(path, word, n_neighbors)
        # 検索結果をリストに追加
        if result_di != {}:
            result_li.append(result_di)
        # ヒット数にlimitを設定
        if (limit is not None) & (len(result_li) == limit):
            if limit == DEFAULT_LIMIT:
                print(f"ヒット数が{limit}を超えたので検索を中断しました。")
            break

    # 出力内容を作成
    output_li = []
    for result_di in result_li:
        output = []
        # ファイル名とヒット数を取得
        output += [get_filename(result_di, show_filename, count)]
        # 検索結果を追加
        output += get_hits(result_di, show_content, decoration)
        # 検索結果をリストに追加
        output_li.append(output)

    # 出力
    print_2dlist(outer_li=output_li)
    return None
