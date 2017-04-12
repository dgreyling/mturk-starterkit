import os
from flask import Flask, render_template, request, make_response, redirect, url_for
import pyrebase
import logging
import sys
import json
from interface import FirebaseInterface as DBInterface
from examples import examples


app = Flask(__name__, static_url_path='')
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

db = DBInterface()


def get_mturk():
    host = "https://workersandbox.mturk.com/mturk/externalSubmit"
    if request.args.get('prod', False):
        host = "https://www.mturk.com/mturk/externalSubmit"
    return {
        "worker_id": request.args.get("workerId", ''),
        "assignment_id": request.args.get("assignmentId", ''),
        "host": host,
        "hit_id": request.args.get("hitId", ''),
        "ip": request.environ.get('REMOTE_ADDR', '')
    }


@app.route('/example/<id>', methods=['GET'])
def example(id):
    mturk = get_mturk()
    d = db.get_example(id)
    return make_response(render_template(
        'example.pug',
        example_id=id,
        example=db.get_example(id),
        mturk=get_mturk(),
        examples=examples,
    ))


if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='run the server in debug mode')
    args = parser.parse_args()

    app.debug = args.debug
    try:
        # relaunch server when pug files change'
        app.run(extra_files=[os.path.join('templates', f) for f in os.listdir('templates') if f.endswith('.pug')])
    except Exception as e:
        print(e)
        raise e
