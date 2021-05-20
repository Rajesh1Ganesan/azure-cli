# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import getopt
import uuid
import sys
from knack.log import get_logger

from datetime import datetime
from time import sleep
from dateutil.tz import tzutc  # pylint: disable=import-error
from azure_devtools.scenario_tests import AllowLargeResponse
from msrestazure.azure_exceptions import CloudError
from azure.cli.core.util import CLIError
from azure.cli.core.util import parse_proxy_resource_id
from azure.cli.testsdk.base import execute
from azure.cli.testsdk.exceptions import CliTestError  # pylint: disable=unused-import
from azure.cli.testsdk import (
    JMESPathCheck,
    NoneCheck,
    ResourceGroupPreparer,
    ScenarioTest,
    StringContainCheck,
    live_only)
from azure.cli.testsdk.preparers import (
    AbstractPreparer,
    SingleValueReplacer)

logger = get_logger(__name__)


class MigrationScenarioTest(ScenarioTest):

    @AllowLargeResponse()
    def test_postgres_server_migration(self):
        self._test_server_migration('postgres')

    def _test_server_migration(self, database_engine):
        # Set this to True or False depending on whether we are in live mode or test mode
        # livemode = True
        livemode = False

        if livemode:
            # Live mode values
            target_subscription_id = "6a37df99-a9de-48c4-91e5-7e6ab00b2362"
            migration_id = str(uuid.uuid4())
        else:
            # Mock test mode values
            target_subscription_id = "00000000-0000-0000-0000-000000000000"
            migration_id = "00000000-0000-0000-0000-000000000000"

        target_resource_group_name = "raganesa-t-m-pg-1"
        target_server_name = "raganesa-t-m-pg-1-vnet"

        # # test create migration - error - no param
        # result = self.cmd('{} flexible-server migration create'
        #                   .format(database_engine), expect_failure=True)

        # # test create migration - error - no sub
        # result = self.cmd('{} flexible-server migration create --resource-group {} --name {} --body @migrationPublic.json'
        #                   .format(database_engine, target_resource_group_name, target_server_name), expect_failure=True)

        # # test create migration - error - no resource-group
        # result = self.cmd('{} flexible-server migration create --subscription-id {} --name {} --body @migrationPublic.json'
        #                   .format(database_engine, target_subscription_id, target_server_name), expect_failure=True)

        # # test create migration - error - no server name
        # result = self.cmd('{} flexible-server migration create --subscription-id {} --resource-group {} --body @migrationPublic.json'
        #                   .format(database_engine, target_subscription_id, target_resource_group_name), expect_failure=True)

        # # test create migration - error - no body
        # result = self.cmd('{} flexible-server migration create --subscription-id {} --resource-group {} --name {}'
        #                   .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name), expect_failure=True)

        # test create migration - success
        result = self.cmd('{} flexible-server migration create --subscription-id {} --resource-group {} --name {} --migration-id {} --body @migrationVNet.json'
                          .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name, migration_id)).get_output_in_json()

        migration_id = result['name']

        # test list migrations - success, with filter
        result = self.cmd('{} flexible-server migration list --subscription-id {} --resource-group {} --name {} --filter Active'
                          .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name)).get_output_in_json()

        # test list migrations - success, without filter
        result = self.cmd('{} flexible-server migration list --subscription-id {} --resource-group {} --name {}'
                          .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name)).get_output_in_json()

        # test show migration - success
        result = self.cmd('{} flexible-server migration show --subscription-id {} --resource-group {} --name {} --migration-id {}'
                          .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name, migration_id)).get_output_in_json()

        # test update migration - error - no param
        result = self.cmd('{} flexible-server migration update --subscription-id {} --resource-group {} --name {} --migration-id {}'
                          .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name, migration_id), expect_failure=True)

        # test delete migration - success
        result = self.cmd('{} flexible-server migration delete --subscription-id {} --resource-group {} --name {} --migration-id {}'
                          .format(database_engine, target_subscription_id, target_resource_group_name, target_server_name, migration_id)).get_output_in_json()
