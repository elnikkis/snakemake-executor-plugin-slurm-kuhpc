"""
Unit tests for snakemake-executor-plugin-slurm-kuhpc.
These tests run locally without a SLURM environment.
"""

import asyncio
import subprocess
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from snakemake_executor_plugin_slurm_kuhpc import Executor, ExecutorSettings
from snakemake_interface_common.exceptions import WorkflowError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_executor_mock(**logger_kwargs):
    """Return a MagicMock that looks like an Executor instance."""
    mock = MagicMock(spec=Executor)
    mock.logger = MagicMock()
    return mock


# ---------------------------------------------------------------------------
# 1. TestExecutorSettings
# ---------------------------------------------------------------------------

class TestExecutorSettings:
    def test_defaults(self):
        s = ExecutorSettings()
        assert s.logdir is None
        assert s.keep_successful_logs is False
        assert s.delete_logfiles_older_than == 10
        assert s.requeue is False
        assert s.no_account is False
        assert s.jobname_prefix == ""
        assert s.qos is None
        assert s.reservation is None
        assert s.pass_command_as_script is False
        assert s.status_attempts == 5

    def test_custom_values(self):
        s = ExecutorSettings(
            logdir="/my/logs",
            keep_successful_logs=True,
            delete_logfiles_older_than=30,
            requeue=True,
            no_account=True,
            jobname_prefix="myjob",
            qos="high",
            reservation="myres",
            pass_command_as_script=True,
            status_attempts=10,
        )
        assert s.logdir == "/my/logs"
        assert s.keep_successful_logs is True
        assert s.delete_logfiles_older_than == 30
        assert s.requeue is True
        assert s.no_account is True
        assert s.jobname_prefix == "myjob"
        assert s.qos == "high"
        assert s.reservation == "myres"
        assert s.pass_command_as_script is True
        assert s.status_attempts == 10


# ---------------------------------------------------------------------------
# 2. TestCheckSlurmExtra
# ---------------------------------------------------------------------------

class TestCheckSlurmExtra:
    def _call(self, slurm_extra: str):
        mock = _make_executor_mock()
        job = MagicMock()
        job.resources.slurm_extra = slurm_extra
        Executor.check_slurm_extra(mock, job)

    def test_long_job_name_raises(self):
        with pytest.raises(WorkflowError):
            self._call("--job-name=foo")

    def test_long_job_name_with_space_raises(self):
        with pytest.raises(WorkflowError):
            self._call("--job-name foo")

    def test_short_job_name_raises(self):
        with pytest.raises(WorkflowError):
            self._call("-J foo")

    def test_unrelated_option_ok(self):
        self._call("--mem=4G")  # must not raise

    def test_empty_string_ok(self):
        self._call("")  # must not raise


# ---------------------------------------------------------------------------
# 3. TestDeleteLogfile
# ---------------------------------------------------------------------------

class TestDeleteLogfile:
    def test_existing_file_deleted(self, tmp_path):
        f = tmp_path / "job.log"
        f.write_text("log content")
        mock = _make_executor_mock()
        Executor._delete_logfile(mock, str(f))
        assert not f.exists()

    def test_missing_file_no_error(self, tmp_path):
        mock = _make_executor_mock()
        Executor._delete_logfile(mock, str(tmp_path / "nonexistent.log"))
        # Must not raise


# ---------------------------------------------------------------------------
# 4. TestDeleteOldLogfiles
# ---------------------------------------------------------------------------

class TestDeleteOldLogfiles:
    def _setup_logs(self, base):
        """Create .snakemake/slurm_logs/ with two files at different ages."""
        log_dir = base / ".snakemake" / "slurm_logs" / "rule_foo"
        log_dir.mkdir(parents=True)

        old_file = log_dir / "old.log"
        new_file = log_dir / "new.log"
        old_file.write_text("old")
        new_file.write_text("new")

        # set mtime: 11 days ago (old) and 1 day ago (new)
        now = datetime.now().timestamp()
        import os
        os.utime(old_file, (now - 11 * 86400, now - 11 * 86400))
        os.utime(new_file, (now - 1 * 86400, now - 1 * 86400))

        return old_file, new_file

    def test_old_file_deleted(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        old_file, new_file = self._setup_logs(tmp_path)
        mock = _make_executor_mock()
        Executor._delete_old_logfiles(mock, 10)
        assert not old_file.exists()

    def test_new_file_kept(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        old_file, new_file = self._setup_logs(tmp_path)
        mock = _make_executor_mock()
        Executor._delete_old_logfiles(mock, 10)
        assert new_file.exists()

    def test_no_log_dir_does_nothing(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mock = _make_executor_mock()
        Executor._delete_old_logfiles(mock, 10)  # must not raise


# ---------------------------------------------------------------------------
# 5. TestJobStati
# ---------------------------------------------------------------------------

class TestJobStati:
    def _run(self, stdout: str):
        mock = _make_executor_mock()
        with patch(
            "snakemake_executor_plugin_slurm_kuhpc.subprocess.check_output",
            return_value=stdout,
        ):
            return asyncio.run(Executor.job_stati(mock, "sacct ..."))

    def test_completed_and_failed(self):
        res, duration = self._run("12345|COMPLETED\n12346|FAILED\n")
        assert res == {"12345": "COMPLETED", "12346": "FAILED"}
        assert duration is not None

    def test_cancelled_with_suffix(self):
        res, duration = self._run("12347|CANCELLED by 1000\n")
        assert res == {"12347": "CANCELLED"}

    def test_called_process_error_returns_none(self):
        mock = _make_executor_mock()
        err = subprocess.CalledProcessError(1, "sacct")
        err.stderr = "error"
        with patch(
            "snakemake_executor_plugin_slurm_kuhpc.subprocess.check_output",
            side_effect=err,
        ):
            res, duration = asyncio.run(Executor.job_stati(mock, "sacct ..."))
        assert res is None
        assert duration is None


# ---------------------------------------------------------------------------
# 6. TestGetJobFailureReason
# ---------------------------------------------------------------------------

class TestGetJobFailureReason:
    def _call(self, stdout: str):
        mock = _make_executor_mock()
        with patch(
            "snakemake_executor_plugin_slurm_kuhpc.subprocess.check_output",
            return_value=stdout,
        ):
            return Executor._get_job_failure_reason(mock, "12345")

    def test_normal_reason(self):
        assert self._call("PartitionTimeLimit") == "PartitionTimeLimit"

    def test_none_string_returns_none(self):
        assert self._call("None") is None

    def test_empty_string_returns_none(self):
        assert self._call("") is None

    def test_called_process_error_returns_none(self):
        mock = _make_executor_mock()
        with patch(
            "snakemake_executor_plugin_slurm_kuhpc.subprocess.check_output",
            side_effect=subprocess.CalledProcessError(1, "sacct"),
        ):
            assert Executor._get_job_failure_reason(mock, "12345") is None


# ---------------------------------------------------------------------------
# 7. TestGetFailedNode
# ---------------------------------------------------------------------------

class TestGetFailedNode:
    def _call(self, stdout: str):
        mock = _make_executor_mock()
        with patch(
            "snakemake_executor_plugin_slurm_kuhpc.subprocess.check_output",
            return_value=stdout,
        ):
            return Executor._get_failed_node(mock, "12345")

    def test_node_name_returned(self):
        assert self._call("node001") == "node001"

    def test_none_string_returns_none(self):
        assert self._call("None") is None

    def test_empty_string_returns_none(self):
        assert self._call("") is None

    def test_none_assigned_returns_none(self):
        assert self._call("none assigned") is None

    def test_called_process_error_returns_none(self):
        mock = _make_executor_mock()
        with patch(
            "snakemake_executor_plugin_slurm_kuhpc.subprocess.check_output",
            side_effect=subprocess.CalledProcessError(1, "sacct"),
        ):
            assert Executor._get_failed_node(mock, "12345") is None
