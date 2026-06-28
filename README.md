# 初台グルメマップ 🍜

初台・渋谷・新宿エリアの**食べログ評価上位1,200店**を、スマートフォンで快適に探せるグルメマップサイトです。
Leaflet + OpenStreetMap を使った静的サイトで、GitHub Pages で公開できます。

## 主な機能

- 🗺️ **地図表示** — 1,200店をマーカークラスタで表示（評価で色分け：金=★4.0+／赤=★3.8+／青=その他）
- 🔍 **検索** — 店名・ジャンル・駅名でインクリメンタル検索
- 🎛️ **絞り込み** — ジャンル（大分類）／最寄駅／予算（夜）／評価／受賞店・個室・予約可・禁煙
- ↕️ **並び替え** — 評価順／口コミ数順／保存数順／**現在地から近い順**
- 📍 **現在地** — 現在地を地図に表示し、近い順に並び替え
- 🏪 **店舗詳細** — 写真・評価・予算・住所・受賞バッジ、ワンタップで **電話／食べログ／Googleマップ経路**
- 📱 スマホ最適化のボトムシートUI（ドラッグで開閉、地図と連動）

## ファイル構成

| パス | 内容 |
|------|------|
| `index.html` | グルメマップ本体（CSS/JSインライン） |
| `data/restaurants.json` | サイトが読み込む店舗データ（UTF-8、`build_data.py` で生成） |
| `data/tabelog_hatsudai_SC_full.csv` | 元データ（ANSI/CP932） |
| `build_data.py` | CSV → JSON 変換スクリプト |
| `vendor/` | Leaflet / markercluster 一式（CDN非依存・オフライン可） |
| `smartphone.html` | 旧「スマホ比較2025-2026」ページ（退避） |

## データ更新の手順

元CSV（`data/tabelog_hatsudai_SC_full.csv`）を差し替えたら、変換スクリプトを実行して JSON を再生成します。

```bash
python3 build_data.py
# -> data/restaurants.json を上書き出力
```

## ローカルでの確認

```bash
python3 -m http.server 8000
# ブラウザで http://localhost:8000/ を開く
```

## GitHub Pages での公開

リポジトリの **Settings → Pages** で、Source を公開したいブランチ（例: `master`）の `/ (root)` に設定してください。
数分後に `https://<ユーザー名>.github.io/smartphone-comparison/` で公開されます。

## データ出典

店舗情報は食べログの公開情報に基づきます。写真・店舗ページの著作権は各提供元に帰属します。
