# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Shengjia Yan
# Date: 2017/3/3
# Email: sjyan@seu.edu.cn
# 实验的第一步：原始知识库数据预处理
# 从原始nt文件中抽取实体及其对应的url，并转码

class Preprocess(object):
    # kb_name: 知识库 label 文件的名称
    # kb_path: 知识库 label 文件的路径
    # kb_entity_quantity: 知识库中实体的数量
    # output_path: 处理好的实体以及url数据的输出路径
    def __init__(self, kb_name, kb_path, output_path):
        self.kb_name = kb_name
        self.kb_path = kb_path
        self.output_path = output_path
        self.kb_entity_quantity = 0

    def extract_entity(self):
        # baidubaike
        if self.kb_name == "baidubaike":
            try:
                baidubaike_labels = open(self.kb_path, 'r')
                baidubaike_entities = open(self.output_path, 'a')
                baidubaike_entity_counter = 0
                baidubaike_entity_sum = 4265127

                for rdf in baidubaike_labels.readlines():
                    baidubaike_entity_counter += 1
                    rdf = rdf.strip('\n')

                    # split
                    firstsplit = rdf.split('> <')
                    url = firstsplit[0]
                    rdf_entity = firstsplit[1]

                    secondsplit = rdf_entity.split('> "')
                    entity = secondsplit[1]

                    # clean
                    url = url[1:]
                    entity = entity[:-7]
                    entity = entity.replace('\'', '')

                    # convert entity
                    entity = eval("u'%s'" %(entity)).encode('utf8')

                    entity_url = '<' + entity + '> <' + url + '>\n'

                    baidubaike_entities.write(entity_url)

            finally:
                print 'baidubaike entity counter: ' + str(baidubaike_entity_counter)
                self.kb_entity_quantity = baidubaike_entity_counter

                if baidubaike_labels:
                    baidubaike_labels.close()

                if baidubaike_entities:
                    baidubaike_entities.close()


        # hudongbaike
        if self.kb_name == "hudongbaike":
            try:
                hudongbaike_labels = open(self.kb_path, 'r')
                hudongbaike_entities = open(self.output_path, 'a')
                hudongbaike_entity_counter = 0
                hudongbaike_entity_sum = 3299288

                for rdf in hudongbaike_labels.readlines():
                    hudongbaike_entity_counter += 1
                    rdf = rdf.strip('\n')

                    # split
                    firstsplit = rdf.split('> <')
                    url = firstsplit[0]
                    rdf_entity = firstsplit[1]

                    secondsplit = rdf_entity.split('> "')
                    entity = secondsplit[1]

                    # clean
                    url = url[1:]
                    entity = entity[:-7]
                    entity = entity.replace('\'', '')

                    # convert entity
                    entity = eval("u'%s'" % (entity)).encode('utf8')

                    entity_url = '<' + entity + '> <' + url + '>\n'
                    hudongbaike_entities.write(entity_url)

            finally:
                print 'hudongbaike entity counter: ' + str(hudongbaike_entity_counter)
                self.kb_entity_quantity = hudongbaike_entity_counter

                if hudongbaike_labels:
                    hudongbaike_labels.close()

                if hudongbaike_entities:
                    hudongbaike_entities.close()


        # zhwiki
        if self.kb_name == "zhwiki":
            try:
                zhwiki_labels = open(self.kb_path, 'r')
                zhwiki_entities = open(self.output_path, 'a')
                zhwiki_entity_counter = 0
                zhwiki_entity_sum = 830734

                for rdf in zhwiki_labels.readlines():
                    zhwiki_entity_counter += 1
                    rdf = rdf.strip('\n')

                    # split
                    firstsplit = rdf.split('> <')
                    url = firstsplit[0]
                    rdf_entity = firstsplit[1]

                    secondsplit = rdf_entity.split('> "')
                    entity = secondsplit[1]

                    # clean
                    url = url[1:]
                    entity = entity[:-6]
                    entity = entity.replace('\'', '')

                    # convert entity
                    entity = eval("u'%s'" %(entity)).encode('utf8')

                    entity_url = '<' + entity + '> <' + url + '>\n'
                    zhwiki_entities.write(entity_url)

            finally:
                print 'zhwiki entity counter: ' + str(zhwiki_entity_counter)
                self.kb_entity_quantity = zhwiki_entity_counter

                if zhwiki_labels:
                    zhwiki_labels.close()

                if zhwiki_entities:
                    zhwiki_entities.close()







    

