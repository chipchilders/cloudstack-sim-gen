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
        cap[capacity["type"]] = {'percentused': capacity["percentused"], 'capacityused': capacity["capacityused"]}
    caps.append(cap)


mempercent = {"key": "Percentage Memory Allocated", "bar": True, "values": []}
memtotal = {"key": "Allocated Memory", "values": [] }
cpupercent = {"key": "Percentage CPU Allocated", "bar": True, "values": []}
cputotal = {"key": "Allocated CPU", "values": [] }
vmcount = 1
for cap in caps:
    mempercent["values"].append([vmcount, cap[0]["percentused"]])
    memtotal["values"].append([vmcount, cap[0]["capacityused"]])
    cpupercent["values"].append([vmcount, cap[1]["percentused"]])
    cputotal["values"].append([vmcount, cap[1]["capacityused"]])
    vmcount += 1

jt = "var memdata = [ \n"
jt += json.dumps(mempercent, sort_keys=True, indent=4, separators=(',', ': '))
jt += ", \n"
jt += json.dumps(memtotal, sort_keys=True, indent=4, separators=(',', ': '))
jt += "\n].map(function(series) { \n series.values = series.values.map(function(d) { return {x: d[0], y: d[1] } });\n return series;\n });"

jt += "var cpudata = [ \n"
jt += json.dumps(cpupercent, sort_keys=True, indent=4, separators=(',', ': '))
jt += ", \n"
jt += json.dumps(cputotal, sort_keys=True, indent=4, separators=(',', ': '))
jt += "\n].map(function(series) { \n series.values = series.values.map(function(d) { return {x: d[0], y: d[1] } });\n return series;\n });"

file_to_write = open('/Users/chip.childers/charting-cloudstack-planners/foo.json', 'w')
file_to_write.truncate()
file_to_write.write(jt)
file_to_write.close()
