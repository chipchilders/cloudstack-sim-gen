#!/usr/bin/env python

import os
import sys
import json

file_to_read = open('test_scenario.out', 'r')
input_json = json.loads(file_to_read.read())
file_to_read.close()

jt = "var memory = "
data = []

for datapoint in input_json["datapoints"]:
    dataline = []
    for host in datapoint["hosts"]:
        ram = float(host["memorytotal"])
        usedram = float(host["memoryallocated"])
        percentram = int(round((usedram/ram)*100))
        dataline.append({"server": host["name"], "value": percentram})
    data.append(dataline)

jt += json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

jt += ";\n"


jt += "var cpu = "
data = []

for datapoint in input_json["datapoints"]:
    dataline = []
    for host in datapoint["hosts"]:
        dataline.append({"server": host["name"], "value": int(host["cpuallocated"].replace('%', ''))})
    data.append(dataline)

jt += json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))

jt += ";\n"

file_to_write = open('test_scenario_out.json', 'w')
file_to_write.truncate()
file_to_write.write(jt)
file_to_write.close()
