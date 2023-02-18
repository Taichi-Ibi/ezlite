import glob
import os
from functools import partial
from itertools import tee

from .utils import *

# 関数一覧
# upgrade, template, p, lsplit, todt, psplit, sniff

# TODO
# sniffのリファクタリング
# typehint
# docstring

upgrade = partial(print_copy, code=INSTALL_CMD)
template = partial(print_copy, code=TEMPLATE)


def p():
    raise Exception("pause")


def lsplit(text, *, multiline=False, pp=True):
    # 改行文字で分割
    li = text.strip().split("\n")
    # 0文字のものは除外
    li = [l for l in li if len(l) != 0]
    # リストを文字列に変換
    code = repr(li)
    # コードを整形
    code = shape_code(code, multiline)
    print_copy(code, pp=pp)
    return None


def todt(
    df_name, /, col, *, fmt="ymd", sep="-", new_col=None, error_handling=True, pp=True
):
    # 変換対象のカラム
    old_srs = f"{df_name}['{col}']"
    if new_col is None:
        new_srs = old_srs
    else:
        new_srs = f"{df_name}['{new_col}']"
    # 日付形式
    format = fmt.replace("y", "Y")
    format = sep.join(["%" + s for s in list(format)])
    # コード作成
    code = f"{new_srs} = pd.to_datetime({old_srs}, format='{format}'"
    # エラー対応
    if error_handling:
        code += ", errors='coerce')"
    else:
        code += ")"
    print_copy(code, pp=pp)
    return None


def psplit(path, *, multiline=False, pp=True):

    # 絶対パスに変更
    path = ref2abs(path)

    # 同じ文字を含む環境変数を抽出
    envs = {k: v for k, v in dict(os.environ).items() if v in path}
    sep_s = fix_sep(path)
    if len(envs):
        # パスの文字数が最も多い環境変数を取得
        envs_sorted = dict(sorted(envs.items(), key=lambda x: -len(x[1])))
        env = next(iter(envs_sorted))

        # 整形のための文字を定義
        left_sep, right_sep = "", ""
        if multiline is True:
            left_sep = "\n    "
        else:
            right_sep = " "

        # 環境変数
        path_front = f"{left_sep}os.getenv('{env}')"

        # 環境変数以降のパスの整形
        join_s = f",{right_sep}"
        path_back = path.replace(os.getenv(env), "").strip(sep_s).split(sep_s)
        path_back = [f"{left_sep}'{p}'" for p in path_back]
        path_back = (join_s).join(path_back)

        # 環境変数部分とそれ以降を結合
        code = (join_s).join([path_front, path_back])
        code = f"os.path.join({code}{left_sep})"

        print_copy(code, pp=pp)
        return None
    else:
        return None


def sniff(
    word,
    /,
    pattern,
    *,
    environ=None,
    limit=20,
    n_neighbors=2,
    count=True,
    decoration=False,
    sep=True,
    show_content=True,
    show_filename=True,
):
    """処理の流れ
    検索パターン作成
    検索ファイル取得
    ファイル検索・インデックス取得
    出力
    """
    # 環境変数で親ディレクトリを取得
    upper_dir = get_upper_dir(environ)
    # 絶対パスの場合はuppper_dirが重複するので空白に置き換え
    pattern = pattern.replace(upper_dir + "/", "")
    # 親ディレクトリとパターンを結合
    _pattern = os.path.join(upper_dir, pattern)
    # パスのブラケットをglob用にescapeする
    _pattern = escape_brackets(_pattern)
    # サーチするパスのリストをイテレータで取得
    paths = glob.iglob(_pattern, recursive=True)
    # イテレータをコピー
    paths, _paths = tee(paths)
    # 検索対象が一定値以上の場合に警告を表示
    check_itr(_paths, file_count=1000)

    # 検索結果を辞書に追加
    result_li = []
    for path in paths:
        # 行ごとにリスト化
        lines = get_lines(path)
        # マッチしたindexを取得
        indexs = get_matched_idxs(lines, word=word)

        if indexs == []:
            # マッチした行がない場合はpass
            pass
        else:
            # マッチした行数を取得
            count = len(indexs)
            # n_neighborsの数だけ前後の行を取得する
            _indexs = collect_neighbor(indexs, n_neighbors=n_neighbors)
            # マッチした行の最大桁数を取得
            max_digits = len(str(max(_indexs)))
            # ファイルの行数からはみ出たものは除外
            _indexs = [i for i in _indexs if i in range(0, len(lines))]

            # dictに格納
            result_di = {
                "path": path,
                "lines": lines,
                "indexs": indexs,
                "count": count,
                "index_added": _indexs,
                "max_digits": max_digits,
            }
            # 検索結果をリストに追加
            result_li.append(result_di)

            # ヒット数にlimitを設定
            if (limit is not None) & (len(result_li) == limit):
                if limit == 20:
                    print(f"ヒット数が{limit}を超えたので検索を中断しました。")
                break

    # 出力を作成
    big_output = []
    for r in result_li:
        small_output = []
        # -nの処理 ファイル名を表示
        if show_filename is True:
            path = "- " + r.get("path")
            # -cの処理 マッチ数を表示
            if count:
                path += " " + str(r.get("count"))
            small_output.append(path)
        # -rの処理 検索結果を表示
        if show_content is True:
            idxs = r.get("index_added")
            for itr, idx in enumerate(idxs):
                line = r.get("lines")[idx]
                # -iの処理 行番号を表示
                if decoration is True:
                    line = "  ".join([str(idx).rjust(r.get("max_digits")), line])
                # -mの処理 マッチした行をハイライト
                if not decoration is True:
                    pass
                elif (decoration is True) & (idx in r.get("indexs")):
                    line = "* " + line
                else:
                    line = "  " + line
                # -sの処理 1/2 マッチごとに改行
                if (sep) & (itr != 0) & ((idxs[itr] - idxs[itr - 1]) != 1):
                    small_output.append("\n")
                # 行を出力リストに追加
                small_output.append(line)
            # -sの処理 2/2 ファイルごとに改行
            if sep:
                small_output.append("\n")
        # 検索結果をリストに追加
        big_output.append(small_output)

    # 出力
    print_2dlist(big_li=big_output)
