import http.server # Our http server handler for http requests
import socketserver # Establish the TCP Socket connections
 
 
class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # self.path = '/'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


class Server:
    def __init__(self, PORT):
        self.handler = MyHttpRequestHandler
        self.PORT = PORT

    def start(self):
        httpd = socketserver.TCPServer(("localhost", self.PORT), self.handler)
        print("Http Server Serving at port", self.PORT)
        httpd.serve_forever()
        
        