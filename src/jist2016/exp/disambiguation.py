# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Shengjia Yan
# Date: 2017/3/3
# Email: sjyan@seu.edu.cn
# 实验的第三步：单知识库候选实体消岐

import Levenshtein
import copy
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import os
import json
from table import *


class EntityDisambiguationGraph(object):
    # table: 第i张表格
    # candidates: 第i张表格中 mentions 的候选实体
    def __init__(self, table_number, table, candidates, graph_path):
        self.table_number = table_number
        self.table = table
        self.mention_quantity = table.mention_quantity
        self.row_num = table.row_num
        self.col_num = table.col_num
        self.candidates = candidates
        self.EDG = nx.Graph(number=str(table_number))       # 完整的 EDG
        self.miniEDG = nx.Graph(number=str(table_number))   # 移除 entity-entity edge 的 EDG
        self.graph_path = graph_path

    # mNode: mention node
    # eNode: entity node
    # meEdge: mention-entity edge
    # eeEdge: entity-entity edge
    def create_entity_disambiguation_graph(self):
        EDG = self.EDG
        table = self.table
        candidates = self.candidates
        nRow = self.row_num
        nCol = self.col_num
        i = self.table_number
        mention_quantity = self.mention_quantity
        mention_node_initial_importance = float(1)/mention_quantity

        # mention node 从 1 开始编号，编号范围为 [1, mention_quantity]
        mention_counter = 1
        mention_low = 1
        mention_high = mention_quantity

        # entity node 从 mention_quantity + 1 开始编号，这样可以将 mention node 和 entity node 的编号区分开
        entity_counter = mention_quantity + 1
        entity_low = mention_quantity + 1
        entity_high = 0


        # 逐行逐列遍历一张表格中的每个单元格
        # i: table number
        # j: row number
        # k: column number
        for j in range(nRow):
            if j == 0:  # 表头不作为 EDG 中的节点
                continue

            for k in range(nCol):
                mention = table.get_cell(j, k)
                mention_candidates = candidates[j][k]['candidates']
                candidates_quantity = len(mention_candidates)
                entity_index = 0

                if candidates_quantity == 0:
                    flag_NIL = True
                else:
                    flag_NIL = False

                # 在 EDG 中添加 mention node
                EDG.add_node(mention_counter, type='mNode', mention=mention, NIL=flag_NIL, table=i, row=j, column=k, probability=float(mention_node_initial_importance))
                EDG.node[mention_counter]['label'] = 'mention: ' + EDG.node[mention_counter]['mention'] + '\n' + str(EDG.node[mention_counter]['probability'])

                if flag_NIL == False:
                    # 在 EDG 中添加 entity node
                    for candidate in mention_candidates:
                        EDG.add_node(entity_counter, type='eNode', candidate=candidate, table=i, row=j, column=k, index=entity_index, probability=float(0))
                        EDG.node[entity_counter]['label'] = 'candidate: ' + EDG.node[entity_counter]['candidate'] + '\n' + str(EDG.node[entity_counter]['probability'])

                        # 在 EDG 中添加 mention-entity edge
                        EDG.add_edge(mention_counter, entity_counter, type='meEdge', probability=float(0))
                        EDG.edge[mention_counter][entity_counter]['label'] = str(EDG.edge[mention_counter][entity_counter]['probability'])

                        entity_index += 1
                        entity_counter += 1

                mention_counter += 1

        entity_high = entity_counter - 1

        self.miniEDG = copy.deepcopy(EDG)

        # 在 EDG 中添加 entity-entity edge
        for p in range(entity_low, entity_high+1):
            for q in range(entity_low, entity_high+1):
                if p < q:
                    EDG.add_edge(p, q, type='eeEdge', probability=float(0))
                    EDG.edge[p][q]['label'] = str(EDG.edge[p][q]['probability'])

        self.EDG = EDG
        return EDG

    # 画出来的 EDG 是不包含 entity-entity edge 的，因为如果要包含的话时间开销太大了
    def draw_entity_disambiguation_graph(self):
        graph_name = self.graph_path + 'edg' + str(self.table_number)
        write_dot(self.miniEDG, graph_name + '.dot')
        os.system('dot -Tsvg ' + graph_name + '.dot' + ' -o ' + graph_name + '.svg')

    def compute_el_impact_factors(self):
        print

    def iterative_probability_propagation(self):
        print





class Disambiguation(object):
    # table_name: 表格文件的名称
    # table_path: 表格文件的路径
    # kb_name: 知识库的名称
    # candidate_name: 候选实体文件的名称
    # candidate_path: 候选实体文件的路径
    # graph_path: Entity Disambiguation Graph 存储路径
    # output_path: 消岐结果文件的路径
    def __init__(self, table_name, table_path, kb_name, candidate_name, candidate_path, graph_path, output_path):
        table_manager = TableManager(table_path)
        self.tables = table_manager.get_tables()  # tables[i][j][k]: 第i张表第j行第k列的单元格中的字符串
        self.table_name = table_name
        self.table_path = table_path
        self.table_quantity = table_manager.table_quantity
        self.kb_name = kb_name
        self.candidate_name = candidate_name
        self.candidate_path = candidate_path
        self.graph_path = graph_path
        self.output_path = output_path

    def disambiguation(self):
        # # baidubaike
        # if self.kb_name == "baidubaike":
        #     try:
        #
        #     finally:
        #
        #
        # # hudongbaike
        # if self.kb_name == "hudongbaike":
        #     try:
        #
        #     finally:


        # zhwiki
        if self.kb_name == "zhwiki":
            try:
                tables = self.tables
                graph_path = self.graph_path
                zhwiki_candidate_file = open(self.candidate_path, 'r')
                zhwiki_candidate = zhwiki_candidate_file.read()
                zhwiki_candidate_json = json.loads(zhwiki_candidate, encoding='utf8')    # kb_candidate[nTable][nRow][nCol] = dict{'mention': m, 'candidates': []}
                zhwiki_disambiguation = open(self.output_path, 'w')

                # (a) 为每张表格生成其 Entity Disambiguation Graph
                # i: 第i张表格，从0开始
                for i in range(self.table_quantity):
                    table = tables[i]
                    candidates = zhwiki_candidate_json[i]

                    # 为表格中的 mention 及其 candidate entities 构建 Entity Disambiguation Graph
                    EDG_master = EntityDisambiguationGraph(i, table, candidates, graph_path)
                    EDG = EDG_master.create_entity_disambiguation_graph()
                    EDG_master.draw_entity_disambiguation_graph()
                    break

                # (b) 基于构建好的 Entity Disambiguation Graph，计算 EL impact factors:
                # 1. node 上的概率值：mention node 的初始权重值。entity node 上的概率值在下一步中计算
                # 2. edge 上的概率值：不同节点间的语义相似度。有2种边，mention-entity edge 和 entity-entity edge



                # isRDF() 在 kb_infobox_properties.nt 中做

                # (c) Iterative Probability Propagation
                # 计算 entity node 上的概率（该 entity 成为 mention 的对应实体的概率）



            finally:
                # zhwiki_disambiguation_json = json.dumps(zhwiki_mention_entity, ensure_ascii=False)
                # zhwiki_disambiguation.write(zhwiki_disambiguation_json)

                if zhwiki_candidate_file:
                    zhwiki_candidate_file.close()

                if zhwiki_disambiguation:
                    zhwiki_disambiguation.close()

