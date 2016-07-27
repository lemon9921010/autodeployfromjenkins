#!/usr/bin/env python
# encoding: utf-8
"""
@author: lnsh
@file: handler_deploy.py
@time: 2016/7/27 13:36
"""
from build_deploy_rollback import  HanderDeploy
import argparse

if __name__ == '__main__':
    URL = ''
    token = ''
    username = ''
    nginx_url = ''
    server = HanderDeploy(URL, username, token, nginx_url)

    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', help='build  a job,need jobname')
    parser.add_argument('-bd', '--buildd', help='build and deploy a job,need jobname')
    parser.add_argument('-d', '--deploy', help='deploy a job,need jobname')
    parser.add_argument('-r', '--rollback', help='rollback a host,need host ip')
    args = parser.parse_args()
    if args.build:
        server.build(args.build)
    if args.deploy:
        server.deploy(args.deploy)
    if args.rollback:
        server.rollback(args.rollback)
    if args.buildd:
        if server.build(args.buildd):
           server.deploy(args.buildd)