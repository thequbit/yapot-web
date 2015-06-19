import uuid
import os
import magic
import json

import yapot

from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    MyModel,
    )

UPLOAD_FOLDER = './uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@view_config(route_name='home', renderer='templates/home.mak')
def view_home(request):

    return {}

@view_config(request_method='POST', route_name='doc_post')
def view_doc_post(request):

    resp = {}
    resp['code'] = 200
    resp['status'] = 'Success.'

    if 'file' in request.POST:

        #filename = request.POST['file'].filename
        doc_file = request.POST['file'].file

        doc_uid = '%s' % uuid.uuid4()

        filename = '%s/%s.pdf' % (UPLOAD_FOLDER, doc_uid)
        with open(filename, 'wb') as f:
            doc_file.seek(0)
            while True:
                data = doc_file.read(2<<16)
                if not data:
                    break
                f.write(data)

        if magic.from_file(filename, mime=True) == 'application/pdf':
            text = yapot.convert_document(filename, resolution=300, pool_count=8)
            with open('%s/%s.txt' % (UPLOAD_FOLDER, doc_uid), 'w') as f:
                f.write(text)
            resp['doc_uid'] = doc_uid
            resp['text'] = text
            resp['code'] = 200
            resp['status'] = "File uploaded successfully."
        else:
            resp['code'] = 415
            resp['status'] = "Invalid file type."

    else:
        resp['code'] = 400
        resp['status'] = "Missing file for upload."

    return Response(json.dumps(resp), content_type='application/json')

@view_config(request_method='GET', route_name='doc_get')
def view_doc_get(request):

    resp = {}
    resp['code'] = 200
    resp['status'] = 'Success.'

    doc_uid = request.matchdict['doc_uid']

    filename = '%s/%s.txt' % (UPLOAD_FOLDER, doc_uid)
    try:
        with open(filename, 'r') as f:
            text = f.read()
        resp['code'] = 200
        resp['status'] = 'Document contents retrieval successful.'
        resp['doc_uid'] = doc_uid
        resp['text'] = text
    except:
        resp['code'] = 404
        resp['status'] = 'Document not found/not converted.'

    return Response(json.dumps(resp), content_type='application/json')

@view_config(request_method='GET', route_name='doc_page')
def view_doc_page(request):

    code = 0
    status = 'Success.'

    return {'status': status, 'code': code}

'''
@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'yapot-web'}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_yapot-web_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
'''
