import os
import pytest
import shutil
import signal
from pathlib import Path

import pipelinewise.cli as cli
from pipelinewise.cli.pipelinewise import PipelineWise

from cli_args import CliArgs

CONFIG_DIR="{}/resources/sample_json_config".format(os.path.dirname(__file__))
VIRTUALENVS_DIR="./virtualenvs-dummy"
TEST_PROJECT_NAME="test-project"
TEST_PROJECT_DIR="{}/{}".format(os.getcwd(), TEST_PROJECT_NAME)


class TestCli(object):
    """
    Unit Tests for PipelineWise CLI executable
    """
    def setup_method(self):
        # Create CLI arguments
        self.args = CliArgs(log="coverage.log")
        self.pipelinewise = PipelineWise(self.args, CONFIG_DIR, VIRTUALENVS_DIR)


    def teardown_method(self):
        # Delete test directories
        try:
            shutil.rmtree(TEST_PROJECT_DIR)
            shutil.rmtree(os.path.join(CONFIG_DIR, "target_one/tap_one/log"))
        except:
            pass


    def test_target_dir(self):
        """Singer target connector config path must be relative to the project config dir"""
        assert \
            self.pipelinewise.get_target_dir("dummy-target") == \
            "{}/dummy-target".format(CONFIG_DIR)


    def test_tap_dir(self):
        """Singer tap connector config path must be relative to the target connector config path"""
        assert \
            self.pipelinewise.get_tap_dir("dummy-target", "dummy-tap") == \
            "{}/dummy-target/dummy-tap".format(CONFIG_DIR)


    def test_tap_log_dir(self):
        """Singer tap log path must be relative to the tap connector config path"""
        assert \
            self.pipelinewise.get_tap_log_dir("dummy-target", "dummy-tap") == \
            "{}/dummy-target/dummy-tap/log".format(CONFIG_DIR)


    def test_connector_bin(self):
        """Singer connector binary must be at a certain location under PIPELINEWISE_HOME .virtualenvs dir"""
        assert \
            self.pipelinewise.get_connector_bin("dummy-type") == \
            "{}/dummy-type/bin/dummy-type".format(VIRTUALENVS_DIR)


    def test_connector_files(self):
        """Every singer connector must have a list of JSON files at certain locations"""

        # TODO: get_connector_files is duplicated in config.py and pipelinewise.py
        #       Refactor to use only one
        assert \
            self.pipelinewise.get_connector_files("/var/singer-connector") == \
            {
                'config': '/var/singer-connector/config.json',
                'inheritable_config': '/var/singer-connector/inheritable_config.json',
                'properties': '/var/singer-connector/properties.json',
                'state': '/var/singer-connector/state.json',
                'transformation': '/var/singer-connector/transformation.json',
                'selection': '/var/singer-connector/selection.json'
            }


    def test_not_existing_config_dir(self):
        """Test with not existing config dir"""
        # Create a new pipelinewise object pointing to a not existing config directory
        pipelinewise_with_no_config = PipelineWise(self.args, "not-existing-config-dir", VIRTUALENVS_DIR)

        # It should return and empty config with empty list targets
        # TODO: Make this scenario to fail with error message of "config dir not exists"
        assert pipelinewise_with_no_config.config == {}
        assert pipelinewise_with_no_config.get_targets() == []


    def test_get_targets(self):
        """Targets should be loaded from JSON as is"""
        assert self.pipelinewise.get_targets() == cli.utils.load_json("{}/config.json".format(CONFIG_DIR)).get("targets", [])


    def test_get_target(self):
        """Selecting target by ID should append connector files"""
        # Get target definitions from JSON file
        targets = cli.utils.load_json("{}/config.json".format(CONFIG_DIR)).get("targets", [])
        exp_target_one = next((item for item in targets if item["id"] == "target_one"), False)
        exp_target_two = next((item for item in targets if item["id"] == "target_two"), False)

        # Append the connector file paths to the expected targets
        exp_target_one['files'] = self.pipelinewise.get_connector_files("{}/target_one".format(CONFIG_DIR))
        exp_target_two['files'] = self.pipelinewise.get_connector_files("{}/target_two".format(CONFIG_DIR))

        # Getting target by ID should match to original JSON and should contains the connector files list
        assert self.pipelinewise.get_target("target_one") == exp_target_one
        assert self.pipelinewise.get_target("target_two") == exp_target_two


    def test_get_taps(self):
        """Selecting taps by target ID should append tap statuses"""
        # Get target definitions from JSON file
        targets = cli.utils.load_json("{}/config.json".format(CONFIG_DIR)).get("targets", [])
        target_one = next((item for item in targets if item["id"] == "target_one"), False)
        target_two = next((item for item in targets if item["id"] == "target_two"), False)

        # Append the tap statuses to every tap in target_one
        exp_tap_one = target_one["taps"][0]
        exp_tap_two = target_one["taps"][1]
        exp_tap_one["status"] = self.pipelinewise.detect_tap_status("target_one", exp_tap_one["id"])
        exp_tap_two["status"] = self.pipelinewise.detect_tap_status("target_one", exp_tap_two["id"])

        # Append the tap statuses to every tap in target_one
        exp_tap_three = target_two["taps"][0]
        exp_tap_three["status"] = self.pipelinewise.detect_tap_status("target_two", exp_tap_three["id"])

        # Tap statuses should be appended to every tap
        assert self.pipelinewise.get_taps("target_one") == [exp_tap_one, exp_tap_two]
        assert self.pipelinewise.get_taps("target_two") == [exp_tap_three]


    def test_get_tap(self):
        """Getting tap by ID should return status, connector and target props as well"""
        # Get target definitions from JSON file
        targets = cli.utils.load_json("{}/config.json".format(CONFIG_DIR)).get("targets", [])
        target_one = next((item for item in targets if item["id"] == "target_one"), False)

        # Append the tap status, files and target keys to the tap
        exp_tap_one = target_one["taps"][0]
        exp_tap_one["status"] = self.pipelinewise.detect_tap_status("target_one", exp_tap_one["id"])
        exp_tap_one["files"] = self.pipelinewise.get_connector_files("{}/target_one/tap_one".format(CONFIG_DIR))
        exp_tap_one["target"] = self.pipelinewise.get_target("target_one")

        # Getting tap by ID should match to original JSON and should contain the status, connector files and target props
        assert self.pipelinewise.get_tap("target_one", "tap_one") == exp_tap_one


    def test_get_not_existing_target(self):
        """Test getting not existing target"""

        # Getting not existing from should raise exception
        with pytest.raises(Exception):
            assert self.pipelinewise.get_target("not-existing-target") == {}


    def test_get_taps_from_not_existing_target(self):
        """Test getting taps from not existing target"""

        # Getting not existing from should raise exception
        with pytest.raises(Exception):
            assert self.pipelinewise.get_tap("not-existing-target", "not-existing-tap") == {}


    def test_get_not_existing_tap(self):
        """Test getting not existing tap from existing target"""

        # Getting not existing from should raise exception
        with pytest.raises(Exception):
            assert self.pipelinewise.get_tap("target_one", "not-existing-tap") == {}


    def test_create_filtered_tap_properties(self):
        """Test creating fastsync and singer specific properties file"""
        # TODO: review this completely
        (
            tap_properties_fastsync,
            fastsync_stream_ids,
            tap_properties_singer,
            singer_stream_ids
        ) = self.pipelinewise.create_filtered_tap_properties(
            "target_snowflake",
            "tap_mysql",
            "{}/resources/sample_json_config/target_one/tap_one/properties.json".format(os.path.dirname(__file__)),
            "{}/resources/sample_json_config/target_one/tap_one/state.json".format(os.path.dirname(__file__)),
            {
                "selected": True,
                "target_type": ["target-snowflake"],
                "tap_type": ["tap-mysql", "tap-postgres"],
                "initial_sync_required": True
            },
            create_fallback = True)

        # Fastsync and singer properties should be created
        assert os.path.isfile(tap_properties_fastsync)
        assert os.path.isfile(tap_properties_singer)

        # Delete generated properties file
        os.remove(tap_properties_fastsync)
        os.remove(tap_properties_singer)

        # Fastsync and singer properties should be created
        #assert fastsync_stream_ids == []
        #assert singer_stream_ids == []


    def test_merge_empty_catalog(self):
        """Merging two empty singer schemas should be another empty"""
        # TODO: Check if pipelinewise.merge_schemas is required at all or not
        assert self.pipelinewise.merge_schemas({}, {}) == {}


    def test_merge_empty_stream_catalog(self):
        """Merging empty schemas should be empty"""
        # TODO: Check if pipelinewise.merge_schemas is required at all or not
        assert self.pipelinewise.merge_schemas({"streams": []}, {"streams": []}) == {"streams": []}


    def test_merge_same_catalog(self):
        """Test merging not empty schemas"""
        # TODO: Check if pipelinewise.merge_schemas is required at all or not
        tap_one_catalog = cli.utils.load_json("{}/resources/sample_json_config/target_one/tap_one/properties.json".format(os.path.dirname(__file__)))

        assert self.pipelinewise.merge_schemas(tap_one_catalog, tap_one_catalog) == tap_one_catalog


    def test_merge_updated_catalog(self):
        """Test merging not empty schemas"""
        # TODO: Check if pipelinewise.merge_schemas is required at all or not
        tap_one_catalog = cli.utils.load_json("{}/resources/sample_json_config/target_one/tap_one/properties.json".format(os.path.dirname(__file__)))
        tap_one_updated_catalog = cli.utils.load_json("{}/resources/sample_json_config/target_one/tap_one/properties_updated.json".format(os.path.dirname(__file__)))

        assert self.pipelinewise.merge_schemas(tap_one_catalog, tap_one_updated_catalog) == tap_one_catalog


    def test_make_default_selection(self):
        """Test if streams selected correctly in catalog JSON"""
        tap_one_catalog = cli.utils.load_json("{}/resources/sample_json_config/target_one/tap_one/properties.json".format(os.path.dirname(__file__)))
        tap_one_selection_file = "{}/resources/sample_json_config/target_one/tap_one/selection.json".format(os.path.dirname(__file__))

        # Update catalog selection
        tap_one_with_selection = self.pipelinewise.make_default_selection(tap_one_catalog, tap_one_selection_file)

        # Table one has to be selected with LOG_BASED replication method
        assert tap_one_with_selection['streams'][0]['metadata'][0]['metadata']['selected'] == True
        assert tap_one_with_selection['streams'][0]['metadata'][0]['metadata']['replication-method'] == "LOG_BASED"

        # Table two has to be selected with INCREMENTAL replication method
        assert tap_one_with_selection['streams'][1]['metadata'][0]['metadata']['selected'] == True
        assert tap_one_with_selection['streams'][1]['metadata'][0]['metadata']['replication-method'] == "INCREMENTAL"
        assert tap_one_with_selection['streams'][1]['metadata'][0]['metadata']['replication-key'] == "id"

        # Table three should not be selected
        assert tap_one_with_selection['streams'][2]['metadata'][0]['metadata']['selected'] == False


    def test_create_consumable_target_config(self):
        """Test merging target config.json and inheritable_config.json"""
        target_config = "{}/resources/target-config.json".format(os.path.dirname(__file__))
        tap_inheritable_config = "{}/resources/tap-inheritable-config.json".format(os.path.dirname(__file__))

        # The merged JSON written into a temp file
        temp_file = self.pipelinewise.create_consumable_target_config(target_config, tap_inheritable_config)
        cons_targ_config = cli.utils.load_json(temp_file)

        # The merged object needs
        assert cons_targ_config == {
            "account": "foo",
            "aws_access_key_id": "secret",
            "aws_secret_access_key": "secret/",
            "client_side_encryption_master_key": "secret=",
            "dbname": "my_db",
            "file_format": "my_file_format",
            "password": "secret",
            "s3_bucket": "foo",
            "s3_key_prefix": "foo/",
            "stage": "my_stage",
            "user": "user",
            "warehouse": "MY_WAREHOUSE",
            "batch_size_rows": 5000,
            "data_flattening_max_level": 0,
            "default_target_schema": "jira_clear",
            "default_target_schema_select_permissions": [
                "grp_power"
            ],
            "hard_delete": True,
            "primary_key_required": True,
            "schema_mapping": {
                "jira": {
                    "target_schema": "jira_clear",
                    "target_schema_select_permissions": [
                        "grp_power"
                    ]
                }
            }
        }

        # Remove temp file with merged JSON
        os.remove(temp_file)


    def test_invalid_create_consumable_target_config(self):
        """Test merging invalid target config.json and inheritable_config.json"""
        target_config = "{}/resources/invalid.json".format(os.path.dirname(__file__))
        tap_inheritable_config = "not-existing-json"

        # Merging invalid or not existing JSONs should raise exception
        with pytest.raises(Exception):
            self.pipelinewise.create_consumable_target_config(target_config, tap_inheritable_config)


    def test_command_encrypt_string(self, capsys):
        """Test vault encryption command output"""
        secret_path = "{}/resources/vault-secret.txt".format(os.path.dirname(__file__))

        args = CliArgs(string="plain text", secret=secret_path)
        pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

        # Encrypted string should be printed to stdout
        pipelinewise.encrypt_string()
        stdout, stderr = capsys.readouterr()
        assert not stderr.strip()
        assert stdout.startswith("!vault |") and "$ANSIBLE_VAULT;" in stdout


    def test_command_init(self):
        """Test init command"""
        args = CliArgs(name=TEST_PROJECT_NAME)
        pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

        # Init new project
        pipelinewise.init()

        # The test project should contain every sample YAML file
        for s in os.listdir("{}/../../../pipelinewise/cli/samples".format(os.path.dirname(__file__))):
            assert os.path.isfile(os.path.join(TEST_PROJECT_DIR, s))

        # Re-creating project should reaise exception of directory not empty
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            pipelinewise.init()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


    def test_command_status(self, capsys):
        """Test status command output"""
        # Status table should be printed to stdout
        self.pipelinewise.status()
        stdout, stderr = capsys.readouterr()
        assert not stderr.strip()

        # Exact output match
        assert stdout == """Tap ID     Tap Type      Target ID    Target Type       Enabled    Status          Last Sync    Last Sync Result
---------  ------------  -----------  ----------------  ---------  --------------  -----------  ------------------
tap_one    tap-mysql     target_one   target-snowflake  True       ready                        unknown
tap_two    tap-postgres  target_one   target-snowflake  True       ready                        unknown
tap_three  tap-mysql     target_two   target-s3-csv     True       not-configured               unknown
3 pipeline(s)
"""

    def test_command_discover_tap(self, capsys):
        """Test discover tap command"""
        args = CliArgs(target="target_one", tap="tap_one")
        pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

        # Running discovery mode should detect the tap type and path to the connector
        # Since the executable is not available in this test then it should fail
        pipelinewise.discover_tap()
        stdout, stderr = capsys.readouterr()

        exp_err_pattern = os.path.join(VIRTUALENVS_DIR, "/tap-mysql/bin/tap-mysql: No such file or directory")
        assert exp_err_pattern in stdout or exp_err_pattern in stderr


    def _test_command_run_tap(self, capsys):
        """Test run tap command"""
        args = CliArgs(target="target_one", tap="tap_one")
        pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

        # Running run mode should detect the tap type and path to the connector
        # Since the executable is not available in this test then it should fail
        # TODO: sync discover_tap and run_tap behaviour. run_tap sys.exit but discover_tap does not.
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            pipelinewise.run_tap()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


    def test_command_sync_tables(self, capsys):
        """Test run tap command"""
        args = CliArgs(target="target_one", tap="tap_one")
        pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

        # Running sync_tables should detect the tap type and path to the connector
        # Since the executable is not available in this test then it should fail
        # TODO: sync discover_tap and run_tap behaviour. run_tap sys.exit but discover_tap does not.
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            pipelinewise.sync_tables()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1


    def test_exit_gracefully(self):
        """Gracefully shoudl run tap command"""
        args = CliArgs(target="target_one", tap="tap_one")
        pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

        # Create a test log file, simulating a running tap
        pipelinewise.tap_run_log_file = "test-tap-run-dummy.log"
        Path("{}.running".format(pipelinewise.tap_run_log_file)).touch()

        # Graceful exit should return 1 by default
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            pipelinewise._exit_gracefully(signal.SIGINT, frame=None)
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 1

        # Graceful exit should rename log file from running status to terminated
        assert os.path.isfile("{}.terminated".format(pipelinewise.tap_run_log_file))

        # Delete test log file
        os.remove("{}.terminated".format(pipelinewise.tap_run_log_file))

    def test_validate_command(self):
        test_validate_command_dir = f'{os.path.dirname(__file__)}/resources/test_validate_command'

        test_cases = [
            {
                'dir': 'missing_replication_key_incremental',
                'exception': True
            },
            {
                'dir': 'missing_replication_key',
                'exception': False
            },
            {
                'dir': 'invalid_target',
                'exception': True
            }
        ]

        for test_case in test_cases:
            args = CliArgs(dir=f'{test_validate_command_dir}/{test_case["dir"]}')
            pipelinewise = PipelineWise(args, CONFIG_DIR, VIRTUALENVS_DIR)

            if test_case['exception']:
                with pytest.raises(SystemExit):
                    pipelinewise.validate()
            else:
                pipelinewise.validate()
