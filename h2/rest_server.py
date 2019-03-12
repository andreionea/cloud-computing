from pymongo import MongoClient
from pprint import pprint
from http import server
from bson.json_util import dumps
from bson.objectid import ObjectId
import re
from bson.errors import InvalidId
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

db_client = MongoClient('mongodb://localhost:27017/')

db = db_client['database']
customer_collection = db["customers"]
user_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "number"}
    }
}


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

    def do_PUT(self):
        if self.path == '/customers':
            self.send_response(405)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>405</h1>, method not allowed')

        elif re.match('/customers/id=', self.path):
            try:
                id = re.split('id=', self.path)[-1]
                content_length = int(self.headers['Content-Length'])
                req_body_raw = self.rfile.read(content_length)
                req_body_json = json.loads(req_body_raw)
                validate(instance=req_body_json, schema=user_schema)
                result = dumps(customer_collection.find_one({"_id": ObjectId(id)}))
                if result is not 'null':
                    customer_collection.find_one_and_replace({"_id": ObjectId(id)}, req_body_json)
                    self.send_response(200)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>200</h1> iz oke')
                else:
                    self.send_response(404)
                    self.send_header('content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<h1>404</h1> customer not found')

            except ValidationError:
                self.send_response(400)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>400</h1> bad request, invalid schema')

        return

    def do_DELETE(self):
        if self.path == '/customers':
            self.send_response(405)
            self.send_header('content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'<h1>405</h1> delete method not allowed')

        elif re.match('/customers/id=', self.path):
            id = re.split('id=', self.path)[-1]
            result = dumps(customer_collection.find_one({"_id": ObjectId(id)}))
            if result is not 'null':
                customer_collection.find_one_and_delete({"_id": ObjectId(id)})
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'<h1>200</h1> deleted iz oke')


server = server.HTTPServer(('', 8080), ReqHandler)
server.serve_forever()
