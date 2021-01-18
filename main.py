'''
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'
'''
import os,cv2
import numpy as np
from flask import Flask, render_template, send_from_directory, request, jsonify
from os.path import dirname,abspath

app = Flask(__name__)

UPLOAD_FOLDER = 'upload'
download='sivedownload'
app.config['download']=download
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER  # 设置文件上传的目标文件夹
basedir = os.path.abspath(os.path.dirname(__file__))  # 获取当前项目的绝对路径


ALLOWED_EXTENSIONS = set(['png', 'jpg', 'tif', 'JPG', 'PNG', 'bmp', 'gif', 'GIF'])  # 允许上传的文件后缀
file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])  # 拼接成合法文件夹地址
resive_dir=os.path.join(basedir,app.config['download'])
downfile=os.path.join(resive_dir,)
# 判断文件是否合法
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# 上传图片
@app.route('/',methods=['GET','POST'])
def upload_test():
    return render_template('upload.html')

#自定义resive
def resive(pic):
    with open('width.txt') as f:
        width=int(f.read())
    with open('height.txt') as f:
        height=int(f.read())
    img = cv2.imread(pic,cv2.IMREAD_COLOR)
    img = cv2.imdecode(np.fromfile(pic, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
    img_write = cv2.imencode('.png', img)[1].tofile(pic)
    new_img = cv2.resize(img, (width,height))
    p1, f1 = os.path.split(pic)  # 分离图片路径和名称
    cv2.imwrite(os.path.join(resive_dir,f1), new_img)

def ra_pic(path):
    filelist = os.listdir(path)
    for file in filelist:
        fileabs = os.path.join(path, file)
        if os.path.isfile(fileabs):
            resive(fileabs)
        else:
            ra_pic(fileabs)


@app.route('/api/upload', methods=['POST'], strict_slashes=False)
def api_upload():
    width=request.values.get('width')
    height=request.values.get('height')
    with open('width.txt', 'w') as f:
        f.write(width)
    with open('height.txt','w') as f:
        f.write(height)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)  # 文件夹不存在就创建
    f=request.files['file']  # 从表单的file字段获取文件
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname = f.filename
        f.save(os.path.join(file_dir,fname))  #保存文件到upload目录
        ra_pic(file_dir)
        return render_template('download.html',fname=fname)
    else:
        return jsonify({"errno": 1})

 # 下载图片 post文件上传之后之返回下载地址，在引导用户跳转到新地址去下载
@app.route("/download/<path:filename>")
def download(filename):
    if request.method == "GET":
        if os.path.isfile(os.path.join(resive_dir, filename)):
                return send_from_directory(resive_dir, filename, as_attachment=True)
if __name__ == '__main__':
    app.run(debug=True)

