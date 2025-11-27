# Snakemake Executor Plugin for Kyoto University Supercomputer - Examples

このディレクトリには、京都大学スーパーコンピュータでSnakemakeを使用する際の実践的な例が含まれています。

## 例の一覧

1. **basic/** - 基本的な使用例
2. **openmp/** - OpenMP並列ジョブの例
3. **mpi/** - MPIジョブの例
4. **gpu/** - GPUジョブの例
5. **profiles/** - プロファイル設定の例

## 使い方

各ディレクトリに移動して、以下のコマンドで実行できます：

```bash
cd basic
snakemake --executor slurm-kuhpc --jobs 10
```

または、プロファイルを使用する場合：

```bash
cd basic
snakemake --profile ../profiles/default
```

## 注意事項

- これらの例を実行する前に、`slurm_account`と`slurm_partition`を自分のアカウント情報に変更してください
- 京都大学スーパーコンピュータのログインノードから実行してください
- ジョブ内でSnakemakeを実行しないでください
