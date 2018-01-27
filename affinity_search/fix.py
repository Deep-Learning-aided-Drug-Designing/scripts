#!/usr/bin/env python

'''Grab all the "Sucess" examples from the database, look if any of the directories exist.
If they do, reval them and update the database'''

import sys, re, MySQLdb, os, argparse
from MySQLdb.cursors import DictCursor


parser = argparse.ArgumentParser(description='Fix evaluation of trained models.')
parser.add_argument('--data_root',type=str,help='Location of gninatypes directory',default='')
parser.add_argument('--prefix',type=str,help='Prefix, not including split',default='../data/refined/all_0.5_')
parser.add_argument('-p','--password',type=str,help='Database password',required=True)
args = parser.parse_args()
        
def getcursor():
    '''create a connection and return a cursor;
    doing this guards against dropped connections'''
    conn = MySQLdb.connect (host = "35.196.158.205",user = "opter",passwd=args.password,db="opt1")
    conn.autocommit(True)
    cursor = conn.cursor(DictCursor)
    return cursor

cursor = getcursor()
cursor.execute('SELECT * FROM params WHERE msg = "Sucess"')
rows = cursor.fetchall()
config = None
for row in rows:
    if not os.path.isdir(row['id']):
        continue
    
    print row['id']

    cmdline = './reval.py --prefix %s --data_root "%s" --split %d --dir %s' % \
            (args.prefix,args.data_root,row['split'], row['id'])
    print cmdline
    
    #call runline to insulate ourselves from catestrophic failure (caffe)
    try:
        output = subprocess.check_output(cmdline,shell=True,stderr=subprocess.STDOUT)
        d, R, rmse, auc, top = output.rstrip().split('\n')[-1].split()
    except Exception as e:
        print "Problem with",row['id']
        continue
    
    print d, R, rmse, auc, top
    sql = 'UPDATE params SET R={},rmse={} WHERE serial = {}'.format(R,rmse,row['serial'])
    cursor = getcursor()
    cursor.execute(sql)
