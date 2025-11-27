# Executor Plugin for Supercomputer at ACCMS, Kyoto University

京都大学学術情報メディアセンター（ACCMS）のスーパーコンピュータシステム向けのSnakemake executor pluginの詳細ガイドです。

## 目次

- [リソース指定方法](#リソース指定方法)
- [京大スパコン特有の仕様](#京大スパコン特有の仕様)
- [詳細な使用例](#詳細な使用例)
- [プロファイル設定例](#プロファイル設定例)
- [トラブルシューティング](#トラブルシューティング)

## リソース指定方法

### 利用可能なリソースパラメータ

| リソース | 説明 | デフォルト値 | 対応する`--rsc`パラメータ |
|----------|------|-------------|------------------------|
| `slurm_account` | Slurmアカウント名 | 自動推測 | - |
| `slurm_partition` | パーティション名 | 自動推測 | - |
| `runtime` | 実行時間制限（分） | - | `-t` |
| `mem_mb` | プロセスあたりのメモリ量（MB） | - | `m` |
| `tasks` | プロセス数（MPIプロセス数） | 1 | `p` |
| `threads` | プロセスあたりのスレッド/コア数 | 1 | `t`, `c` |
| `gpus` | GPU数 | 0 | `g` |
| `slurm_extra` | 追加のSlurmオプション | - | - |

この表に載っていないリソースの指定方法（memやdiskなど）は考慮していないので使えるかわかりません。

メモリ量の指定は--rscにならっており、プロセスあたりの使用量の指定になっています。

### Snakefileでのリソース指定

各ルールでリソースを指定できます：

```python
rule my_analysis:
    input: "data.txt"
    output: "result.txt"
    resources:
        slurm_partition="gr19999b",
        slurm_account="gr19999",
        runtime=120,      # 2時間
        mem_mb=8000,      # 8GB
        threads=4         # 4コア
    shell:
        "my_program {input} > {output}"
```

### プロファイルでのデフォルト設定

すべてのルールに共通のデフォルト値をプロファイルで設定できます：

```yaml
# profiles/kyoto-hpc/config.yaml
executor: slurm-kuhpc
jobs: 10
default-resources:
    slurm_partition: "gr19999b"
    slurm_account: "gr19999"
    runtime: 1440  # 1日（分単位）
    mem_mb: 4000   # 4GB
```

## 京大スパコン特有の仕様

### --rscパラメータの対応

京都大学スーパーコンピュータでは、リソース指定に`--rsc`パラメータを使用します。このプラグインは自動的にSnakemakeのリソース指定を京大スパコンの形式に変換します。

#### 通常のジョブ（非GPU）

Snakemakeのリソース指定：
```python
resources:
    tasks=2,      # MPIプロセス数
    threads=4,    # OpenMPスレッド数
    mem_mb=8000   # 8GB
```

自動的に以下のように変換されます：
```bash
--rsc p=2:t=4:c=4:m=8000M
```

**パラメータの意味：**
- `p=2`: MPIプロセス数
- `t=4`: プロセスあたりのOpenMPスレッド数
- `c=4`: プロセスあたりのコア数（`threads`と同じ値）
- `m=8000M`: プロセスあたりのメモリ量

tとcの値を異なる値に設定することはできません。

#### GPUジョブ

GPUを使用する場合は、`gpus`リソースを指定します：

```python
resources:
    gpus=2,
    mem_mb=128000  # GPUジョブでは通常大量のメモリが必要
```

自動的に以下のように変換されます：
```bash
--rsc g=2
```

**重要な注意点：**
- 京大スパコンでは、`g=1`を指定すると自動的に`p=1:c=16:m=128000M`が設定されます
- `g=2`を指定すると自動的に`p=2:c=16:m=128000M`が設定されます
- GPUジョブでは、メモリやコア数は自動設定されるため、個別指定は不要です

### システムごとのスペック

京都大学スーパーコンピュータのシステムB（一般的なケース）：
- CPU: 112コア/ノード
- メモリ: 1コアあたり4571M（ノード全体で約500GB）

詳細は[京都大学スーパーコンピュータマニュアル](https://web.kudpc.kyoto-u.ac.jp/manual/ja/run/resource)を参照してください。

## 詳細な使用例

### 例1: シンプルなシングルコアジョブ

```python
rule simple_task:
    input: "input.txt"
    output: "output.txt"
    resources:
        runtime=30,    # 30分
        mem_mb=2000    # 2GB
    shell:
        "process {input} > {output}"
```

### 例2: OpenMP並列ジョブ

```python
rule openmp_task:
    input: "data.csv"
    output: "processed.csv"
    threads: 8
    resources:
        runtime=180,     # 3時間
        mem_mb=16000     # 16GB
    shell:
        """
        export OMP_NUM_THREADS={threads}
        my_openmp_program {input} {output}
        """
```

### 例3: MPIジョブ

```python
rule mpi_simulation:
    input: "config.ini"
    output: "simulation_result.dat"
    resources:
        tasks=4,         # 4 MPIプロセス
        threads=1,       # プロセスあたり1スレッド
        runtime=720,     # 12時間
        mem_mb=8000      # プロセスあたり8GB
    shell:
        "mpirun -n {resources.tasks} my_mpi_program {input} {output}"
```

### 例4: ハイブリッド並列（MPI + OpenMP）

```python
rule hybrid_parallel:
    input: "initial.dat"
    output: "final.dat"
    threads: 4
    resources:
        tasks=2,         # 2 MPIプロセス
        runtime=1440,    # 24時間
        mem_mb=32000     # プロセスあたり32GB
    shell:
        """
        export OMP_NUM_THREADS={threads}
        mpirun -n {resources.tasks} my_hybrid_program {input} {output}
        """
```

### 例5: GPUジョブ

```python
rule gpu_training:
    input: "training_data.h5"
    output: "model.pt"
    resources:
        gpus=1,
        runtime=2880,    # 48時間
        mem_mb=128000    # 128GB（自動設定されるが明示も可能）
    shell:
        """
        export CUDA_VISIBLE_DEVICES=0
        python train_model.py {input} {output}
        """
```

### 例6: 追加のSlurmオプション

`slurm_extra`を使用して、その他のSlurmオプションを指定できます：

```python
rule custom_slurm:
    input: "data.txt"
    output: "result.txt"
    resources:
        runtime=60,
        mem_mb=4000,
        slurm_extra="--mail-type=END --mail-user=user@example.com"
    shell:
        "process {input} > {output}"
```

**注意：** `--job-name`オプションは`slurm_extra`で指定できません（内部的に使用されています）。

## プロファイル設定例

### 基本的なプロファイル

```yaml
# profiles/default/config.yaml
executor: slurm-kuhpc
jobs: 20
default-resources:
    slurm_partition: "gr19999b"
    slurm_account: "gr19999"
    runtime: 1440
    mem_mb: 4000
```

### GPU特化プロファイル

```yaml
# profiles/gpu/config.yaml
executor: slurm-kuhpc
jobs: 4
default-resources:
    slurm_partition: "gg12345b"  # GPUパーティション
    slurm_account: "gg12345"
    runtime: 2880
    gpus: 1
    mem_mb: 128000
```

### 長時間ジョブ用プロファイル

```yaml
# profiles/long-jobs/config.yaml
executor: slurm-kuhpc
jobs: 5
default-resources:
    slurm_partition: "gr19999b"
    slurm_account: "gr19999"
    runtime: 10080  # 7日間（分単位）
    mem_mb: 8000
```

## トラブルシューティング

### アカウント・パーティションが見つからない

**エラー：**
```
Unable to guess SLURM account
```

**解決方法：**
プロファイルまたはルールで明示的に指定してください：

```yaml
default-resources:
    slurm_account: "your_account"
    slurm_partition: "your_partition"
```

### ジョブがメモリ不足で失敗する

**エラー：**
```
SLURM status is: 'OUT_OF_MEMORY'
```

**解決方法：**
`mem_mb`を増やしてください。

### ランタイムエラー

**エラー：**
```
SLURM status is: 'TIMEOUT'
```

**解決方法：**
`runtime`を増やしてください（分単位で指定）。

### ジョブログの確認

ジョブのログは以下のディレクトリに保存されます：
```
.snakemake/slurm_logs/rule_{rule_name}/{wildcards}/{job_id}.log
```

### Snakemakeをジョブ内で実行する警告

**警告：**
```
Running Snakemake in a SLURM within a job may lead to unexpected behavior
```

**解決方法：**
Snakemakeはログインノードから直接実行してください。ジョブ内でSnakemakeを実行しないでください。

## 参考資料

- [Snakemake公式ドキュメント](https://snakemake.readthedocs.io/)
- [京都大学スーパーコンピュータマニュアル](https://web.kudpc.kyoto-u.ac.jp/manual/)
- [Snakemake Plugin Catalog](https://snakemake.github.io/snakemake-plugin-catalog/)

