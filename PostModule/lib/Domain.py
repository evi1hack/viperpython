# -*- coding: utf-8 -*-
# @File  : Domain.py
# @Date  : 2019/3/27
# @Desc  :

import json
import re

from Core.lib import logger
from PostModule.lib.MsfModule import MsfModule


class Domain(object):
    def __init__(self, sessionid):
        self._sessionid = sessionid

    def _deal_powershell_json_result(self, result):
        result_without_error = re.sub('ERROR:.+\s', '', result)
        result_without_empty = result_without_error.replace('\r', '').replace('\n', '').replace('\t', '')
        try:
            result_json = json.loads(result_without_empty)
            return result_json
        except Exception as E:
            logger.warning(E)
            logger.warning("解析powershell结果失败")
            return None

    def get_domain_controller(self):
        type = 'post'
        mname = 'windows/manage/powershell/exec_powershell_function_mem'
        opts = {
            'SESSION': self._sessionid,
            'SCRIPT': 'PowerView_dev.ps1',
            'EXECUTE_STRING': 'Get-DomainController',
            'CHECK_FUNCTION': False,
        }
        result = MsfModule.run_with_output(type, mname, opts)
        return self._deal_powershell_json_result(result)

    def get_group_member(self, group):
        type = 'post'
        mname = 'windows/manage/powershell/exec_powershell_function_mem'
        opts = {
            'SESSION': self._sessionid,
            'SCRIPT': 'PowerView_dev.ps1',
            'EXECUTE_STRING': ' \'{}\' | Get-DomainGroupMember'.format(group),
            'CHECK_FUNCTION': False,
        }
        result = MsfModule.run_with_output(type, mname, opts)
        try:
            result_json = json.loads(result.replace('\r', '').replace('\n', '').replace('\t', ''))
            return result_json
        except Exception as E:
            logger.warning(E)
            return None

    def find_local_admin_access(self):
        type = 'post'
        mname = 'windows/manage/powershell/exec_powershell_function_mem'
        opts = {
            'SESSION': self._sessionid,
            'SCRIPT': 'PowerView_dev.ps1',
            'EXECUTE_STRING': 'Find-LocalAdminAccess -Delay 1',
            'CHECK_FUNCTION': False,
        }
        result = MsfModule.run_with_output(type, mname, opts)
        try:
            result_json = json.loads(result.replace('\r', '').replace('\n', '').replace('\t', ''))
            return result_json
        except Exception as E:
            logger.warning(E)
            return None

    def get_domain_computers(self):
        type = 'post'
        mname = 'windows/manage/powershell/exec_powershell_function_mem'
        opts = {
            'SESSION': self._sessionid,
            'SCRIPT': 'PowerView_dev.ps1',
            'EXECUTE_STRING': 'Get-DomainComputer |select-object name,distinguishedname,operatingsystem,dnshostname | ConvertTo-Json -maxDepth 2',
            'CHECK_FUNCTION': False,
        }
        result = MsfModule.run_with_output(type, mname, opts)
        computers = self._deal_powershell_json_result(result)
        ipaddresses = self.get_computers_ipaddress()
        if computers is None:
            computers = []
        if ipaddresses is None:
            ipaddresses = []
        for computer in computers:
            for ipaddress in ipaddresses:
                if ipaddress.get('ComputerName') == computer.get('dnshostname'):
                    if computer.get('ipaddress') is None:
                        computer['ipaddress'] = [ipaddress.get('IPAddress')]
                    else:
                        computer['ipaddress'].append(ipaddress.get('IPAddress'))

        return computers

    def get_computers_ipaddress(self):

        type = 'post'
        mname = 'windows/manage/powershell/exec_powershell_function_mem'
        opts = {
            'SESSION': self._sessionid,
            'SCRIPT': 'PowerView_dev.ps1',
            'EXECUTE_STRING': 'Get-DomainComputer | select-object dnshostname | Resolve-IPAddress | ConvertTo-JSON',
            'CHECK_FUNCTION': False,
        }
        result = MsfModule.run_with_output(type, mname, opts)
        return self._deal_powershell_json_result(result)

    def get_domain_users(self):
        type = 'post'
        mname = 'windows/manage/powershell/exec_powershell_function_mem'
        opts = {
            'SESSION': self._sessionid,
            'SCRIPT': 'PowerView_dev.ps1',
            'EXECUTE_STRING': 'Get-DomainUser',
            'CHECK_FUNCTION': False,
        }
        result = MsfModule.run_with_output(type, mname, opts)
        return self._deal_powershell_json_result(result)
