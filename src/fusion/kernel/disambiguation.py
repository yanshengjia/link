# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Shengjia Yan
# Date: 2017/3/3
# Email: sjyan@seu.edu.cn
# 实验的第三步：候选实体融合消岐，将多知识库间的 SameAs 关系放进了实体消岐图的构建

import Levenshtein
import time
import copy
import networkx as nx
from networkx.drawing.nx_agraph import write_dot
import numpy as np
import os
import json
import jieba
from table import *


class EntityDisambiguationGraph(object):
    # table_number: 表格的编号，即为 i
    # table: 第i张表格，Table 类型对象
    # baidubaike_candidates: 当前表格中 mentions 的 baidubaike 候选实体
    # hudongbaike_candidates: 当前表格中 mentions 的 hudongbaike 候选实体
    # zhwiki_candidates: 当前表格中 mentions 的 zhwiki 候选实体
    # graph_path: EDG 图片输出路径前缀
    # edg_path: EDG 输出路径
    # baidubaike_infobox_property: baidubaike 的 infobox_property 文件，用于计算 IsRDF 特征和获取实体上下文
    # hudongbaike_infobox_property: hudongbaike 的 infobox_property 文件，用于计算 IsRDF 特征和获取实体上下文
    # zhwiki_infobox_property: zhwiki 的 infobox_property 文件，用于计算 IsRDF 特征和获取实体上下文
    # baidubaike_abstracts: baidubaike 的 abstracts 文件，用于获取实体的上下文
    # hudongbaike_abstracts: hudongbaike 的 abstracts 文件，用于获取实体的上下文
    # zhwiki_abstracts: zhwiki 的 abstracts 文件，用于获取实体的上下文
    # baidubaike_hudongbaike_sameas: baidubaike - hudongbaike SameAs 关系数据
    # hudongbaike_zhwiki_sameas: hudongbaike - zhwiki SameAs 关系数据
    # zhwiki_baidubaike_sameas: zhwiki - baidubaike SameAs 关系数据
    # disambiguation_result_path: 消岐结果输出路径
    # mention_quantity: 当前表格中的 mention 数量
    # row_num: 当前表格的行数
    # col_num: 当前表格的列数
    # EDG: 当前表格及其候选实体生成的完成的 EDG
    # miniEDG: 去除 entity-entity Edge 的 EDG，为了更快速地画图
    # mention_node_begin: mention node 编号的开始
    # mention_node_end: mention node 编号的结束
    # entitySet_node_begin: entitySet node 编号的开始
    # entitySet_node_end: entitySet node 编号的结束
    # node_quantity: 所有节点的总数
    # A: 概率转移列表
    # r: 消岐结果概率列表
    def __init__(self, table_number, table, baidubaike_candidates, hudongbaike_candidates, zhwiki_candidates, baidubaike_infobox_property, hudongbaike_infobox_property, zhwiki_infobox_property, baidubaike_abstracts, hudongbaike_abstracts, zhwiki_abstracts, baidubaike_hudongbaike_sameas, hudongbaike_zhwiki_sameas, zhwiki_baidubaike_sameas, graph_path, result_path):
        self.table_number = table_number
        self.table = table
        self.mention_quantity = table.mention_quantity
        self.row_num = table.row_num
        self.col_num = table.col_num
        self.baidubaike_candidates = baidubaike_candidates
        self.hudongbaike_candidates = hudongbaike_candidates
        self.zhwiki_candidates = zhwiki_candidates
        self.baidubaike_infobox_property = baidubaike_infobox_property
        self.hudongbaike_infobox_property = hudongbaike_infobox_property
        self.zhwiki_infobox_property = zhwiki_infobox_property
        self.baidubaike_abstracts = baidubaike_abstracts
        self.hudongbaike_abstracts = hudongbaike_abstracts
        self.zhwiki_abstracts = zhwiki_abstracts
        self.baidubaike_hudongbaike_sameas = baidubaike_hudongbaike_sameas
        self.hudongbaike_zhwiki_sameas = hudongbaike_zhwiki_sameas
        self.zhwiki_baidubaike_sameas = zhwiki_baidubaike_sameas
        self.EDG = nx.Graph(number=str(table_number))
        self.miniEDG = nx.Graph(number=str(table_number))
        self.graph_path = graph_path
        self.edg_path = graph_path + 'edg' + str(table_number) + '.txt'
        self.disambiguation_result_path = result_path + str(table_number) + '.txt'
        self.mention_node_begin = 0
        self.mention_node_end = self.mention_quantity - 1
        self.entitySet_node_begin = self.mention_quantity
        self.entitySet_node_end = 0
        self.node_quantity = 0
        self.A = []
        self.r = []
        self.damping_factor = 0.5
        self.iterations = 1000
        self.delta = 0.00001
        print 'Table ' + str(table_number)

    # 获取当前表格中一个 mention 的上下文，该 mention 位于第r行第c列，r与c都从0开始
    # r: mention 所处的行号
    # c: mention 所处的列号
    def get_mention_context(self, r, c):
        table = self.table
        mention_context = table.get_mention_context(r, c)
        return mention_context

    # 获取一个 entity e 的上下文，来自 abstract 和 infobox_property
    # e: entity 字符串
    # kb: entity 来自的知识库
    def get_entity_context(self, e, kb):
        entity_context = []

        # 从 infobox properties 中找实体的上下文
        if kb == 'baidubaike':
            infobox_property = self.baidubaike_infobox_property
        if kb == 'hudongbaike':
            infobox_property = self.hudongbaike_infobox_property
        if kb == 'zhwiki':
            infobox_property = self.zhwiki_infobox_property

        for rdf in infobox_property.readlines():
            rdf = rdf.strip('\n')

            # split
            split = rdf.split('> <')
            subject = split[0]
            object = split[2]

            # clean
            subject = subject[1:]
            object = object[:-1]

            if e == subject:
                object = object.decode('utf8')
                entity_context.append(object)

            if e == object:
                subject = subject.decode('utf8')
                entity_context.append(subject)

        # 从 abstracts 中找实体的上下文
        if kb == 'baidubaike':
            abstracts = self.baidubaike_abstracts
        if kb == 'hudongbaike':
            abstracts = self.hudongbaike_abstracts
        if kb == 'zhwiki':
            abstracts = self.zhwiki_abstracts

        seg_list = []

        for line in abstracts.readlines():
            line = line.strip('\n')

            # split
            split = line.split('> <')
            entity = split[0]
            abstract = split[1]

            # clean
            entity = entity[1:]
            abstract = abstract[:-1]

            if e == entity:
                seg_list = jieba.lcut(abstract)     # unicode

                if entity in seg_list:
                    seg_list.remove(entity)     # 移除摘要中的第一个出现的 entity，之后出现的 entity 都认为是上下文

                break

        entity_context.extend(seg_list)

        return entity_context   # unicode

    # 判断分别来自 kb1 和 kb2 的 e1 与 e2 是否存在 sameAs 关系
    def isSameAs(self, e1, kb1, e2, kb2):
        # e1 (baidubaike) - e2 (hudongbaike)
        if kb1 == 'baidubaike' and kb2 == 'hudongbaike':
            for dict in self.baidubaike_hudongbaike_sameas:
                if e1 == dict['baidubaike_entity'] and e2 == dict['hudongbaike_entity']:
                    return True

        # e1 (hudongbaike) - e2 (baidubaike)
        if kb1 == 'hudongbaike' and kb2 == 'baidubaike':
            for dict in self.baidubaike_hudongbaike_sameas:
                if e1 == dict['hudongbaike_entity'] and e2 == dict['baidubaike_entity']:
                    return True

        # e1 (hudongbaike) - e2 (zhwiki)
        if kb1 == 'hudongbaike' and kb2 == 'zhwiki':
            for dict in self.hudongbaike_zhwiki_sameas:
                if e1 == dict['hudongbaike_entity'] and e2 == dict['zhwiki_entity']:
                    return True

        # e1 (zhwiki) - e2 (hudongbaike)
        if kb1 == 'zhwiki' and kb2 == 'hudongbaike':
            for dict in self.baidubaike_hudongbaike_sameas:
                if e1 == dict['zhwiki_entity'] and e2 == dict['hudongbaike_entity']:
                    return True

        # e1 (baidubaike) - e2 (zhwiki)
        if kb1 == 'baidubaike' and kb2 == 'zhwiki':
            for dict in self.zhwiki_baidubaike_sameas:
                if e1 == dict['baidubaike_entity'] and e2 == dict['zhwiki_entity']:
                    return True

        # e1 (zhwiki) - e2 (baidubaike)
        if kb1 == 'zhwiki' and kb2 == 'baidubaike':
            for dict in self.baidubaike_hudongbaike_sameas:
                if e1 == dict['zhwiki_entity'] and e2 == dict['baidubaike_entity']:
                    return True

        return False

    # Building Entity Disambiguation Graph
    # mNode: mention node
    # esNode: entitySet node
    # meEdge: mention-entitySet edge
    # eeEdge: entitySet-entitySet edge
    # node probability: mention node probability 为初始权重值。entitySet node probability 在 iterative_probability_propagation() 中计算
    # edge probability: 边两端节点间的语义相似度。有2种边，mention-entitySet edge 和 entitySet-entitySet edge
    def build_entity_disambiguation_graph(self):
        print 'Building Entity Disambiguation Graph......',
        EDG = self.EDG
        table = self.table
        baidubaike_candidates = self.baidubaike_candidates
        hudongbaike_candidates = self.hudongbaike_candidates
        zhwiki_candidates = self.zhwiki_candidates
        nRow = self.row_num
        nCol = self.col_num
        i = self.table_number
        mention_quantity = self.mention_quantity
        mention_node_initial_importance = float(1)/mention_quantity

        # mention node 编号范围为 [0, mention_quantity - 1]
        # entitySet node 编号范围为 [mention_quantity, entity_node_end]
        # 所有节点的编号范围为 [0, entity_node_end]
        mention_counter = 0
        entitySet_counter = mention_quantity

        # 逐行逐列遍历一张表格中的每个单元格
        # i: table number
        # r: row number
        # c: column number
        for r in range(nRow):
            if r == 0:  # 表头不作为 EDG 中的节点
                continue

            for c in range(nCol):
                mention = table.get_cell(r, c)                                                  # unicode

                # build baidubaike candidates list
                kb = 'baidubaike'
                baidubaike_candidates_list = []    # [(candidate1, kb), (candidate2, kb)]
                baidubaike_mention_candidates = baidubaike_candidates[r][c]['candidates']       # unicode    [candidate1, candidate2, ...,]
                baidubaike_candidates_quantity = len(baidubaike_mention_candidates)

                for candidate in baidubaike_mention_candidates:
                    tuple = (candidate, kb)
                    baidubaike_candidates_list.append(tuple)

                # build hudongbaike candidates list
                kb = 'hudongbaike'
                hudongbaike_candidates_list = []
                hudongbaike_mention_candidates = hudongbaike_candidates[r][c]['candidates']     # unicode
                hudongbaike_candidates_quantity = len(hudongbaike_mention_candidates)

                for candidate in hudongbaike_mention_candidates:
                    tuple = (candidate, kb)
                    hudongbaike_candidates_list.append(tuple)

                # build zhwiki candidates list
                kb = 'zhwiki'
                zhwiki_candidates_list = []
                zhwiki_mention_candidates = zhwiki_candidates[r][c]['candidates']               # unicode
                zhwiki_candidates_quantity = len(zhwiki_mention_candidates)

                for candidate in zhwiki_mention_candidates:
                    tuple = (candidate, kb)
                    zhwiki_candidates_list.append(tuple)

                candidates_total_quantity = baidubaike_candidates_quantity + hudongbaike_candidates_quantity + zhwiki_candidates_quantity

                if candidates_total_quantity == 0:
                    flag_NIL = True
                else:
                    flag_NIL = False

                # 在 EDG 中添加 mention node
                # ranking: [(entitySet node index i, the probability for the node i to be the referent entitySet of the mention)] 候选实体集合根据概率逆序排列的列表
                EDG.add_node(mention_counter, type='mNode', mention=mention, NIL=flag_NIL, table=i, row=r, column=c, ranking=[], probability=float(mention_node_initial_importance), context=[])
                EDG.node[mention_counter]['label'] = 'mention: ' + EDG.node[mention_counter]['mention']
                EDG.node[mention_counter]['context'] = self.get_mention_context(r, c)

                if flag_NIL == False:
                    # 将 mention 来自三个知识库的候选实体根据 SameAs 关系分组，有 SameAs 关系的分在一组，这样的"一组"放入一个 entitySet node 中，并与 mention node 相连

                    list = []    # [[(entity1, kb1), (entity2, kb2)], [(entity3, kb3)]]

                    # baidubaike - hudongbaike - zhwiki
                    for baidubaike_candidate_index in range(len(baidubaike_candidates_list)):
                        set = []  # [(entity1, kb1), (entity2, kb2)]
                        baidubaike_entity = baidubaike_candidates_list[baidubaike_candidate_index][0]
                        set.append(baidubaike_candidates_list[baidubaike_candidate_index])
                        flag_hudongbaike_pop = False

                        for hudongbaike_candidate_index in range(len(hudongbaike_candidates_list)):
                            hudongbaike_entity = hudongbaike_candidates_list[hudongbaike_candidate_index][0]

                            if self.isSameAs(baidubaike_entity, 'baidubaike', hudongbaike_entity, 'hudongbaike'):
                                set.append(hudongbaike_candidates_list[hudongbaike_candidate_index])
                                hudongbaike_pop_index = hudongbaike_candidate_index
                                flag_hudongbaike_pop = True
                                flag_zhwiki_pop = False

                                for zhwiki_candidate_index in range(len(zhwiki_candidates_list)):
                                    zhwiki_entity = zhwiki_candidates_list[zhwiki_candidate_index][0]

                                    if self.isSameAs(hudongbaike_entity, 'hudongbaike', zhwiki_entity, 'zhwiki'):
                                        set.append(zhwiki_candidates_list[zhwiki_candidate_index])
                                        zhwiki_pop_index = zhwiki_candidate_index
                                        flag_zhwiki_pop = True
                                        break

                                if flag_zhwiki_pop:
                                    zhwiki_candidates_list.pop(zhwiki_pop_index)

                                break

                        if flag_hudongbaike_pop:
                            hudongbaike_candidates_list.pop(hudongbaike_pop_index)

                        flag_zhwiki_pop = False
                        for zhwiki_candidate_index in range(len(zhwiki_candidates_list)):
                            zhwiki_entity = zhwiki_candidates_list[zhwiki_candidate_index][0]

                            if self.isSameAs(baidubaike_entity, 'baidubaike', zhwiki_entity, 'zhwiki'):
                                set.append(zhwiki_candidates_list[zhwiki_candidate_index])
                                zhwiki_pop_index = zhwiki_candidate_index
                                flag_zhwiki_pop = True
                                break

                        if flag_zhwiki_pop:
                            zhwiki_candidates_list.pop(zhwiki_pop_index)

                        list.append(set)

                    # hudongbaike - zhwiki
                    for hudongbaike_candidate_index in range(len(hudongbaike_candidates_list)):
                        set = []  # [(entity2, kb2), (entity3, kb3)]
                        hudongbaike_entity = hudongbaike_candidates_list[hudongbaike_candidate_index][0]
                        set.append(hudongbaike_candidates_list[hudongbaike_candidate_index])
                        flag_zhwiki_pop = False

                        for zhwiki_candidate_index in range(len(zhwiki_candidates_list)):
                            zhwiki_entity = zhwiki_candidates_list[zhwiki_candidate_index][0]

                            if self.isSameAs(hudongbaike_entity, 'hudongbaike', zhwiki_entity, 'zhwiki'):
                                set.append(zhwiki_candidates_list[zhwiki_candidate_index])
                                zhwiki_pop_index = zhwiki_candidate_index
                                flag_zhwiki_pop = True
                                break

                        if flag_zhwiki_pop:
                            zhwiki_candidates_list.pop(zhwiki_pop_index)

                        list.append(set)

                    # zhwiki
                    for zhwiki_candidate_index in range(len(zhwiki_candidates_list)):
                        set = []  # [(entity3, kb3)]
                        set.append(zhwiki_candidates_list[zhwiki_candidate_index])

                        list.append(set)

                    newlist = []    # [[{'entity': entity1, 'kb': kb1, 'context': [entity1 context]}, {'entity': entity2, 'kb': kb2, 'context': [entity2 context]}], [{'entity': entity3, 'kb': kb3, 'context': [entity3 context]}]]
                    # rebuild entitySet
                    # list: [[(entity1, kb1), (entity2, kb2)], [(entity3, kb3)]]
                    # entitySet: [(entity1, kb1), (entity2, kb2)]
                    for entitySet in list:
                        set = []    # [{'entity': entity1, 'kb': kb1, 'context': [entity1 context]}, {'entity': entity2, 'kb': kb2, 'context': [entity2 context]}]
                        for tuple in entitySet:
                            dict = {}       # {'entity': entity1, 'kb': kb1, 'context': [entity context]}
                            dict['entity'] = tuple[0]
                            dict['kb'] = tuple[1]
                            dict['context'] = self.get_entity_context(tuple[0], tuple[1])
                            set.append(dict)
                        newlist.append(set)

                    # 在 EDG 中添加 entitySet node
                    # mNode_index: entitySet node 相邻的唯一一个 mention node 的编号
                    # entitySet: [{'entity': entity1, 'kb': kb1, 'context': [entity1 context]}, {'entity': entity2, 'kb': kb2, 'context': [entity2 context]}]
                    for entitySet in newlist:
                        EDG.add_node(entitySet_counter, type='esNode', entitySet=entitySet, mNode_index=mention_counter, probability=float(0))

                        # 在 EDG 中添加 mention-entity edge
                        EDG.add_edge(mention_counter, entitySet_counter, type='meEdge', probability=float(0))

                        entitySet_counter += 1
                mention_counter += 1

        self.entitySet_node_end = entitySet_counter - 1
        self.node_quantity = self.entitySet_node_end + 1
        self.miniEDG = copy.deepcopy(EDG)

        # 在 EDG 中添加 entitySet-entitySet edge
        for p in range(self.entitySet_node_begin, self.entitySet_node_end + 1):
            for q in range(self.entitySet_node_begin, self.entitySet_node_end + 1):
                if p < q:
                    EDG.add_edge(p, q, type='eeEdge', probability=float(0))
                    EDG.edge[p][q]['label'] = str(EDG.edge[p][q]['probability'])

        self.EDG = EDG
        print 'Done!'

    def save_entity_disambiguation_graph(self):
        print 'Saving Entity Disambiguation Graph......',
        EDG = self.EDG
        nx.write_gpickle(EDG, self.edg_path)
        print 'Done!'

    def load_entity_disambiguation_graph(self):
        self.EDG = nx.read_gpickle(self.edg_path)

    # 画出来的 EDG 图不包含 entity-entity Edge，否则时间开销太大
    def draw_entity_disambiguation_graph(self):
        print 'Drawing Entity Disambiguation Graph......',
        graph_name = self.graph_path + 'edg' + str(self.table_number)
        write_dot(self.miniEDG, graph_name + '.dot')
        os.system('dot -Tsvg ' + graph_name + '.dot' + ' -o ' + graph_name + '.svg')
        print 'Done!'

    # String Similarity
    # s1: string 1
    # s2: string 2
    def string_similarity(self, s1, s2):
        s1 = s1.decode('utf8')
        s2 = s2.decode('utf8')
        edit_distance = Levenshtein.distance(s1, s2)
        len_s1 = len(s1)
        len_s2 = len(s2)

        if len_s1 > len_s2:
            max = len_s1
        else:
            max = len_s2

        string_similarity = 1.0 - float(edit_distance) / max
        return string_similarity

    # 计算 mention 和 entitySet 之间的字符串相似度特征 (String Similarity Feature)
    # mention 与 entitySet 中的每个 entity 的字符串相似度的平均值
    # m: mention node index
    # e: entitySet node index
    def strSim(self, m, e):
        string_similarity = 0.0
        mention = self.EDG.node[m]['mention']           # unicode
        entitySet = self.EDG.node[e]['entitySet']       # unicode

        for dict in entitySet:
            entity = dict['entity']
            kb = dict['kb']

            if kb == 'baidubaike':                      # 完整的实体，包括消岐义内容 real_entity[disambiguation]
                split = entity.split('[')
                real_entity = split[0]                  # 真实的实体 (unicode)，去除了消岐义内容 real_entity

            if kb == 'hudongbaike':                     # 完整的实体，包括消岐义内容 real_entity [disambiguation]
                split = entity.split(' [')
                real_entity = split[0]                  # 真实的实体 (unicode)，去除了消岐义内容 real_entity

            if kb == 'zhwiki':                          # 完整的实体，包括消岐义内容 real_entity (disambiguation)
                split = entity.split(' (')
                real_entity = split[0]                  # 真实的实体 (unicode)，去除了消岐义内容 real_entity

            string_similarity += self.string_similarity(mention, real_entity)

        string_similarity /= len(entitySet)
        return string_similarity

    # Jaccard Similarity
    # x: string list
    # y: string list
    def jaccard_similarity(self, x, y):
        intersection_cardinality = len(set.intersection(*[set(x), set(y)]))
        union_cardinality = len(set.union(*[set(x), set(y)]))
        jaccard_similarity = intersection_cardinality / float(union_cardinality)
        return jaccard_similarity

    # 计算 mention 和 entitySet 之间的上下文相似度特征 (Mention-Entity Context Similarity Feature)
    # mention 与 entitySet 中的每个 entity 的上下文相似度的平均值
    # m: mention node index
    # e: entitySet node index
    def contSim_me(self, m, e):
        context_similarity_me = 0.0
        mention_context = self.EDG.node[m]['context']
        entitySet = self.EDG.node[e]['entitySet']

        for dict in entitySet:
            entity_context = dict['context']

            if len(entity_context) == 0:
                context_similarity_me = 0.0
                return context_similarity_me

            context_similarity_me += self.jaccard_similarity(mention_context, entity_context)

        context_similarity_me /= len(entitySet)
        return context_similarity_me

    # 计算 mention 和 entitySet 之间的语义相似度 (Mention-Entity Semantic Relatedness)
    # m: mention node index
    # e: entitySet node index
    def SR_me(self, m, e):
        alpha1 = 0.5
        beta1 = 0.5
        sr_me = 0.99 * (alpha1 * self.strSim(m, e) + beta1 * self.contSim_me(m, e)) + 0.01
        return sr_me

    # 计算 mention node 和其所有相邻 entitySet node 之间的语义相似度之和
    # m: mention node index
    def SR_me_star(self, m):
        sr_me_star = 0.0

        if self.EDG.node[m]['NIL'] == True:
            return sr_me_star
        else:
            candidates = self.EDG.neighbors(m)  # 所有与 m 节点相邻的节点列表

            for e in candidates:
                sr_me_star += self.EDG.edge[m][e]['probability']

            return sr_me_star

    # 计算 2 entitySet 之间的三元组关系特征 (Triple Relation Feature)
    # entitySet1 中所有实体与 entitySet2 中所有实体的三元组关系值的平均值
    # 如果2个实体来自不同的知识库，IsRDF=0; 2个实体来自相同的知识库，计算方式不变
    # e1: entitySet1 node index
    # e2: entitySet2 node index
    def IsRDF(self, e1, e2):
        is_rdf = 0.0
        entitySet1 = self.EDG.node[e1]['entitySet']
        entitySet2 = self.EDG.node[e2]['entitySet']

        for dict1 in entitySet1:
            entity1 = dict1['entity']
            kb1 = dict1['kb']

            for dict2 in entitySet2:
                entity2 = dict2['entity']
                kb2 = dict2['kb']

                if kb1 != kb2:
                    is_rdf += 0
                else:
                    if kb1 == 'baidubaike':
                        infobox_property = self.baidubaike_infobox_property
                    if kb1 == 'hudongbaike':
                        infobox_property = self.hudongbaike_infobox_property
                    if kb1 == 'zhwiki':
                        infobox_property = self.zhwiki_infobox_property

                    for rdf in infobox_property.readlines():
                        rdf = rdf.strip('\n')

                        if entity1 in rdf and entity2 in rdf:
                            is_rdf += 1
                            break

        is_rdf /= (len(entitySet1) * len(entitySet2))
        return is_rdf

    # 计算 2 entitySet 之间的上下文相似度特征 (Entity-Entity Context Similarity Feature)
    # entitySet1 中所有实体与 entitySet2 中所有实体的上下文相似度的平均值
    # e1: entitySet1 node index
    # e2: entitySet2 node index
    def contSim_ee(self, e1, e2):
        context_similarity_ee = 0.0
        entitySet1 = self.EDG.node[e1]['entitySet']
        entitySet2 = self.EDG.node[e2]['entitySet']

        for dict1 in entitySet1:
            entity1_context = dict1['context']

            for dict2 in entitySet2:
                entity2_context = dict2['context']

                if len(entity1_context) == 0 or len(entity2_context) == 0:
                    context_similarity_ee += 0
                    continue

                context_similarity_ee += self.jaccard_similarity(entity1_context, entity2_context)

        context_similarity_ee /= (len(entitySet1) * len(entitySet2))
        return context_similarity_ee

    # 计算 2 entitySet 之间的语义相似度 (Entity-Entity Semantic Relatedness)
    # e1: entitySet1 node index
    # e2: entitySet2 node index
    def SR_ee(self, e1, e2):
        alpha2 = 0.5
        beta2 = 0.5
        sr_ee = 0.99 * (alpha2 * self.IsRDF(e1, e2) + beta2 * self.contSim_ee(e1, e2)) + 0.01
        return sr_ee

    # 计算 entitySet node 和其相邻的唯一一个 mention node 之间的语义相似度
    # e: entitySet node index
    def SR_em(self, e):
        m = self.EDG.node[e]['mNode_index']
        sr_em = self.EDG.edge[m][e]['probability']
        return sr_em

    # 计算 entitySet node 和其所有相邻 entitySet node 之间的语义相似度之和
    # e: entitySet node index
    def SR_ee_star(self, e):
        sr_ee_star = 0.0

        m = self.EDG.node[e]['mNode_index']
        sr_me = self.EDG.edge[m][e]['probability']

        entities = self.EDG.neighbors(e)

        for ee in entities:
            sr_ee_star += self.EDG.edge[e][ee]['probability']

        sr_ee_star -= sr_me

        return sr_ee_star

    # Computing EL Impact Factors
    def compute_el_impact_factors(self):
        print 'Computing the EL Impact Factors......',
        EDG = self.EDG

        # compute semantic relatedness between mentions and entitySets
        # k: mention node 编号
        # i: entitySet node 编号
        for k in range(self.mention_node_begin, self.mention_node_end + 1):
            if EDG.node[k]['NIL'] == True:
                continue

            candidates = EDG.neighbors(k)

            for i in candidates:
                EDG.edge[k][i]['probability'] = self.SR_me(k, i)

        # compute semantic relatedness between entitySets
        # p: entitySet1 node 编号
        # q: entitySet2 node 编号
        for p in range(self.entitySet_node_begin, self.entitySet_node_end + 1):
            for q in range(self.entitySet_node_begin, self.entitySet_node_end + 1):
                if p < q:
                    EDG.edge[p][q]['probability'] = self.SR_ee(p, q)

        self.EDG = EDG
        print 'Done!'

    # Iterative Probability Propagation
    # 计算 entity node probability (该 entity 成为 mention 的对应实体的概率)
    def iterative_probability_propagation(self):
        print 'Iterative Probability Propagation (Iteration Limit: ' + str(self.iterations) + ', Delta: ' + str(self.delta) + ', Damping Factor: ' + str(self.damping_factor) + ')......',
        EDG = self.EDG
        n = self.node_quantity
        damping_factor = self.damping_factor
        iterations = self.iterations
        delta = self.delta
        A = [[0.0 for col in range(n)] for row in range(n)]
        E = [[1.0 for col in range(n)] for row in range(n)]
        r = [0.0 for i in range(n)]
        flag_convergence = False

        # compute A[i][j]
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue

                i_type = EDG.node[i]['type']
                j_type = EDG.node[j]['type']

                if i_type == 'mNode' and j_type == 'mNode':
                    continue

                if i_type == 'mNode' and j_type == 'esNode':
                    if EDG.node[i]['NIL'] == True:
                        continue
                    else:
                        if EDG.has_edge(i, j) == False:
                            continue
                        else:
                            A[i][j] = EDG.edge[i][j]['probability'] / self.SR_me_star(i)

                if i_type == 'esNode' and j_type == 'mNode':
                    if EDG.node[j]['NIL'] == True:
                        continue
                    else:
                        if EDG.has_edge(i, j) == False:
                            continue
                        else:
                            A[i][j] = A[j][i]

                if i_type == 'esNode' and j_type == 'esNode':
                    A[i][j] = (1.0 - self.SR_em(i)) * self.EDG.edge[i][j]['probability'] / self.SR_ee_star(i)

        self.A = A

        # initialize r(i)
        # epoch 0
        for i in range(n):
            if i < self.mention_quantity:
                r[i] = 1.0 / self.mention_quantity  # mNode
            else:
                r[i] = 0.0  # eNode

        matrix_r = np.matrix(r).T
        matrix_A = np.matrix(A)
        matrix_E = np.matrix(E)

        # update r(i)
        for epoch in range(1, iterations + 1):
            matrix_r_next = ((1.0 - damping_factor) * matrix_E / n + damping_factor * matrix_A) * matrix_r

            r_list = matrix_r.tolist()
            r_next_list = matrix_r_next.tolist()
            max_difference = 0.0

            for i in range(n):
                difference = abs(r_list[i][0] - r_next_list[i][0])

                if difference > max_difference:
                    max_difference = difference

            if max_difference <= delta:
                print 'At Epoch ' + str(epoch) + ' Convergence is Reached!'
                matrix_r = matrix_r_next
                flag_convergence = True
                break

            matrix_r = matrix_r_next

        r_list = matrix_r.tolist()

        for i in range(n):
            r[i] = r_list[i][0]

        if flag_convergence == False:
            print 'After Epoch ' + str(iterations) + ' Iterative Probability Propagation is Done!'

        # 计算 esNode 上的概率 并 打上标签
        for p in range(self.entitySet_node_begin, self.entitySet_node_end + 1):
            EDG.node[p]['probability'] = r[p]
            self.miniEDG.node[p]['label'] = 'entitySet: '

            entitySet = EDG.node[p]['entitySet']

            for dict in entitySet:
                entity = dict['entity']
                kb = dict['kb']
                entity_kb = entity + '<' + kb + '> '
                self.miniEDG.node[p]['label'] += entity_kb

            self.miniEDG.node[p]['label'] += '\n' + str(EDG.node[p]['probability'])

        self.r = r
        self.EDG = EDG

    # 给 mention 的候选实体集合排名
    def rank_candidates(self):
        print 'Ranking entitySets......',
        EDG = self.EDG
        r = self.r

        for i in range(self.mention_node_begin, self.mention_node_end + 1):
            if EDG.node[i]['NIL'] == True:
                continue

            candidates = EDG.neighbors(i)
            ranking = []

            for e in candidates:
                probability = r[e]
                tuple = (e, probability)    # (实体集合节点编号，实体集合成为 mention 的对应实体集合的概率)
                ranking.append(tuple)

            ranking.sort(key=lambda x: x[1], reverse=True)  # ranking 根据概率逆序排序，下标越小概率越大
            EDG.node[i]['ranking'] = ranking

        self.EDG = EDG
        print 'Done!'

    # 挑选出 mention 的候选实体中概率最高的一个 entitySet
    # 将消岐后的结果文件存储于 disambiguation_output_path
    def pick_entity(self):
        print 'Picking the referent entitySet......',
        EDG = self.EDG
        table = self.table
        nRow = self.row_num
        nCol = self.col_num
        i = self.mention_node_begin
        t = []

        for m in range(nRow):
            row = []
            for n in range(nCol):
                dict = {}

                if m == 0:
                    dict['header'] = table.get_cell(m, n)
                else:
                    mention = EDG.node[i]['mention']
                    entity = []     # [(entity1, kb1), (entity2, kb2)]

                    if EDG.node[i]['NIL'] == False:
                        esNode_index = EDG.node[i]['ranking'][0][0]
                        entitySet = EDG.node[esNode_index]['entitySet']

                        for d in entitySet:
                            e = d['entity']
                            kb = d['kb']
                            tuple = (e, kb)
                            entity.append(tuple)

                    dict['mention'] = mention
                    dict['entity'] = entity
                    i += 1

                row.append(dict)
            t.append(row)

        try:
            disambiguation_file = open(self.disambiguation_result_path, 'w')

        finally:
            disambiguation_result = json.dumps(t, ensure_ascii=False)
            disambiguation_file.write(disambiguation_result)

            if disambiguation_file:
                disambiguation_file.close()

        print 'Done!'


class Disambiguation(object):
    # table_name: 表格文件的名称
    # table_path: 表格文件的路径
    # baidubaike_candidate_path: baidubaike 候选实体文件的路径
    # hudongbaike_candidate_path: hudongbaike 候选实体文件的路径
    # zhwiki_candidate_path: zhwiki 候选实体文件的路径
    # baidubaike_infobox_property_path: baidubaike 的 infobox_property 文件路径
    # hudongbaike_infobox_property_path: hudongbaike 的 infobox_property 文件路径
    # zhwiki_infobox_property_path: zhwiki 的 infobox_property 文件路径
    # baidubaike_abstracts_path: baidubaike 的 abstracts 文件路径
    # hudongbaike_abstracts_path: hudongbaike 的 abstracts 文件路径
    # zhwiki_abstracts_path: zhwiki 的 abstracts 文件路径
    # baidubaike_hudongbaike_sameas_path: baidubaike - hudongbaike SameAs 文件路径
    # hudongbaike_zhwiki_sameas_path: hudongbaike - zhwiki SameAs 文件路径
    # zhwiki_baidubaike_sameas_path: zhwiki - baidubaike SameAs 文件路径
    # graph_path: Entity Disambiguation Graph 存储路径
    # result_path: 消岐结果文件的路径
    # final_path: 整个表格文件的实体链接结果文件路径
    def __init__(self, table_name, table_path, baidubaike_candidate_path, hudongbaike_candidate_path, zhwiki_candidate_path, baidubaike_infobox_property_path, hudongbaike_infobox_property_path, zhwiki_infobox_property_path, baidubaike_abstracts_path, hudongbaike_abstracts_path, zhwiki_abstracts_path, baidubaike_hudongbaike_sameas_path, hudongbaike_zhwiki_sameas_path, zhwiki_baidubaike_sameas_path, graph_path, result_path, final_path):
        table_manager = TableManager(table_path)
        self.tables = table_manager.get_tables()  # tables 是 Table 类型数组
        self.table_name = table_name
        self.table_path = table_path
        self.table_quantity = table_manager.table_quantity
        self.baidubaike_candidate_path = baidubaike_candidate_path
        self.hudongbaike_candidate_path = hudongbaike_candidate_path
        self.zhwiki_candidate_path = zhwiki_candidate_path
        self.baidubaike_infobox_property_path = baidubaike_infobox_property_path
        self.hudongbaike_infobox_property_path = hudongbaike_infobox_property_path
        self.zhwiki_infobox_property_path = zhwiki_infobox_property_path
        self.baidubaike_abstracts_path = baidubaike_abstracts_path
        self.hudongbaike_abstracts_path = hudongbaike_abstracts_path
        self.zhwiki_abstracts_path = zhwiki_abstracts_path
        self.baidubaike_hudongbaike_sameas_path = baidubaike_hudongbaike_sameas_path
        self.hudongbaike_zhwiki_sameas_path = hudongbaike_zhwiki_sameas_path
        self.zhwiki_baidubaike_sameas_path = zhwiki_baidubaike_sameas_path
        self.baidubaike_hudongbaike_sameas = []
        self.hudongbaike_zhwiki_sameas = []
        self.zhwiki_baidubaike_sameas = []
        self.graph_path = graph_path
        self.result_path = result_path
        self.final_path = final_path

    def disambiguation(self):
        try:
            tables = self.tables
            graph_path = self.graph_path
            result_path = self.result_path

            # read baidubaike data
            baidubaike_candidate_file = open(self.baidubaike_candidate_path, 'r')
            baidubaike_candidate = baidubaike_candidate_file.read()
            baidubaike_candidate_json = json.loads(baidubaike_candidate, encoding='utf8')    # kb_candidate[nTable][nRow][nCol] = dict{'mention': m, 'candidates': []}
            baidubaike_infobox_property = open(self.baidubaike_infobox_property_path, 'r')
            baidubaike_abstracts = open(self.baidubaike_abstracts_path, 'r')

            # read hudongbaike data
            hudongbaike_candidate_file = open(self.hudongbaike_candidate_path, 'r')
            hudongbaike_candidate = hudongbaike_candidate_file.read()
            hudongbaike_candidate_json = json.loads(hudongbaike_candidate, encoding='utf8')
            hudongbaike_infobox_property = open(self.hudongbaike_infobox_property_path, 'r')
            hudongbaike_abstracts = open(self.hudongbaike_abstracts_path, 'r')

            # read zhwiki data
            zhwiki_candidate_file = open(self.zhwiki_candidate_path, 'r')
            zhwiki_candidate = zhwiki_candidate_file.read()
            zhwiki_candidate_json = json.loads(zhwiki_candidate, encoding='utf8')
            zhwiki_infobox_property = open(self.zhwiki_infobox_property_path, 'r')
            zhwiki_abstracts = open(self.zhwiki_abstracts_path, 'r')

            # get SameAs data
            baidubaike_hudongbaike_sameas_file = open(self.baidubaike_hudongbaike_sameas_path, 'r')
            hudongbaike_zhwiki_sameas_file = open(self.hudongbaike_zhwiki_sameas_path, 'r')
            zhwiki_baidubaike_sameas_file = open(self.zhwiki_baidubaike_sameas_path, 'r')

            # process baidubaike - hudongbaiek sameas data
            for line in baidubaike_hudongbaike_sameas_file.readlines():
                line = line.strip('\n')

                # split
                split = line.split('> <')
                baidubaike_entity = split[0]
                hudongbaike_entity = split[1]

                # clean
                baidubaike_entity = baidubaike_entity[1:]
                hudongbaike_entity = hudongbaike_entity[:-1]

                dict = {}
                dict['baidubaike_entity'] = baidubaike_entity
                dict['hudongbaike_entity'] = hudongbaike_entity
                self.baidubaike_hudongbaike_sameas.append(dict)
            baidubaike_hudongbaike_sameas = self.baidubaike_hudongbaike_sameas

            # process hudongbaike - zhwiki sameas data
            for line in hudongbaike_zhwiki_sameas_file.readlines():
                line = line.strip('\n')

                # split
                split = line.split('> <')
                hudongbaike_entity = split[0]
                zhwiki_entity = split[1]

                # clean
                hudongbaike_entity = hudongbaike_entity[1:]
                zhwiki_entity = zhwiki_entity[:-1]

                dict = {}
                dict['hudongbaike_entity'] = hudongbaike_entity
                dict['zhwiki_entity'] = zhwiki_entity
                self.hudongbaike_zhwiki_sameas.append(dict)
            hudongbaike_zhwiki_sameas = self.hudongbaike_zhwiki_sameas

            # process zhwiki - baidubaike sameas data
            for line in zhwiki_baidubaike_sameas_file.readlines():
                line = line.strip('\n')

                # split
                split = line.split('> <')
                zhwiki_entity = split[0]
                baidubaike_entity = split[1]

                # clean
                zhwiki_entity = zhwiki_entity[1:]
                baidubaike_entity = baidubaike_entity[:-1]

                dict = {}
                dict['zhwiki_entity'] = zhwiki_entity
                dict['baidubaike_entity'] = baidubaike_entity
                self.zhwiki_baidubaike_sameas.append(dict)
            zhwiki_baidubaike_sameas = self.zhwiki_baidubaike_sameas

            # i: 第i张表格，从0开始
            for i in range(self.table_quantity):
                table = tables[i]
                baidubaike_candidates = baidubaike_candidate_json[i]
                hudongbaike_candidates = hudongbaike_candidate_json[i]
                zhwiki_candidates = zhwiki_candidate_json[i]

                EDG_master = EntityDisambiguationGraph(i, table, baidubaike_candidates, hudongbaike_candidates, zhwiki_candidates, baidubaike_infobox_property, hudongbaike_infobox_property, zhwiki_infobox_property, baidubaike_abstracts, hudongbaike_abstracts, zhwiki_abstracts, baidubaike_hudongbaike_sameas, hudongbaike_zhwiki_sameas, zhwiki_baidubaike_sameas, graph_path, result_path)

                time1 = time.time()

                EDG_master.build_entity_disambiguation_graph()
                EDG_master.compute_el_impact_factors()
                EDG_master.iterative_probability_propagation()
                EDG_master.rank_candidates()
                EDG_master.pick_entity()
                EDG_master.save_entity_disambiguation_graph()
                EDG_master.draw_entity_disambiguation_graph()

                time2 = time.time()
                print 'Consumed Time: ' + str(time2 - time1) + ' s'
                print

        finally:
            if baidubaike_candidate_file:
                baidubaike_candidate_file.close()

            if baidubaike_infobox_property:
                baidubaike_infobox_property.close()

            if baidubaike_abstracts:
                baidubaike_abstracts.close()

            if hudongbaike_candidate_file:
                hudongbaike_candidate_file.close()

            if hudongbaike_infobox_property:
                hudongbaike_infobox_property.close()

            if hudongbaike_abstracts:
                hudongbaike_abstracts.close()

            if zhwiki_candidate_file:
                zhwiki_candidate_file.close()

            if zhwiki_infobox_property:
                zhwiki_infobox_property.close()

            if zhwiki_abstracts:
                zhwiki_abstracts.close()

    # 将每张表格的实体链接结果合并到一个文件
    def conbine_el_result(self):
        try:
            multiple_kb_el_result_file = open(self.final_path, 'w')

            whole = []

            for i in range(self.table_quantity):
                table = self.tables[i]
                row_num = table.row_num
                col_num = table.col_num
                t = []

                # fusion
                fusion_result_file_path = self.result_path + str(i) + '.txt'
                fusion_result_file = open(fusion_result_file_path, 'r').read()
                fusion_result_json = json.loads(fusion_result_file)

                for r in range(row_num):
                    row = []
                    for c in range(col_num):
                        dict = {}  # {'header': h} or {'mention': m, 'entity': [(entity1, kb1), (entity2, kb2), (entity3, kb3)]}

                        if r == 0:
                            dict['header'] = fusion_result_json[r][c]['header']
                            row.append(dict)
                        else:
                            dict['mention'] = fusion_result_json[r][c]['mention']
                            dict['entity'] = fusion_result_json[r][c]['entity']
                            row.append(dict)
                    t.append(row)
                whole.append(t)

        finally:
            multiple_kb_el_result_json = json.dumps(whole, ensure_ascii=False)
            multiple_kb_el_result_file.write(multiple_kb_el_result_json)

            if multiple_kb_el_result_file:
                multiple_kb_el_result_file.close()

