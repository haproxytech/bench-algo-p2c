#!/usr/bin/env python

'''
Simple and functional REST server for Python (3.5) using no dependencies beyond the Python standard library.
Logs the info of the requested user on /Log with its full name and current time. Uses CurrentTime() and
UserAttr(). The info is passed using PUT and JSON :

  { "user" : user, "method" : method, "ip" : ip }

Takes 3 args :
  argv[1] : listening [address:]port
  argv[2] : time service url[#key]
  argv[3] : user service url[#key]

Loosely inspired by this one by Ivan Averin :
   https://gist.github.com/iaverin/f81720df9ed37a49ecee6341e4d5c0c6
'''
import http.server
import importlib
import json
import os
import re
import shutil
import sys
import urllib.request
import urllib.parse 
import syslog
import threading
import socketserver

time_url = ''
time_key = ''

user_url = ''
user_key = ''

def service_worker():
    pass

poll_interval = 0.1


def rest_call_json(url, key, payload=None, with_payload_method='PUT'):
    'REST call with JSON decoding of the response and JSON payloads'
    try:
        if payload:
            if not isinstance(payload, str):
                payload = json.dumps(payload)
            # PUT or POST
            request = MethodRequest(url, payload.encode(), {'Content-Type': 'application/json'}, method=with_payload_method)
        else:
            # GET
            request = urllib.request.Request(url)

        if key:
            request.add_header('X-Api-Key', key)
        response = urllib.request.urlopen(request)
        response = response.read().decode()
        if response:
            response = json.loads(response)
        return response
    except urllib.error.HTTPError:
        return None


class MethodRequest(urllib.request.Request):
    'See: https://gist.github.com/logic/2715756'

    def __init__(self, *args, **kwargs):
        if 'method' in kwargs:
            self._method = kwargs['method']
            del kwargs['method']
        else:
            self._method = None
        return urllib.request.Request.__init__(self, *args, **kwargs)

    def get_method(self, *args, **kwargs):
        return self._method if self._method is not None else urllib.request.get_method(self, *args, **kwargs)


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

    def get_payload(self):
        payload_len = int(self.headers.get('content-length', 0))
        payload = self.rfile.read(payload_len)
        payload = json.loads(payload.decode())
        return payload

    def handle_method(self, method):
        if not re.match('^/Log', self.path):
            self.send_response(404)
            self.end_headers()
            if method != 'HEAD':
                self.wfile.write('No such service\n'.encode())
            return

        if method == 'PUT':
            payload = self.get_payload()
            user = payload['user']
            if not user:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('Missing user ("user")\n'.encode())
                return

            meth = payload['meth']
            if not meth:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('Missing method ("meth")\n'.encode())
                return

            addr = payload['addr']
            if not addr:
                self.send_response(400)
                self.end_headers()
                self.wfile.write('Missing client address ("addr")\n'.encode())
                return

            attr = rest_call_json(user_url + '/' + str(user), user_key)
            if not attr:
                self.send_response(404)
                self.end_headers()
                self.wfile.write('No such user\n'.encode())
                return

            time = rest_call_json(time_url, time_key)
            if not time:
                self.send_response(500)
                self.end_headers()
                self.wfile.write('Failed to access time service\n'.encode())
                return

            syslog.syslog('time=' + str(time['hour']) + ':' + str(time['minute']) +
                          ' addr=' + str(addr) + ' meth=' + str(meth) +
                          ' user=' + str(user) + ' name="' + str(attr['name']) +
                          '" offset=' + str(attr['offset']))

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
        else:
            self.send_response(405)
            self.end_headers()
            if method != 'HEAD':
                self.wfile.write(method + ' is not supported\n'.encode())

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def rest_server(port):
    'Starts the REST server'
    port = port.split(':')
    if len(port) > 1:
        addr = port[0]
        port = int(port[1])
    else:
        addr = ''
        port = int(port[0])

    #http_server = http.server.HTTPServer((addr, port), RESTRequestHandler)
    #http_server.service_actions = service_worker
    #try:
    #    http_server.serve_forever(poll_interval)
    #except KeyboardInterrupt:
    #    pass

    http_server = ThreadedTCPServer((addr, port), RESTRequestHandler)
    http_server.allow_reuse_address = True
    server_thread = threading.Thread(target=http_server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    server_thread.join()

    print('Stopping HTTP server')
    http_server.server_close()


def main(argv):
    global time_url
    global time_key
    global user_url
    global user_key

    time_url = argv[1].split('#')
    if len(time_url) > 1:
        time_key = time_url[1]
    time_url = time_url[0]

    user_url = argv[2].split('#')
    if len(user_url) > 1:
        user_key = user_url[1]
    user_url = user_url[0]

    rest_server(argv[0] if argv else '2003')

if __name__ == '__main__':
    main(sys.argv[1:])
