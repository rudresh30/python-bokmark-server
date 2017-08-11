#!/usr/bin/env python3

from http import server
import requests
from urllib.parse import unquote,parse_qs
import os


existing_entries = {}

def readHtml():
    html_path = './form.html' #this html will be formatted later
    print("can read file")
    with open(html_path,'r') as f:
        fhtml = ''.join(each_line.strip() for each_line in f)
        f.seek(0)
    return fhtml

def validlongURI(longurl):

    try:
        req_response = requests.get(longurl,timeout=5)
        return True if req_response.status_code in (200,303) else False
    except:
         return False


class bookmarkserver(server.BaseHTTPRequestHandler):
    def do_GET(self):

            #check whether the path includes a shorturl
            if (len(self.path.strip()) > 1) and ("css" not in (self.path)):
                req_redirect = True
            else:
                req_redirect = False

            if (req_redirect):
                if validlongURI(existing_entries[self.path[1:]]):
                    self.send_response(303)
                    self.send_header('Content-type','text/plain; \
                                    charset=utf-8')
                    self.send_header('Location',
                                    existing_entries[self.path[1:]])
                    self.end_headers()
                    self.wfile.write("redirecting....".encode())
                else:
                    self.send_header(404)
                    self.send_header('Content-type',
                                    'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write("invalid long uri..pls check".encode())

            else: #no path provided or asking for css

                if ("css" not in self.path):
                    print("this is html request")

                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()

                    fhtml = readHtml()

                    if (len(existing_entries) == 0):
                        table_entry =  "<tr><td>None</td><td>None</td></tr>"
                    else:
                        table_entry = "".join("<tr><td>{}</td><td>{}</td></tr>"
                                    .format(key,existing_entries[key])
                                    for key in sorted(existing_entries.keys()))

                    self.wfile.write(fhtml.format(table_entry).encode())

                else:
                    print("this is css request")
                    self.send_response(200)
                    self.send_header('Content-type','text/css')
                    self.end_headers()

                    css_path = './css/main.css'
                    with open(css_path,'r') as fcss:
                        css_file = ''.join(each_line.strip()
                                    for each_line in fcss)

                    self.wfile.write(css_file.encode())

    def do_POST(self):
        length=int(self.headers.get('Content-length',0))
        print(self.headers)

        data = self.rfile.read(length).decode()
        print("data is \n {}".format(str(data)))
        #first extract the longurl and validate--if ok then storein dictionary
        longurl = parse_qs(data)["longurl"][0]

        if validlongURI(longurl):
            existing_entries[parse_qs(data)["shorturl"][0]] = longurl
            self.send_response(303)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.send_header('Location','http://localhost:8000')
            self.end_headers()

            self.wfile.write("sucess...".encode())

        else:
            self.send_response(404)
            self.send_header('Content-type','text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write("provide a valid url..".encode())

if __name__ == '__main__':
    server_address = ('',8000)
    httpd = server.HTTPServer(server_address,bookmarkserver)
    httpd.serve_forever()
