#/usr/bin/env python
#coding utf-8

import logging
import json

import requests
from bottle import Bottle,request


from isolate_instance import *

logging.basicConfig(level=logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S')


app=Bottle()

@app.route('/isolate/:instance',method=['GET','POST'])
def isolate(instance):
    result={
            "status":"",
            "instance":instance
            }
    #req_data=json.loads(request.body.read())
    #if not req_data["instance"]==instance:
    #    result["status"]="NOT OK"
    #    logging.debug("The instance : {} is not expected ...".format(instance))
    #    return result
    try:
        isolate_r=isolate_instance(instance)
        tag_r=tag_instance(instance)
        if isolate_r["status"]=="OK" and tag_r["status"]=="OK":
            result["status"]="OK"
        else:
            logging.debug("The result of  isolate_instance() or tag_instance() is Wrong...")
            result["status"]="NOT OK"
    except Exception:
            logging.debug("Call isolate_instance() or tag_instance() Failed...")
            result["status"]="NOT OK"
    return result
        
@app.route('/recovery/:instance',method=['GET','POST'])
def recovery(instance):
    result={
            "status":"",
            "instance":instance
            }
    #req_data=json.loads(request.body.read())
    #if not req_data["instance"]==instance:
    #    logging.debug("The instance: {} is not expected".format(instance))
    #    result["status"]="NOT OK"
    #    return result
    try:
        cancel_isolate_r=cancel_isolate_instance(instance)
        cancel_tag_r=cancel_tag_instance(instance)
        if cancel_isolate_r["status"]=="OK" and cancel_tag_r["status"]=="OK":
            result["status"]="OK"
        else:
            logging.debug("The result of cancel_isolate_instance() or cancel_tag_instance is WRONG...")
            result["status"]="NOT OK"
    except Exception:
        logging.debug("Call cancel_isolate_instance() or cancel_tag_instance Failed...")
        result["status"]="NOT OK"
 
    return result


@app.route('/apps',method=['GET','POST'])
def apps():
    result={
            "status":"",
            "apps":[]
            }
    apps_s=set()
    if not os.path.isfile('haproxy_apps'):
        result["status"]="NOT OK"
        logging.debug("The apps' metadata doesn't exist...")
        return result
    try:
        with open('haproxy_apps','r+') as fd:
            for line in fd.readlines():
                apps_s.add(line.split()[0])
            apps=list(apps_s)
            result["apps"]=apps
            result["status"]="OK"
    except Exception:
        result["status"]="NOT OK"
        logging.debug("Read the file haproxy_apps failed...")
    return result

    
@app.route('/instances/:app',method=['GET','POST'])
def instances(app):
    result={
            "status":"",
            "app":app,
            "instances":[]
            }
    #req_data=json.loads(request.body.read())
    #print app.split()[0]
    #if not req_data["app"]==app:
     #   result["status"]="NOT OK"
      #  logging.debug("The app : {} is not expected ...".format(app))
       # return result
    try:
        app_instances_r=app_instances(app)
        instances=app_instances_r[1:]
        result["instances"]=instances
        result["status"]="OK"
    except Exception:
        logging.debug("Call the method app_instances() Failed...")
        result["status"]="NOT OK"
    return result

@app.route('/balance/:app',method=['GET','POST'])
def balance_algorithm(app):
    result={
            "status":"",
            "app":app,
            "balance":[]
            }
    get_balance()
    #req_data=json.loads(request.body.read())
    #if not req_data["app"]==app:
    #    logging.debug("The app : {} is not the expected ...".format(app))
    #    result["status"]="NOT OK"
    #    return result
    try:
        apps=[]
        balance=[]
        with open('haproxy_apps','r+') as fapp:
            print "============================================open haproxy_apps========================================"
            for line_app in fapp.readlines():
                apps.append(line_app.split()[0])
            print apps
        with open('balance_algorithm','r+') as fbalance:
            print "============================================open balance_algorithm========================================"
            for line_balance in fbalance.readlines():
                print "in for .................."
                print line_balance.split()
                balance_r=line_balance.split()[1]
                balance.append(balance_r)
            print balance
        combination=zip(apps,balance)
        print combination
        for iterm in combination:
            print iterm[0]==app
            if iterm[0]==app:
                result["balance"]=iterm[1]
                result["status"]="OK"
                break
    except Exception:
        logging.debug("Open haproxy_apps or balance_algorithm Failed...")
        result["status"]="NOT OK"
    return result
@app.route('/acl/:app',method=['GET','POST'])
def acl_list(app):
    result={
            "status":"",
            "acl":[]
            }
    #acl=[]
    #req_data=json.loads(request.body.read())
    #if req_data["acl"]!="test":
    #    logging.debug("The request body is not expect...")
    #    result["status"]="NOT OK"
    #    return result
    try:
        #with open('haproxy_acl','r+') as fd:
         #   for line in fd.readlines():
          #      acl.append(line.split()[0]+' '+line.split()[1])
           # result["acl"]=acl
        acl_r=get_acl(app)
        result["acl"]=acl_r
        result["status"]="OK"
    except Exception:
        logging.debug("Call get_acl() Failed...")
        result["status"]="NOT OK"
    return result
        
@app.route('/lbnodes/:app',method=['GET','POST'])
def combine(app):
    result={
            "status":"",
            "acl":[],
            "lbpolicy":[],
            }
    try:
        balance_r=balance_algorithm(app)
        logging.debug("==================================print balance_r===========================================")
        logging.debug(balance_r)
        result["lbpolicy"]=balance_r["balance"]
        acl_r=acl_list(app)
        logging.debug("==================================print acl_r===========================================")
        logging.debug(acl_r)
        if len(acl_r["acl"]):
            result["status"]=True
            result["acl"]=acl_r["acl"]
        else:
            result["status"]=False
            result["acl"]=acl_r["acl"]

    except Exception:
        logging.debug("Call balance_algorithm() or acl_list() Failed!!!...")

    return result

@app.route('/test',method=['GET','POST'])
def test_request():
    rq_data=json.loads(request.body.read())
    user=rq_data["user"]
    password=rq_data["password"]
    result={"status":"OK"}
    result.update(rq_data)
    return result

if __name__=='__main__':
    app.run(host='0.0.0.0',port=8888)
