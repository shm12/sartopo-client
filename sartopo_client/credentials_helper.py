
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import requests
import webbrowser
from random import randint

class MyHandler(BaseHTTPRequestHandler):
    HTML = """<!-- Copyright (C) Microsoft Corporation. All rights reserved. -->
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/speed-highlight/core/dist/themes/atom-dark.css">
    <style>
        .wrapper {
            height: 100%;
            width: 100%;
            left: 0;
            right: 0;
            top: 0;
            bottom: 0;
            position: absolute;
            background: linear-gradient(1deg, #eaff7b, #00ffab, #29bdc1, #d84242, #913f92);
            background-size: 1500% 1500%;

            -webkit-animation: rainbow 15s ease infinite;
            -z-animation: rainbow 15s ease infinite;
            -o-animation: rainbow 15s ease infinite;
            animation: rainbow 15s ease infinite;
        }

        @-webkit-keyframes rainbow {
            0% {
                background-position: 0% 82%
            }

            50% {
                background-position: 100% 19%
            }

            100% {
                background-position: 0% 82%
            }
        }

        @-moz-keyframes rainbow {
            0% {
                background-position: 0% 82%
            }

            50% {
                background-position: 100% 19%
            }

            100% {
                background-position: 0% 82%
            }
        }

        @-o-keyframes rainbow {
            0% {
                background-position: 0% 82%
            }

            50% {
                background-position: 100% 19%
            }

            100% {
                background-position: 0% 82%
            }
        }

        @keyframes rainbow {
            0% {
                background-position: 0% 82%
            }

            50% {
                background-position: 100% 19%
            }

            100% {
                background-position: 0% 82%
            }
        }

        .code-container {
            max-width: 1000px;
            margin: auto;
            margin-top: 100px;
        }


        ::-webkit-scrollbar {
            width:0px;
            scroll-margin: 300px;
        }
        
        ::-webkit-scrollbar-track {
            border-radius: 8px;
            background-color: #95a5a6;
            border: 1px solid #cacaca;
        }
        
        ::-webkit-scrollbar-thumb {
            border-radius: 8px;
            background-color: #1f374e;
        }

        


        .button {
            margin-top: 10px;
            margin-right: 10px;
            float: right;
            cursor: pointer;
            outline: 0;
            display: inline-block;
            font-weight: 400;
            line-height: 1.5;
            text-align: center;
            background-color: transparent;
            border: 1px solid transparent;
            padding: 6px 12px;
            font-size: 1rem;
            border-radius: .25rem;
            transition: color .15s ease-in-out, background-color .15s ease-in-out, border-color .15s ease-in-out, box-shadow .15s ease-in-out;
            color: #0d6efd;
            border-color: #0d6efd;
        }

        .button:hover {
            color: #fff;
            background-color: #0d6efd;
            border-color: #0d6efd;
        }

        .btns {
            margin-top: 10px;
            margin-right: 10px;
            float: right;
        }
    </style>

<body>
    <!-- <script src="https://cdn.jsdelivr.net/gh/speed-highlight/core/dist/index.js"/> -->
    <script type="module">
        import { highlightAll } from 'https://cdn.jsdelivr.net/gh/speed-highlight/core/dist/index.js'

        // Setup the code
        var comment = `# You can now copy paste this line to get started with SarTopoClient 🙂\\n` +
            `# Just make sure to keep these credentials otherwise you will have to repeat this process\\n`;
        var code = `s = SarTopoClient(user_id='{user_id}', auth_key='{auth_key}', auth_id='{auth_id}')`
        // var padding = '\\n\\n'
        var error = ''
        document.getElementById("code").innerHTML = comment + '\\n' + code

        // Error is being set by python code
        if (error != ''){
            document.getElementById("code").innerHTML = '# ' + error
        }

        // Highlight
        highlightAll();

        // Copy
        document.getElementById("copy-button").addEventListener("click", on_copy);
        function on_copy() {
            navigator.clipboard.writeText(code)
        }
    </script>
    <div class="wrapper">
        <div class="code-container scrollbar" style="position:relative;">
            <!-- <div class="btns"> -->
                <!-- </div> -->
                <div class='fira shj-lang-py shj-multiline shj-mode-header' style="padding-bottom: 70px" id="code" ></div>
                <button class="button" style="position:absolute; bottom:20px; right:10px;" id="copy-button">COPY</button>
        </div>
    </div>
</body>
</html>"""
            
    def request_credentials(self):
        url = urlparse(self.path)
        code = ''
        for i in url.query.split("&"):
            splitted = i.split("=")
            if len(splitted) != 2:
                continue
            if splitted[0] == 'code':
                code = splitted[1]
                break
        assert code, 'something went wrong the OAuth1 code was not provided'
        
        res = requests.get(f'http://sartopo.com/api/v1/activate?code={code}')
        assert res.status_code == 200, f'Failed to get credentials. code: {res.status_code}, reason: {res.text}'
        try:
            creds = res.json()
        except:
            raise ValueError('http://sartopo.com/api/v1/activate didn\'t responded with json for http://sartopo.com/api/v1/activate')
        
        try:
            return creds['account']['id'], creds['key'], creds['code']
        except:
            raise ValueError('http://sartopo.com/api/v1/activate response does not contains expected credentials')
            
    def do_GET(self):
        html = self.HTML
        try:
            user_id, auth_key, auth_id = self.request_credentials()
            status = 200
            html = html.replace("user_id='{user_id}', auth_key='{auth_key}', auth_id='{auth_id}'",
                                f"user_id='{user_id}', auth_key='{auth_key}', auth_id='{auth_id}'")
            
        except Exception as e:
            status = 500
            html = html.replace("var error = ''", f"var error = `{e}`")
            html = html.replace('<button class="button" style="position:absolute; bottom:20px; right:10px;" id="copy-button">COPY</button>', '')
        
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(html, 'utf-8'))

def fetch_sartopo_credentials():
    port = randint(2**15, 2**15 + 2**14)
    webbrowser.open_new_tab(f'https://sartopo.com/app/activate/offline?redirect=http://localhost:{port}')
    with HTTPServer(('0.0.0.0', port), MyHandler) as server:
        server.handle_request()


if __name__ == '__main__':
    fetch_sartopo_credentials()