"""A simple webserver for redirecting traffic to latest discussion thread"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import os

import praw


class Redirect(BaseHTTPRequestHandler):
    """Handle incoming requests"""

    def do_GET(self):
        """Handle HTTP GET requests"""
        self.send_response(302)
        try:
            self.send_header('Location', find_dt(self.path))
        except Exception:
            self.send_header('Location', 'https://reddit.com/r/neoliberal')
        self.end_headers()

    def log_message(self, *_):
        # Nginx logs are sufficient
        pass


def find_dt(path = ''):
    """Locate the current DT using praw.

    Assumes the existence of a 'neoliberal' object in outer scope
    """
    try:
        url = next(dt_bot.submissions.new(limit=1)).url
    except Exception:
        # If we can't find the DT for whatever reason, send people to the sub
        url = 'https://www.reddit.com/r/neoliberal'
    if path.strip('/') == 'dt/old':
        url = url.replace('www', 'old')
    elif path.strip('/') == 'dt/stream':
        url = url.replace('reddit.com', 'reddit-stream.com')
    elif path.strip('/') == 'dt/compact':
        url = url.replace('www', 'i')
    return(url)


if __name__ == "__main__":
    """Create our Reddit instance and run the webserver indefinitely"""
    reddit = praw.Reddit(
        client_id = os.environ['client_id'],
        client_secret = os.environ['client_secret'],
        refresh_token = os.environ['refresh_token'],
        user_agent = 'linux:dt_redirect:v1.1 (by /u/jenbanim)'
    )
    dt_bot = reddit.redditor(os.environ['dt_bot_username'])
    HTTPServer(("", 8080), Redirect).serve_forever()
