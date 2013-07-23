#!/usr/bin/env python

import os
import sys
from optparse import OptionParser
import random
import json
import inspect

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

    output_json = ""

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
#        input_json["vm_dispersion"], 
#        input_json["vm_growth"])

    day = 1
    output_json += "{\n\t\"days\": [\n"
    while day < input_json["number_of_days"]+1:
        output_json += plan_day(day, input_json)
        day+=1
        if day == input_json["number_of_days"]+1:
            output_json += "\n"
        else:
            output_json += ",\n"

    output_json += "\t]\n}\n"

    if outputfilename == "stdout":
        print output_json
    else:
        file_to_write = open(outputfilename, 'w')
        file_to_write.truncate()
        file_to_write.write(output_json)
        file_to_write.close()

    return 0

def plan_day(day, input_json):
    day_definition = "\t\t{\n"
    day_definition += "\t\t\"day\": %s, \n\t\t\"newvms\": [\n" % day

    x = day
    num_vms_for_day = int(round(eval(input_json["vm_growth"]), 0))

    i = 1
    while i <= num_vms_for_day:
        account_for_vm = weighted_choice(input_json["account_dispersion"])
        #print "Account selected: %s" % input_json["accounts"][account_for_vm]["username"]
        service_offering_for_vm = weighted_choice(input_json["vm_dispersion"])
        #print "Service offering selected: %s" % input_json["service_offerings"][service_offering_for_vm]["name"]
        day_definition += "\t\t\t{\"account\": \"%s\", \"service_offering\": \"%s\"}" % (input_json["accounts"][account_for_vm]["username"], input_json["service_offerings"][service_offering_for_vm]["name"])
        i+=1
        if i > num_vms_for_day:
            day_definition += "\n"
        else:
            day_definition += ",\n"

    day_definition += "\t\t\t]\n\t\t}"
    return day_definition

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
    check_specific_param(inputobj, 'vm_dispersion')
    check_specific_param(inputobj, 'account_dispersion')
    check_specific_param(inputobj, 'accounts')
    check_specific_param(inputobj, 'service_offerings')

def check_specific_param(inputobj, param_name):
    if not param_name in inputobj:
        raise Exception(param_name + ' not specified')


if __name__ == "__main__":
    main()