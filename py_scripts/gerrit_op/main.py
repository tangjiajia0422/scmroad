#!/usr/bin/env python
# _*_ coding=utf-8 _*_

import http_gerrit_query
import ssh_gerrit_query
import write2csv

a = http_gerrit_query.http_gerrit_query()._query()
b = ssh_gerrit_query.ssh_gerrit_query()._query(a)
write2csv.write2csv().write(b)
