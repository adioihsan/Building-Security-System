import pymysql
import time
from elasticsearch import Elasticsearch
from threading import Thread

class _Connection:
    def __init__(self):
        self.mysql = None
        self.elastic_search = None
        self.th_mysql = Thread(target=self.__create_mysql_connection)
        self.th_elastic = Thread(target=self.__create_elastic_search_connection)
    
    def __create_mysql_connection(self):
        while self.mysql is None:
            try:
                print("INFO : ","Creating mysql connection")
                self.mysql = pymysql.connect(host='192.168.1.2',
                                        user='sc_admin',
                                        password='123456',
                                        database='sc_db',
                                        charset='utf8mb4',
                                        cursorclass=pymysql.cursors.DictCursor,
                                        autocommit=True
                                        )
                print("INFO : ","Mysql connection created")
            except:
                print("ERROR : Cant connect to mysql database with host : ")
                print("INFO : Retry in 5 seconds...")
                time.sleep(5)
                self.mysql =  None
    
    def __create_elastic_search_connection(self):
        while self.elastic_search is None:
            try:
                self.elastic_search =  Elasticsearch(
                            [
                                {'host': '192.168.1.2', 'port': 9200, "scheme": "https"}
                            ],
                                basic_auth=('elastic', 'B+4lU1Sb4-6s0QPGde=v'),
                                verify_certs=False,
                        ) 
                print("INFO : ","Elastic search connection created")
            except:
                print("ERROR : Cant connect to elastic search  with host : ")
                print("INFO : Retry in 5 seconds...")
                time.sleep(5)
                self.elastic_search =  None
    
    def create_connection(self):
        self.th_mysql.start()
        self.th_elastic.start()
        self.th_mysql.join()
        self.th_elastic.join()

get_connection = _Connection()
get_connection.create_connection()