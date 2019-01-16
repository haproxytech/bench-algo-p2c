#!/usr/bin/env python

'''
Simple and functional REST server for Python (3.5) using no dependencies beyond the Python standard library.
Returns the current time for requests on /GetTime.

Takes 1 arg :
  argv[1] : listening [address:]port

Loosely inspired by this one by Ivan Averin :
   https://gist.github.com/iaverin/f81720df9ed37a49ecee6341e4d5c0c6
'''

import http.server
import json
import re
import sys
import datetime

def service_worker():
    pass

poll_interval = 0.1

class RESTRequestHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        return http.server.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    # disable console logging
    def log_message(self, format, *args):
        return

    def do_HEAD(self):
        self.handle_method('HEAD')

    def do_GET(self):
        self.handle_method('GET')

    def do_POST(self):
        self.handle_method('POST')

    def do_PUT(self):
        self.handle_method('PUT')

    def do_DELETE(self):
        self.handle_method('DELETE')

    def handle_method(self, method):
        if not re.match('^/GetTime', self.path):
            self.send_response(404)
            self.end_headers()
            if method != 'HEAD':
                self.wfile.write('No such service\n'.encode())
        elif method == 'HEAD':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        elif method == 'GET':
            t = datetime.datetime.now()
            content = { 'hour' : t.hour, 'minute' : t.minute }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(content).encode())
        else:
            self.send_response(405)
            self.end_headers()
            self.wfile.write(method + ' is not supported\n'.encode())

def rest_server(port):
    'Starts the REST server'
    port = port.split(':')
    if len(port) > 1:
        addr = port[0]
        port = int(port[1])
    else:
        addr = ''
        port = int(port[0])

    http_server = http.server.HTTPServer((addr, port), RESTRequestHandler)
    http_server.service_actions = service_worker
    print('Starting HTTP server at port %s:%d' % (addr,port))
    try:
        http_server.serve_forever(poll_interval)
    except KeyboardInterrupt:
        pass
    print('Stopping HTTP server')
    http_server.server_close()


def main(argv):
    rest_server(argv[0] if argv else '2001')


if __name__ == '__main__':
    main(sys.argv[1:])
