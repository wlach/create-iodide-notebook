import argparse
import base64
import mimetypes
import os
import threading
import time
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote

RESPONSE = ""
RESPONDED = False
IOMD = """
%% fetch
text: fileContent={filename}

%% js
// You can access the file content in js-space via the
// `fileContent` variable
fileContent

%% py
# similarly, in a python cell you can use the standard idiom
# for importing the data
from js import fileContent as file_content
file_content
"""


class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        global RESPONDED
        self.send_response(200)
        self.end_headers()
        self.wfile.write(bytes(RESPONSE.encode("utf-8")))
        RESPONDED = True


def serve(filename):
    global RESPONSE
    base_filename = os.path.basename(filename)
    file_content = open(filename, 'rb').read()

    RESPONSE = open('create-file-intermediary.html').read().format(
        server="localhost:8000",
        iomd=quote(
            IOMD.format(filename=base_filename)),
        filename=base_filename,
        mimetype=mimetypes.guess_type(base_filename)[
            0],
        content=base64.b64encode(file_content).decode("utf-8")
    )

    httpd = HTTPServer(('localhost', 0), RequestHandler)

    server = threading.Thread(target=httpd.serve_forever)
    server.setDaemon(True)  # don't hang on exit
    server.start()

    webbrowser.open_new_tab(f'http://localhost:{httpd.server_port}')

    while not RESPONDED:
        time.sleep(0.1)


parser = argparse.ArgumentParser()
parser.add_argument("file", nargs=1, help="file to upload")
args = parser.parse_args()
serve(args.file[0])
