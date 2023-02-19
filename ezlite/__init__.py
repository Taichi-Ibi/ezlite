import glob
import os
from functools import partial
from itertools import tee

from .utils import *

# 関数一覧
# upgrade, template, p, lsplit, todt, psplit, sniff

# TODO
# sniffの出力部分リファクタリング
# 逐次出力
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
    limit=(DEFAULT_LIMIT := 20),
    n_neighbors=2,
    count=True,
    decoration=False,
    show_content=True,
    show_filename=True,
):
    # 環境変数で親ディレクトリを取得
    upper_dir = get_upper_dir(environ)
    # 引数が絶対パスの場合はuppper_dirが重複するので空白に置き換え
    pattern = pattern.replace(upper_dir + "/", "")
    # 親ディレクトリとパターンを結合
    pattern = os.path.join(upper_dir, pattern)
    # パスの[]をglob用にescapeする
    pattern = escape_brackets(pattern)
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
        print(f"検索対象ファイル数は{file_count}です。")

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

    # 出力を作成
    output_li = []
    for result_di in result_li:
        output = []
        # ファイル名とヒット数を取得
        path = get_filename(result_di, show_filename, count)
        output.append(path)
        # 検索結果を表示
        if show_content is True:
            idxs = result_di.get("index_added")
            for itr, idx in enumerate(idxs):
                line = result_di.get("lines")[idx]
                # 行番号とヒット行に*を表示
                if decoration is True:
                    # ヒットマーク
                    if idx in result_di.get("indexs"):
                        head = "* "
                    else:
                        head = "  "
                    # 行番号
                    line = head + "  ".join(
                        [str(idx).rjust(result_di.get("max_digits")), line]
                    )
                # 1行目ではなくて、行番号が2以上離れている場合は改行
                idxs_diff = idxs[itr] - idxs[itr - 1]
                if (itr != 0) & (idxs_diff != 1):
                    output.append("")
                # 行を出力リストに追加
                output.append(line)
            # ファイルごとに改行
            output.append("")
        # 検索結果をリストに追加
        output_li.append(output)

    # 出力
    print()
    print_2dlist(outer_li=output_li)
    return None
