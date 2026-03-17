# Snakemake executor plugin: slurm-kuhpc

Snakemake executor plugin for the supercomputer systems at the Academic Center for Computing and Media Studies, Kyoto University.

このプラグインは、京都大学学術情報メディアセンターのスーパーコンピュータシステム向けのSnakemakeのSlurm executor pluginです。京大スパコン特有のリソース指定方法（`--rsc`パラメータ）に対応しています。

## インストール

uvを使用してインストールできます：

```bash
uv add snakemake-executor-plugin-slurm-kuhpc
```

または、Snakemakeと一緒にインストール：

```bash
uv add snakemake snakemake-executor-plugin-slurm-kuhpc
```

pipを使う場合：

```bash
pip install snakemake-executor-plugin-slurm-kuhpc
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

## プラグイン設定オプション

`--slurm-kuhpc-<option>` または プロファイルの `executor-settings` で指定できます。

| オプション | デフォルト | 説明 |
|---|---|---|
| `logdir` | `.snakemake/slurm_logs` | SLURMログファイルの保存ディレクトリ |
| `keep-successful-logs` | `false` | 成功したジョブのログを保持する（デフォルトは削除） |
| `delete-logfiles-older-than` | `10` | 指定日数より古いログファイルを削除（0で無効） |
| `requeue` | `false` | ノード障害時にジョブを再キューする（`--requeue`をsbatchに渡す） |
| `no-account` | `false` | sbatchにアカウント引数を渡さない |
| `jobname-prefix` | `""` | SLURMジョブ名のプレフィックス（最大50文字、英数字/アンダースコア/ハイフン） |
| `qos` | なし | sbatchに渡すSLURMのQoS文字列 |
| `reservation` | なし | sbatchに渡すSLURMのリザベーション名 |
| `pass-command-as-script` | `false` | コマンドを`--wrap`ではなく標準入力スクリプトとして渡す（長いコマンドラインに有効） |
| `status-attempts` | `5` | sacctでジョブステータスを問い合わせる最大試行回数 |

## 主な機能

- 京都大学スーパーコンピュータの`--rsc`パラメータに対応
- GPU、MPI、OpenMPジョブのサポート
- 自動的なアカウント・パーティション推測
- ジョブステータスの自動監視
- ログファイルの自動管理（成功ジョブのログ削除、古いログの自動削除）
- ジョブ失敗時の原因・障害ノードの記録

## テストの実行

### ユニットテスト（SLURM環境不要）

```bash
uv run pytest tests/test_unit.py -v
```

### 京大スパコン上での動作確認

ヘッドノードにログインし、リポジトリをクローンしてプラグインをインストールします：

```bash
git clone https://github.com/elnikkis/snakemake-executor-plugin-slurm-kuhpc.git
cd snakemake-executor-plugin-slurm-kuhpc
uv sync
```

`examples/basic/` の Snakefile を使って動作確認します：

```bash
cd examples/basic
uv run snakemake --executor slurm-kuhpc --jobs 4 \
  --default-resources slurm_partition=gr19999b slurm_account=gr19999
```

ジョブの投入状況は `squeue -u $USER` で確認できます。

#### デバッグ時のヒント

ログファイルの自動削除を無効にすると、失敗・成功を問わずログが残るため原因調査がしやすくなります：

```bash
uv run snakemake --executor slurm-kuhpc --jobs 4 \
  --default-resources slurm_partition=gr19999b slurm_account=gr19999 \
  --slurm-kuhpc-delete-logfiles-older-than 0
```

ログは `.snakemake/slurm_logs/` に保存されます。

## さらに詳しい情報

詳細なリソース指定方法や高度な使い方については、[docs/further.md](docs/further.md)を参照してください。

使い方の例は[examples/README.md](examples/README.md)を参照してください。

## ライセンス

MIT License

