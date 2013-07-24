# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from marvin.cloudstackTestCase import cloudstackTestCase
from marvin.integration.lib.base import Account, VirtualMachine, ServiceOffering, Host, Cluster
from marvin.integration.lib.common import get_zone, get_domain, get_template, cleanup_resources
import json
import os
import sys
import pprint

from nose.plugins.attrib import attr

class Services:

    def __init__(self):
        self.services = {
            "ostype": 'CentOS 5.3 (64-bit)',
            "virtual_machine": {
                "hypervisor": "XenServer",
            }
        }

        input_json_file = open('/home/sg-user/cloudstack-sim-gen/test_scenario.json', 'r')
        self.services["scenario"] = json.loads(input_json_file.read())
        input_json_file.close()



class TestScenario(cloudstackTestCase):
    """ Test scenario based on input json
    """


    def find_account(self, value_to_find):
        for account in self.accounts:
            if account.__dict__["name"].startswith(value_to_find + "-"):
                return account
        raise Exception("Couldn't find the account name.")

    def find_service_offering(self, value_to_find):
        for service_offering in self.service_offerings:
            if service_offering.name == value_to_find:
                return service_offering
        raise Exception("Couldn't find the service_offering name.")

    def setUp(self):
        self.pp = pprint.PrettyPrinter(indent=4, depth=6)

        self.apiclient = super(TestScenario, self).getClsTestClient().getApiClient()
        self.services = Services().services
        # Get Zone, Domain and templates
        self.domain = get_domain(self.apiclient, self.services)
        self.zone = get_zone(self.apiclient, self.services)
        self.template = get_template(
            self.apiclient,
            self.zone.id,
            self.services["ostype"]
        )

        self.accounts = []
        for account in self.services["scenario"]["accounts"]:
            self.accounts.append(self.CreateAccount(account))

        self.service_offerings = []
        for service_offering in self.services["scenario"]["service_offerings"]:
            self.service_offerings.append(self.CreateServiceOffering(service_offering))

        self.cleanup = [
        #    self.account
        ]

        self.file_to_write = open('/home/sg-user/cloudstack-sim-gen/test_scenario.out', 'w')
        self.file_to_write.truncate()


    def CreateAccount(self, account):
        return Account.create(
            self.apiclient,
            account,
            domainid=self.domain.id
        )

    def CreateServiceOffering(self, service_offering):
        return ServiceOffering.create(
            self.apiclient,
            service_offering
        )

    def GetStats(self):
        hosts_list = Host.list(self.apiclient)
        stats = {}
        statarr = []
        for host in hosts_list:
            if "cpuallocated" in host.__dict__:
                statarr.append({
                    "name": host.__dict__["name"],
                    "cpuwithoverprovisioning": host.__dict__["cpuwithoverprovisioning"],
                    "cpunumber": host.__dict__["cpunumber"],
                    "cpuallocated": host.__dict__["cpuallocated"],
                    "cpuused": host.__dict__["cpuused"],
                    "cpuspeed": host.__dict__["cpuspeed"],
                    "memorytotal": host.__dict__["memorytotal"],
                    "memoryused": host.__dict__["memoryused"],
                    "memoryallocated": host.__dict__["memoryallocated"]
                    })

        stats["statpoint"] = statarr

        self.file_to_write.write(json.dumps(stats, sort_keys=True, indent=4, separators=(',', ': ')))

    @attr(tags=["simulator", "advanced", "basic", "sg"])
    def test_runscenario(self):
        """Test to deploy vms using the defined scenario
        """

        for day in self.services["scenario"]["days"]:
            for newvm in day["newvms"]:
                self.CreateVM(newvm)
                self.GetStats()

    def CreateVM(self, newvm):

        virtual_machine = VirtualMachine.create(
            self.apiclient,
            self.services["virtual_machine"],
            zoneid=self.zone.id,
            domainid=self.domain.id,
            templateid=self.template.id,
            accountid=self.find_account(newvm["account"]).__dict__["name"],
            serviceofferingid=self.find_service_offering(newvm["service_offering"]).id
        )

        list_vms = VirtualMachine.list(self.apiclient, id=virtual_machine.id)
        self.debug(
            "Verify listVirtualMachines response for virtual machine: %s"\
            % virtual_machine.id
        )
        self.assertEqual(
            isinstance(list_vms, list),
            True,
            "List VM response was not a valid list"
        )
        self.assertNotEqual(
            len(list_vms),
            0,
            "List VM response was empty"
        )

        vm = list_vms[0]
        self.assertEqual(
            vm.state,
            "Running",
            msg="VM is not in Running state"
        )

    def tearDown(self):
        self.file_to_write.close()
        try:
            cleanup_resources(self.apiclient, self.cleanup)
        except Exception as e:
            raise Exception("Warning: Exception during cleanup : %s" % e)
