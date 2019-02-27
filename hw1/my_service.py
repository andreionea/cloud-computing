import http.server
from urllib import request
import json
import requests

PORT = 1234

Handler = http.server.BaseHTTPRequestHandler


class ReqHandler(Handler):

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.img_url = self.get_image_url()
            self.imagga_tag = self.get_imagga_tag(self.img_url)
            content = bytes(
                self.img_url + ' ' + self.imagga_tag,
                encoding="UTF-8")
            self.wfile.write(content)

        return

    def get_image_url(self):
        response = requests.get("http://www.splashbase.co/api/v1/images/random")
        print("[my_service] GET completed " + str(response.elapsed))
        content = json.loads(response.content)
        image_url = content.get("url")

        return image_url

    def get_imagga_tag(self, url):
        config = json.load(open("config"))

        api_key = config.get("api_key")
        api_secret = config.get("api_secret")

        response = requests.get('https://api.imagga.com/v2/tags?image_url=%s' % url,
                                auth=(api_key, api_secret))
        print("[my_service] GET completed in " + str(response.elapsed))
        metrics_f = open("metrics.txt", "w+")
        metrics_f.write("[my_service] GET completed in " + str(response.elapsed) + ' with headers '+ str(response.headers))
        metrics_f.close()
        dic = json.loads(response.content)
        top_prediction_name = dict(dic.get('result').get('tags')[:1][0]).get('tag').get('en')
        top_prediction_confidence = dict(dic.get('result').get('tags')[:1][0]).get('confidence')

        return top_prediction_name + ' ' + str(top_prediction_confidence)


server = http.server.HTTPServer(('', PORT), ReqHandler)
server.serve_forever()
