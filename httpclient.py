#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, https://github.com/treedust, and Long Ma
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        headers=self.get_headers(data)
        first_line=headers[0].split(' ')
        return int(first_line[1])
    
    def get_headers(self,data):
        data_split=data.split('\r\n')
        return data_split[:-1]

    def get_body(self, data):
        data_split=data.split('\r\n')
        return data_split[-1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        self.socket.shutdown(socket.SHUT_WR)
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        #parses url
        url_parse=urllib.parse.urlparse(url)
        url_with_port=url_parse.netloc.split(':')
        if url_parse.port==None:
            port=80
        else:
            port=url_parse.port

        #connect to the url given using sockets
        self.connect(url_with_port[0],port)

        #http get request
        request='GET {} HTTP/1.1\r\nHost: {}\r\n\r\n'.format('/'+url_parse.path,url_parse.netloc)

        #sends and recieves the data
        self.sendall(request)
        data=self.recvall(self.socket)
        self.close()

        #parses the returned data
        code=self.get_code(data)
        body=self.get_body(data)
        sys.stdout.write(data)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        #similar to Get, parses the url first
        url_parse=urllib.parse.urlparse(url)
        url_with_port=url_parse.netloc.split(':')
        if url_parse.port==None:
            port=80
        else:
            port=url_parse.port

        #connects using socket
        self.connect(url_with_port[0],port)
        load=''
        try:
            #tries to get the args to be POST
            keys=list(args.keys())
            vals=list(args.values())

            #creates a string to be added to the POST http statement
            for i in range(len(keys)):
                if len(load)>0:
                    load=load+'&'
                load=load+keys[i]+'='+vals[i]

    
            length=len(load)
        except:
            #if args=None
            length=0

        #sends the request
        request='POST {} HTTP/1.1\r\nHost: {}\r\nContent-Type: application/x-www-form-urlencodeda\r\nContent-Length: {}\r\n\r\n'.format('/'+url_parse.path,url_parse.netloc,length)
        
        request=request+load

        self.sendall(request)

        #recieves the result ad parse it
        data=self.recvall(self.socket)
        self.close()
        code=self.get_code(data)
        body=self.get_body(data)

        sys.stdout.write(data)
        return HTTPResponse(code, body)
        

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
