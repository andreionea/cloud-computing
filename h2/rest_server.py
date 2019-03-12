from pymongo import MongoClient
from pprint import pprint
from http import server
from bson import Binary, Code
from bson.json_util import dumps
from bson.objectid import ObjectId
import re
from bson.errors import InvalidId

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
                self.wfile.write(b'<h1>403</h1> bad request, invalid id')

        return


server = server.HTTPServer(('', 8080), ReqHandler)
server.serve_forever()
