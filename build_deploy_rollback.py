#!/usr/bin/env python2.7
# encoding: utf-8
"""
@author: lnsh
@file: build_deploy_rollback.py.py
@time: 2016/6/29 10:34
"""

from  jenkinsapi_wrapper import JenkinsApiWrapper
from playbook_api import PlayBook
from build_job import Juser
from alter_backend_ip import AlterBackendIp


class HanderDeploy():
    '''
    Auto deploy a job handler class;
    Delpoy a job half ips by half ips;
    Need nginx upstream name is job name.
    '''

    def __init__(self, URL, username, token, nginxurl):
        self.URL = URL
        self.username = username
        self.token = token
        self.nginxurl = nginxurl

    def get_war_url(self, job_name):
        server = JenkinsApiWrapper(self.URL, self.username, self.token)
        war_url = server.get_job_war_url(job_name)
        return war_url

    # add ensure per step
    def deploy(self, job_name):
        server_nginx = AlterBackendIp(self.nginxurl, job_name)

        for upstream_list in server_nginx.get_deploy_group():
            # pass only one backend host
            war_url = self.get_war_url(job_name)
            extra_dict = {'url': war_url}
            for upstream_entry in upstream_list:
                extra_dict['host'] = server_nginx.format_ip_for_playbook(upstream_entry)
                deploy_ip = extra_dict['host']
                server_nginx.del_backendip(upstream_entry)
                if upstream_entry not in server_nginx.get_upstream_list():
                    server = PlayBook('d.yml', inventory="/etc/ansible/hosts", extra_vars=extra_dict)
                    # stats = server.run().summarize(job_ip[0])
                    # print "\n########{}\n######".format(server.run().summarize('172.16.200.157'))
                    # return stats dict like {'unreachable': 0, 'skipped': 0, 'ok': 8, 'changed': 7, 'failures': 0}
                    # 返回当前ansible 主机
                    # server.run()
                    pbrz = server.run().summarize(deploy_ip)
                    if pbrz['changed'] != 0 and pbrz['unreachable'] == 0 and pbrz['failures'] == 0:
                        server_nginx.add_backendip(upstream_entry)
                        if upstream_entry in server_nginx.get_upstream_list():
                            print 'Good deploy {}'.format(upstream_entry)
                        else:
                            print 'Add backendip error {}'.format(upstream_entry)
                            exit()
                    else:
                        server_nginx.add_backendip(upstream_entry)
                        print 'deploy error {}'.format(upstream_entry)
                        exit()
                else:
                    server_nginx.add_backendip(upstream_entry)
                    print 'Del backendip error {}'.format(upstream_entry)
                    exit()
                    # return result for script to do

    def rollback(self, job_ip):
        extra_dict = {}
        extra_dict['host'] = job_ip
        server = PlayBook('r.yml', inventory="/etc/ansible/hosts", extra_vars=extra_dict)
        print server.run()

    def build(self, job_name):
        server = Juser(self.URL, self.username, self.token)
        ##
        if server.build(job_name):
            print 'Good build. run script -d to deploy'
            return True
        else:
            print 'Bad build,please check!!!'
            return False
