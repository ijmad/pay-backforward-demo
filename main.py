#!/usr/bin/env python

from flask import Flask, redirect, url_for, request, make_response
import os
import requests

DEMO_APP_URL = os.environ['PAY_APP_URL']

app = Flask(__name__)

from random import randint
def id_generator():
  return randint(100000000,999999999)

@app.after_request
def cache_headers(response):    
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  response.headers['Pragma'] = 'no-cache'
  return response

def get_status(id):
  r = requests.get(os.environ['PAY_APP_URL'] + '/status/' + id)
  return r.json()

@app.route('/', methods = ['GET'])
def create_get():
    res = make_response(
      '<html><head><title>New Payment</title></head>'\
      '<body>'\
      '  <h1>Government Service</h1>'\
      '  <form action="' + url_for('create_post') + '" method="POST">'\
      '    <input type="hidden" name="id" value="' + str(id_generator()) + '" />' \
      '    <p><button type="submit">Create Payment</button></p>'\
      '  </form>'\
      '</body>'\
      '</html>'
    )
    
    res.set_cookie('id', '', expires=0)
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
            '<body>'\
            '  <h1>Government Service - Completed</h1>'\
            '  <p>You have already paid</p>'\
            '  <p><a href="' + url_for('returned', id=id) + '">Next</a></p>'\
            '</body>'\
            '</html>'
      else:
        return \
          '<html><head><title>Start Payment</title></head>'\
          '<body>'\
          '  <h1>Government Service - Resume Paying</h1>'\
          '  <p>Your payment is in progress</p>'\
          '  <p><a href="' + url_for('forward', id=id)  + '">Resume</a></p>'\
          '</body>'\
          '</html>'
    else:
      return \
        '<html><head><title>Start Payment</title></head>'\
        '<body>'\
        '  <h1>Government Service</h1>'\
        '  <p><a href="' + url_for('forward', id=id)  + '">Start Payment</a></p>'\
        '</body>'\
        '</html>'
        
        
@app.route('/forward/<int:id>', methods=['GET'])
def forward(id):
  return redirect(PAY_APP_URL + '/start/' + str(id), code=302)
  

@app.route('/return')
def returned():
    id = request.cookies.get('id')
    status = get_status(id)
    return \
      '<html><head><title>Payment Complete</title></head>'\
      '<body>'\
      '  <h1>Government Service</h1>'\
      '  <p>Payment ' + ('success' if status['success'] else 'FAILED') + ' - reference is ' + str(id) + '</p>'\
      '</body>'\
      '</html>'


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5555))
    app.run(host='0.0.0.0', port=port, debug=True)