from pymongo import MongoClient
from pprint import pprint
from http import server
from bson import Binary, Code
from bson.json_util import dumps
import json
import re

db_client = MongoClient('mongodb://localhost:27017/')

db = db_client['database']
customer_collection = db["customers"]


class ReqHandler(server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/customers":
            #self.send_response(100)
            result = dumps([i for i in customer_collection.find()])
            print(result)
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            response_bytes = bytes(result, encoding='ASCII')
            self.wfile.write(response_bytes)

        return


server = server.HTTPServer(('', 8080), ReqHandler)
server.serve_forever()
