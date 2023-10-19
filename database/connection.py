import pymysql
from elasticsearch import Elasticsearch

mysql = pymysql.connect(host='192.168.1.2',
                             user='sc_admin',
                             password='123456',
                             database='sc_db',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor,
                             autocommit=True
                             )

elastic_search = Elasticsearch(
            [
                {'host': '192.168.1.2', 'port': 9200, "scheme": "https"}
            ],
                basic_auth=('elastic', 'B+4lU1Sb4-6s0QPGde=v'),
                verify_certs=False,
        ) 