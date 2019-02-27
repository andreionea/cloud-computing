import http.server
from urllib import request
import re

PORT = 8080

Handler = http.server.BaseHTTPRequestHandler

class ReqHandler(Handler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            content = bytes(self.make_html(), encoding="UTF-8")
            self.wfile.write(content)

        elif self.path == "/metrics":
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            content = open("metrics.txt").read()
            self.wfile.write(bytes(content, encoding='UTF-8'))

        return

    def make_html(self):
        response = re.split(' ', str(request.urlopen("http://localhost:1234").read(), encoding='UTF-8'))

        return '''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Welcome to page</title>
            </head>
            <body>
                <h1>Hello welcom to page many services good</h1>
                <ul>
                    <li>get random image</li>
                    <li>the internet tells you what it is in the image</li>
                    <li>????</li>
                    <li>profit</li>
                </ul> ''' + "<img src='" + response[0] + "'/>" + "<p>" + response[1] + ' ' + response[
            2] + "</p>" + "</body></html>"


server = http.server.HTTPServer(('', PORT), ReqHandler)
server.serve_forever()
