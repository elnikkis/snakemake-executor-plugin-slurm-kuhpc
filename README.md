# Snakemake executor plugin: slurm-kuhpc

Snakemake executor plugin for the supercomputer systems at the Academic Center for Computing and Media Studies, Kyoto University.

このプラグインは、京都大学学術情報メディアセンターのスーパーコンピュータシステム向けのSnakemakeのSlurm executor pluginです。京大スパコン特有のリソース指定方法（`--rsc`パラメータ）に対応しています。

## インストール

pipを使用してインストールできます(TODO)：

```bash
pip install snakemake-executor-plugin-slurm-kuhpc
```

または、Snakemakeと一緒にインストール：

```bash
pip install snakemake snakemake-executor-plugin-slurm-kuhpc
```

## 基本的な使い方

Snakemake 8.0以上が必要です。ワークフローディレクトリから以下のコマンドで実行します：

```bash
snakemake --executor slurm-kuhpc --jobs 10
```

`--jobs`オプションで並行実行するジョブ数を指定します。

## クイックスタート例

### 1. Snakefileの準備

```python
rule example:
    input: "input.txt"
    output: "output.txt"
    resources:
        slurm_partition="gr19999b",  # パーティション名
        slurm_account="gr19999",     # アカウント名
        runtime=60,                  # 実行時間（分）
        mem_mb=4000,                 # メモリ（MB）
        threads=4                    # スレッド数
    shell:
        "cat {input} > {output}"
```

### 2. 実行

```bash
snakemake --executor slurm-kuhpc --jobs 10
```

## プロファイルを使った設定（推奨）

複数のオプションを毎回指定するのは大変です。プロファイルを使用すると便利です。

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

プロファイルを使用して実行：

```bash
snakemake --profile profiles/kyoto-hpc
```

## 主な機能

- 京都大学スーパーコンピュータの`--rsc`パラメータに対応
- GPU、MPI、OpenMPジョブのサポート
- 自動的なアカウント・パーティション推測
- ジョブステータスの自動監視

## さらに詳しい情報

詳細なリソース指定方法や高度な使い方については、[docs/further.md](docs/further.md)を参照してください。

使い方の例は[examples/README.md](examples/README.md)を参照してください。

## ライセンス

MIT License

