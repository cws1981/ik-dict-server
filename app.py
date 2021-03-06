import sys

from bloom_filter2 import BloomFilter
from flask import Flask, request
from waitress import serve

import configparser

app = Flask(__name__)

# 布隆过滤器，词库去重复
bloom: BloomFilter

# 创建配置文件对象
config = configparser.ConfigParser()

# 读取文件
config.read('config/config.ini', encoding='utf-8')


@app.post('/dict')
def put_dict():
    body = request.json
    dicts = body.get("dicts")
    with open(config['app']['dict_file'], 'a') as f:
        for word in dicts:
            if word in bloom:
                continue
            f.write(word + '\n')
            bloom.add(word)

    return "Done"


@app.delete('/dict')
def delete():
    body = request.json
    dicts = body.get("dicts")

    with open(config['app']['dict_file'], 'r') as f:
        lines = f.readlines()
    with open(config['app']['dict_file'], 'w') as f_w:
        for line in lines:
            word2 = line.strip("\n")
            existed = False
            for word in dicts:
                if word == word2:
                    existed = True
                    break

            if existed:
                continue
            f_w.write(line)

        load_dict()

    return 'Done'


def load_dict():
    print('dict loading...')
    global bloom
    bloom = BloomFilter(max_elements=1000000, error_rate=0.0001)
    with open(config['app']['dict_file'], 'r') as f:
        line = f.readline()
        while line:
            # print(line, end='')
            word = line.strip('\n')
            bloom.add(word)
            line = f.readline()


if __name__ == '__main__':
    try:
        load_dict()
    except:
        print('load dict error!')
    print('server start at port:'+config['app']['port'])
    serve(app, listen='*:'+config['app']['port'])
    # waitress-serve --port=5000 app:app
