#!/usr/bin/env python

import os
import sys
from optparse import OptionParser
import random
import json
import inspect
import uuid

# Testing

def main():
    usage = "usage: %prog [options] INPUTFILE"
    parser = OptionParser(usage)
    parser.add_option("-o", "--out", 
                  action="store",
                  type="string",
                  dest="outputfilename",
                  metavar="OUTPUTFILE",
                  help="File name for the simulation definition output.  If not supplied, the results will be output to stdout.")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")

    inputfilename = args[0]
    
    if options.outputfilename is not None:
        outputfilename = options.outputfilename
    else:
        outputfilename = "stdout"

    returncode = create_scenario(inputfilename, outputfilename)

    exit(returncode)


def create_scenario(inputfilename, outputfilename):

    input_json_file = open(inputfilename, 'r')
    input_json = json.loads(input_json_file.read())
    input_json_file.close()

    output = {}

    scenario_vms = []

    try:
        check_required_data(input_json)
    except Exception as inex:
        print inex
        return 1

#    print "Planning scenario for %s days using %s accounts (dispersion of %s), %s offerings (dispersion of %s), and a growth function of %s" % (
#        input_json["number_of_days"], 
#        len(input_json["accounts"]), 
#        input_json["account_dispersion"], 
#        len(input_json["service_offerings"]), 
#        input_json["offering_dispersion"], 
#        input_json["vm_growth"])

    day = 1
    output["accounts"] = input_json["accounts"]
    output["service_offerings"] = input_json["service_offerings"]
    output["capacity_increase_rules"] = input_json["capacity_increase_rules"]
    output["days"] = []

    while day < input_json["number_of_days"]+1:
        planned_day, scenario_vms = plan_day(day, input_json, scenario_vms)
        output["days"].append(planned_day)
        day+=1

    if outputfilename == "stdout":
        print json.dumps(output, sort_keys=True, indent=4, separators=(',', ': '))
    else:
        file_to_write = open(outputfilename, 'w')
        file_to_write.truncate()
        file_to_write.write(json.dumps(output, sort_keys=True, indent=4, separators=(',', ': ')))
        file_to_write.close()

    return 0

def plan_day(day, input_json, scenario_vms):
    day_definition = { "day": day }
    day_definition["newvms"] = []
    day_definition["removedvms"] = []

    x = day
    num_vms_to_add_for_day = int(round(eval(input_json["vm_growth"]), 0))
    num_vms_to_remove_for_day = int(round(eval(input_json["vm_decline"]), 0))

    i = 1
    while i <= num_vms_to_add_for_day:
        account_for_vm = weighted_choice(input_json["account_dispersion"])
        service_offering_for_vm = weighted_choice(input_json["offering_dispersion"])
        newvm = { 
            "account": input_json["accounts"][account_for_vm]["username"], 
            "service_offering": input_json["service_offerings"][service_offering_for_vm]["name"], 
            "vm_scenario_uuid": str(uuid.uuid4())
            }
        day_definition["newvms"].append(newvm)
        scenario_vms.append(newvm["vm_scenario_uuid"])
        i+=1

    i = 1
    while i <= num_vms_to_remove_for_day:
        if len(scenario_vms) > 0:
            vm_to_remove = random.sample(scenario_vms, 1)
            scenario_vms = list(set(scenario_vms).difference(set(vm_to_remove)))
            day_definition["removedvms"].append(vm_to_remove[0])
        i+=1

    return day_definition, scenario_vms

# Cargo Cult fun with the function below (from http://eli.thegreenplace.net/2010/01/22/weighted-random-generation-in-python/)
def weighted_choice(weights):
    totals = []
    running_total = 0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random() * running_total
    for i, total in enumerate(totals):
        if rnd < total:
            return i

def check_required_data(inputobj):
    check_specific_param(inputobj, 'number_of_days')
    check_specific_param(inputobj, 'vm_growth')
    check_specific_param(inputobj, 'offering_dispersion')
    check_specific_param(inputobj, 'account_dispersion')
    check_specific_param(inputobj, 'accounts')
    check_specific_param(inputobj, 'service_offerings')

def check_specific_param(inputobj, param_name):
    if not param_name in inputobj:
        raise Exception(param_name + ' not specified')


if __name__ == "__main__":
    main()