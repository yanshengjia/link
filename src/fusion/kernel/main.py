# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Shengjia Yan
# Date: 2017/3/3
# Email: sjyan@seu.edu.cn
# 总控程序
# 系统内部所有数据都是 unicode，处理好的文件都以 utf8 编码保存

from preprocess import *
from candidate import *
from disambiguation import *
from result import *
from mark import *


# Step 1: 原始数据预处理
def preprocess():
    # baidubaike
    kb_name = 'baidubaike'
    kb_labels_path = '../../../data/raw/kb_labels/3.0_baidubaike_labels_zh.nt'
    entity_url_output_path = '../../../data/entity/baidubaike_entity_url.txt'
    kb_infobox_properties_path = '../../../data/raw/kb_infobox_properties/3.0_baidubaike_infobox_properties_zh.nt'
    infobox_properties_output_path = '../../../data/property/baidubaike_infobox_properties.txt'
    kb_abstracts_path = '../../../data/raw/kb_abstracts/3.0_baidubaike_abstracts_zh.nt'
    abstracts_output_path = '../../../data/abstract/baidubaike_abstracts.txt'
    synonym_path = '../../../data/synonym/baidubaike_entities_syn.txt'
    entity_synonym_output_path = '../../../data/entity/baidubaike_entity_synonym.txt'

    extracter_baidubaike = Preprocess(kb_name, kb_labels_path, entity_url_output_path, kb_infobox_properties_path, infobox_properties_output_path, kb_abstracts_path, abstracts_output_path, synonym_path, entity_synonym_output_path)

    # print 'Extracting entities from ' + kb_name + ' labels......',
    # extracter_baidubaike.extract_entity()
    # print 'Done!'
    #
    # print 'Extracting infobox properties from ' + kb_name + ' infobox properties......',
    # extracter_baidubaike.extract_infobox_properties()
    # print 'Done!'
    #
    # print 'Extracting abstracts from ' + kb_name + ' abstracts......',
    # extracter_baidubaike.extract_abstracts()
    # print 'Done!'
    #
    # print 'Conbining entities and synonyms of ' + kb_name + '......',
    # extracter_baidubaike.conbine_entity_synonym()
    # print 'Done!'


    # hudongbaike
    kb_name = 'hudongbaike'
    kb_labels_path = '../../../data/raw/kb_labels/3.0_hudongbaike_labels_zh.nt'
    entity_url_output_path = '../../../data/entity/hudongbaike_entity_url.txt'
    kb_infobox_properties_path = '../../../data/raw/kb_infobox_properties/3.0_hudongbaike_infobox_properties_zh.nt'
    infobox_properties_output_path = '../../../data/property/hudongbaike_infobox_properties.txt'
    kb_abstracts_path = '../../../data/raw/kb_abstracts/3.0_hudongbaike_abstracts_zh.nt'
    abstracts_output_path = '../../../data/abstract/hudongbaike_abstracts.txt'
    synonym_path = '../../../data/synonym/hudongbaike_entities_syn.txt'
    entity_synonym_output_path = '../../../data/entity/hudongbaike_entity_synonym.txt'

    extracter_hudongbaike = Preprocess(kb_name, kb_labels_path, entity_url_output_path, kb_infobox_properties_path, infobox_properties_output_path, kb_abstracts_path, abstracts_output_path, synonym_path, entity_synonym_output_path)

    # print 'Extracting entities from ' + kb_name + ' labels......',
    # extracter_hudongbaike.extract_entity()
    # print 'Done!'
    #
    # print 'Extracting infobox properties from ' + kb_name + ' infobox properties......',
    # extracter_hudongbaike.extract_infobox_properties()
    # print 'Done!'
    #
    # print 'Extracting abstracts from ' + kb_name + ' abstracts......',
    # extracter_hudongbaike.extract_abstracts()
    # print 'Done!'
    #
    # print 'Conbining entities and synonyms of ' + kb_name + '......',
    # extracter_hudongbaike.conbine_entity_synonym()
    # print 'Done!'

    # zhwiki
    kb_name = 'zhwiki'
    kb_labels_path = '../../../data/raw/kb_labels/3.1_zhwiki_labels_zh.nt'
    entity_url_output_path = '../../../data/entity/zhwiki_entity_url.txt'
    kb_infobox_properties_path = '../../../data/raw/kb_infobox_properties/2.0_zhwiki_infobox_properties_zh.nt'
    infobox_properties_output_path = '../../../data/property/zhwiki_infobox_properties.txt'
    kb_abstracts_path = '../../../data/raw/kb_abstracts/2.0_zhwiki_abstracts_zh.nt'
    abstracts_output_path = '../../../data/abstract/zhwiki_abstracts.txt'
    synonym_path = '../../../data/synonym/zhwiki_entities_syn.txt'
    entity_synonym_output_path = '../../../data/entity/zhwiki_entity_synonym.txt'

    extracter_zhwiki = Preprocess(kb_name, kb_labels_path, entity_url_output_path, kb_infobox_properties_path, infobox_properties_output_path, kb_abstracts_path, abstracts_output_path, synonym_path, entity_synonym_output_path)

    # print 'Extracting entities from ' + kb_name + ' labels......',
    # extracter_zhwiki.extract_entity()
    # print 'Done!'
    #
    # print 'Extracting infobox properties from ' + kb_name + ' infobox properties......',
    # extracter_zhwiki.extract_infobox_properties()
    # print 'Done!'
    #
    # print 'Extracting abstracts from ' + kb_name + ' abstracts......',
    # extracter_zhwiki.extract_abstracts()
    # print 'Done!'
    #
    # print 'Conbining entities and synonyms of ' + kb_name + '......',
    # extracter_zhwiki.conbine_entity_synonym()
    # print 'Done!'


# Step 2: 候选实体生成
def candidate_generation():
    # baidubaike
    table_name = 'table'
    table_path = '../../../data/table/table.xls'
    kb_name = 'baidubaike'
    entity_path = '../../../data/entity/baidubaike_entity_synonym.txt'
    candidate_path = '../../../data/candidate/baidubaike_candidate_entities.txt'

    baidubaike_candidate_generater = Candidate(table_name, table_path, kb_name, entity_path, candidate_path)

    print 'Generating candidate entities for mentions based on ' + kb_name + '......',
    baidubaike_candidate_generater.generate_candidate()
    print 'Done!'


    # hudongbaike
    table_name = 'table'
    table_path = '../../../data/table/table.xls'
    kb_name = 'hudongbaike'
    entity_path = '../../../data/entity/hudongbaike_entity_synonym.txt'
    candidate_path = '../../../data/candidate/hudongbaike_candidate_entities.txt'

    hudongbaike_candidate_generater = Candidate(table_name, table_path, kb_name, entity_path, candidate_path)

    print 'Generating candidate entities for mentions based on ' + kb_name + '......',
    hudongbaike_candidate_generater.generate_candidate()
    print 'Done!'


    # zhwiki
    table_name = 'table'
    table_path = '../../../data/table/table.xls'
    kb_name = 'zhwiki'
    entity_path = '../../../data/entity/zhwiki_entity_synonym.txt'
    candidate_path = '../../../data/candidate/zhwiki_candidate_entities.txt'

    zhwiki_candidate_generater = Candidate(table_name, table_path, kb_name, entity_path, candidate_path)

    print 'Generating candidate entities for mentions based on ' + kb_name + '......',
    zhwiki_candidate_generater.generate_candidate()
    print 'Done!'


# Step 3: 实体消岐
def entity_disambiguation():
    table_name = 'table'
    table_path = '../../../data/table/table.xls'
    baidubaike_candidate_path = '../../../data/candidate/baidubaike_candidate_entities.txt'
    hudongbaike_candidate_path = '../../../data/candidate/hudongbaike_candidate_entities.txt'
    zhwiki_candidate_path = '../../../data/candidate/zhwiki_candidate_entities.txt'
    baidubaike_infobox_property_path = '../../../data/property/baidubaike_infobox_properties.txt'
    hudongbaike_infobox_property_path = '../../../data/property/hudongbaike_infobox_properties.txt'
    zhwiki_infobox_property_path = '../../../data/property/zhwiki_infobox_properties.txt'
    baidubaike_abstracts_path = '../../../data/abstract/baidubaike_abstracts.txt'
    hudongbaike_abstracts_path = '../../../data/abstract/hudongbaike_abstracts.txt'
    zhwiki_abstracts_path = '../../../data/abstract/zhwiki_abstracts.txt'
    baidubaike_hudongbaike_sameas_path = '../../../data/sameas/baidubaike_hudongbaike_sameas.txt'
    hudongbaike_zhwiki_sameas_path = '../../../data/sameas/hudongbaike_zhwiki_sameas.txt'
    zhwiki_baidubaike_sameas_path = '../../../data/sameas/zhwiki_baidubaike_sameas.txt'
    graph_path = '../../../data/disambiguation/fusion/graph/'
    result_path = '../../../data/disambiguation/fusion/result/'
    final_path = '../../../data/final/fusion/multiple_kb_el_result.txt'

    judger = Disambiguation(table_name, table_path, baidubaike_candidate_path, hudongbaike_candidate_path, zhwiki_candidate_path, baidubaike_infobox_property_path, hudongbaike_infobox_property_path, zhwiki_infobox_property_path, baidubaike_abstracts_path, hudongbaike_abstracts_path, zhwiki_abstracts_path, baidubaike_hudongbaike_sameas_path, hudongbaike_zhwiki_sameas_path, zhwiki_baidubaike_sameas_path, graph_path, result_path, final_path)

    print 'Disambiguating candidate entities:'
    judger.disambiguation()

    print 'Conbining multiple kb EL results into one file......',
    judger.conbine_el_result()
    print 'Done!'


# 人工标注
def mark():
    table_path = '../../../data/table/table.xls'
    baidubaike_candidates_path = '../../../data/candidate/baidubaike_candidate_entities.txt'
    hudongbaike_candidates_path = '../../../data/candidate/hudongbaike_candidate_entities.txt'
    zhwiki_candidates_path = '../../../data/candidate/zhwiki_candidate_entities.txt'
    baidubaike_single_human_mark_path = '../../../data/mark/baidubaike/'
    hudongbaike_single_human_mark_path = '../../../data/mark/hudongbaike/'
    zhwiki_single_human_mark_path = '../../../data/mark/zhwiki/'
    baidubaike_total_human_mark_path = '../../../data/mark/baidubaike/baidubaike_human_mark.txt'
    hudongbaike_total_human_mark_path = '../../../data/mark/hudongbaike/hudongbaike_human_mark.txt'
    zhwiki_total_human_mark_path = '../../../data/mark/zhwiki/zhwiki_human_mark.txt'

    marker = Mark(table_path, baidubaike_candidates_path, hudongbaike_candidates_path, zhwiki_candidates_path, baidubaike_single_human_mark_path, hudongbaike_single_human_mark_path, zhwiki_single_human_mark_path, baidubaike_total_human_mark_path, hudongbaike_total_human_mark_path, zhwiki_total_human_mark_path)

    print 'Marking mentions in tables with 3 KBs......'
    marker.mark()
    print 'Done!'

    print 'Conbining human mark files to one file......'
    marker.conbine()
    print 'Done!'


# 结果对比
def result():
    table_path = '../../../data/table/table.xls'
    multiple_kb_el_result_path = '../../../data/final/fusion/multiple_kb_el_result.txt'
    baidubaike_human_mark_entity_path = '../../../data/mark/baidubaike/baidubaike_human_mark.txt'
    hudongbaike_human_mark_entity_path = '../../../data/mark/hudongbaike/hudongbaike_human_mark.txt'
    zhwiki_human_mark_entity_path = '../../../data/mark/zhwiki/zhwiki_human_mark.txt'

    comparer = Result(table_path, multiple_kb_el_result_path, baidubaike_human_mark_entity_path, hudongbaike_human_mark_entity_path, zhwiki_human_mark_entity_path)

    print 'Comparing System EL Results with Huamn Mark Results......'
    comparer.compare()
    print 'Done!'


def main():
    print "Entity Linking System in Web Tables with Multiple Linked Knowledge Bases"
    print "Version 2.1"
    print "Copyright @2017/3/1 Shengjia Yan. All Rights Reserved."

    # mark()
    # preprocess()
    # candidate_generation()
    entity_disambiguation()
    result()

if __name__ == "__main__":
    main()
