#!/usr/bin/env python3
import http.server
import json
import os

PORT = 8765
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPES_DIR = os.path.join(BASE_DIR, '..', 'recipes')


def load_charts():
    manifest_path = os.path.join(RECIPES_DIR, '03_artist_manifest.json')
    try:
        with open(manifest_path) as f:
            artist = json.load(f)
    except FileNotFoundError:
        raise RuntimeError(f'Artist manifest not found at {manifest_path} — run Agent 3 first.')
    except json.JSONDecodeError as e:
        raise RuntimeError(f'Invalid JSON in artist manifest: {e}')

    return [
        {
            'id': c['id'],
            'question': c['question'],
            'chart_type': c['chart_type'],
            'insight': c.get('insight', ''),
            'echarts_option': c['echarts_option'],
        }
        for c in artist['charts']
    ]


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/data':
            try:
                body = json.dumps(load_charts()).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                body = json.dumps({'error': str(e)}).encode()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        elif self.path in ('/', '/index.html'):
            path = os.path.join(BASE_DIR, 'index.html')
            try:
                with open(path, 'rb') as f:
                    body = f.read()
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, fmt, *args):
        pass  # suppress access logs


if __name__ == '__main__':
    with http.server.HTTPServer(('', PORT), Handler) as httpd:
        print(f'Server running at http://localhost:{PORT}', flush=True)
        httpd.serve_forever()
