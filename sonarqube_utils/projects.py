#!/usr/bin/env python
#-*- coding:utf-8 -*-
from .config import *

class SonarQubeProject(object):
    def __init__(self, sonarqube):
        self.sonarqube = sonarqube
        self._data = None

    def poll(self, filter=None):
        self._data = self.get_projects_data(filter)

    def iterkeys(self):
        """
        获取所有项目的key，返回生成器
        """
        self.poll()
        for item in self._data:
            yield item['key']

    def keys(self):
        """
        获取所有项目的key，返回列表
        """
        return list(self.iterkeys())

    def __len__(self):
        """
        获取项目
        :return:
        """
        return len(self.keys())

    def __contains__(self, project_key):
        """
        判断项目是否存在
        """
        self.poll(filter=project_key)
        project_keys = [item['key'] for item in self._data]
        return project_key in project_keys

    def __getitem__(self, index):
        """
        根据坐标获取项目信息
        :param index:
        :return:
        """
        self.poll()
        return list(self._data)[index]

    def __iter__(self):
        """
        实现迭代
        :return:
        """
        self.poll()
        return self._data

    def get_projects_data(self, filter=None):
        """
        获取所有项目信息
        :param filter:
        :return:
        """
        params = {}
        page_num = 1
        page_size = 1
        total = 2

        if filter is not None:
            params['q'] = filter

        while page_num * page_size < total:
            resp = self.sonarqube._make_call('get', RULES_PROJECTS_SEARCH_ENDPOINT, **params)
            response = resp.json()

            page_num = response['paging']['pageIndex']
            page_size = response['paging']['pageSize']
            total = response['paging']['total']

            params['p'] = page_num + 1

            for component in response['components']:
                yield component

    def create_project(self, key, name, branch=None):
        """
        创建项目
        :param key:
        :param name:
        :param branch:
        :return:
        """
        params = {
            'name': name,
            'project': key
        }
        if branch:
            params['branch'] = branch

        self.sonarqube._make_call('post', RULES_PROJECTS_CREATE_ENDPOINT, **params)

    def get_project_id(self, project_key):
        """
        获取指定项目的id
        :param project_key:
        :return:
        """
        result = self.get_projects_data(filter=project_key)
        id = [item['id'] for item in result]
        return id

    def delete_project(self, project_key):
        """
        删除项目
        :param project_key:
        :return:
        """
        params = {
            'project': project_key
        }
        self.sonarqube._make_call('post', RULES_PROJECTS_DELETE_ENDPOINT, **params)

    def update_project_key(self, previous_project_key, new_project_key):
        """
        更新项目key
        :param previous_project_key:
        :param new_project_key:
        :return:
        """
        params = {
            'from': previous_project_key,
            'to': new_project_key
        }
        self.sonarqube._make_call('post',RULES_PROJECTS_UPDATE_KEY_ENDPOINT,**params)

    def update_project_visibility(self, project_key, visibility):
        """
        更新项目可视状态('public','private')
        :param project_key:
        :param visibility:
        :return:
        """
        params = {
            'project': project_key,
            'visibility': visibility
        }
        self.sonarqube._make_call('post', RULES_PROJECTS_UPDATE_VISIBILITY_ENDPOINT, **params)