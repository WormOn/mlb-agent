#!/usr/bin/env python
#coding=utf-8
__version__="V1.0"
import os
import re
import shutil

#应用列表
def apps_list():
    """
    return all  apps
    :None
    """
    if os.path.exists('haproxy_apps'):
        os.system('rm -rf haproxy_apps')
    with open('haproxy.cfg','r+') as fd:
        for line in fd.readlines():
            r_search=re.search('^backend',line)
            if r_search:
                r_sub=re.sub(r'backend ',"",line)
                r_sub2=re.sub(r'_.*$',"",r_sub)
                if r_sub2=='  use\n':
                    continue
                else:
                    with open('haproxy_apps','a+') as fapp:
                        fapp.write(r_sub2)
#所有应用和对应实例
def apps_instances():
    """
    return all apps and  instances 
    :None
    """
    if os.path.isfile('haproxy_apps_instances.original'):
        os.system('rm -rf haproxy_apps_instances.original')
    with open('pre_haproxy.cfg','r+') as fd:
        for line in fd.readlines():
            backend_r=re.search(r'backend',line)
            server_r=re.search(r'  server |#  server ',line)


            if backend_r:
                r_sub=re.sub(r'backend ',"",line)
                r_sub2=re.sub(r'_.*$',"",r_sub)
                if r_sub2=='  use\n':
                    continue
                else:
                    with open('haproxy_apps_instances.original','a+') as fapp:
                        fapp.write(r_sub2)


            if server_r:
                server_l=line.split()[1]+' '+line.split()[2]
                
                print (server_l)
                #os.system('echo  $server_l >> haproxy_app_instances')
                with open('haproxy_apps_instances.original','a+') as finstance:
                    server_l=server_l+'\n'
                    finstance.write(server_l)

#单个应用和对应实例
def app_instances(app_name):
    """
    return the specified app's name and the respond instances
    :app_name the specified app's name
    """
    with open('haproxy_apps_instances.current','r+') as fd:
        flag=False
        app_instances=[]
        for line in fd.readlines():
            match_r=re.match(app_name+'\n',line)
            if match_r:
                flag=True
                app_instances.append(line)
            elif flag:
                if len(line)>15:
                    split_r=line.split()
                    print (split_r)
                    if len(split_r)==2:
                        app_instances.append(line.split()[0]+' '+line.split()[1])
                    else:
                        app_instances.append(line.split()[0]+' '+line.split()[1]+' '+line.split()[2])
                else:
                    flag=False
        print (app_instances)
        return app_instances
#获取Haproxy的balance算法
def get_balance():
    """
    get the haproxy's load balance algorithm 
    :None
    """
    result={"status":"","balance":[]}
    if os.path.isfile('balance_algorithm'):
        os.system('rm -rf balance_algorithm')
    with open('haproxy.cfg','r+') as fd:
        for line in fd.readlines():
            search_r=re.search('  balance \w+',line)
            #print (search_r)
            if search_r:
                line=re.sub('^  ',"",line)
                print (line)
                with open('balance_algorithm','a+') as fb:
                    fb.write(line)

#获取Haproxy的ACL规则
def get_acl(app):
    """
    get the haproxy's acl rule
    :None
    """
    acl=[]
    if os.path.exists("haproxy_acl"):
        os.system("rm -rf haproxy_acl")

    with open("haproxy.cfg","r+") as fd:
        for line in fd.readlines():
            acl_r=re.match(r'  acl ',line)
            if acl_r:
                r=re.match(r"[\S\s]*?{}[\s]".format(app),line)
                if r:
                    logging.debug(line)
                    acl.append(line.split()[4])
    logging.debug(acl)
    return acl


        
#隔离实例
def isolate_instance(instance):
    """
    isolate specified instance
    :instance the instance to be isolated
    """
    result={"status":""}
    with open('pre_haproxy.cfg','r+') as fd:
        for line in fd.readlines():
            isolate_r=re.search(instance,line)
            with open('haproxy.cfg.tmp','a+') as ftmp:
                if isolate_r:
                    symbol_isolate_r=re.search(r'^#',line)
                    if symbol_isolate_r:
                        print("The instance: {} have been isolated...".format(instance))
                        result["status"]="OK"
                        ftmp.write(line)
                    else:
                        line='#'+line
                        ftmp.write(line)
                        result["status"]="OK"
                else:
                    ftmp.write(line)

    os.system('rm -rf pre_haproxy.cfg')
    os.rename('haproxy.cfg.tmp','pre_haproxy.cfg')
    return result
    #shutil.copy('/root/haproxy.cfg.tmp','/root/haproxy/haproxy.cfg')
#取消隔离
def cancel_isolate_instance(instance):
    """
    cancel the isolation of the specified instance
    :instance the specified instance the to be canceled isolation
    """
    result={"status":""}
    with open('haproxy.cfg','r+') as fd:
        for line in fd.readlines():
            isolate_r=re.search(instance,line)
            with open('haproxy.cfg.tmp','a+') as ftmp:
                if isolate_r:
                    symbol_isolate_r=re.search(r'^#',line)
                    if symbol_isolate_r:
                        result["status"]="OK"
                        print("The instance: {}  is canceling isolation...".format(instance))
                        line=re.sub('#',"",line)
                        ftmp.write(line)
                    else:
                        result["status"]="OK"
                        ftmp.write(line)
                else:
                    ftmp.write(line)

    os.system('rm -rf haproxy.cfg')
    os.rename('haproxy.cfg.tmp','haproxy.cfg')
    return result

#标记过滤以后的apps_instances中实例
def pre_tag_instance(instance):
    """
    tag the specified instance that to be isolated
    :instance the instance to be taged
    """
    if not os.path.isfile('haproxy_apps_instances.current'):
        with open('haproxy_apps_instances.original','r+') as fd:
            for line in fd.readlines():
                isolate_r=re.search(instance,line)
                with open('haproxy_apps_instances.current.tmp','a+') as ftmp:
                    if isolate_r:
                        line=line.split()[0]+' '+line.split()[1]+' '+'D'+'\n'
                        ftmp.write(line)
                    else:
                        ftmp.write(line)
            os.rename('haproxy_apps_instances.current.tmp','haproxy_apps_instances.current')
            os.system('rm -rf haproxy_apps_instances.current.tmp')
    else:
        with open('haproxy_apps_instances.current','r+') as fdcur:
            for line_cur in fdcur.readlines():
                with open('haproxy_apps_instances_current.transfer','a+') as ftrans:
                    cur_isolate_r=re.search(instance,line_cur)
                    if cur_isolate_r:
                        line_cur_end=re.search('D$',line_cur)
                        if line_cur_end:
                            print ('the instance:{} have been isolated already!'.format(instance))
                            ftrans.write(line_cur)
                        else:
                            line_cur=line_cur.split()[0]+' '+line_cur.split()[1]+' '+'D'+'\n'
                            ftrans.write(line_cur)
                    else:
                         ftrans.write(line_cur)
        os.system('rm -rf haproxy_apps_instances.current')
        os.rename('haproxy_apps_instances_current.transfer','haproxy_apps_instances.current')
                
#对指定实例进行隔离符号标记
def tag_instance(instance):
    """
    tag the specified instance
    :instance the instance that to be taged
    """
    result={"status":""}
    if not os.path.isfile('haproxy_apps_instances.current'):
        result["status"]="haproxy_apps_instances.current doesn't exist..."
        return result
    with open('haproxy_apps_instances.current','a+') as fd:
        for line in fd.readlines():
            tag_r=re.search(instance,line)
            if tag_r:
                with open('haproxy_apps_instances.tag','a+') as ftag:
                    symbol_tag_r=re.search('D',line)
                    if symbol_tag_r:
                        result["status"]="OK"
                        ftag.write(line)
                    else:
                        line=line.split()[0]+' '+line.split()[1]+' '+'D'+'\n'
                        ftag.write(line)
                        result["status"]="OK"
            else:
                with open('haproxy_apps_instances.tag','a+') as ftag2:
                    ftag2.write(line)
    os.system('rm -rf haproxy_apps_instances.current')
    os.rename('haproxy_apps_instances.tag','haproxy_apps_instances.current')
    return result

                



#对指定实例取消隔离标记
def cancel_tag_instance(instance):
    """
    cancel the isolation of the specified instance that have isolated before
    :instance the specified instance that have been isolated before
    """
    result={"status":""}
    if not os.path.isfile('haproxy_apps_instances.current'):
        result["status"]="NOT OK"
        return result
    with open('haproxy_apps_instances.current','r+') as fd:
        for line in fd.readlines():
            can_isolate_r=re.search(instance,line)
            if can_isolate_r:
                with open('haproxy_apps_instances.cancel','a+') as fcan:
                    symbol_r=re.search('D$',line)
                    if symbol_r:
                        line=re.sub('D',"",line)
                        fcan.write(line)
                        result["status"]="OK"
                    else:
                        fcan.write(line)
                        result["status"]="OK"
            else:
                with open('haproxy_apps_instances.cancel','a+') as fcan2:
                    fcan2.write(line)
        os.system('rm -rf haproxy_apps_instances.current')
        os.rename('haproxy_apps_instances.cancel','haproxy_apps_instances.current')
    return result





#在haproxy.cfg生成时，将haproxy.cfg进行一些处理
def haproxy_recreate():
    """
    from th haproxy.cfg generated by marathon-lb create the files that we will use
    """
    apps_instances()
    if os.path.isfile('haproxy_apps_instances.current'):
        with open('haproxy_apps_instances.current','r+') as fd:
            for line in fd.readlines():
                isolate_r=re.search(r'D',line)
                if isolate_r:
                    isolate_instance=line.split()[1]
                    isolate_instance(isolate_instance)
                    tag_instance(isolate_instance)

#在haproxy加载haproxy.cfg之前对haproxy.cfg进行必要处理
def haproxycfg_pre_ops():
    """
    operate the content of haproxy.cfg before  haporxy load haporxy.cfg
    :None
    """
    if os.path.isfile('haproxy_apps_instances.current'):
        os.rename('haproxy_apps_instances.current','haproxy_apps_instances.old')
        with open('haproxy_apps_instances.old','r+') as fd:
            for line in fd.readlines():
                isolate_r=re.search('D$',line)
                if isolate_r:
                    instance=line.split()[1]
                    isolate_instance(instance)
                    pre_tag_instance(instance)
            os.system('rm -rf haproxy_apps_instances.old')
    else:
        os.system('cp haproxy_apps_instances.original haproxy_apps_instances.current')
         

if __name__=='__main__':
    print("Test Module...")

    #tag_instance('192.168.1.14:31150')
    #r=cancel_tag_instance('192.168.1.14:31689')
    #cancel_isolate_instance('192.168.1.16:31295')
    #haproxycfg_pre_ops()
    #get_balance()
   # apps_instances()
    #pre_tag_instance('192.168.1.14:31689')

    #haproxy_recreate()isolate_instance('192.168.1.14:31053')
    #isolate_instance('192.168.1.14:31689')
    #r= app_instances('cgz')
   #print r

    #app_instance()
    #apps_list()
    #get_acl()
