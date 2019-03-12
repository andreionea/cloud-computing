from pymongo import MongoClient
from pprint import pprint
from http import server
from bson import Binary, Code
from bson.json_util import dumps
from bson.objectid import ObjectId
import re
from bson.errors import InvalidId
import json

db_client = MongoClient('mongodb://localhost:27017/')

db = db_client['database']
customer_collection = db["customers"]


class ReqHandler(server.BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/customers":
            result = dumps([i for i in customer_collection.find()])
            pprint(result)
            self.send_response(200)
            self.send_header('content-type', 'application/json')
            self.end_headers()
            response_bytes = bytes(result, encoding='ASCII')
            self.wfile.write(response_bytes)

        elif re.match('/customers/id=', self.path):
            id = re.split('id=', self.path)[-1]
            try:
                result = dumps(customer_collection.find_one({"_id": ObjectId(id)}))
                pprint(result)
                if result is not 'null':
                    self.send_response(200)
                    self.send_header('content-type', 'application/json')
                    self.end_headers()
                    response_bytes = bytes(result, encoding='ASCII')
                    self.wfile.write(response_bytes)
                else:
                    self.send_response(404)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>404</h1> not found')
            except InvalidId:
                self.send_response(400)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>400</h1> bad request, invalid id')

        return

    def do_POST(self):
        if self.path == '/customers':
            print("executing post")
            content_length = int(self.headers['Content-Length'])
            req_body_raw = self.rfile.read(content_length)
            print("read")
            print(req_body_raw)
            req_body_json = json.loads(req_body_raw)
            print("loaded json")
            insert_result = customer_collection.insert_one(req_body_json)
            print("inserted")
            # if insert_result.inserted_id is not None:
            self.send_response(201)
            self.send_header('Location', 'http://localhost:8080/customers/id=' + str(insert_result.inserted_id))
            self.send_header('content-type', 'text/html')
            self.end_headers()
            print("end headers")
            self.wfile.write(b'<h1>201</h1> created')

        elif re.match('/customers/id=', self.path):
            id = re.split('id=', self.path)[-1]
            try:
                result = dumps(customer_collection.find_one({"_id": ObjectId(id)}))
                pprint(result)
                if result is not 'null':
                    self.send_response(409)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>409</h1> conflict, resource already exists')
                else:
                    self.send_response(404)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>404</h1> not found')
            except InvalidId:
                self.send_response(400)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>400</h1> bad request, invalid id')

        return


server = server.HTTPServer(('', 8080), ReqHandler)
server.serve_forever()
