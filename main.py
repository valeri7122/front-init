from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import socket
from datetime import *
import json


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        if url.path == '/':
            self.send('index.html')
        elif url.path == '/message':
            self.send('message.html')   
        else:
            if pathlib.Path().joinpath(url.path[1:]).exists():
                self.sendstatic()
            else:
                self.send('error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        server_client = Thread(target=run_client, args=('localhost', 5000, data))
        server_client.start()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())    

    def sendstatic(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())        

def run():
    serveraddress = ('', 3000)
    http = HTTPServer(serveraddress, HttpHandler)
    try:
        server = Thread(target=http.serve_forever)
        server.start()
    except KeyboardInterrupt:
        http.server_close()

def run_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    with open('storage/data.json', "r") as fh:
        unpacked = json.load(fh)
    try:
        data = sock.recvfrom(1024)
        time = datetime.now()
        data_parse = urllib.parse.unquote_plus(data[0].decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        unpacked.update({str(time):data_dict})
        with open('storage/data.json', "w") as fh:
            json.dump(unpacked, fh)
    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()

def run_client(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.sendto(data, server)
    sock.close()

if __name__ == '__main__':
    server_server = Thread(target=run_server, args=('localhost', 5000))
    server_server.start()
    run()
