#!/usr/bin/env python3
import http.server
import json
import os

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPES_DIR = os.path.join(BASE_DIR, '..', 'recipes')


def load_charts():
    with open(os.path.join(RECIPES_DIR, '03_artist_manifest.json')) as f:
        artist = json.load(f)
    with open(os.path.join(RECIPES_DIR, '02_chef_kitchen.json')) as f:
        chef = json.load(f)

    insights = {c['id']: c['echarts_data'].get('insight', '') for c in chef['charts']}

    return [
        {
            'id': c['id'],
            'question': c['question'],
            'chart_type': c['chart_type'],
            'insight': insights.get(c['id'], ''),
            'echarts_option': c['echarts_option'],
        }
        for c in artist['charts']
    ]


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            body = json.dumps(load_charts()).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(body)
        elif self.path in ('/', '/index.html'):
            path = os.path.join(BASE_DIR, 'index.html')
            with open(path, 'rb') as f:
                body = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass  # suppress access logs


if __name__ == '__main__':
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        print(f'Server running at http://localhost:{PORT}', flush=True)
        httpd.serve_forever()
