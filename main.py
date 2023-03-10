# coding:utf8
import time
import re
import sys

# 版本提示
if 3 > sys.version_info.major or 6 > sys.version_info.minor:
    ver = sys.version_info
    ver = str(ver.major) + '.' + str(ver.minor) + '.' + str(ver.micro)
    raise SystemExit('请使用 Python3.6+ 以上版本运行，当前版本：' + ver)

#
http_lib = 'raw'
try:
    import requests

    http_lib = 'requests'
except ImportError:
    from urllib import request, parse
    from json import dumps as json_stringify, loads as json_parse

"""
做 requests 库兼容
    没安装 requests 库，则切换成使用系统自带的 urllib 库发送请求
    这里不实现没用到的功能
"""


class Http(object):
    headers: dict = {}
    use_http_lib: str = ''
    __resp_content: str = ''

    def __init__(self, headers: dict[str, str] = {}, use_http_lib: str = http_lib):
        self.headers = headers
        self.use_http_lib = use_http_lib

    def json(self, **kwargs):
        return json_parse(self.__resp_content, **kwargs)

    @property
    def text(self):
        return self.__resp_content

    content = text

    def _post(self, url: str, json: dict = None):
        self.headers.setdefault('content-type', 'application/json')
        resp = request.urlopen(
            request.Request(url, method='POST', headers=self.headers,
                            data=json and json_stringify(json).encode('utf-8') or b'')
        )
        self.__resp_content = resp.read().decode('utf-8')
        return self

    def post(self, url: str, json: dict = None):
        if self.use_http_lib == 'raw':
            return self._post(url, json)
        return requests.post(url, json=json, headers=self.headers)


class Yun(object):
    # 想直接使用 requests 库，可以换成 requests.Session()
    http = Http()
    http.headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
    }
    api_url: str = 'http://my.yunt.pro/api'
    ssr_matcher = re.compile(r"(ssr://[^'\"]+?)'")

    def __init__(self):
        print('=' * 10, '助力每一个梦想，动动手指关注公众号：随心记事', '=' * 10)

    def login(self, name: str = '', password: str = '') -> str:
        password = password or name
        print(f'准备执行登录流程 -> 账号：{name} | 密码：{password}')
        resp = self.http.post(self.api_url + '/login', json={
            "email": name,
            "password": password,
            "terminal": "windows"
        }).json()
        if resp['code'] != 200:
            print('登录失败：', resp['message'])
            return ''
        return resp['token']

    def register(self, name: str = f'{int(time.time())}@qq.com') -> tuple[str, str, int]:
        print(f'准备执行注册流程 -> 账号：{name} | 密码：{name}')
        resp = self.http.post(self.api_url + '/signup', json={
            "email": name,
            "password": name,
            "terminal": "windows"
        }).json()
        if resp['code'] != 200:
            print('注册失败：', resp['message'])
            return '', '', 0
        return name, name, resp['user_id']

    def get_ssr_nodes(self, token: str = '', name: str = '', password: str = '') -> list:
        print(f'准备尝试获取节点信息..')
        if name:
            token = self.login(name, password)
        if not token:
            print('获取失败！')
            return []
        resp = self.http.post(self.api_url + '/users/1256480/ssrnodes', json={
            'token': token
        }).json()
        if resp['code'] != 200:
            print('获取节点失败：', resp['message'])
            return []
        return self.ssr_matcher.findall(str(resp['nodes']))

    def auto_get_ssr_nodes(self, save_path: str = 'ssr.txt', display_result: bool = True):
        with open(save_path, 'w') as f:
            nodes = '\n'.join(self.get_ssr_nodes(self.login(self.register()[0])))
            if not nodes:
                return
            f.write(nodes)
            if display_result:
                print(nodes)
            print('已将节点信息写入:', save_path)
            return nodes


if __name__ == '__main__':
    Yun().auto_get_ssr_nodes(display_result=False)

    ssr_download_link = 'https://ghproxy.com/https://github.com/shadowsocksrr/shadowsocksr-csharp/releases/download/4.9.2/ShadowsocksR-win-4.9.2.zip'
    print(f"生成的节点需要配合 SSR (ShadowsocksR) 使用，下载地址：\n{ssr_download_link}\n\n使用方法：复制文本里面的内容，选择从剪切板中导入即可")
