import glob
import os

from .utils import *

# TODO
# importのテンプレート
# 相対パスを絶対パスにする関数
# sniffでヒットしすぎたら停止する


def impt(*modules, tpl=False, pp=True):
    if tpl is True:
        modules = [
            "glob",
            "os",
            "from datetime import datetime",
            "",
            "numpy as np",
            "pandas as pd",
        ]
    else:
        modules = sorted(modules)
    line = []
    for m in modules:
        if m.startswith("from "):
            line.append(m)
        elif m != "":
            line.append(f"import {m}")
        else:
            line.append("")
    code = ("\n").join(line)
    print_copy(code, pp)
    return None


def pause():
    raise Exception("stop")


def sniff(
    word,
    /,
    pattern,
    environ="",
    *,
    count=True,
    decoration=True,
    fname=True,
    n_neighbors=2,
    show_content=True,
    sep=True,
):
    # 環境変数でホームパスを取得
    home_path = get_home_path(environ)
    # 親ディレクトリとパターンを結合
    ptn = os.path.join(home_path, pattern)

    # サーチするパスのリストを取得
    paths = glob.glob(ptn, recursive=True)

    # 検索対象のファイル数を表示
    print(f"検索対象ファイル数: {len(paths)}")

    # 検索結果を辞書に追加
    result = []
    for path in paths:
        lines = get_lines(path)
        r_dict = {}
        r_dict["path"] = path
        r_dict["lines"] = lines
        # マッチしたindexを取得
        r_dict["index"] = get_matched_idxs(lines, word=word)
        r_dict["count"] = len(r_dict["index"])
        # 前後の行を取得する
        r_dict["index_added"] = collect_neighbor(
            r_dict["index"], n_neighbors=n_neighbors
        )
        # 最大桁数を取得する
        if r_dict["count"]:
            r_dict["max_digits"] = len(str(max(r_dict["index_added"])))
        # ファイルの行数からはみ出たものは除外
        r_dict["index_added"] = [
            i for i in r_dict["index_added"] if i in range(0, len(lines))
        ]
        # 検索結果を辞書に追加
        result.append(r_dict)

        if len(result) == 20:
            print("ヒット数が20を超えたので検索を停止しました。")
            break

    # 出力を作成
    big_output = []
    for r in result:
        if r.get("count"):
            small_output = []
            # -nの処理 ファイル名を表示
            if fname:
                path = "- " + r.get("path")
                # -cの処理 マッチ数を表示
                if count:
                    path += " " + str(r.get("count"))
                small_output.append(path)
            # -rの処理 検索結果を表示
            if show_content:
                idxs = r.get("index_added")
                for itr, idx in enumerate(idxs):
                    line = r.get("lines")[idx]
                    # -iの処理 行番号を表示
                    if decoration:
                        line = "  ".join([str(idx).rjust(r.get("max_digits")), line])
                    # -mの処理 マッチした行をハイライト
                    if not decoration:
                        pass
                    elif (decoration) & (idx in r.get("index")):
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
    for big in big_output:
        for small in big:
            print(small)


def psplit(path, *, pp=True):

    path = ref2abs(path)

    # 同じ文字を含む環境変数を抽出
    envs = {k: v for k, v in dict(os.environ).items() if v in path}
    sep_s = fix_sep(path)
    if len(envs):
        # パスの文字数が最も多い環境変数を取得
        envs_sorted = dict(sorted(envs.items(), key=lambda x: -len(x[1])))
        env = next(iter(envs_sorted))

        # 環境変数
        path_front = f"os.getenv('{env}')"

        # 環境変数以降のパスの整形
        join_s = ", "
        path_back = path.replace(os.getenv(env), "").strip(sep_s).split(sep_s)
        path_back = [f"'{p}'" for p in path_back]
        path_back = (join_s).join(path_back)

        # 環境変数部分とそれ以降を結合
        code = (join_s).join([path_front, path_back])
        code = f"os.path.join({code})"

        print_copy(code, pp)
        return None
    else:
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
    print_copy(code, pp)
    return None


def upgrade(*, pp=True):
    code = "pip install git+https://github.com/Taichi-Ibi/ezlite --upgrade"
    print_copy(code, pp)
    return None
