import argparse
import glob
import json
import os
import re


def main(
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


def get_home_path(env):
    if not os.getenv(env) is None:
        # 環境変数を指定した場合
        home_path = os.getenv(env)
    else:
        # MacとWindowsのホームパスを取得
        default_paths = [os.getenv("HOME"), os.getenv("HOMEPATH")]
        home_path = [hp for hp in default_paths if not hp is None][0]
    return home_path


def get_lines(path):
    if path.endswith("ipynb"):
        lines = parse_ipynb(path)
    else:
        lines = parse_text(path)
    return lines


def parse_ipynb(path):
    with open(path) as f:
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
    with open(path, "r") as f:
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


if __name__ == "__main__":
    main()
