def df_to_csv(df, filename):
    df.to_csv(f"{filename}.csv", index=False)
