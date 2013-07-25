#!/usr/bin/env python

import os
import sys
import json

file_to_read = open('test_scenario.out', 'r')
input_json = json.loads(file_to_read.read())
file_to_read.close()

caps = []
for datapoint in input_json["datapoints"]:
    cap = [0,0,0,0,0,0,0,0,0,0]
    for capacity in datapoint["zone"]["capacity"]:
        cap[capacity["type"]] = {'capacitytotal': capacity["capacitytotal"], 'percentused': capacity["percentused"]}
    caps.append(cap)


jt = ""
for cap in caps:
    jt += str(cap[0]["capacitytotal"]) + ","
    jt += str(cap[0]["percentused"]) + ","
    jt += str(cap[1]["capacitytotal"]) + ","
    jt += str(cap[1]["percentused"]) + ""
    jt += "\n"

file_to_write = open('foo.csv', 'w')
file_to_write.truncate()
file_to_write.write(jt)
file_to_write.close()
