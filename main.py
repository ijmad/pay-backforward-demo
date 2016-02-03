#!/usr/bin/env python

from flask import Flask, redirect, url_for, request, make_response
import os
import requests

PAY_APP_URL = os.environ['PAY_APP_URL']

app = Flask(__name__)

@app.after_request
def cache_headers(response):    
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  response.headers['Pragma'] = 'no-cache'
  return response

def get_status(id):
  global PAY_APP_URL
  url = PAY_APP_URL + 'status/' + id
  r = requests.get(url)
  return r.json()

@app.route('/', methods = ['GET'])
def create_get():
    res = make_response(
      '<html>'\
      '<head>'\
      '  <title>New Payment</title>'\
      '  <script type="text/javascript">'\
      '    function set_id() {'\
      '      var id = Math.floor(Math.random() * 899999) + 100000;'\
      '      document.getElementById(\'id\').value = id;'\
      '      document.getElementById(\'iddiv\').innerHTML = id;'\
      '    }'\
      '  </script>'\
      '</head>'\
      '<body onload="set_id(); ">'\
      '  <form action="' + url_for('create_post') + '" method="POST" target="_blank">'\

      '    <input type="hidden" id="id" name="id" value="" />' \
      '    <p><button type="submit" onclick="set_id(); ">Start Back/Forward Demo</button></p>'\
      '    <p>ID = <span id="iddiv"></span></p>'\
      '    <p>(Opens in new Tab)</p>'
      '  </form>'\
      '</body>'\
      '</html>'
    )
    
    return res

@app.route('/', methods = ['POST'])
def create_post():
    id = request.form['id']
    res = make_response(redirect(url_for('start_get'), code = 302))
    res.set_cookie('id', id)
    return res

@app.route('/start', methods = ['GET'])
def start_get():
    id = request.cookies.get('id')
    status = get_status(id)
    if status['found']:
      if status['confirmed']:
          return \
            '<html><head><title>Start Payment</title></head>'\
            '<body style=\"font-size: 150%;\">'\
            '  <h1>Government Service</h1>'\
            '  <h2>Time to Pay</h2>'\
            '  <p>You have already paid</p>'\
            '  <p><a href="' + url_for('returned', id=id) + '">Next</a></p>'\
            '</body>'\
            '</html>'
      else:
        return \
          '<html><head><title>Start Payment</title></head>'\
          '<body style=\"font-size: 150%;\">'\
          '  <h1>Government Service - Resume Paying</h1>'\
          '  <h2>Time to Pay</h2>'\
          '  <p>Your payment is in progress</p>'\
          '  <p><a href="' + url_for('forward', id=id)  + '">Resume</a></p>'\
          '</body>'\
          '</html>'
    else:
      return \
        '<html><head><title>Start Payment</title></head>'\
        '<body style=\"font-size: 150%;\">'\
        '  <h1>Government Service</h1>'\
        '  <h2>Time to Pay</h2>'\
        '  <p><a href="' + url_for('forward', id=id)  + '">Start Payment</a></p>'\
        '</body>'\
        '</html>'
        
        
@app.route('/forward/<int:id>', methods=['GET'])
def forward(id):
  global PAY_APP_URL
  return redirect(PAY_APP_URL + 'start/' + str(id), code=302)
  

@app.route('/return')
def returned():
    id = request.cookies.get('id')
    status = get_status(id)
    return \
      '<html><head><title>Payment Complete</title></head>'\
      '<body style="font-size: 150%;">'\
      '  <h1>Government Service</h1>'\
      '  <h2>Payment Outcome</h2>'\
      '  <p>Payment ' + ('success' if status['success'] else 'FAILED') + ' - reference is ' + str(id) + '</p>'\
      '</body>'\
      '</html>'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)