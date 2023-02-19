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

upgrade = partial(pNc, code=INSTALL_CMD)
template = partial(pNc, code=TEMPLATE)


def p():
    raise Exception("pause")


def lsplit(text, *, multiline=False, pp=True):
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
    # エラー対応
    if error_handling is True:
        tail = ", errors='coerce'"
    else:
        tail = ""
    # コード作成
    code = f"{new_srs} = pd.to_datetime({old_srs}, format='{format}'{tail})"
    pNc(code, pp=pp)
    return None


def psplit(path, *, multiline=False, pp=True):
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
        pNc(code)
    else:
        pass
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
