# The Executor Plugin for Supercomputer at ACCMS, Kyoto University 

## Resource Specifications

resourcesで設定できる項目：

| Resource | Description |
|----------|-------------|
| slurm_account | the account for slurm execusion |
| slurm_partition | the partition a rule/job is to use |
| runtime | wall time |
| mem_mb | required memory per process |
| tasks | number of process (MPI process) |
| threads | number of threads/cores per process (OpenMP) |
| gpus | number of GPUs |
| constraint | |
| slurm_extra | additional slurm options |

各ルールのresource指定で使える：

```python
rule:
    input: ...
    output: ...
    resources:
        threads=<number of threads to run>,
        mem_mb=3000,
```


初期値の設定がworkflow profileでできる。

```YAML
default-resources:
    slurm_partition: "<your default partition>"
    slurm_account: "<your account>"
    runtime: 1440  # 1 day
    mem_mb: 4000  # 4GB
```


