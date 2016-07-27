#!/usr/bin/env python
# encoding: utf-8
"""
@author: lnsh
@file: alter_backend_ip.py
@time: 2016/7/6 15:59
"""
import requests
import json

def divide(data_list, groups):
    """
    :param data_list: 带分组数组
    :param groups: 分组组数
    """
    length = len(data_list)
    if length == 1:
        return tuple(data_list)

    # 组数应该小于长度
    if groups > length:
        groups = length

    num_per_group = length // groups
    if num_per_group <= length % groups:
        num_per_group += 1

    slices = []
    start = 0
    for i in range(groups):
        end = start + num_per_group
        slices.append(slice(start, end))
        start = end
    # 最后一次切割应该到data的末尾
    slices[-1] = slice(start - num_per_group, length)
    return tuple([data_list[s] for s in slices])

###save a global ip list to add back
# requests.post(job_url,data='["10.201.10.133:3333", "111", "10s"]')
# print requests.delete(job_url,data="10.201.10.133")
class AlterBackendIp(object):
    def __init__(self, nginx_url, upstream_name):
        self.nginx_url = nginx_url
        self.upstream_name = upstream_name

    def get_upstream_list(self):
        # 判断长度，智能分组
        self.job_url = self.nginx_url + '/' + self.upstream_name
        rs = requests.get(self.job_url)
        upstream_list = json.loads(rs.text)
        return upstream_list

    def get_deploy_group(self):
        data_list = self.get_upstream_list()
        length = len(data_list)
        if length > 8 :
            return divide(data_list,length/3)
        else:
            return divide(data_list,2)

    def format_ip_for_playbook(self, upstream):
        return upstream[0].split(':')[0]

    # 判断结果
    def del_backendip(self, upstream_ip):

        rs = requests.delete(self.job_url, data=upstream_ip[0].split(':')[0])
        if upstream_ip not in self.get_upstream_list():
            return True
        else:
            return False

    # 判断结果
    def add_backendip(self, upstream_ip):

        rs = requests.post(self.job_url, data=json.dumps(upstream_ip))

if __name__ == '__main__':
    nginx_url = 'http://172.16.200.158:8000'
    job_name = 'yqt'
    server = AlterBackendIp(nginx_url, job_name)

    for upstream_entry in server.get_upstream_list():
        server.del_backendip(upstream_entry)
        print upstream_entry
        print server.get_upstream_list()
        if  upstream_entry not in server.get_upstream_list():
            print 'ok del'
        server.add_backendip(upstream_entry)
        if upstream_entry in server.get_upstream_list():
            print 'add ok'
    print server.get_upstream_list()