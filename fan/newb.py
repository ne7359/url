import re
import base64
import requests
import hashlib
import configparser
import json
headers = {'User-Agent': 'okhttp/3.15'}

def get_fan_conf():
    config = configparser.ConfigParser()
    config.read("fan/config.ini")

    url = 'http://饭太硬.com/tv'
    response = requests.get(url, headers=headers)
    match = re.search(r'[A-Za-z0]{8}\*\*(.*)', response.text)

    if not match:
        return
    result = match.group(1)

    m = hashlib.md5()
    m.update(result.encode('utf-8'))
    md5 = m.hexdigest()

    try:
        old_md5 = config.get("md5", "conf")
        if md5 == old_md5:
            print("No update needed")
            return
    except:
        pass

    content = base64.b64decode(result).decode('utf-8')
    url = re.search(r'spider"\:"(.*);md5;', content).group(1)
    content = content.replace(url, './fan/JAR/fan.txt')
    content = diy_conf(content)             # 这里添加diy_conf
    content = modify_content(content)
        
    # DIY添加自定义接口，写入b.json
    local_content = local_myconf(content)
    with open('c.json', 'w', encoding='utf-8') as f:
        for line in local_content.split('\n'):  # 将内容按行分割
            if line.strip():  # 如果该行非空（移除空白字符后有内容）
                f.write(line + '\n')  # 将非空行写入到文件中，记得在最后加上 '\n' 以保持原有的行分割

    # Update conf.md5
    config.set("md5", "conf", md5)
    with open("fan/config.ini", "w") as f:
        config.write(f)

    jmd5 = re.search(r';md5;(\w+)"', content).group(1)
    current_md5 = config.get("md5", "jar").strip()

    if jmd5 != current_md5:
        # Update jar.md5
        config.set("md5", "jar", jmd5)
        with open("fan/config.ini", "w") as f:
            config.write(f)

        response = requests.get(url)
        with open("./fan/JAR/fan.txt", "wb") as f:
            f.write(response.content)

def modify_content(content):   # 更改自定义
    # Replace specified key and name  替换"key":"豆豆","name":"全接口智能过滤广告" 为"key":"豆豆","name":"智能AI广告过滤"
    content = re.sub(r'{"key":"豆豆","name":"全接口智能过滤广告",', r'{"key":"豆豆","name":"智能AI广告过滤",', content)
    
    # 删除 //{"key":  整行
    content = re.sub(r'^\s*//\{"key":.*\n', '', content, flags=re.MULTILINE)
    
def diy_conf(content):
    #content = content.replace('https://fanty.run.goorm.site/ext/js/drpy2.min.js', './fan/JS/lib/drpy2.min.js')
    #content = content.replace('公众号【神秘的哥哥们】', '豆瓣')
    pattern = r'{"key":"Bili"(.)*\n{"key":"Biliych"(.)*\n'
    replacement = ''
    content = re.sub(pattern, replacement, content)
    pattern = r'{"key":"Nbys"(.|\n)*(?={"key":"cc")'
    replacement = ''
    content = re.sub(pattern, replacement, content)

    return content

def read_local_file(file_path):   # 用于加载read_local_file("./fan/res/replace.txt") 函数
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def local_myconf(content):
    # 从文件加载要添加的新内容
    new_content = read_local_file("./fan/res/parses_flags_rules.txt")
    # 替换指定模式的内容，从{"key":"88js"到{"key":"dr_兔小贝"前的内容
    pattern = r'{"key":"88js"(.|\n)*?(?={"key":"dr_兔小贝")'
    replacement = read_local_file("./fan/res/replace.txt")
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    pattern = r'{"name":"live","type"(.)*\n'
    replacement = read_local_file("./fan/res/lives.txt")
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    # 替换指定{"key":"cc"行内容
    pattern = r'{"key":"cc"(.)*\n'
    replacement = r'{"key":"cc","name":"请勿相信视频中广告","type":3,"api":"./fan/JS/lib/drpy2.min.js","ext":"./fan/JS/js/drpy.js"}\n'
    content = re.sub(pattern, replacement, content)
    # 查找并添加新内容
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        new_lines.append(line)
        if '"logo":"http' in line:
            # 在找到的行之后添加新内容
            new_lines.append(new_content)
    return '\n'.join(new_lines)

if __name__ == '__main__':
    get_fan_conf()