#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import utils, json, os, csv

class write2csv:
    def __init__(self):
        self.utils = utils.utils()

    def write(self, query_result_json_dict_list):
        print 'Starting to write to csv files >>> '
        csv_file_name = 'gerrit_list_%s.csv' % (self.utils.readable_today())
        csvfile = file(csv_file_name, 'wb')
        csvwriter = csv.writer(csvfile, delimiter = ',')
        _csv_header = self.utils.get_csv_head()
        csvwriter.writerow(_csv_header)
        for _json_dict in query_result_json_dict_list:
            _result = self.utils.items_result(_json_dict)
            #print _result
            csvwriter.writerow(_result)




