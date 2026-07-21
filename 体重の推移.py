from pathlib import Path
import pandas as pd


# ファイルパス
BASE_DIR = Path(__file__).resolve().parent
INPUT_PATH = BASE_DIR / "体重計記録.csv"
CLEANED_PATH = BASE_DIR / "体重計記録_前処理済み.csv"
MONTHLY_PATH = BASE_DIR / "体重計記録_月別集計.csv"


# CSV読み込み・日時変換
df = pd.read_csv(INPUT_PATH)
df["時間"] = pd.to_datetime(df["時間"], errors="coerce")
df = df.dropna(subset=["時間"])


# 測定失敗行を削除
failed_measurement = (
    df["体脂肪率 %"].eq(0)
    & df["筋肉量 (kg)"].eq(0)
)
df = df.loc[~failed_measurement].copy()


# 同じ日の記録は、最後に測定したものだけ残す
df["日付"] = df["時間"].dt.normalize()
df = (
    df.sort_values("時間")
    .drop_duplicates(subset="日付", keep="last")
    .reset_index(drop=True)
)


# 0になっている割合を再計算
rate_columns = {
    "筋肉率 %": "筋肉量 (kg)",
    "骨量（％） %": "骨量（kg） (kg)"
}

for rate_column, weight_column in rate_columns.items():
    zero_rows = df[rate_column].eq(0)

    df.loc[zero_rows, rate_column] = (
        df.loc[zero_rows, weight_column]
        .div(df.loc[zero_rows, "体重 (kg)"])
        .mul(100)
        .round(1)
    )


# 0が40%以上の列と、分析に不要な列を削除
zero_ratio = (
    df.select_dtypes(include="number")
    .eq(0)
    .mean()
)

drop_columns = zero_ratio[zero_ratio >= 0.4].index.tolist()
drop_columns += ["家族", "ボディタイプ"]

df = df.drop(columns=drop_columns, errors="ignore")


# 列名を整理
df = df.rename(
    columns={
        "骨量（kg） (kg)": "骨量 (kg)",
        "骨量（％） %": "骨量率 %"
    }
)


# 月別集計
df["年月"] = df["時間"].dt.to_period("M").astype(str)

monthly_summary = (
    df.groupby("年月", as_index=False)
    .agg(
        測定日数=("日付", "nunique"),
        平均体重_kg=("体重 (kg)", "mean"),
        最低体重_kg=("体重 (kg)", "min"),
        最高体重_kg=("体重 (kg)", "max"),
        平均BMI=("BMI", "mean"),
        平均体脂肪率=("体脂肪率 %", "mean"),
        平均筋肉量_kg=("筋肉量 (kg)", "mean"),
        平均体脂肪量_kg=("体脂肪量 (kg)", "mean"),
        平均除脂肪体重_kg=("除脂肪体重 (kg)", "mean"),
        平均基礎代謝量=("基礎代謝量", "mean"),
        平均内臓脂肪=("内臓脂肪", "mean")
    )
    .round(1)
)


# CSV出力
df.to_csv(CLEANED_PATH, index=False, encoding="utf-8-sig")
monthly_summary.to_csv(
    MONTHLY_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("前処理済みCSV：", CLEANED_PATH)
print("月別集計CSV：", MONTHLY_PATH)