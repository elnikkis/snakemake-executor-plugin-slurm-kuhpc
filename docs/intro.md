# 京都大学スーパーコンピュータ用 Snakemake Executor Plugin

京都大学学術情報メディアセンター（ACCMS）のスーパーコンピュータのジョブスケジューラ（Slurm）を使ってSnakemakeワークフローを実行するための executor plugin です。

## はじめに

このプラグインは、京都大学スーパーコンピュータ特有のリソース指定方法（`--rsc`パラメータ）に対応しています。標準のSlurm executor pluginとは異なり、京大スパコンのジョブスケジューラの仕様に最適化されています。

## 主な特徴

- **京大スパコン対応**: `--rsc`パラメータを自動生成
- **簡単な設定**: Snakemakeの標準的なリソース指定をそのまま利用可能
- **自動推測**: アカウントやパーティションを自動的に推測
- **GPU対応**: GPUジョブの簡単な実行

## クイックスタート

### 1. インストール

```bash
pip install snakemake-executor-plugin-slurm-kuhpc
```

### 2. 実行

```bash
snakemake --executor slurm-kuhpc --jobs 10
```

### 3. プロファイル設定（推奨）

`profiles/kyoto-hpc/config.yaml`を作成：

```yaml
executor: slurm-kuhpc
jobs: 10
default-resources:
  slurm_partition: "gr19999b"
  slurm_account: "gr19999"
  runtime: 1440  # 1日（分単位）
  mem_mb: 4000   # 4GB
```

実行：

```bash
snakemake --profile profiles/kyoto-hpc
```

## 次のステップ

詳細なリソース指定方法、使用例、トラブルシューティングについては [further.md](further.md) を参照してください。
