# !/usr/bin/python
# -*- coding:utf-8 -*-
# Author: Shengjia Yan
# Date: 2017/5/1
# Email: sjyan@seu.edu.cn
# Tornado Web Server: 人工标注模块，用于人工标注表格中的 mention 对应的 entity

import json
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from table import *

# 定义监听的端口
define('port', default=8888, help='run on the given port', type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/home', HomeHandler),
            (r'/mark', MarkHandler),
            (r'/remark', RemarkHandler),
            (r'/result', ResultHandler)
        ]

        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            debug=True
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        # 选择当前人工标注的数据来源
        self.kb = 'baidubaike'
        # self.kb = 'hudongbaike'
        # self.kb = 'zhwiki'

        # read tables
        self.table_path = '../../../../data/table/table_123.xls'
        table_manager = TableManager(self.table_path)
        tables = table_manager.get_tables()
        self.table_quantity = table_manager.table_quantity
        self.current_table_id = 0                                   # 当前标注表格的编号
        self.status = [[0 for i in range(self.table_quantity)]]     # 每张表格的标注状态，未标完为0，标完为1
        self.result = []                                            # 人工表格结果  [[['mention': m, 'entity': e], ['mention': m, 'entity': e]]]

        # candidates path
        self.baidubaike_candidates_path = '../../../../data/candidate/baidubaike_candidate_entities.txt'
        self.hudongbaike_candidates_path = '../../../../data/candidate/hudongbaike_candidate_entities.txt'
        self.zhwiki_candidates_path = '../../../../data/candidate/zhwiki_candidate_entities.txt'

        # human mark data path
        self.baidubaike_human_mark_path = '../../../../data/mark/baidubaike_human_mark.txt'
        self.hudongbaike_human_mark_path = '../../../../data/mark/hudongbaike_human_mark.txt'
        self.zhwiki_human_mark_path = '../../../../data/mark/zhwiki_human_mark.txt'

        # 确定输入输出的路径
        if self.kb == 'baidubaike':
            self.chosen_candidates_path = self.baidubaike_candidates_path
            self.chosen_human_mark_path = self.baidubaike_human_mark_path
        if self.kb == 'hudongbaike':
            self.chosen_candidates_path = self.hudongbaike_candidates_path
            self.chosen_human_mark_path = self.hudongbaike_human_mark_path
        if self.kb == 'zhwiki':
            self.chosen_candidates_path = self.zhwiki_candidates_path
            self.chosen_human_mark_path = self.zhwiki_human_mark_path

        try:
            candidates_file = open(self.chosen_candidates_path, 'r')
            candidates = candidates_file.read()
            candidates_json = json.loads(candidates, encoding='utf8')  # candidates[nTable][nRow][nCol] = dict{'header': h} or dict{'mention': m, 'candidates': [can1, can2, can3]}

            self.tables = []    # [{'nrow': the number of rows in current table, 'ncol': the number of columns in current table, 'data': [['mention': m, 'candidates': [c1, c2, c3]]]]
            for i in range(self.table_quantity):
                dict = {}
                row_num = tables[i].row_num
                col_num = tables[i].col_num

                dict['nrow'] = row_num
                dict['ncol'] = col_num
                dict['data'] = candidates_json[i]
                self.tables.append(dict)

            print 'Human Mark Page is Done!'

        finally:
            if candidates_file:
                candidates_file.close()


class MarkHandler(tornado.web.RequestHandler):
    def get(self):
        current_table_id = self.application.current_table_id

        if current_table_id >= self.application.table_quantity:
            self.write(u'人工标注已完成!')
            return

        self.render("../templates/mark.html",
                    title='huamn mark',
                    table=json.dumps(self.tables[current_table_id], ensure_ascii=False),
                    m_table=self.tables[current_table_id]['data'],
                    page=current_table_id + 1,
                    totalpage=self.application.table_quantity
                    )

        self.application.status[current_table_id] = 1
        self.application.current_table_id += 1

    def post(self):
        pagenum = self.get_argument('pagenum')
        pageresult = self.get_argument('result')
        _status = self.get_argument('status')
        _time = self.get_argument('time')
        _ratio = self.get_argument('mark_ratio')

        res = ResultCache(table_id=pagenum, result=pageresult, status=_status, time=_time, mark_ratio=_ratio)

        if self.db.query(ResultCache).filter(ResultCache.table_id == pagenum).first() != None:
            self.db.query(ResultCache).filter(ResultCache.table_id == pagenum).delete()

        self.db.add(res)
        try:
            self.db.commit()
        except:
            self.db.rollback()


class HomeHandler(tornado.web.RequestHandler):
    def get(self):
        id = self.db.query(StatusCache).first().progress
        resArr = self.db.query(ResultCache).all()[::-1]
        _res = []
        for res in resArr:
            _res.append({
                'id': res.table_id,
                'status': res.status,
                'time': res.time,
                'mark_ratio': res.mark_ratio
            })

        self.render("../templates/home.html", page=id, totalpage=len(self.tables), resArr=_res)


class RemarkHandler(tornado.web.RequestHandler):
    def get(self):
        id = int(self.get_argument('id'))
        print id, len(self.tables)

        if id >= len(self.tables):
            self.write(u'人工标注已完成！')
            return

        self.render("../templates/mark.html",
                    table=json.dumps(self.tables[id], ensure_ascii=False),
                    m_table=self.tables[id]['data'],
                    page=id,
                    totalpage=len(self.tables)
                    )


class ResultHandler(tornado.web.RequestHandler):
    @property
    def auto_mark_tables(self):
        return self.application.auto_mark_tables

    @property
    def human_mark_tables(self):
        return self.application.human_mark_tables

    def get(self):
        id = int(self.get_argument('id'))
        _resArr = []
        _sum = _right = 0

        for mention, entity in self.auto_mark_tables[id].iteritems():
            res = {}
            res['mention'] = mention
            res['auto'] = entity
            res['human'] = self.human_mark_tables[id][mention]
            if self.human_mark_tables[id][mention] == entity and entity != None:
                _right += 1
                _sum += 1
                res['res'] = 'accept'
            elif entity != None:
                _sum += 1
                res['res'] = 'wrong answer'
            else:
                res['res'] = 'None'
            _resArr.append(res)

        self.render("../html/result.html", id=id, sum=_sum, right=_right, resArr=_resArr)


def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()

