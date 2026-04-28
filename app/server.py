#!/usr/bin/env python3
import argparse
import http.server
import json
import os
import urllib.parse

import pyexasol

ALLOWED_VIEWS = {
    'REMOTE_WORK_PAY_PREMIUM',
    'AI_ADOPTION_PAY_PARADOX',
    'AI_THREAT_CONFIDENCE_PREMIUM',
    'EXPERIENCE_VS_AI_ADOPTION',
    'COUNTRY_COMPENSATION_MAP',
}

FILTER_COLS = {
    'REMOTE_WORK_PAY_PREMIUM': ['RemoteWork'],
    'AI_ADOPTION_PAY_PARADOX': ['AISelect'],
    'AI_THREAT_CONFIDENCE_PREMIUM': ['AIThreat'],
    'EXPERIENCE_VS_AI_ADOPTION': ['exp_bucket', 'AISelect'],
    'COUNTRY_COMPENSATION_MAP': ['Country'],
}

APP_DIR = os.path.dirname(os.path.abspath(__file__))


def get_conn():
    return pyexasol.connect(
        dsn=f"{os.environ['EXASOL_HOST']}:{os.environ.get('EXASOL_PORT', '8563')}",
        user=os.environ['EXASOL_USER'],
        password=os.environ['EXASOL_PASSWORD'],
        websocket_sslopt={'cert_reqs': 0},
    )


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        if parsed.path in ('/', '/index.html'):
            self._serve_file()
        elif parsed.path == '/api/query':
            self._serve_query(params)
        else:
            self._send(404, {'error': 'not found'})

    def _serve_file(self):
        path = os.path.join(APP_DIR, 'index.html')
        with open(path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(data))
        self.end_headers()
        self.wfile.write(data)

    def _serve_query(self, params):
        view_name = params.get('view_name', [None])[0]
        if not view_name or view_name.upper() not in ALLOWED_VIEWS:
            self._send(400, {'error': f'view_name must be one of: {sorted(ALLOWED_VIEWS)}'})
            return

        view_name = view_name.upper()
        allowed_filters = FILTER_COLS.get(view_name, [])

        where_clauses = []
        for col in allowed_filters:
            val = params.get(col, [None])[0]
            if val and val.lower() != 'all':
                safe_val = val.replace("'", "''")
                where_clauses.append(f'"{col}" = \'{safe_val}\'')

        if where_clauses:
            sql = f'SELECT * FROM ANALYTICS."{view_name}" WHERE {" AND ".join(where_clauses)}'
        else:
            sql = f'SELECT * FROM ANALYTICS."{view_name}"'

        try:
            conn = get_conn()
            stmt = conn.execute(sql)
            cols = list(stmt.columns().keys())
            rows = [dict(zip(cols, row)) for row in stmt.fetchall()]
            conn.close()
            self._send(200, rows)
        except Exception as e:
            self._send(500, {'error': str(e)})

    def _send(self, code, data):
        body = json.dumps(data, default=str).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()

    with http.server.HTTPServer(('', args.port), Handler) as srv:
        print(f'Server running at http://localhost:{args.port}')
        srv.serve_forever()
