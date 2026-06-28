#!/usr/bin/env python3
"""食べログCSV(ANSI/CP932) を UTF-8 の data/restaurants.json に変換する。

使い方:
    python3 build_data.py

入力:  data/tabelog_hatsudai_SC_full.csv  (CP932 / Shift-JIS)
出力:  data/restaurants.json              (UTF-8, グルメマップが読み込む)

データの注意点:
- CSVのデータ行は ANSI(CP932)。ヘッダ行のみエンコードが異なるため、
  列名はこのスクリプト側で固定定義し、ヘッダ行は読み飛ばす。
- 各レコードは地図表示に必要なフィールドのみを短いキーに整形して軽量化する。
"""
import csv
import io
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "data", "tabelog_hatsudai_SC_full.csv")
OUT = os.path.join(BASE, "data", "restaurants.json")

# データ行の列順（ヘッダ行は別エンコードのため使わず固定定義する）
COLUMNS = [
    "name", "rating", "reviews", "saves", "genre", "station",
    "budgetNight", "budgetDay", "url", "address", "postal",
    "lat", "lng", "phone", "hours", "holiday", "seats",
    "privateRoom", "smoking", "reservation", "award", "parking",
    "access", "photo",
]


def parse_budget(s):
    """ '\\1,000～\\1,999' のような予算文字列から下限/上限(円)を取り出す。

    取れない場合は (None, None)。'～\\999' は (0, 999)、'\\30,000～' は (30000, None)。
    """
    if not s or s == "-":
        return None, None
    nums = [int(n.replace(",", "")) for n in re.findall(r"[\d,]+", s)]
    if not nums:
        return None, None
    if s.strip().startswith("～") or s.strip().startswith("\\") is False and s.strip().startswith("~"):
        # 上限のみ表記（例: ～\999）
        return 0, nums[-1]
    if len(nums) == 1:
        # 下限のみ表記（例: \30,000～）
        return nums[0], None
    return nums[0], nums[-1]


def to_float(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def to_int(x):
    try:
        return int(str(x).replace(",", ""))
    except (TypeError, ValueError):
        return None


def award_flags(award):
    """受賞文字列から bool フラグを作る。"""
    has_hyaku = "百名店" in award
    has_award = "Tabelog Award" in award or "Award" in award
    return has_hyaku, has_award


DAYS = "月火水木金土日"  # index 0=月 .. 6=日


def open_days(hours, holiday):
    """営業時間と定休日から「営業している曜日」を [月..日] の 0/1 配列で推定する。

    営業時間は「<営業曜日> 11:30 - 23:00 ... <定休曜日>」の形式が多く、
    最初の時刻より前に並ぶ曜日を営業日とみなす。曜日表記が無い店は
    全曜日営業とみなし、定休日フィールドにある曜日は閉店として除外する。
    判定材料が無い店は全曜日営業（ベストエフォート）。
    """
    open_set = set(range(7))  # 既定は全曜日営業
    if any(c in DAYS for c in hours):
        m = re.search(r"\d{1,2}:\d{2}", hours)
        lead = hours[:m.start()] if m else hours
        lead_days = {DAYS.index(c) for c in lead if c in DAYS}
        if lead_days:
            open_set = lead_days
    # 定休日に明記された曜日を除外
    for c in holiday:
        if c in DAYS:
            open_set.discard(DAYS.index(c))
    return [1 if i in open_set else 0 for i in range(7)]


def main():
    with open(SRC, "rb") as fh:
        raw = fh.read()

    records = []
    skipped = 0
    for lineno, b in enumerate(raw.split(b"\n")):
        if lineno == 0:           # ヘッダ行は読み飛ばす
            continue
        if not b.strip():
            continue
        text = b.decode("cp932")
        row = next(csv.reader(io.StringIO(text)))
        if len(row) < len(COLUMNS):
            skipped += 1
            continue
        r = dict(zip(COLUMNS, row[:len(COLUMNS)]))

        lat, lng = to_float(r["lat"]), to_float(r["lng"])
        if lat is None or lng is None:
            skipped += 1
            continue

        bmin, bmax = parse_budget(r["budgetNight"])
        hyaku, award = award_flags(r["award"])

        records.append({
            "name": r["name"],
            "rating": to_float(r["rating"]),
            "reviews": to_int(r["reviews"]) or 0,
            "saves": to_int(r["saves"]) or 0,
            "genre": r["genre"],
            "genreTop": r["genre"].split("/")[0].strip(),
            "station": r["station"],
            "budgetNight": r["budgetNight"] if r["budgetNight"] != "-" else "",
            "budgetDay": r["budgetDay"] if r["budgetDay"] != "-" else "",
            "budgetMin": bmin,
            "budgetMax": bmax,
            "url": r["url"],
            "address": r["address"],
            "lat": lat,
            "lng": lng,
            "phone": r["phone"],
            "hours": r["hours"],
            "holiday": r["holiday"],
            "openDays": open_days(r["hours"], r["holiday"]),
            "seats": r["seats"],
            "privateRoom": r["privateRoom"].startswith("有"),
            "smoking": r["smoking"],
            "reservation": r["reservation"],
            "award": r["award"],
            "hyakumeiten": hyaku,
            "tabelogAward": award,
            "access": r["access"],
            "photo": r["photo"],
        })

    # 評価の高い順で並べておく（初期表示・リストのデフォルト）
    records.sort(key=lambda x: (x["rating"] or 0, x["reviews"]), reverse=True)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, separators=(",", ":"))

    size_kb = os.path.getsize(OUT) / 1024
    print(f"wrote {len(records)} records -> {OUT} ({size_kb:.0f} KB), skipped {skipped}")


if __name__ == "__main__":
    main()
