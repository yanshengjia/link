# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Shengjia Yan
# Date: 2017/3/3
# Email: sjyan@seu.edu.cn
# 总控程序

from preprocess import *
from candidate import *
from disambiguation import *
from sameas import *


# Step 1: 原始数据预处理
def preprocess():
    print 'Extracting entities from KB labels......',

    # baidubaike
    extracter_baidubaike = Preprocess("baidubaike", "../../../data/raw/kb_labels/3.0_baidubaike_labels_zh.nt", "../../../data/entity/baidubaike_entities.txt")
    extracter_baidubaike.extract_entity()

    # hudongbaike
    extracter_hudongbaike = Preprocess("hudongbaike", "../../../data/raw/kb_labels/3.0_hudongbaike_labels_zh.nt", "../../../data/entity/hudongbaike_entities.txt")
    extracter_hudongbaike.extract_entity()

    # zhwiki
    extracter_zhwiki = Preprocess("zhwiki", "../../../data/raw/kb_labels/3.1_zhwiki_labels_zh.nt", "../../../data/entity/zhwiki_entities.txt")
    extracter_zhwiki.extract_entity()

    print 'Done!'


# Step 2: 候选实体生成
def candidate_generation():
    print 'Generating candidate entities for mentions based on each single KB......',

    # baidubaike
    baidubaike_candidate_generater = Candidate('table_123', '../../../data/table/table_123.xls', 'baidubaike', '../../../data/entity/baidubaike_entities.txt', 'BabelNet', '../../../data/candidate/baidubaike_candidate_entities.txt')
    baidubaike_candidate_generater.generate_candidate()

    # hudongbaike
    hudongbaike_candidate_generater = Candidate('table_123', '../../../data/table/table_123.xls', 'hudongbaike', '../../../data/entity/hudongbaike_entities.txt', 'BabelNet', '../../../data/candidate/hudongbaike_candidate_entities.txt')
    hudongbaike_candidate_generater.generate_candidate()

    # zhwiki
    zhwiki_candidate_generater = Candidate('table_123', '../../../data/table/table_123.xls', 'zhwiki', '../../../data/entity/zhwiki_entities.txt', 'BabelNet', '../../../data/candidate/zhwiki_candidate_entities.txt')
    zhwiki_candidate_generater.generate_candidate()

    print 'Done!'


# Step 3: 实体消岐
def entity_disambiguation():
    print 'Disambiguating candidate entities......',

    # # baidubaike
    # baidubaike_judger = Disambiguation('table_123', '../../../data/table/table_123.xls', 'baidubaike', 'baidubaike_candidate_entities', '../../../data/candidate/baidubaike_candidate_entities.txt', '../../../data/disambiguation/baidubaike/graph/', '../../../data/disambiguation/baidubaike/baidubaike_disambiguation.txt')
    # baidubaike_judger.disambiguation()
    #
    # # hudongbaike
    # hudongbaike_judger = Disambiguation('table_123', '../../../data/table/table_123.xls', 'hudongbaike', 'hudongbaike_candidate_entities', '../../../data/candidate/hudongbaike_candidate_entities.txt', '../../../data/disambiguation/hudongbaike/graph/', '../../../data/disambiguation/hudongbaike/hudongbaike_disambiguation.txt')
    # hudongbaike_judger.disambiguation()

    # zhwiki
    zhwiki_judger = Disambiguation('table_123', '../../../data/table/table_123.xls', 'zhwiki', 'zhwiki_candidate_entities', '../../../data/candidate/zhwiki_candidate_entities.txt', '../../../data/disambiguation/zhwiki/graph/', '../../../data/disambiguation/zhwiki/zhwiki_disambiguation.txt')
    zhwiki_judger.disambiguation()

    print 'Done!'


# Step 4: 利用多知识库间sameAs关系提升链接质量
def sameAs():
    print 'Improving entity linking with multiple linked KBs......',

    multiple_kb_improver = SameAs()
    multiple_kb_improver.sameAs()

    print 'Done!'


def main():
    print "Entity Linking System in Web Tables with Multiple Linked Knowledge Bases"
    print "Version 1.0"
    print "Copyright @2017/3/1 Shengjia Yan. All Rights Reserved."

    entity_disambiguation()
    # sameAs()

if __name__ == "__main__":
    main()
