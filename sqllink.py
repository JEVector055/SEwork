import json
import pymysql
def linkcursor():
    settingsdict={}
    try:
        print(f"finding database settings. . .")
        with open('Settings.json','r',encoding='utf-8') as fp:
            settingsdict=json.load(fp)
    except Exception as e:
        print(f'Exception occurred:{e},please ensure Settings.json in folder processing.')
    else:
        print('success.')
        connection=pymysql.connect(
            host=settingsdict['host'],
            port=settingsdict['port'],
            user=settingsdict['user'],
            password=settingsdict['password'],
            database=settingsdict['database'],
            charset=settingsdict['charset']
            )
        try:
            cursor=connection.cursor()#建立游标
            cursor.execute(f"SHOW DATABASES LIKE '{settingsdict['database']}'")#检查数据库是否存在
            result=cursor.fetchone()
            if result:#数据库存在
                print(f"Database '{settingsdict['database']}' already exists, connecting...")    
            else:#数据库不存在，新建
                print(f"Database '{settingsdict['database']}' does not exist, creating...")
                cursor.execute(f"CREATE DATABASE {settingsdict['database']}")
                print(f"Database '{settingsdict['database']}' created successfully.")
            cursor.close()
        finally:#出现任意异常关闭连接
            connection.close() 
        return cursor    
    