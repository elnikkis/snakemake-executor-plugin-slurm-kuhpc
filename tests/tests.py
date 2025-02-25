from typing import Mapping, Optional
import snakemake.common.tests
from snakemake_interface_common.plugin_registry.plugin import TaggedSettings
from snakemake_interface_executor_plugins.settings import ExecutorSettingsBase


# Check out the base classes found here for all possible options and methods:
# https://github.com/snakemake/snakemake/blob/main/snakemake/common/tests/__init__.py
class TestWorkflowsBase(snakemake.common.tests.TestWorkflowsBase):
    __test__ = True

    def get_executor(self) -> str:
        return "slurm-kuhpc"

    def get_executor_settings(self) -> Optional[ExecutorSettingsBase]:
        # instantiate ExecutorSettings of this plugin as appropriate
        ...

    def get_default_storage_provider(self) -> Optional[str]: ...

    def get_default_storage_prefix(self) -> Optional[str]: ...

    def get_default_storage_provider_settings(
        self,
    ) -> Optional[Mapping[str, TaggedSettings]]: ...
