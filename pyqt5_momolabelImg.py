import codecs
import json
import os
import os.path
import pickle
import platform
import shutil
import sys
import webbrowser
from collections import OrderedDict
from csv import writer
from datetime import datetime
from enum import Enum
from functools import lru_cache, partial
from getpass import getuser
from hashlib import md5, sha256
from itertools import chain
from locale import getdefaultlocale, getlocale
from os import getcwd
from pathlib import Path
from re import findall, split, compile as recompile
from shutil import copy2
from socket import gethostname, gethostbyname
from time import localtime, strftime, time
from traceback import print_exc
from uuid import getnode
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement

import yaml
from cv2 import cvtColor, imdecode, COLOR_GRAY2BGR, COLOR_BGRA2BGR, imencode
from loguru import logger
from lxml import etree
from numpy import sqrt, uint8, fromfile, std
from pytz import UTC
from unidecode import unidecode


# ================================参数区================================
def a1_const():
    return


# Platforms
SYSTEM = ''
platform_system = platform.system()
os_uname = platform.uname()
os_kernal = os_uname.machine
if os_kernal in ['x86_64', 'AMD64']:
    if platform_system == 'Windows':
        SYSTEM = 'WINDOWS'
    elif platform_system == 'Linux':
        SYSTEM = 'LINUX'
    else:  # 'Darwin'
        SYSTEM = 'MAC'
else:  # os_kernal = 'arm64'
    if platform_system == 'Darwin':
        SYSTEM = 'M1'
    else:
        SYSTEM = 'PI'

if SYSTEM == 'M1':
    qt_lib = 'PyQt6'
else:  # SYSTEM in ['WINDOWS', 'MAC', 'LINUX']
    qt_lib = 'PyQt5'

if qt_lib == 'PyQt5':
    from PyQt5.QtCore import QVariant, QByteArray, QFileInfo, QProcess, QPoint, QSize, QPointF, QTimer, \
        QRegExp, QCoreApplication, pyqtSignal, QStringListModel, Qt, QLocale, QRect
    from PyQt5.QtGui import QIcon, QCursor, QPixmap, QBrush, QWindow, QPainterPath, QRegExpValidator, QFont, QColor, \
        QFontMetrics, QImage, QPainter, QPen, QImageReader
    from PyQt5.QtWidgets import QColorDialog, QCompleter, QToolBar, QDialogButtonBox, QDockWidget, QMessageBox, \
        QLineEdit, QSpinBox, QComboBox, QAbstractSpinBox, QFileDialog, QDialog, QListWidgetItem, QPushButton, \
        QHBoxLayout, QAction, QLabel, QVBoxLayout, QCheckBox, QToolButton, QWidget, QApplication, QMainWindow, QMenu, \
        QListWidget, QScrollArea, QWidgetAction, QStatusBar, QSizePolicy
else:
    from PyQt6.QtCore import QByteArray, QFileInfo, QProcess, QPoint, QSize, QPointF, QTimer, \
        QCoreApplication, QStringListModel, QLocale, Qt, pyqtSignal, QRect
    from PyQt6.QtGui import QIcon, QCursor, QPixmap, QBrush, QWindow, QPainterPath, QFont, QColor, \
        QFontMetrics, QImage, QPainter, QPen, QImageReader, QAction
    from PyQt6.QtWidgets import QColorDialog, QCompleter, QToolBar, QDialogButtonBox, QDockWidget, QMessageBox, \
        QLineEdit, QSpinBox, QComboBox, QAbstractSpinBox, QFileDialog, QDialog, QListWidgetItem, QPushButton, \
        QHBoxLayout, QLabel, QVBoxLayout, QCheckBox, QToolButton, QWidget, QApplication, QMainWindow, QMenu, \
        QListWidget, QScrollArea, QWidgetAction, QStatusBar, QSizePolicy
    from PyQt6.QtGui import QRegularExpressionValidator
    from PyQt6.QtCore import QRegularExpression

locale_tup = getdefaultlocale()
language_code = locale_tup[0]
if language_code == 'zh_CN':
    lang = 'Chinese'
else:
    lang = 'English'

username = getuser()
homedir = os.path.expanduser('~')
homedir = Path(homedir)
DOWNLOADS = homedir / 'Downloads'
DOCUMENTS = homedir / 'Documents'

mac_address = ':'.join(findall('..', '%012x' % getnode()))
uname = platform.uname()
node_name = uname.node

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = Path(current_dir)

dirpath = getcwd()
ProgramFolder = Path(dirpath)
UserDataFolder = ProgramFolder / 'MomoYoloUserData'

app_en_name = 'momoyolo'

# 全局配置
global_config_yml = UserDataFolder / f'{app_en_name}-config-global.yml'
# 用户配置
user_config_yml = UserDataFolder / f'{app_en_name}-config-user.yml'
# 软件配置
custom_config_yml = UserDataFolder / f'{app_en_name}-config-custom.yml'

en_qm = UserDataFolder / f'{app_en_name}_en.qm'
cn_qm = UserDataFolder / f'{app_en_name}_cn.qm'
cn_csv = UserDataFolder / f'{app_en_name}_cn.csv'
dst_txt = UserDataFolder / f'{app_en_name}_cn.txt'
zh_ts = UserDataFolder / f'{app_en_name}_cn.ts'
py_name = f'pyqt5_{app_en_name}.py'
py_path = ProgramFolder / py_name

if SYSTEM == 'WINDOWS':
    encoding = 'gbk'
    line_feed = '\r\n'
    cmct = 'ctrl'
    loop_time_leng = 100
    style_qss = UserDataFolder / 'style_win.qss'

else:  # Mac
    encoding = 'utf-8'
    line_feed = '\n'
    cmct = 'command'
    loop_time_leng = 1000
    style_qss = UserDataFolder / 'style_mac.qss'

line_feeds = line_feed * 2

lf = line_feed
lfs = line_feeds

_punct_re = recompile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')

DATE_FORMATTER = '%Y-%m-%d %H:%M:%S'

ignores = ('~$', '._')

type_dic = {
    'xlsx': '.xlsx',
    'csv': '.csv',
    'pr': '.prproj',
    'psd': '.psd',
    'tor': '.torrent',
    'xml': '.xml',
    'audio': ('.aif', '.mp3', '.wav'),
    'video': ('.mp4', '.mkv', '.rm', '.ts', '.flv'),
    'vid': ('.asf', '.avi', '.gif', '.m4v', '.mkv', '.mov', '.mp4', '.mpeg', '.mpg', '.ts', '.wmv'),
    'compressed': ('.zip', '.rar'),
    'font': ('.ttc', '.ttf'),
    'comic': ('.cbr', '.cbz', '.rar', '.zip', '.pdf', '.txt'),
    'pic': ('.jpg', '.jpeg', '.png', '.gif'),
    'img': ('.bmp', '.dng', '.jpeg', '.jpg', '.mpo', '.png', '.tif', '.tiff', '.webp'),
    'log': '.log',
    'json': '.json',
    'pickle': '.pkl',
    'python': '.py',
    'txt': '.txt',
    'yml': ('.yml', '.yaml'),
    'label': ('.xml', '.txt', '.json'),
    'labelpic': ('.bmp', '.cur', '.gif', '.icns', '.ico', '.jpeg', '.jpg', '.pbm', '.pdf', '.pgm', '.png', '.ppm',
                 '.svg', '.svgz', '.tga', '.tif', '.tiff', '.wbmp', '.webp', '.xbm', '.xpm'),
}

__appname__ = 'labelImg'

os.environ['QT_IMAGEIO_MAXALLOC'] = "256"  # 能够打开的图片的最大大小

# extensions = ['.%s' % fmt.data().decode("ascii").lower() for fmt in QImageReader.supportedImageFormats()]
extensions = [
    '.bmp', '.cur', '.gif', '.icns', '.ico', '.jpeg', '.jpg', '.pbm', '.pdf', '.pgm', '.png', '.ppm',
    '.svg', '.svgz', '.tga', '.tif', '.tiff', '.wbmp', '.webp', '.xbm', '.xpm'
]

pictures_exclude = '加框,分框,框,涂白,填字,修图,-,copy,副本,拷贝,顺序,打码,测试,标注'
pic_tuple = tuple(pictures_exclude.split(','))

explain_names = [
    'images', 'labels', 'image', 'label',
    'train', 'test', 'valid', 'val',
    'annotation', 'annotations',
    'export',
    'all', 'manual', 'other', 'others', 'preview',
]

PROP_SEPERATOR = '='

area_size = 60
ratio = 4
glassSize = area_size * ratio

SETTING_FILENAME = 'filename'
SETTING_RECENT_FILES = 'recentFiles'
SETTING_WIN_SIZE = 'window/size'
SETTING_WIN_POSE = 'window/position'
SETTING_WIN_GEOMETRY = 'window/geometry'
SETTING_LINE_COLOR = 'line/color'
SETTING_FILL_COLOR = 'fill/color'
SETTING_ADVANCE_MODE = 'advanced'
SETTING_WIN_STATE = 'window/state'
SETTING_SAVE_DIR = 'savedir'
SETTING_PAINT_LABEL = 'paintlabel'
SETTING_LAST_OPEN_DIR = 'lastOpenDir'
SETTING_AUTO_SAVE = 'autosave'
SETTING_SINGLE_CLASS = 'singleclass'
FORMAT_PASCALVOC = 'PascalVOC'
FORMAT_YOLO = 'YOLO'
FORMAT_CREATEML = 'CreateML'
SETTING_DRAW_SQUARE = 'draw/square'
SETTING_Magnifying_Lens = "magnifyinglens"
SETTING_LABEL_FILE_FORMAT = 'labelFileFormat'
DEFAULT_ENCODING = 'utf-8'

TXT_EXT = '.txt'
XML_EXT = '.xml'
JSON_EXT = '.json'
ENCODE_METHOD = DEFAULT_ENCODING

DEFAULT_LINE_COLOR = QColor(0, 255, 0, 128)
DEFAULT_FILL_COLOR = QColor(255, 0, 0, 128)
DEFAULT_SELECT_LINE_COLOR = QColor(255, 255, 255)
DEFAULT_SELECT_FILL_COLOR = QColor(0, 128, 255, 155)
DEFAULT_VERTEX_FILL_COLOR = QColor(0, 255, 0, 255)
DEFAULT_HVERTEX_FILL_COLOR = QColor(255, 0, 0)

CURSOR_DEFAULT = Qt.CursorShape.ArrowCursor
CURSOR_POINT = Qt.CursorShape.PointingHandCursor
CURSOR_DRAW = Qt.CursorShape.CrossCursor
CURSOR_MOVE = Qt.CursorShape.ClosedHandCursor
CURSOR_GRAB = Qt.CursorShape.OpenHandCursor

qss_cn = """
QMessageBox QPushButton[text="OK"] {
    qproperty-text: "好的";
}
QMessageBox QPushButton[text="Open"] {
    qproperty-text: "打开";
}
QMessageBox QPushButton[text="Save"] {
    qproperty-text: "保存";
}
QMessageBox QPushButton[text="Cancel"] {
    qproperty-text: "取消";
}
QMessageBox QPushButton[text="Close"] {
    qproperty-text: "关闭";
}
QMessageBox QPushButton[text="Discard"] {
    qproperty-text: "放弃";
}
QMessageBox QPushButton[text="Don't Save"] {
    qproperty-text: "不保存";
}
QMessageBox QPushButton[text="Apply"] {
    qproperty-text: "应用";
}
QMessageBox QPushButton[text="Reset"] {
    qproperty-text: "重置";
}
QMessageBox QPushButton[text="Restore Defaults"] {
    qproperty-text: "恢复默认";
}
QMessageBox QPushButton[text="Help"] {
    qproperty-text: "帮助";
}
QMessageBox QPushButton[text="Save All"] {
    qproperty-text: "保存全部";
}
QMessageBox QPushButton[text="&Yes"] {
    qproperty-text: "是";
}
QMessageBox QPushButton[text="Yes to &All"] {
    qproperty-text: "全部都是";
}
QMessageBox QPushButton[text="&No"] {
    qproperty-text: "否";
}
QMessageBox QPushButton[text="N&o to All"] {
    qproperty-text: "全部都不";
}
QMessageBox QPushButton[text="Abort"] {
    qproperty-text: "终止";
}
QMessageBox QPushButton[text="Retry"] {
    qproperty-text: "重试";
}
QMessageBox QPushButton[text="Ignore"] {
    qproperty-text: "忽略";
}

QDialogButtonBox QPushButton[text="OK"] {
    qproperty-text: "好的";
}
QDialogButtonBox QPushButton[text="Open"] {
    qproperty-text: "打开";
}
QDialogButtonBox QPushButton[text="Save"] {
    qproperty-text: "保存";
}
QDialogButtonBox QPushButton[text="Cancel"] {
    qproperty-text: "取消";
}
QDialogButtonBox QPushButton[text="Close"] {
    qproperty-text: "关闭";
}
QDialogButtonBox QPushButton[text="Discard"] {
    qproperty-text: "放弃";
}
QDialogButtonBox QPushButton[text="Don't Save"] {
    qproperty-text: "不保存";
}
QDialogButtonBox QPushButton[text="Apply"] {
    qproperty-text: "应用";
}
QDialogButtonBox QPushButton[text="Reset"] {
    qproperty-text: "重置";
}
QDialogButtonBox QPushButton[text="Restore Defaults"] {
    qproperty-text: "恢复默认";
}
QDialogButtonBox QPushButton[text="Help"] {
    qproperty-text: "帮助";
}
QDialogButtonBox QPushButton[text="Save All"] {
    qproperty-text: "保存全部";
}
QDialogButtonBox QPushButton[text="&Yes"] {
    qproperty-text: "是";
}
QDialogButtonBox QPushButton[text="Yes to &All"] {
    qproperty-text: "全部都是";
}
QDialogButtonBox QPushButton[text="&No"] {
    qproperty-text: "否";
}
QDialogButtonBox QPushButton[text="N&o to All"] {
    qproperty-text: "全部都不";
}
QDialogButtonBox QPushButton[text="Abort"] {
    qproperty-text: "终止";
}
QDialogButtonBox QPushButton[text="Retry"] {
    qproperty-text: "重试";
}
QDialogButtonBox QPushButton[text="Ignore"] {
    qproperty-text: "忽略";
}
"""


# ================================基础函数区================================
def a2_base():
    return


# ================创建目录================
def make_dir(file_path):
    if not os.path.exists(file_path):
        try:
            # os.mkdir(file_path)
            os.makedirs(file_path)
        except Exception as e:
            print(e)


# ================运行时间计时================
# @logger.catch
def run_time(start_time):
    rtime = time() - start_time
    show_run_time = ''
    if rtime >= 3600:
        show_run_time += f'{(rtime // 3600):.0f}时'
    if rtime >= 60:
        show_run_time += f'{(rtime % 3600 // 60):.0f}分'
    show_run_time += f'{(rtime % 60):.2f}秒'
    return show_run_time


# ================当前时间================
# @logger.catch
def current_time():
    now_time_str = strftime(DATE_FORMATTER, localtime())
    return now_time_str


# @logger.catch
def time_utcnow():
    """Returns a timezone aware utc timestamp."""
    return datetime.now(UTC)


@logger.catch
def clam(n, minn, maxn):
    return max(min(maxn, n), minn)


# @logger.catch
def slugify(text, delim=u'-'):
    """Generates an ASCII-only slug."""
    result = []
    for word in _punct_re.split(text.lower()):
        result.extend(unidecode(word).lower().split())
    return delim.join(result)


# @logger.catch
def is_str(input_par):
    return isinstance(input_par, str)


# @logger.catch
def is_list(input_par):
    return isinstance(input_par, list)


# @logger.catch
def is_dict(input_par):
    return isinstance(input_par, dict)


# @logger.catch
def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows',
    }
    if sys.platform not in platforms:
        return sys.platform
    return platforms[sys.platform]


# @logger.catch
def getSystemInfo():
    SystemInfo = {'platform': platform.system(),
                  'platform-release': platform.release(),
                  'platform-version': platform.version(),
                  'architecture': platform.machine(),
                  'hostname': gethostname(),
                  'mac-address': ':'.join(findall('..',
                                                  '%012x' % getnode())),
                  'processor': platform.processor()}

    try:
        SystemInfo['ip-address'] = gethostbyname(gethostname())
    except BaseException as e:
        printe(e)

    try:
        from psutil import virtual_memory
        virtual_mem = virtual_memory().total / (1024.0 ** 3)
        SystemInfo['ram'] = f'{round(virtual_mem)} GB'
    except BaseException as e:
        printe(e)

    return SystemInfo


# ================对文件算MD5================
# @logger.catch
def md5_w_size(path, blocksize=2 ** 20):
    if os.path.isfile(path) and os.path.exists(path):  # 判断目标是否文件,及是否存在
        file_size = os.path.getsize(path)
        if file_size <= 256 * 1024 * 1024:  # 512MB
            hash_object = md5(open(path, 'rb').read())
            this_md5 = hash_object.hexdigest()
            return this_md5, file_size
        else:
            m = md5()
            with open(path, 'rb') as f:
                while True:
                    buf = f.read(blocksize)
                    if not buf:
                        break
                    m.update(buf)
            this_md5 = m.hexdigest()
            return this_md5, file_size
    else:
        return None


@logger.catch
def hex2int(hex_num):
    hex_num = f'0x{hex_num}'
    int_num = int(hex_num, 16)
    return int_num


@logger.catch
def int2hex(int_num):
    hex_num = hex(int_num)
    hex_num = hex_num.replace('0x', '')
    return hex_num


@logger.catch
def loge(imes, loglevel=None, holder=None):
    if loglevel == 'success':
        logger.debug(imes)
    elif loglevel == 'info':
        logger.info(imes)
    elif loglevel == 'warning':
        logger.warning(imes)
    elif loglevel == 'error':
        logger.error(imes)
    elif loglevel == 'code':
        logger.info(imes)
    elif loglevel == 'debug':
        logger.debug(imes)
    elif loglevel == 'write':
        logger.info(imes)
    else:
        logger.warning(imes)


@logger.catch
def printe(e):
    # print(e)
    logger.error(e)
    print_exc()


@logger.catch
@lru_cache
def get_files(rootdir, file_type, direct=False):
    file_paths = []

    suffixes = None
    if file_type in type_dic:
        suffixes = type_dic[file_type]
    if isinstance(suffixes, str):
        suffixes = (suffixes,)

    if rootdir and rootdir.exists():
        if direct:
            # ================只读取当前文件夹下的文件================
            files = os.listdir(rootdir)
            for file in files:
                file_path = Path(rootdir) / file
                if file_path.stem.startswith(ignores):
                    pass
                else:
                    if file_path.is_file():
                        if suffixes:
                            if file_path.suffix.lower() in suffixes:
                                file_paths.append(file_path)
                        else:
                            file_paths.append(file_path)
        else:
            # ================读取所有文件================
            for root, dirs, files in os.walk(rootdir):
                for file in files:
                    file_path = Path(root) / file
                    if file_path.stem.startswith(ignores):
                        pass
                    else:
                        if suffixes:
                            if file_path.suffix.lower() in suffixes:
                                file_paths.append(file_path)
                        else:
                            file_paths.append(file_path)
    file_paths.sort()
    return file_paths


# ================获取文件夹列表================
def get_dirs(rootdir):
    dirs_list = []
    lines = os.listdir(rootdir)  # 列出目录下的所有文件和目录
    for line in lines:
        filepath = Path(rootdir) / line
        if filepath.is_dir():
            dirs_list.append(filepath)
    dirs_list.sort()
    return dirs_list


def reduce_list(input_list):
    output_list = list(OrderedDict.fromkeys(input_list))
    return output_list


def int2time(timestamp, formatter='%Y-%m-%d %H:%M:%S'):
    timestamp = int(timestamp)
    timestamp /= 1000
    time_str = datetime.utcfromtimestamp(timestamp).strftime(formatter)
    return time_str


@logger.catch
def desel_list(old_list, tup, method='stem'):
    if method == 'name':
        new_list = [x for x in old_list if not x.name.endswith(tup)]
    else:
        new_list = [x for x in old_list if not x.stem.endswith(tup)]
    return new_list


@logger.catch
def sel_list(old_list, tup, method='stem'):
    if method == 'name':
        new_list = [x for x in old_list if x.name.endswith(tup)]
    else:
        new_list = [x for x in old_list if x.stem.endswith(tup)]
    return new_list


# ================读取文本================
@logger.catch
def read_txt(file_path, encoding='utf-8'):
    file_content = None
    if file_path.exists():
        file_object = open(file_path, mode='r', encoding=encoding)
        try:
            file_content = file_object.read()
        finally:
            file_object.close()
    return file_content


@logger.catch
def read_img(img_path, to_BGR=True):
    input_img = imdecode(fromfile(img_path, dtype=uint8), -1)
    output_img = input_img
    if to_BGR:
        if len(input_img.shape) == 2:
            # input_img_mode = 'BW'
            input_img_bgr = cvtColor(input_img, COLOR_GRAY2BGR)
        elif input_img.shape[2] == 3:
            # input_img_mode = 'BGR'
            input_img_bgr = input_img
        else:
            # input_img_mode = 'BGRA'
            input_img_bgr = cvtColor(input_img, COLOR_BGRA2BGR)
        output_img = input_img_bgr
    return output_img


@logger.catch
def write_img(pic_path, target_img):
    if isinstance(pic_path, str):
        pic_path = Path(pic_path)
    ext = pic_path.suffix
    imencode(ext, target_img)[1].tofile(pic_path)
    return


# ================写入文件================
@logger.catch
def write_txt(file_path, text_input, encoding='utf-8', ignore_empty=True):
    if text_input:
        save_text = True

        if isinstance(text_input, list):
            otext = lf.join(text_input)
        else:
            otext = text_input

        file_content = None
        if Path(file_path).exists():
            file_object = open(file_path, mode='r', encoding=encoding)
            try:
                file_content = file_object.read()
            finally:
                file_object.close()

        if file_content == otext:
            save_text = False
        elif ignore_empty and otext == '':
            save_text = False

        if save_text:
            f = open(file_path, mode='w', encoding=encoding, errors='ignore')
            try:
                f.write(otext)
            finally:
                f.close()


# ================保存 CSV================
@logger.catch
def write_csv(csv_path, data_input, headers=None):
    temp_csv = csv_path.parent / 'temp.csv'

    try:
        if isinstance(data_input, list):
            if len(data_input) >= 1:
                if csv_path.exists():
                    with codecs.open(temp_csv, 'w', 'utf_8_sig') as f:
                        f_csv = writer(f)
                        if headers:
                            f_csv.writerow(headers)
                        f_csv.writerows(data_input)
                    if md5_w_size(temp_csv) != md5_w_size(csv_path):
                        copy2(temp_csv, csv_path)
                    if temp_csv.exists():
                        os.remove(temp_csv)
                else:
                    with codecs.open(csv_path, 'w', 'utf_8_sig') as f:
                        f_csv = writer(f)
                        if headers:
                            f_csv.writerow(headers)
                        f_csv.writerows(data_input)
        else:  # DataFrame
            if csv_path.exists():
                data_input.to_csv(temp_csv, encoding='utf-8', index=False)
                if md5_w_size(temp_csv) != md5_w_size(csv_path):
                    copy2(temp_csv, csv_path)
                if temp_csv.exists():
                    os.remove(temp_csv)
            else:
                data_input.to_csv(csv_path, encoding='utf-8', index=False)
    except BaseException as e:
        printe(e)


@logger.catch
def write_docx(docx_path, docu):
    temp_docx = docx_path.parent / 'temp.docx'
    if docx_path.exists():
        docu.save(temp_docx)
        if md5_w_size(temp_docx) != md5_w_size(docx_path):
            copy2(temp_docx, docx_path)
        if temp_docx.exists():
            os.remove(temp_docx)
    else:
        docu.save(docx_path)


@logger.catch
def write_yml(yml_path, conta):
    temp_yml = yml_path.parent / 'temp.yml'

    if yml_path.exists():
        with open(temp_yml, mode='w', encoding='utf-8') as yf:
            documents = yaml.dump(
                conta,
                yf,
                default_flow_style=False,
                encoding='utf-8',
                allow_unicode=True)
        if md5_w_size(temp_yml) != md5_w_size(yml_path):
            copy2(temp_yml, yml_path)
        if temp_yml.exists():
            os.remove(temp_yml)
    else:
        with open(yml_path, mode='w', encoding='utf-8') as yf:
            documents = yaml.dump(
                conta,
                yf,
                default_flow_style=False,
                encoding='utf-8',
                allow_unicode=True)
    return documents


@logger.catch
def write_pic(pic_path, target_img):
    temp_pic = pic_path.parent / f'temp{pic_path.suffix}'

    if pic_path.exists():
        ext = temp_pic.suffix
        imencode(ext, target_img)[1].tofile(temp_pic)
        if md5_w_size(temp_pic) != md5_w_size(pic_path):
            copy2(temp_pic, pic_path)
        if temp_pic.exists():
            os.remove(temp_pic)
    else:
        ext = pic_path.suffix
        imencode(ext, target_img)[1].tofile(pic_path)
    return


# ================================类区================================
def a6_class():
    return


class ConfigGlobal:
    description = ''

    with open(global_config_yml, mode="r", encoding='utf-8') as yf:
        global_cfg = yaml.load(yf, Loader=yaml.FullLoader)

    def __init__(self):
        self.type = self.__class__.__name__
        self.load_cg()

    def load_cg(self):
        self.iconfig = self.global_cfg
        self.momoyolo = self.iconfig[app_en_name]
        self.themes = self.iconfig["themes"]
        self.color_map = self.iconfig["color_map"]
        self.all_color_names = set(list(self.color_map.values()))
        self.library = self.iconfig['library']
        self.lang = self.iconfig['lang']
        self.fusion = self.iconfig["fusion"]
        self.win_point_size = self.iconfig["win_point_size"]
        self.mac_point_size = self.iconfig["mac_point_size"]
        self.epsilon = self.iconfig["epsilon"]
        self.mac_max_path_len = self.iconfig["mac_max_path_len"]
        self.win_max_path_len = self.iconfig["win_max_path_len"]

        self.labeling = self.iconfig['labeling']
        self.labelimg_save_dir = self.labeling['labelimg_save_dir']
        self.labelimg_open_dir = self.labeling['labelimg_open_dir']
        self.labelme_save_dir = self.labeling['labelme_save_dir']
        self.labelme_open_dir = self.labeling['labelme_open_dir']
        self.agentocr_save_dir = self.labeling['agentocr_save_dir']
        self.agentocr_open_dir = self.labeling['agentocr_open_dir']

        self.default_save_dir = self.labelimg_save_dir
        self.default_open_dir = self.labelimg_open_dir

    @logger.catch
    def put_default_save_dir(self, default_save_dir):
        self.default_save_dir = default_save_dir

    @logger.catch
    def __str__(self):
        return f'{self.type}({global_config_yml})'

    @logger.catch
    def __repr__(self):
        return f'{self}'


config_global = ConfigGlobal()
cg = config_global

if cg.lang == 'cn':
    Language = 'CN'
else:
    Language = 'EN'


@lru_cache
@logger.catch
def get_possible_e_ymls(class_dir):
    par_yml_dirs = [UserDataFolder, class_dir, ConfigData]
    par_yml_dirs_files = [get_files(x, 'yml', False) for x in par_yml_dirs]
    candidate_ymls = list(chain(*par_yml_dirs_files))
    possible_ymls = [x for x in candidate_ymls if x.stem.lower() == class_dir.name.lower()]
    class_data_yml = class_dir / 'data.yaml'
    possible_ymls.append(class_data_yml)
    possible_e_ymls = [x for x in possible_ymls if x.exists()]
    if debug:
        loge(f'{class_dir=}', 'warning')
        loge(f'{possible_ymls=}', 'warning')
        loge(f'{possible_e_ymls=}', 'warning')
    return possible_e_ymls


@lru_cache
@logger.catch
def get_classes(par_dir, class_list_path=None):
    class_dir = par_dir
    if class_dir.parent.name in explain_names:
        class_dir = class_dir.parent
    while class_dir.name in explain_names:
        class_dir = class_dir.parent

    if class_list_path is None:
        class_list_path = par_dir / "classes.txt"
    else:
        class_list_path = Path(class_list_path)

    possible_e_ymls = get_possible_e_ymls(class_dir)

    classes = []
    if class_list_path.exists():
        classes_file = read_txt(class_list_path).splitlines()
    elif possible_e_ymls:
        possible_e_yml = possible_e_ymls[0]
        with open(possible_e_yml, errors='ignore') as f:
            data = yaml.safe_load(f)  # dictionary
        classes = data.get('names', [])
    return classes


class Config:
    description = ''

    def __init__(self):
        self.type = self.__class__.__name__
        self.reload(True)

    def save_custom(self, update_dict):
        with open(custom_config_yml, mode="r", encoding='utf-8') as yf:
            self.custom_cfg = yaml.load(yf, Loader=yaml.FullLoader)
        self.custom_cfg.update(update_dict)
        write_yml(custom_config_yml, self.custom_cfg)

    def reload(self, init=False):
        self.style = read_txt(style_qss)

        if init:
            with open(user_config_yml, mode="r", encoding='utf-8') as yf:
                self.user_cfg = yaml.load(yf, Loader=yaml.FullLoader)
            with open(custom_config_yml, mode="r", encoding='utf-8') as yf:
                self.custom_cfg = yaml.load(yf, Loader=yaml.FullLoader)
        else:
            try:
                with open(user_config_yml, mode="r", encoding='utf-8') as yf:
                    self.user_cfg = yaml.load(
                        lf, Loader=yaml.FullLoader)
            except BaseException:
                pass
        write_yml(custom_config_yml, self.custom_cfg)
        self.iconfig = self.user_cfg
        self.iconfig.update(self.custom_cfg)
        self.nickname = self.iconfig["nickname"]
        self.theme = self.iconfig["theme"]
        self.theme_setting = self.iconfig["theme_setting"]
        self.self_tr = self.iconfig['self_tr']

        self.qta_dic = self.iconfig['qta_dic']
        self.icon_color = self.theme_setting["icon_color"]
        self.icon_color_active = self.theme_setting["icon_color_active"]
        self.ic = self.icon_color
        self.ica = self.icon_color_active

        self.display_width = self.iconfig["display_width"]
        self.display_height = self.iconfig["display_height"]
        self.DW = self.display_width
        self.DH = self.display_height
        if isinstance(self.DW, int):
            self.DW = clam(self.DW, 200, 800)
        else:
            self.DW = 800
        if isinstance(self.DH, int):
            self.DH = clam(self.DH, 320, 1280)
        else:
            self.DH = 1280

        self.show_debug = self.iconfig['show_debug']
        self.play_interval = self.iconfig['play_interval']
        self.do_mode = self.iconfig['do_mode']
        self.run_check = self.iconfig['run_check']

        self.train = self.iconfig['train']
        self.batch_size = self.train['batch_size']
        self.train_img_size = self.train['train_img_size']
        self.evolve_const = self.train['evolve_const']
        self.weights_name = self.train['weights_name']
        self.hyp_yml_stem = self.train['hyp_yml_stem']
        self.cfg_yml_stem = self.train['cfg_yml_stem']
        self.data_yml_stem = self.train['data_yml_stem']
        self.dsdata_yml_stem = self.train['dsdata_yml_stem']
        self.epochs = self.train['epochs']
        self.max_batch = self.train['max_batch']

        self.detect = self.iconfig['detect']
        self.model_stem = self.detect['model_stem']
        self.detect_imgsz = self.detect['detect_imgsz']
        self.conf_thres = self.detect['conf_thres']
        self.iou_thres = self.detect['iou_thres']
        self.nms_classes = self.detect['nms_classes']
        self.max_det = self.detect['max_det']
        self.source_pic_dir_name = self.detect['source_pic_dir_name']
        self.source_video_dir_name = self.detect['source_video_dir_name']
        self.ip = self.detect['ip']
        self.count = self.detect['count']

        self.generate = self.iconfig['generate']
        self.go2func = self.generate['go2func']
        self.force_generate = self.generate['force_generate']
        self.parent_folder = self.generate['parent_folder']
        self.dist_names = self.generate['dist_names']
        self.valid_class_names = self.generate['valid_class_names']
        self.comic_titles = self.generate['comic_titles']

        # ================预定义分类================
        predefined_classes_txt = UserDataFolder / "predefined_classes.txt"
        self.label_hist = []
        if predefined_classes_txt.exists():
            predefined_classes_text = read_txt(predefined_classes_txt)
            self.label_hist = predefined_classes_text.splitlines()
            self.label_hist = [x.strip() for x in self.label_hist if x.strip() != '']
            self.label_hist = reduce_list(self.label_hist)

        self.file_dir = None
        self.pattern = None
        self.full_image_list = []
        self.image_list = []

    @logger.catch
    def put_file_dir(self, file_dir, pattern):
        # TODO put_file_dir
        self.file_dir = file_dir
        self.pattern = pattern

        pic_start_time = time()
        self.full_image_list = get_files(self.file_dir, 'labelpic', False)
        pic_run_time = run_time(pic_start_time)
        loge(f'获取到{len(self.full_image_list)}张图片的路径,耗时{pic_run_time}', 'warning')

        if self.pattern and self.pattern != '':
            self.image_list = [x for x in self.full_image_list if self.pattern in x.stem]
        else:
            self.image_list = self.full_image_list
        self.image_list.sort()
        loge(f'筛选到{len(self.image_list)}张图片的路径', 'warning')
        # natural_sort(self.image_list, key=lambda x: x.lower())

        self.imgRelPaths = [str(x.relative_to(file_dir)) for x in self.image_list]

        self.label_dirs = []
        self.label_stems_set = set()
        self.no_labels = []
        if self.image_list:
            self.imgPath = self.image_list[0]
            self.label_dirs = get_label_dirs(self.imgPath)
            loge(f'{self.label_dirs=}', 'debug')

            self.label_dirs_files = [get_files(x, 'label', False) for x in self.label_dirs]
            self.label_files = list(chain(*self.label_dirs_files))
            self.label_stems = [x.stem for x in self.label_files]
            self.label_stems_set = set(self.label_stems)
            loge(f'{len(self.label_stems_set)=}', 'debug')

            self.no_labels = [Path(x) for x in self.image_list]
            self.no_labels = [x for x in self.no_labels if x.stem not in self.label_stems_set]

            loge(f'{len(self.no_labels)=}', 'error')

            # if len(self.no_labels) <= 0.2 * len(self.image_list):
            #     loge(f'{self.no_labels=}', 'warning')
        self.imgChecks = [True if x.stem in self.label_stems_set else False for x in self.image_list]

    @logger.catch
    def __str__(self):
        try:
            _str = f"{self.type}('{self.nickname}')"
        except:
            _str = f"{self.type}"
        return _str

    @logger.catch
    def __repr__(self):
        return f'{self}'


class Signal:
    descript = ''

    @logger.catch
    def __init__(self):
        self.type = self.__class__.__name__
        self.idata = 'y'  # 创建标志位

    @logger.catch
    def change_data(self, idata):
        self.idata = idata

    @logger.catch
    def __str__(self):
        return f"{self.type}('{self.idata}')"

    @logger.catch
    def __repr__(self):
        return f'{self}'


class Supervisor:
    description = ''
    storage = None
    worker = 0
    preview = 0
    stop = 0
    task = 0

    def __init__(self):
        self.type = self.__class__.__name__

    def change_worker(self, worker):
        self.worker = worker

    def change_preview(self, preview):
        self.preview = preview

    def change_stop(self, stop):
        self.stop = stop

    def change_task(self, task):
        self.task = task

    def change_storage(self, storage):
        self.storage = storage

    def __str__(self):
        return f"{self.type}('{self.worker}')"

    def __repr__(self):
        return str(self)


@logger.catch
def get_color_name(rgb):
    r, g, b = rgb
    names = []
    color_name = ''
    for key in cg.color_map:
        value = cg.color_map[key]
        color = '#' + key
        red = hex2int(color[1:3])
        green = hex2int(color[3:5])
        blue = hex2int(color[5:7])
        dif = [red - r, green - g, blue - b]
        dif = [abs(x) for x in dif]
        diff_sum = sum(dif)
        stdd = std(dif)
        tup = (value, diff_sum, stdd)
        names.append(tup)
    names.sort(key=lambda x: (x[1], x[2]))
    if names:
        color_name = names[0][0]
    return color_name


@logger.catch
def new_icon(icon):
    icon_path = ImgResource / icon
    icon_suffixes = ['.svg', '.png']
    icon_ignore_dict = {
        '.svg': ['next', 'fit-width', 'zoom-in', 'zoom-out', 'new', 'delete', 'copy'],
    }
    if icon_path.exists():
        pass
    else:
        for i in range(len(icon_suffixes)):
            icon_suffix = icon_suffixes[i]
            igs = icon_ignore_dict.get(icon_suffix, [])
            icon_cand_path = ImgResource / f'{icon}{icon_suffix}'
            if icon not in igs and icon_cand_path.exists():
                icon_path = icon_cand_path
                break
    # loge(f'{icon_path=}', 'info')
    return QIcon(icon_path.as_posix())


@logger.catch
def new_button(text, icon=None, slot=None):
    b = QPushButton(text)
    if icon is not None:
        b.setIcon(new_icon(icon))
    if slot is not None:
        b.clicked.connect(slot)
    return b


def new_action(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, enabled=True):
    """Create a new action and assign callbacks, shortcuts, etc."""
    a = QAction(text, parent)
    if icon is not None:
        a.setIcon(new_icon(icon))
    if shortcut is not None:
        if isinstance(shortcut, (list, tuple)):
            a.setShortcuts(shortcut)
        else:
            a.setShortcut(shortcut)
    if tip is not None:
        a.setToolTip(tip)
        a.setStatusTip(tip)
    if slot is not None:
        a.triggered.connect(slot)
    if checkable:
        a.setCheckable(True)
    a.setEnabled(enabled)
    return a


def add_actions(widget, actions):
    for action in actions:
        if action is None:
            widget.addSeparator()
        elif isinstance(action, QMenu):
            widget.addMenu(action)
        else:
            widget.addAction(action)


def label_validator():
    if SYSTEM == 'M1':
        reg_lv = QRegularExpression(r'^[^ \t].+')
        lv = QRegularExpressionValidator()
        lv.setRegularExpression(reg_lv)
    else:
        lv = QRegExpValidator(QRegExp(r'^[^ \t].+'), None)
    return lv


def exists(filename):
    return os.path.exists(filename)


def distance(p):
    return sqrt(p.x() * p.x() + p.y() * p.y())


def format_shortcut(text):
    mod, key = text.split('+', 1)
    return '<b>%s</b>+<b>%s</b>' % (mod, key)


@logger.catch
def generate_color_by_text(text):
    s = text
    if not isinstance(s, str):
        s = ''
    hash_code = int(sha256(s.encode('utf-8')).hexdigest(), 16)
    r = int((hash_code / 255) % 255)
    g = int((hash_code / 65025) % 255)
    b = int((hash_code / 16581375) % 255)
    return QColor(r, g, b, 100)


def get_alphanum_key_func(key):
    convert = lambda text: int(text) if text.isdigit() else text
    return lambda s: [convert(c) for c in split('([0-9]+)', key(s))]


def natural_sort(list, key=lambda s: s):
    """
    Sort the list into natural alphanumeric order.
    """
    sort_key = get_alphanum_key_func(key)
    list.sort(key=sort_key)


# QT4 has a trimmed method, in QT5 this is called strip
def trimmed(text):
    return text.strip()


def get_format_meta(format):
    """
    returns a tuple containing (title, icon_name) of the selected format
    """
    if format == LabelFileFormat.PASCAL_VOC:
        return '&PascalVOC', 'format_voc'
    elif format == LabelFileFormat.YOLO:
        return '&YOLO', 'format_yolo'
    elif format == LabelFileFormat.CREATE_ML:
        return '&CreateML', 'format_createml'


def format_shape(s):
    return dict(label=s.label,
                line_color=s.line_color.getRgb(),
                fill_color=s.fill_color.getRgb(),
                points=[(p.x(), p.y()) for p in s.points],
                # add chris
                difficult=s.difficult)


def inverted(color):
    return QColor(*[255 - v for v in color.getRgb()])


def qread(filename, default=None):
    try:
        reader = QImageReader(filename)
        reader.setAutoTransform(True)
        return reader.read()
    except:
        return default


@logger.catch
def get_label_dirs(file_path):
    label_dirs = []
    if cg.default_save_dir is not None:
        label_dir = cg.default_save_dir
        label_dirs.append(label_dir)

    if file_path is not None:
        file_path = Path(file_path)
        label_dirs.append(file_path.parent)

        if file_path.parent.name.lower().startswith('image'):
            label_dir = file_path.parent.parent / 'labels'
            label_dirs.append(label_dir)
        elif file_path.parent.parent.name.lower().startswith('image'):
            label_dir = file_path.parent.parent.parent / 'labels' / file_path.parent.name
            label_dirs.append(label_dir)

    label_dirs = reduce_list(label_dirs)
    label_dirs = [Path(x) for x in label_dirs if Path(x).exists()]
    return label_dirs


def keysInfo(locale_str='en'):
    if 'cn' in locale_str.lower():
        msg = "快捷键\t\t\t说明\n" \
              "———————————————————————\n" \
              "Ctrl + shift + R\t\t对当前图片的所有标记重新识别\n" \
              "W\t\t\t新建矩形框\n" \
              "Q\t\t\t新建四点框\n" \
              "Ctrl + E\t\t编辑所选框标签\n" \
              "Ctrl + R\t\t重新识别所选标记\n" \
              "Ctrl + C\t\t复制并粘贴选中的标记框\n" \
              "Ctrl + 鼠标左键\t\t多选标记框\n" \
              "Backspace\t\t删除所选框\n" \
              "Ctrl + V\t\t确认本张图片标记\n" \
              "Ctrl + Shift + d\t删除本张图片\n" \
              "D\t\t\t下一张图片\n" \
              "A\t\t\t上一张图片\n" \
              "Ctrl++\t\t\t缩小\n" \
              "Ctrl--\t\t\t放大\n" \
              "↑→↓←\t\t\t移动标记框\n" \
              "———————————————————————\n" \
              "注：Mac用户Command键替换上述Ctrl键"
    else:
        msg = "Shortcut Keys\t\tDescription\n" \
              "———————————————————————\n" \
              "Ctrl + shift + R\t\tRe-recognize all the labels\n" \
              "\t\t\tof the current image\n" \
              "\n" \
              "W\t\t\tCreate a rect box\n" \
              "Q\t\t\tCreate a four-points box\n" \
              "Ctrl + E\t\tEdit label of the selected box\n" \
              "Ctrl + R\t\tRe-recognize the selected box\n" \
              "Ctrl + C\t\tCopy and paste the selected\n" \
              "\t\t\tbox\n" \
              "\n" \
              "Ctrl + Left Mouse\tMulti select the label\n" \
              "Button\t\t\tbox\n" \
              "\n" \
              "Backspace\t\tDelete the selected box\n" \
              "Ctrl + V\t\tCheck image\n" \
              "Ctrl + Shift + d\tDelete image\n" \
              "D\t\t\tNext image\n" \
              "A\t\t\tPrevious image\n" \
              "Ctrl++\t\t\tZoom in\n" \
              "Ctrl--\t\t\tZoom out\n" \
              "↑→↓←\t\t\tMove selected box" \
              "———————————————————————\n" \
              "Notice:For Mac users, use the 'Command' key instead of the 'Ctrl' key"

    return msg


class Struct(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class LightWidget(QSpinBox):

    def __init__(self, title, value=50):
        super(LightWidget, self).__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setRange(0, 100)
        self.setSuffix(' %')
        self.setValue(value)
        self.setToolTip(title)
        self.setStatusTip(self.toolTip())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def minimumSizeHint(self):
        height = super(LightWidget, self).minimumSizeHint().height()
        fm = QFontMetrics(self.font())
        # width = fm.width(str(self.maximum()))
        width = fm.maxWidth()
        return QSize(width, height)

    def light_color(self):
        if self.value() == 50:
            return None

        strength = int(self.value() / 100 * 255 + 0.5)
        return QColor(strength, strength, strength)


class ZoomWidget(QSpinBox):

    def __init__(self, value=100):
        super(ZoomWidget, self).__init__()
        self.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.setRange(1, 500)
        self.setSuffix(' %')
        self.setValue(value)
        self.setToolTip(get_str('Zoom Level'))
        self.setStatusTip(self.toolTip())
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def minimumSizeHint(self):
        height = super(ZoomWidget, self).minimumSizeHint().height()
        fm = QFontMetrics(self.font())
        # width = fm.width(str(self.maximum()))
        width = fm.maxWidth()
        return QSize(width, height)


class YOLOWriter:

    def __init__(self, folder_name, filename, img_size, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False

    def add_bnd_box(self, x_min, y_min, x_max, y_max, name, difficult):
        bnd_box = {'xmin': x_min, 'ymin': y_min, 'xmax': x_max, 'ymax': y_max}
        bnd_box['name'] = name
        bnd_box['difficult'] = difficult
        self.box_list.append(bnd_box)

    def bnd_box_to_yolo_line(self, box, class_list=[]):
        x_min = box['xmin']
        x_max = box['xmax']
        y_min = box['ymin']
        y_max = box['ymax']

        x_center = float((x_min + x_max)) / 2 / self.img_size[1]
        y_center = float((y_min + y_max)) / 2 / self.img_size[0]

        w = float((x_max - x_min)) / self.img_size[1]
        h = float((y_max - y_min)) / self.img_size[0]

        # PR387
        box_name = box['name']
        if box_name not in class_list:
            class_list.append(box_name)

        class_index = class_list.index(box_name)

        return class_index, x_center, y_center, w, h

    def save(self, class_list=[], target_file=None):

        out_file = None  # Update yolo .txt
        out_class_file = None  # Update class list .txt

        if target_file is None:
            out_file = open(
                self.filename + TXT_EXT, 'w', encoding=ENCODE_METHOD)
            classes_file = os.path.join(os.path.dirname(os.path.abspath(self.filename)), "classes.txt")
            out_class_file = open(classes_file, 'w')

        else:
            out_file = codecs.open(target_file, 'w', encoding=ENCODE_METHOD)
            classes_file = os.path.join(os.path.dirname(os.path.abspath(target_file)), "classes.txt")
            out_class_file = open(classes_file, 'w')

        for box in self.box_list:
            class_index, x_center, y_center, w, h = self.bnd_box_to_yolo_line(box, class_list)
            # print (classIndex, x_center, y_center, w, h)
            out_file.write("%d %.6f %.6f %.6f %.6f\n" % (class_index, x_center, y_center, w, h))

        # print (classList)
        # print (out_class_file)
        for c in class_list:
            out_class_file.write(c + '\n')

        out_class_file.close()
        out_file.close()


class YoloReader:

    def __init__(self, file_path, image, class_list_path=None):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.file_path = file_path
        self.par_dir = Path(file_path).parent
        self.classes = get_classes(self.par_dir, class_list_path)

        img_size = [image.height(), image.width(),
                    1 if image.isGrayscale() else 3]

        self.img_size = img_size

        self.verified = False
        self.parse_yolo_format()

    def get_shapes(self):
        return self.shapes

    def add_shape(self, label, x_min, y_min, x_max, y_max, difficult):
        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.shapes.append((label, points, None, None, difficult))

    def yolo_line_to_shape(self, class_index, x_center, y_center, w, h):
        label = self.classes[int(class_index)]

        x_min = max(float(x_center) - float(w) / 2, 0)
        x_max = min(float(x_center) + float(w) / 2, 1)
        y_min = max(float(y_center) - float(h) / 2, 0)
        y_max = min(float(y_center) + float(h) / 2, 1)

        x_min = round(self.img_size[1] * x_min)
        x_max = round(self.img_size[1] * x_max)
        y_min = round(self.img_size[0] * y_min)
        y_max = round(self.img_size[0] * y_max)

        return label, x_min, y_min, x_max, y_max

    def parse_yolo_format(self):
        bnd_box_text = read_txt(self.file_path)
        bnd_box_lines = bnd_box_text.splitlines()
        bnd_box_lines = [x for x in bnd_box_lines if x.strip() != '']
        for bnd_box_line in bnd_box_lines:
            class_index, x_center, y_center, w, h = bnd_box_line.strip().split(' ')
            label, x_min, y_min, x_max, y_max = self.yolo_line_to_shape(class_index, x_center, y_center, w, h)

            # Caveat: difficult flag is discarded when saved as yolo format.
            self.add_shape(label, x_min, y_min, x_max, y_max, False)


class Settings(object):
    def __init__(self):
        # Be default, the home will be in the same folder as labelImg
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getitem__(self, key):
        return self.data[key]

    def get(self, key, default=None):
        if key in self.data:
            return self.data[key]
        return default

    def save(self):
        with open(momolabelimg_pkl, 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
            return True

    def load(self):
        try:
            if os.path.exists(momolabelimg_pkl):
                with open(momolabelimg_pkl, 'rb') as f:
                    self.data = pickle.load(f)
                    return True
        except:
            loge(get_str('Loading setting failed'), 'warning')
        return False

    def reset(self):
        if momolabelimg_pkl.exists():
            os.remove(momolabelimg_pkl)
            loge(f"{get_str('Remove setting file')} {momolabelimg_pkl}", 'warning')
        self.data = {}


class PascalVocWriter:

    def __init__(self, folder_name, filename, img_size, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True, encoding=ENCODE_METHOD).replace("  ".encode(), "\t".encode())
        # minidom does not support UTF-8
        # reparsed = minidom.parseString(rough_string)
        # return reparsed.toprettyxml(indent="\t", encoding=ENCODE_METHOD)

    def gen_xml(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or self.folder_name is None or self.img_size is None:
            return None

        top = Element('annotation')
        if self.verified:
            top.set('verified', 'yes')

        folder = SubElement(top, 'folder')
        folder.text = self.folder_name

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        if self.local_img_path is not None:
            local_img_path = SubElement(top, 'path')
            local_img_path.text = self.local_img_path

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.database_src

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.img_size[1])
        height.text = str(self.img_size[0])
        if len(self.img_size) == 3:
            depth.text = str(self.img_size[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def add_bnd_box(self, x_min, y_min, x_max, y_max, name, difficult):
        bnd_box = {'xmin': x_min, 'ymin': y_min, 'xmax': x_max, 'ymax': y_max}
        bnd_box['name'] = name
        bnd_box['difficult'] = difficult
        self.box_list.append(bnd_box)

    def append_objects(self, top):
        for each_object in self.box_list:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            name.text = each_object['name']
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            if int(float(each_object['ymax'])) == int(float(self.img_size[0])) or (
                    int(float(each_object['ymin'])) == 1):
                truncated.text = "1"  # max == height or min
            elif (int(float(each_object['xmax'])) == int(float(self.img_size[1]))) or (
                    int(float(each_object['xmin'])) == 1):
                truncated.text = "1"  # max == width or min
            else:
                truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = str(bool(each_object['difficult']) & 1)
            bnd_box = SubElement(object_item, 'bndbox')
            x_min = SubElement(bnd_box, 'xmin')
            x_min.text = str(each_object['xmin'])
            y_min = SubElement(bnd_box, 'ymin')
            y_min.text = str(each_object['ymin'])
            x_max = SubElement(bnd_box, 'xmax')
            x_max.text = str(each_object['xmax'])
            y_max = SubElement(bnd_box, 'ymax')
            y_max.text = str(each_object['ymax'])

    def save(self, target_file=None):
        root = self.gen_xml()
        self.append_objects(root)
        out_file = None
        if target_file is None:
            out_file = codecs.open(
                self.filename + XML_EXT, 'w', encoding=ENCODE_METHOD)
        else:
            out_file = codecs.open(target_file, 'w', encoding=ENCODE_METHOD)

        prettify_result = self.prettify(root)
        out_file.write(prettify_result.decode('utf8'))
        out_file.close()


class PascalVocReader:

    def __init__(self, file_path):
        # shapes type:
        # [labbel, [(x1,y1), (x2,y2), (x3,y3), (x4,y4)], color, color, difficult]
        self.shapes = []
        self.file_path = file_path
        self.verified = False
        try:
            self.parse_xml()
        except:
            pass

    def get_shapes(self):
        return self.shapes

    def add_shape(self, label, bnd_box, difficult):
        x_min = int(float(bnd_box.find('xmin').text))
        y_min = int(float(bnd_box.find('ymin').text))
        x_max = int(float(bnd_box.find('xmax').text))
        y_max = int(float(bnd_box.find('ymax').text))
        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.shapes.append((label, points, None, None, difficult))

    def parse_xml(self):
        assert self.file_path.endswith(XML_EXT), "Unsupported file format"
        parser = etree.XMLParser(encoding=ENCODE_METHOD)
        xml_tree = ElementTree.parse(self.file_path, parser=parser).getroot()
        filename = xml_tree.find('filename').text
        try:
            verified = xml_tree.attrib['verified']
            if verified == 'yes':
                self.verified = True
        except KeyError:
            self.verified = False

        for object_iter in xml_tree.findall('object'):
            bnd_box = object_iter.find("bndbox")
            label = object_iter.find('name').text
            # Add chris
            difficult = False
            if object_iter.find('difficult') is not None:
                difficult = bool(int(object_iter.find('difficult').text))
            self.add_shape(label, bnd_box, difficult)
        return True


class LabelFileFormat(Enum):
    PASCAL_VOC = 1
    YOLO = 2
    CREATE_ML = 3


class LabelFileError(Exception):
    pass


class LabelFile(object):
    # It might be changed as window creates. By default, using XML ext
    # suffix = '.lif'
    suffix = XML_EXT

    def __init__(self, filename=None):
        self.shapes = ()
        self.image_path = None
        self.image_data = None
        self.verified = False

    def save_create_ml_format(self, filename, shapes, image_path, image_data, class_list, line_color=None,
                              fill_color=None, database_src=None):
        img_folder_name = os.path.basename(os.path.dirname(image_path))
        img_file_name = os.path.basename(image_path)

        image = QImage()
        image.load(image_path)
        image_shape = [image.height(), image.width(),
                       1 if image.isGrayscale() else 3]
        writer = CreateMLWriter(img_folder_name, img_file_name,
                                image_shape, shapes, filename, local_img_path=image_path)
        writer.verified = self.verified
        writer.write()
        return

    def save_pascal_voc_format(self, filename, shapes, image_path, image_data,
                               line_color=None, fill_color=None, database_src=None):
        img_folder_path = os.path.dirname(image_path)
        img_folder_name = os.path.split(img_folder_path)[-1]
        img_file_name = os.path.basename(image_path)
        # imgFileNameWithoutExt = os.path.splitext(img_file_name)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        if isinstance(image_data, QImage):
            image = image_data
        else:
            image = QImage()
            image.load(image_path)
        image_shape = [image.height(), image.width(),
                       1 if image.isGrayscale() else 3]
        writer = PascalVocWriter(img_folder_name, img_file_name,
                                 image_shape, local_img_path=image_path)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bnd_box = LabelFile.convert_points_to_bnd_box(points)
            writer.add_bnd_box(bnd_box[0], bnd_box[1], bnd_box[2], bnd_box[3], label, difficult)

        writer.save(target_file=filename)
        return

    def save_yolo_format(self, filename, shapes, image_path, image_data, class_list,
                         line_color=None, fill_color=None, database_src=None):
        img_folder_path = os.path.dirname(image_path)
        img_folder_name = os.path.split(img_folder_path)[-1]
        img_file_name = os.path.basename(image_path)
        # imgFileNameWithoutExt = os.path.splitext(img_file_name)[0]
        # Read from file path because self.imageData might be empty if saving to
        # Pascal format
        if isinstance(image_data, QImage):
            image = image_data
        else:
            image = QImage()
            image.load(image_path)
        image_shape = [image.height(), image.width(),
                       1 if image.isGrayscale() else 3]
        writer = YOLOWriter(img_folder_name, img_file_name,
                            image_shape, local_img_path=image_path)
        writer.verified = self.verified

        for shape in shapes:
            points = shape['points']
            label = shape['label']
            # Add Chris
            difficult = int(shape['difficult'])
            bnd_box = LabelFile.convert_points_to_bnd_box(points)
            writer.add_bnd_box(bnd_box[0], bnd_box[1], bnd_box[2], bnd_box[3], label, difficult)

        writer.save(target_file=filename, class_list=class_list)
        return

    def toggle_verify(self):
        self.verified = not self.verified

    ''' ttf is disable
    def load(self, filename):
        import json
        with open(filename, 'rb') as f:
                data = json.load(f)
                imagePath = data['imagePath']
                imageData = b64decode(data['imageData'])
                lineColor = data['lineColor']
                fillColor = data['fillColor']
                shapes = ((s['label'], s['points'], s['line_color'], s['fill_color']) for s in data['shapes'])
                # Only replace data after everything is loaded.
                self.shapes = shapes
                self.imagePath = imagePath
                self.imageData = imageData
                self.lineColor = lineColor
                self.fillColor = fillColor

    def save(self, filename, shapes, imagePath, imageData, lineColor=None, fillColor=None):
        import json
        with open(filename, 'wb') as f:
                json.dump(dict(
                    shapes=shapes,
                    lineColor=lineColor, fillColor=fillColor,
                    imagePath=imagePath,
                    imageData=b64encode(imageData)),
                    f, ensure_ascii=True, indent=2)
    '''

    @staticmethod
    def is_label_file(filename):
        file_suffix = os.path.splitext(filename)[1].lower()
        return file_suffix == LabelFile.suffix

    @staticmethod
    def convert_points_to_bnd_box(points):
        x_min = float('inf')
        y_min = float('inf')
        x_max = float('-inf')
        y_max = float('-inf')
        for p in points:
            x = p[0]
            y = p[1]
            x_min = min(x, x_min)
            y_min = min(y, y_min)
            x_max = max(x, x_max)
            y_max = max(y, y_max)

        # Martin Kersner, 2015/11/12
        # 0-valued coordinates of BB caused an error while
        # training faster-rcnn object detector.
        if x_min < 1:
            x_min = 1

        if y_min < 1:
            y_min = 1

        return int(x_min), int(y_min), int(x_max), int(y_max)


class LabelDialog(QDialog):

    def __init__(self, text="Enter object label", parent=None, list_item=None):
        super(LabelDialog, self).__init__(parent)

        self.edit = QLineEdit()
        self.edit.setText(text)
        self.edit.setValidator(label_validator())
        self.edit.editingFinished.connect(self.post_process)

        model = QStringListModel()
        model.setStringList(list_item)
        completer = QCompleter()
        completer.setModel(model)
        self.edit.setCompleter(completer)

        self.button_box = bb = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel, Qt.Orientation.Horizontal,
            self)
        bb.button(QDialogButtonBox.StandardButton.Ok).setIcon(new_icon('done'))
        bb.button(QDialogButtonBox.StandardButton.Cancel).setIcon(new_icon('undo'))
        bb.accepted.connect(self.validate)
        bb.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(bb, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.edit)

        if list_item is not None and len(list_item) > 0:
            self.list_widget = QListWidget(self)
            for item in list_item:
                self.list_widget.addItem(item)
            self.list_widget.itemClicked.connect(self.list_item_click)
            self.list_widget.itemDoubleClicked.connect(self.list_item_double_click)
            layout.addWidget(self.list_widget)

        self.setLayout(layout)

    def validate(self):
        if trimmed(self.edit.text()):
            self.accept()

    def post_process(self):
        self.edit.setText(trimmed(self.edit.text()))

    def pop_up(self, text='', move=True):
        """
        Shows the dialog, setting the current text to `text`, and blocks the caller until the user has made a choice.
        If the user entered a label, that label is returned, otherwise (i.e. if the user cancelled the action)
        `None` is returned.
        """
        self.edit.setText(text)
        self.edit.setSelection(0, len(text))
        self.edit.setFocus(Qt.FocusReason.PopupFocusReason)
        if move:
            cursor_pos = QCursor.pos()

            # move OK button below cursor
            btn = self.button_box.buttons()[0]
            self.adjustSize()
            btn.adjustSize()
            offset = btn.mapToGlobal(btn.pos()) - self.pos()
            offset += QPoint(btn.size().width() // 4, btn.size().height() // 2)
            cursor_pos.setX(max(0, cursor_pos.x() - offset.x()))
            cursor_pos.setY(max(0, cursor_pos.y() - offset.y()))

            parent_bottom_right = self.parentWidget().geometry()
            max_x = parent_bottom_right.x() + parent_bottom_right.width() - self.sizeHint().width()
            max_y = parent_bottom_right.y() + parent_bottom_right.height() - self.sizeHint().height()
            max_global = self.parentWidget().mapToGlobal(QPoint(max_x, max_y))
            if cursor_pos.x() > max_global.x():
                cursor_pos.setX(max_global.x())
            if cursor_pos.y() > max_global.y():
                cursor_pos.setY(max_global.y())
            self.move(cursor_pos)
        return trimmed(self.edit.text()) if self.exec() else None

    def list_item_click(self, t_qlist_widget_item):
        text = trimmed(t_qlist_widget_item.text())
        self.edit.setText(text)

    def list_item_double_click(self, t_qlist_widget_item):
        self.list_item_click(t_qlist_widget_item)
        self.validate()


class HashableQListWidgetItem(QListWidgetItem):

    def __init__(self, *args):
        super(HashableQListWidgetItem, self).__init__(*args)

    def __hash__(self):
        return hash(id(self))


class CreateMLWriter:
    def __init__(self, folder_name, filename, img_size, shapes, output_file, database_src='Unknown',
                 local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False
        self.shapes = shapes
        self.output_file = output_file

    def write(self):
        if os.path.isfile(self.output_file):
            with open(self.output_file, "r") as file:
                input_data = file.read()
                output_dict = json.loads(input_data)
        else:
            output_dict = []

        output_image_dict = {
            "image": self.filename,
            "verified": self.verified,
            "annotations": []
        }

        for shape in self.shapes:
            points = shape["points"]

            x1 = points[0][0]
            y1 = points[0][1]
            x2 = points[1][0]
            y2 = points[2][1]

            height, width, x, y = self.calculate_coordinates(x1, x2, y1, y2)

            shape_dict = {
                "label": shape["label"],
                "coordinates": {
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height
                }
            }
            output_image_dict["annotations"].append(shape_dict)

        # check if image already in output
        exists = False
        for i in range(0, len(output_dict)):
            if output_dict[i]["image"] == output_image_dict["image"]:
                exists = True
                output_dict[i] = output_image_dict
                break

        if not exists:
            output_dict.append(output_image_dict)

        Path(self.output_file).write_text(json.dumps(output_dict), ENCODE_METHOD)

    def calculate_coordinates(self, x1, x2, y1, y2):
        if x1 < x2:
            x_min = x1
            x_max = x2
        else:
            x_min = x2
            x_max = x1
        if y1 < y2:
            y_min = y1
            y_max = y2
        else:
            y_min = y2
            y_max = y1
        width = x_max - x_min
        if width < 0:
            width = width * -1
        height = y_max - y_min
        # x and y from center of rect
        x = x_min + width / 2
        y = y_min + height / 2
        return height, width, x, y


class CreateMLReader:
    def __init__(self, json_path, file_path):
        self.json_path = json_path
        self.shapes = []
        self.verified = False
        self.filename = os.path.basename(file_path)
        try:
            self.parse_json()
        except ValueError:
            print("JSON decoding failed")

    def parse_json(self):
        with open(self.json_path, "r") as file:
            input_data = file.read()

        # Returns a list
        output_list = json.loads(input_data)

        if output_list:
            self.verified = output_list[0].get("verified", False)

        if len(self.shapes) > 0:
            self.shapes = []
        for image in output_list:
            if image["image"] == self.filename:
                for shape in image["annotations"]:
                    self.add_shape(shape["label"], shape["coordinates"])

    def add_shape(self, label, bnd_box):
        x_min = bnd_box["x"] - (bnd_box["width"] / 2)
        y_min = bnd_box["y"] - (bnd_box["height"] / 2)

        x_max = bnd_box["x"] + (bnd_box["width"] / 2)
        y_max = bnd_box["y"] + (bnd_box["height"] / 2)

        points = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
        self.shapes.append((label, points, None, None, True))

    def get_shapes(self):
        return self.shapes


class Shape(object):
    P_SQUARE, P_ROUND = range(2)

    MOVE_VERTEX, NEAR_VERTEX = range(2)

    # The following class variables influence the drawing
    # of _all_ shape objects.
    line_color = DEFAULT_LINE_COLOR
    fill_color = DEFAULT_FILL_COLOR
    select_line_color = DEFAULT_SELECT_LINE_COLOR
    select_fill_color = DEFAULT_SELECT_FILL_COLOR
    vertex_fill_color = DEFAULT_VERTEX_FILL_COLOR
    h_vertex_fill_color = DEFAULT_HVERTEX_FILL_COLOR
    point_type = P_ROUND
    if SYSTEM == 'WINDOWS':
        point_size = cg.win_point_size
    else:
        point_size = cg.mac_point_size
    scale = 1.0
    label_font_size = 8

    def __init__(self, label=None, line_color=None, difficult=False, paint_label=False):
        self.label = label
        self.points = []
        self.fill = False
        self.selected = False
        self.difficult = difficult
        self.paint_label = paint_label

        self._highlight_index = None
        self._highlight_mode = self.NEAR_VERTEX
        self._highlight_settings = {
            self.NEAR_VERTEX: (4, self.P_ROUND),
            self.MOVE_VERTEX: (1.5, self.P_SQUARE),
        }

        self._closed = False

        if line_color is not None:
            # Override the class line_color attribute
            # with an object attribute. Currently this
            # is used for drawing the pending line a different color.
            self.line_color = line_color

    def close(self):
        self._closed = True

    def reach_max_points(self):
        if len(self.points) >= 4:
            return True
        return False

    def add_point(self, point):
        if not self.reach_max_points():
            self.points.append(point)

    def pop_point(self):
        if self.points:
            return self.points.pop()
        return None

    def is_closed(self):
        return self._closed

    def set_open(self):
        self._closed = False

    def paint(self, painter):
        if self.points:
            color = self.select_line_color if self.selected else self.line_color
            pen = QPen(color)
            # Try using integer sizes for smoother drawing(?)
            pen.setWidth(max(1, int(round(2.0 / self.scale))))
            painter.setPen(pen)

            line_path = QPainterPath()
            vertex_path = QPainterPath()

            line_path.moveTo(self.points[0])
            # Uncommenting the following line will draw 2 paths
            # for the 1st vertex, and make it non-filled, which
            # may be desirable.
            # self.drawVertex(vertex_path, 0)

            for i, p in enumerate(self.points):
                line_path.lineTo(p)
                self.draw_vertex(vertex_path, i)
            if self.is_closed():
                line_path.lineTo(self.points[0])

            painter.drawPath(line_path)
            painter.drawPath(vertex_path)
            painter.fillPath(vertex_path, self.vertex_fill_color)

            # Draw text at the top-left
            if self.paint_label:
                min_x = sys.maxsize
                min_y = sys.maxsize
                min_y_label = int(1.25 * self.label_font_size)
                for point in self.points:
                    min_x = min(min_x, point.x())
                    min_y = min(min_y, point.y())
                if min_x != sys.maxsize and min_y != sys.maxsize:
                    font = QFont()
                    font.setPointSize(self.label_font_size)
                    font.setBold(True)
                    painter.setFont(font)
                    if self.label is None:
                        self.label = ""
                    if min_y < min_y_label:
                        min_y += min_y_label
                    painter.drawText(int(min_x), int(min_y), self.label)

            if self.fill:
                color = self.select_fill_color if self.selected else self.fill_color
                painter.fillPath(line_path, color)

    def draw_vertex(self, path, i):
        d = self.point_size / self.scale
        shape = self.point_type
        point = self.points[i]
        if i == self._highlight_index:
            size, shape = self._highlight_settings[self._highlight_mode]
            d *= size
        if self._highlight_index is not None:
            self.vertex_fill_color = self.h_vertex_fill_color
        else:
            self.vertex_fill_color = Shape.vertex_fill_color
        if shape == self.P_SQUARE:
            path.addRect(point.x() - d / 2, point.y() - d / 2, d, d)
        elif shape == self.P_ROUND:
            path.addEllipse(point, d / 2.0, d / 2.0)
        else:
            assert False, "unsupported vertex shape"

    def nearest_vertex(self, point, epsilon):
        index = None
        for i, p in enumerate(self.points):
            dist = distance(p - point)
            if dist <= epsilon:
                index = i
                epsilon = dist
        return index

    def contains_point(self, point):
        return self.make_path().contains(point)

    def make_path(self):
        path = QPainterPath(self.points[0])
        for p in self.points[1:]:
            path.lineTo(p)
        return path

    def bounding_rect(self):
        return self.make_path().boundingRect()

    def move_by(self, offset):
        self.points = [p + offset for p in self.points]

    def move_vertex_by(self, i, offset):
        self.points[i] = self.points[i] + offset

    def highlight_vertex(self, i, action):
        self._highlight_index = i
        self._highlight_mode = action

    def highlight_clear(self):
        self._highlight_index = None

    def copy(self):
        shape = Shape("%s" % self.label)
        shape.points = [p for p in self.points]
        shape.fill = self.fill
        shape.selected = self.selected
        shape._closed = self._closed
        if self.line_color != Shape.line_color:
            shape.line_color = self.line_color
        if self.fill_color != Shape.fill_color:
            shape.fill_color = self.fill_color
        shape.difficult = self.difficult
        return shape

    def __len__(self):
        return len(self.points)

    def __getitem__(self, key):
        return self.points[key]

    def __setitem__(self, key, value):
        self.points[key] = value


class ColorDialog(QColorDialog):

    def __init__(self, parent=None):
        super(ColorDialog, self).__init__(parent)
        self.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        # The Mac native dialog does not support our restore button.
        self.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog)
        # Add a restore defaults button.
        # The default is set at invocation time, so that it
        # works across dialogs for different elements.
        self.default = None
        self.bb = self.layout().itemAt(1).widget()
        self.bb.addButton(QDialogButtonBox.StandardButton.RestoreDefaults)
        self.bb.clicked.connect(self.check_restore)

    def getColor(self, value=None, title=None, default=None):
        self.default = default
        if title:
            self.setWindowTitle(title)
        if value:
            self.setCurrentColor(value)
        return self.currentColor() if self.exec() else None

    def check_restore(self, button):
        if self.bb.buttonRole(button) & QDialogButtonBox.ResetRole and self.default:
            self.setCurrentColor(self.default)


# class Canvas(QGLWidget):


class Canvas(QWidget):
    zoomRequest = pyqtSignal(int)
    lightRequest = pyqtSignal(int)
    scrollRequest = pyqtSignal(int, int)
    newShape = pyqtSignal()
    selectionChanged = pyqtSignal(bool)
    shapeMoved = pyqtSignal()
    drawingPolygon = pyqtSignal(bool)

    CREATE, EDIT = list(range(2))

    epsilon = cg.epsilon

    def __init__(self, *args, **kwargs):
        super(Canvas, self).__init__(*args, **kwargs)
        # Initialise local state.
        self.mode = self.EDIT
        self.shapes = []
        self.current = None
        self.selected_shape = None  # save the selected shape here
        self.selected_shape_copy = None
        self.drawing_line_color = QColor(0, 0, 255)
        self.drawing_rect_color = QColor(0, 0, 255)
        self.line = Shape(line_color=self.drawing_line_color)
        self.prev_point = QPointF()
        self.offsets = QPointF(), QPointF()
        self.scale = 1.0
        self.overlay_color = None
        self.label_font_size = 8
        self.pixmap = QPixmap()
        self.visible = {}
        self._hide_background = False
        self.hide_background = False
        self.h_shape = None
        self.h_vertex = None
        self._painter = QPainter()
        self._cursor = CURSOR_DEFAULT
        # Menus:
        self.menus = (QMenu(), QMenu())
        # Set widget options.
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
        self.verified = False
        self.draw_square = False

        # initialisation for panning
        self.pan_initial_pos = QPoint()

        self.pen_cross = QPen(Qt.GlobalColor.red)
        self.pen_cross.setStyle(Qt.PenStyle.DashLine)  # 实线SolidLine，虚线DashLine，点线DotLine
        self.pen_cross.setWidthF(0)  # 0表示线宽为1

    def set_drawing_color(self, qcolor):
        self.drawing_line_color = qcolor
        self.drawing_rect_color = qcolor

    def enterEvent(self, ev):
        self.override_cursor(self._cursor)

    def leaveEvent(self, ev):
        self.restore_cursor()

    def focusOutEvent(self, ev):
        self.restore_cursor()

    def isVisible(self, shape):
        return self.visible.get(shape, True)

    def drawing(self):
        return self.mode == self.CREATE

    def editing(self):
        return self.mode == self.EDIT

    def set_editing(self, value=True):
        self.mode = self.EDIT if value else self.CREATE
        if not value:  # Create
            self.un_highlight()
            self.de_select_shape()
        self.prev_point = QPointF()
        self.repaint()

    def un_highlight(self, shape=None):
        if shape == None or shape == self.h_shape:
            if self.h_shape:
                self.h_shape.highlight_clear()
            self.h_vertex = self.h_shape = None

    def selected_vertex(self):
        return self.h_vertex is not None

    def mouseMoveEvent(self, ev):
        """Update line with last point and current coordinates."""
        pos = self.transform_pos(ev.pos())

        # Update coordinates in status bar if image is opened
        # 父窗口
        window = self.parent().window()

        # TODO lb_magnifier.setPixmap
        if window.file_path is not None:
            label_coordinates_str = f'X: {pos.x():.0f}; Y: {pos.y():.0f}'
            self.parent().window().label_coordinates.setText(label_coordinates_str)
            if window.use_magnifying_glass.isChecked():
                # 显示放大镜
                image_data = window.image_data
                x_pos = int(pos.x() - area_size)
                y_pos = int(pos.y() - area_size)
                qimg = image_data.copy(x_pos, y_pos, area_size * 2, area_size * 2)

                qimg = qimg.scaled(glassSize, glassSize, Qt.AspectRatioMode.KeepAspectRatio)
                qpximg = QPixmap.fromImage(qimg)

                painter = QPainter()
                painter.begin(qpximg)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                if SYSTEM != 'M1':
                    painter.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                painter.drawImage(QRect(0, 0, glassSize, glassSize), qimg)

                halfWidth = qpximg.width() / 2
                halfHeight = qpximg.height() / 2
                painter.setPen(self.pen_cross)
                painter.drawLine(QPointF(0, halfHeight), QPointF(qpximg.width(), halfHeight))
                painter.drawLine(QPointF(halfWidth, 0), QPointF(halfWidth, qpximg.height()))
                painter.end()

                window.lb_magnifier.setPixmap(qpximg)
            else:
                window.lb_magnifier.clear()

        # Polygon drawing.
        if self.drawing():
            self.override_cursor(CURSOR_DRAW)
            if self.current:
                # Display annotation width and height while drawing
                current_width = abs(self.current[0].x() - pos.x())
                current_height = abs(self.current[0].y() - pos.y())
                label_coordinates_str = f'{get_str("Width")}: {current_width:.0f}, {get_str("Height")}: {current_height:.0f} / X: {pos.x():.0f}; Y: {pos.y():.0f}'
                self.parent().window().label_coordinates.setText(label_coordinates_str)

                color = self.drawing_line_color
                if self.out_of_pixmap(pos):
                    # Don't allow the user to draw outside the pixmap.
                    # Clip the coordinates to 0 or max,
                    # if they are outside the range [0, max]
                    size = self.pixmap.size()
                    clipped_x = min(max(0, pos.x()), size.width())
                    clipped_y = min(max(0, pos.y()), size.height())
                    pos = QPointF(clipped_x, clipped_y)
                elif len(self.current) > 1 and self.close_enough(pos, self.current[0]):
                    # Attract line to starting point and colorise to alert the
                    # user:
                    pos = self.current[0]
                    color = self.current.line_color
                    self.override_cursor(CURSOR_POINT)
                    self.current.highlight_vertex(0, Shape.NEAR_VERTEX)

                if self.draw_square:
                    init_pos = self.current[0]
                    min_x = init_pos.x()
                    min_y = init_pos.y()
                    min_size = min(abs(pos.x() - min_x), abs(pos.y() - min_y))
                    direction_x = -1 if pos.x() - min_x < 0 else 1
                    direction_y = -1 if pos.y() - min_y < 0 else 1
                    self.line[1] = QPointF(min_x + direction_x * min_size, min_y + direction_y * min_size)
                else:
                    self.line[1] = pos

                self.line.line_color = color
                self.prev_point = QPointF()
                self.current.highlight_clear()
            else:
                self.prev_point = pos
            self.repaint()
            return

        # Polygon copy moving.
        if Qt.MouseButton.RightButton & ev.buttons():
            if self.selected_shape_copy and self.prev_point:
                self.override_cursor(CURSOR_MOVE)
                self.bounded_move_shape(self.selected_shape_copy, pos)
                self.repaint()
            elif self.selected_shape:
                self.selected_shape_copy = self.selected_shape.copy()
                self.repaint()
            return

        # Polygon/Vertex moving.
        if Qt.MouseButton.LeftButton & ev.buttons():
            if self.selected_vertex():
                self.bounded_move_vertex(pos)
                self.shapeMoved.emit()
                self.repaint()

                # Display annotation width and height while moving vertex
                point1 = self.h_shape[1]
                point3 = self.h_shape[3]
                current_width = abs(point1.x() - point3.x())
                current_height = abs(point1.y() - point3.y())
                label_coordinates_str = f'{get_str("Width")}: {current_width:.0f}, {get_str("Height")}: {current_height:.0f} / X: {pos.x():.0f}; Y: {pos.y():.0f}'
                self.parent().window().label_coordinates.setText(label_coordinates_str)
            elif self.selected_shape and self.prev_point:
                self.override_cursor(CURSOR_MOVE)
                self.bounded_move_shape(self.selected_shape, pos)
                self.shapeMoved.emit()
                self.repaint()

                # Display annotation width and height while moving shape
                point1 = self.selected_shape[1]
                point3 = self.selected_shape[3]
                current_width = abs(point1.x() - point3.x())
                current_height = abs(point1.y() - point3.y())
                label_coordinates_str = f'{get_str("Width")}: {current_width:.0f}, {get_str("Height")}: {current_height:.0f} / X: {pos.x():.0f}; Y: {pos.y():.0f}'
                self.parent().window().label_coordinates.setText(label_coordinates_str)
            else:
                # pan
                delta = ev.pos() - self.pan_initial_pos
                self.scrollRequest.emit(delta.x(), delta.y())
                self.update()
            return

        # Just hovering over the canvas, 2 possibilities:
        # - Highlight shapes
        # - Highlight vertex
        # Update shape/vertex fill and tooltip value accordingly.
        self.setToolTip("Image")
        priority_list = self.shapes + ([self.selected_shape] if self.selected_shape else [])
        for shape in reversed([s for s in priority_list if self.isVisible(s)]):
            # Look for a nearby vertex to highlight. If that fails,
            # check if we happen to be inside a shape.
            index = shape.nearest_vertex(pos, self.epsilon)
            if index is not None:
                if self.selected_vertex():
                    self.h_shape.highlight_clear()
                self.h_vertex, self.h_shape = index, shape
                shape.highlight_vertex(index, shape.MOVE_VERTEX)
                self.override_cursor(CURSOR_POINT)
                self.setToolTip(get_str("Click & drag to move point"))
                self.setStatusTip(self.toolTip())
                self.update()
                break
            elif shape.contains_point(pos):
                if self.selected_vertex():
                    self.h_shape.highlight_clear()
                self.h_vertex, self.h_shape = None, shape
                self.setToolTip(f"{get_str('Click & drag to move shape')} '{shape.label}'")
                self.setStatusTip(self.toolTip())
                self.override_cursor(CURSOR_GRAB)
                self.update()

                # Display annotation width and height while hovering inside
                point1 = self.h_shape[1]
                point3 = self.h_shape[3]
                current_width = abs(point1.x() - point3.x())
                current_height = abs(point1.y() - point3.y())
                label_coordinates_str = f'{get_str("Width")}: {current_width:.0f}, {get_str("Height")}: {current_height:.0f} / X: {pos.x():.0f}; Y: {pos.y():.0f}'
                self.parent().window().label_coordinates.setText(label_coordinates_str)
                break
        else:  # Nothing found, clear highlights, reset state.
            if self.h_shape:
                self.h_shape.highlight_clear()
                self.update()
            self.h_vertex, self.h_shape = None, None
            self.override_cursor(CURSOR_DEFAULT)

    def mousePressEvent(self, ev):
        pos = self.transform_pos(ev.pos())

        if ev.button() == Qt.MouseButton.LeftButton:
            if self.drawing():
                self.handle_drawing(pos)
            else:
                selection = self.select_shape_point(pos)
                self.prev_point = pos

                if selection is None:
                    # pan
                    QApplication.setOverrideCursor(QCursor(Qt.CursorShape.OpenHandCursor))
                    self.pan_initial_pos = ev.pos()

        elif ev.button() == Qt.MouseButton.RightButton and self.editing():
            self.select_shape_point(pos)
            self.prev_point = pos
        self.update()

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MouseButton.RightButton:
            menu = self.menus[bool(self.selected_shape_copy)]
            self.restore_cursor()
            if not menu.exec(self.mapToGlobal(ev.pos())) \
                    and self.selected_shape_copy:
                # Cancel the move by deleting the shadow copy.
                self.selected_shape_copy = None
                self.repaint()
        elif ev.button() == Qt.MouseButton.LeftButton and self.selected_shape:
            if self.selected_vertex():
                self.override_cursor(CURSOR_POINT)
            else:
                self.override_cursor(CURSOR_GRAB)
        elif ev.button() == Qt.MouseButton.LeftButton:
            pos = self.transform_pos(ev.pos())
            if self.drawing():
                self.handle_drawing(pos)
            else:
                # pan
                QApplication.restoreOverrideCursor()

    def end_move(self, copy=False):
        assert self.selected_shape and self.selected_shape_copy
        shape = self.selected_shape_copy
        # del shape.fill_color
        # del shape.line_color
        if copy:
            self.shapes.append(shape)
            self.selected_shape.selected = False
            self.selected_shape = shape
            self.repaint()
        else:
            self.selected_shape.points = [p for p in shape.points]
        self.selected_shape_copy = None

    def hide_background_shapes(self, value):
        self.hide_background = value
        if self.selected_shape:
            # Only hide other shapes if there is a current selection.
            # Otherwise the user will not be able to select a shape.
            self.set_hiding(True)
            self.repaint()

    def handle_drawing(self, pos):
        if self.current and self.current.reach_max_points() is False:
            init_pos = self.current[0]
            min_x = init_pos.x()
            min_y = init_pos.y()
            target_pos = self.line[1]
            max_x = target_pos.x()
            max_y = target_pos.y()
            self.current.add_point(QPointF(max_x, min_y))
            self.current.add_point(target_pos)
            self.current.add_point(QPointF(min_x, max_y))
            self.finalise()
        elif not self.out_of_pixmap(pos):
            self.current = Shape()
            self.current.add_point(pos)
            self.line.points = [pos, pos]
            self.set_hiding()
            self.drawingPolygon.emit(True)
            self.update()

    def set_hiding(self, enable=True):
        self._hide_background = self.hide_background if enable else False

    def can_close_shape(self):
        return self.drawing() and self.current and len(self.current) > 2

    def mouseDoubleClickEvent(self, ev):
        # We need at least 4 points here, since the mousePress handler
        # adds an extra one before this handler is called.
        if self.can_close_shape() and len(self.current) > 3:
            self.current.pop_point()
            self.finalise()

    def select_shape(self, shape):
        self.de_select_shape()
        shape.selected = True
        self.selected_shape = shape
        self.set_hiding()
        self.selectionChanged.emit(True)
        self.update()

    def select_shape_point(self, point):
        """Select the first shape created which contains this point."""
        self.de_select_shape()
        if self.selected_vertex():  # A vertex is marked for selection.
            index, shape = self.h_vertex, self.h_shape
            shape.highlight_vertex(index, shape.MOVE_VERTEX)
            self.select_shape(shape)
            return self.h_vertex
        for shape in reversed(self.shapes):
            if self.isVisible(shape) and shape.contains_point(point):
                self.select_shape(shape)
                self.calculate_offsets(shape, point)
                return self.selected_shape
        return None

    def calculate_offsets(self, shape, point):
        rect = shape.bounding_rect()
        x1 = rect.x() - point.x()
        y1 = rect.y() - point.y()
        x2 = (rect.x() + rect.width()) - point.x()
        y2 = (rect.y() + rect.height()) - point.y()
        self.offsets = QPointF(x1, y1), QPointF(x2, y2)

    def snap_point_to_canvas(self, x, y):
        """
        Moves a point x,y to within the boundaries of the canvas.
        :return: (x,y,snapped) where snapped is True if x or y were changed, False if not.
        """
        if x < 0 or x > self.pixmap.width() or y < 0 or y > self.pixmap.height():
            x = max(x, 0)
            y = max(y, 0)
            x = min(x, self.pixmap.width())
            y = min(y, self.pixmap.height())
            return x, y, True

        return x, y, False

    def bounded_move_vertex(self, pos):
        index, shape = self.h_vertex, self.h_shape
        point = shape[index]
        if self.out_of_pixmap(pos):
            size = self.pixmap.size()
            clipped_x = min(max(0, pos.x()), size.width())
            clipped_y = min(max(0, pos.y()), size.height())
            pos = QPointF(clipped_x, clipped_y)

        if self.draw_square:
            opposite_point_index = (index + 2) % 4
            opposite_point = shape[opposite_point_index]

            min_size = min(abs(pos.x() - opposite_point.x()), abs(pos.y() - opposite_point.y()))
            direction_x = -1 if pos.x() - opposite_point.x() < 0 else 1
            direction_y = -1 if pos.y() - opposite_point.y() < 0 else 1
            shift_pos = QPointF(opposite_point.x() + direction_x * min_size - point.x(),
                                opposite_point.y() + direction_y * min_size - point.y())
        else:
            shift_pos = pos - point

        shape.move_vertex_by(index, shift_pos)

        left_index = (index + 1) % 4
        right_index = (index + 3) % 4
        left_shift = None
        right_shift = None
        if index % 2 == 0:
            right_shift = QPointF(shift_pos.x(), 0)
            left_shift = QPointF(0, shift_pos.y())
        else:
            left_shift = QPointF(shift_pos.x(), 0)
            right_shift = QPointF(0, shift_pos.y())
        shape.move_vertex_by(right_index, right_shift)
        shape.move_vertex_by(left_index, left_shift)

    def bounded_move_shape(self, shape, pos):
        if self.out_of_pixmap(pos):
            return False  # No need to move
        o1 = pos + self.offsets[0]
        if self.out_of_pixmap(o1):
            pos -= QPointF(min(0, o1.x()), min(0, o1.y()))
        o2 = pos + self.offsets[1]
        if self.out_of_pixmap(o2):
            pos += QPointF(min(0, self.pixmap.width() - o2.x()),
                           min(0, self.pixmap.height() - o2.y()))
        # The next line tracks the new position of the cursor
        # relative to the shape, but also results in making it
        # a bit "shaky" when nearing the border and allows it to
        # go outside of the shape's area for some reason. XXX
        # self.calculateOffsets(self.selectedShape, pos)
        dp = pos - self.prev_point
        if dp:
            shape.move_by(dp)
            self.prev_point = pos
            return True
        return False

    def de_select_shape(self):
        if self.selected_shape:
            self.selected_shape.selected = False
            self.selected_shape = None
            self.set_hiding(False)
            self.selectionChanged.emit(False)
            self.update()

    def delete_selected(self):
        if self.selected_shape:
            shape = self.selected_shape
            self.un_highlight(shape)
            self.shapes.remove(self.selected_shape)
            self.selected_shape = None
            self.update()
            return shape

    def copy_selected_shape(self):
        if self.selected_shape:
            shape = self.selected_shape.copy()
            self.de_select_shape()
            self.shapes.append(shape)
            shape.selected = True
            self.selected_shape = shape
            self.bounded_shift_shape(shape)
            return shape

    def bounded_shift_shape(self, shape):
        # Try to move in one direction, and if it fails in another.
        # Give up if both fail.
        point = shape[0]
        offset = QPointF(2.0, 2.0)
        self.calculate_offsets(shape, point)
        self.prev_point = point
        if not self.bounded_move_shape(shape, point - offset):
            self.bounded_move_shape(shape, point + offset)

    def paintEvent(self, event):
        if not self.pixmap:
            return super(Canvas, self).paintEvent(event)

        p = self._painter
        p.begin(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if SYSTEM != 'M1':
            p.setRenderHint(QPainter.RenderHint.HighQualityAntialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        p.scale(self.scale, self.scale)
        p.translate(self.offset_to_center())

        temp = self.pixmap
        if self.overlay_color:
            temp = QPixmap(self.pixmap)
            painter = QPainter(temp)
            painter.setCompositionMode(painter.CompositionMode.CompositionMode_Overlay)
            painter.fillRect(temp.rect(), self.overlay_color)
            painter.end()

        p.drawPixmap(0, 0, temp)
        Shape.scale = self.scale
        Shape.label_font_size = self.label_font_size
        for shape in self.shapes:
            if (shape.selected or not self._hide_background) and self.isVisible(shape):
                shape.fill = shape.selected or shape == self.h_shape
                shape.paint(p)
        if self.current:
            self.current.paint(p)
            self.line.paint(p)
        if self.selected_shape_copy:
            self.selected_shape_copy.paint(p)

        # Paint rect
        if self.current is not None and len(self.line) == 2:
            left_top = self.line[0]
            right_bottom = self.line[1]
            rect_width = right_bottom.x() - left_top.x()
            rect_height = right_bottom.y() - left_top.y()
            p.setPen(self.drawing_rect_color)
            brush = QBrush(Qt.BrushStyle.BDiagPattern)
            p.setBrush(brush)
            p.drawRect(int(left_top.x()), int(left_top.y()), int(rect_width), int(rect_height))

        if self.drawing() and not self.prev_point.isNull() and not self.out_of_pixmap(self.prev_point):
            p.setPen(QColor(0, 0, 0))
            p.drawLine(int(self.prev_point.x()), 0, int(self.prev_point.x()), int(self.pixmap.height()))
            p.drawLine(0, int(self.prev_point.y()), int(self.pixmap.width()), int(self.prev_point.y()))

        self.setAutoFillBackground(True)
        if self.verified:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), QColor(184, 239, 38, 128))
            self.setPalette(pal)
        else:
            pal = self.palette()
            pal.setColor(self.backgroundRole(), QColor(232, 232, 232, 255))
            self.setPalette(pal)

        p.end()

    def transform_pos(self, point):
        """Convert from widget-logical coordinates to painter-logical coordinates."""
        point = QPointF(point.x(), point.y())
        new_pos = point / self.scale - self.offset_to_center()
        return new_pos

    def offset_to_center(self):
        s = self.scale
        area = super(Canvas, self).size()
        w, h = self.pixmap.width() * s, self.pixmap.height() * s
        aw, ah = area.width(), area.height()
        x = (aw - w) / (2 * s) if aw > w else 0
        y = (ah - h) / (2 * s) if ah > h else 0
        return QPointF(x, y)

    def out_of_pixmap(self, p):
        w, h = self.pixmap.width(), self.pixmap.height()
        return not (0 <= p.x() <= w and 0 <= p.y() <= h)

    def finalise(self):
        assert self.current
        if self.current.points[0] == self.current.points[-1]:
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
            return

        self.current.close()
        self.shapes.append(self.current)
        self.current = None
        self.set_hiding(False)
        self.newShape.emit()
        self.update()

    def close_enough(self, p1, p2):
        # d = distance(p1 - p2)
        # m = (p1-p2).manhattanLength()
        # print "d %.2f, m %d, %.2f" % (d, m, d - m)
        return distance(p1 - p2) < self.epsilon

    # These two, along with a call to adjustSize are required for the
    # scroll area.
    def sizeHint(self):
        return self.minimumSizeHint()

    def minimumSizeHint(self):
        if self.pixmap:
            return self.scale * self.pixmap.size()
        return super(Canvas, self).minimumSizeHint()

    def wheelEvent(self, ev):
        delta = ev.angleDelta()
        h_delta = delta.x()
        v_delta = delta.y()

        mods = ev.modifiers()
        if SYSTEM == 'M1':
            if Qt.KeyboardModifier.ControlModifier == mods and v_delta:
                # 按住ctrl
                self.zoomRequest.emit(v_delta)
            else:
                # loge(f'{v_delta=},{Qt.Orientation.Vertical=}', 'warning')
                # loge(f'{h_delta=},{Qt.Orientation.Horizontal=}', 'warning')
                self.scrollRequest.emit(h_delta, v_delta)
        else:
            if int(Qt.KeyboardModifier.ControlModifier) | int(Qt.KeyboardModifier.ShiftModifier) == int(
                    mods) and v_delta:
                # 按住ctrl和shift
                self.lightRequest.emit(v_delta)
            elif Qt.KeyboardModifier.ControlModifier == int(mods) and v_delta:
                # 按住ctrl
                self.zoomRequest.emit(v_delta)
            else:
                self.scrollRequest.emit(h_delta, v_delta)
        ev.accept()

    def keyPressEvent(self, ev):
        key = ev.key()
        if key == Qt.Key.Key_Escape and self.current:
            print('ESC press')
            self.current = None
            self.drawingPolygon.emit(False)
            self.update()
        elif key == Qt.Key.Key_Return and self.can_close_shape():
            self.finalise()
        elif key == Qt.Key.Key_Left and self.selected_shape:
            self.move_one_pixel('Left')
        elif key == Qt.Key.Key_Right and self.selected_shape:
            self.move_one_pixel('Right')
        elif key == Qt.Key.Key_Up and self.selected_shape:
            self.move_one_pixel('Up')
        elif key == Qt.Key.Key_Down and self.selected_shape:
            self.move_one_pixel('Down')

    def move_one_pixel(self, direction):
        # print(self.selectedShape.points)
        if direction == 'Left' and not self.move_out_of_bound(QPointF(-1.0, 0)):
            # print("move Left one pixel")
            self.selected_shape.points[0] += QPointF(-1.0, 0)
            self.selected_shape.points[1] += QPointF(-1.0, 0)
            self.selected_shape.points[2] += QPointF(-1.0, 0)
            self.selected_shape.points[3] += QPointF(-1.0, 0)
        elif direction == 'Right' and not self.move_out_of_bound(QPointF(1.0, 0)):
            # print("move Right one pixel")
            self.selected_shape.points[0] += QPointF(1.0, 0)
            self.selected_shape.points[1] += QPointF(1.0, 0)
            self.selected_shape.points[2] += QPointF(1.0, 0)
            self.selected_shape.points[3] += QPointF(1.0, 0)
        elif direction == 'Up' and not self.move_out_of_bound(QPointF(0, -1.0)):
            # print("move Up one pixel")
            self.selected_shape.points[0] += QPointF(0, -1.0)
            self.selected_shape.points[1] += QPointF(0, -1.0)
            self.selected_shape.points[2] += QPointF(0, -1.0)
            self.selected_shape.points[3] += QPointF(0, -1.0)
        elif direction == 'Down' and not self.move_out_of_bound(QPointF(0, 1.0)):
            # print("move Down one pixel")
            self.selected_shape.points[0] += QPointF(0, 1.0)
            self.selected_shape.points[1] += QPointF(0, 1.0)
            self.selected_shape.points[2] += QPointF(0, 1.0)
            self.selected_shape.points[3] += QPointF(0, 1.0)
        self.shapeMoved.emit()
        self.repaint()

    def move_out_of_bound(self, step):
        points = [p1 + p2 for p1, p2 in zip(self.selected_shape.points, [step] * 4)]
        return True in map(self.out_of_pixmap, points)

    def set_last_label(self, text, line_color=None, fill_color=None):
        assert text
        self.shapes[-1].label = text
        if line_color:
            self.shapes[-1].line_color = line_color

        if fill_color:
            self.shapes[-1].fill_color = fill_color

        return self.shapes[-1]

    def undo_last_line(self):
        assert self.shapes
        self.current = self.shapes.pop()
        self.current.set_open()
        self.line.points = [self.current[-1], self.current[0]]
        self.drawingPolygon.emit(True)

    def reset_all_lines(self):
        assert self.shapes
        self.current = self.shapes.pop()
        self.current.set_open()
        self.line.points = [self.current[-1], self.current[0]]
        self.drawingPolygon.emit(True)
        self.current = None
        self.drawingPolygon.emit(False)
        self.update()

    def load_pixmap(self, pixmap):
        self.pixmap = pixmap
        self.shapes = []
        self.repaint()

    def load_shapes(self, shapes):
        self.shapes = list(shapes)
        self.current = None
        self.repaint()

    def set_shape_visible(self, shape, value):
        self.visible[shape] = value
        self.repaint()

    def current_cursor(self):
        cursor = QApplication.overrideCursor()
        if cursor is not None:
            cursor = cursor.shape()
        return cursor

    def override_cursor(self, cursor):
        self._cursor = cursor
        if self.current_cursor() is None:
            QApplication.setOverrideCursor(cursor)
        else:
            QApplication.changeOverrideCursor(cursor)

    def restore_cursor(self):
        QApplication.restoreOverrideCursor()

    def reset_state(self):
        self.de_select_shape()
        self.un_highlight()
        self.selected_shape_copy = None

        self.restore_cursor()
        self.pixmap = None
        self.update()

    def set_drawing_shape_to_square(self, status):
        self.draw_square = status


class LabelImgWindow(QMainWindow):
    FIT_WINDOW, FIT_WIDTH, MANUAL_ZOOM = list(range(3))

    def __init__(self):
        super().__init__()

        self.a0_para()
        self.a1_initialize()
        self.a2_components()
        self.a3_statusbar()
        self.a4_menubar()
        self.a5_toolbar()
        self.a6_btngroup()
        self.a7_widgets()
        self.a8_layout()
        self.a9_set()

    def b1_window(self):
        return

    def a0_para(self):
        # ================初始化变量================
        self.file_path = image_dir
        # Load predefined classes to the list

        # Application state.
        self.qimage = QImage()

        self.recent_files = []
        self.max_recent = 7
        self.line_color = None
        self.fill_color = None
        self.zoom_level = 100
        self.fit_window = False
        # Add Chris
        self.difficult = False

        self.setWindowTitle(__appname__)

        self.cur_img_idx = 0

        # Whether we need to save or not.
        self.dirty = False

        self._no_selection_slot = False
        self._beginner = True
        self.screencast = "https://youtu.be/p0nR2YsCY_U"

        # Main widgets and related state.
        self.label_dialog = LabelDialog(parent=self, list_item=mc.label_hist)

        self.items_to_shapes = {}
        self.shapes_to_items = {}
        self.prev_label_text = ''

        self.recent_files = []
        self.max_recent = 7
        self.line_color = None
        self.fill_color = None
        self.zoom_level = 100
        self.fit_window = False
        # Add Chris
        self.difficult = False

    def a1_initialize(self):
        pass

    def a2_components(self):
        # Save as Pascal voc xml
        self.label_file_format = app_settings.get(SETTING_LABEL_FILE_FORMAT, LabelFileFormat.PASCAL_VOC)

        # ================编辑标签================
        self.edit_button = QToolButton()
        self.edit_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        # ================有难度的================
        # Create a widget for edit and diffc button
        self.diffc_button = QCheckBox(get_str('useDifficult'))
        self.diffc_button.setChecked(False)
        self.diffc_button.stateChanged.connect(self.button_state)

        # ================使用预设标签================
        # Create a widget for using default label
        self.cb_use_default_label = QCheckBox(get_str('useDefaultLabel'))
        self.cb_use_default_label.setChecked(False)
        self.le_default_label = QLineEdit()

        # ================放大镜================
        # test: show local enlarge img
        self.lb_magnifier = QLabel()
        # self.lb_magnifier.setGeometry(40, 20, 90, 180)
        # x坐标，y坐标，宽度，高度
        # 使用setGeometry(int x, int y, int w, int h)或setGeometry(QRect)设置该属性的值

        # ================下拉框================
        # Create and add combobox for showing unique labels in group
        self.cb_text_list = QComboBox()
        self.items = []
        self.cb_text_list.addItems(self.items)
        self.cb_text_list.currentIndexChanged.connect(self.combo_selection_changed)

        # ================标签列表================
        # Create and add a widget for showing current label items
        self.label_list = QListWidget()
        self.label_list.itemActivated.connect(self.label_selection_changed)
        self.label_list.itemSelectionChanged.connect(self.label_selection_changed)
        self.label_list.itemDoubleClicked.connect(self.edit_label)
        # Connect to itemChanged to detect checkbox changes.
        self.label_list.itemChanged.connect(self.label_item_changed)

        # ================文件工具================
        self.prev_button = QToolButton()
        self.next_button = QToolButton()
        self.play_button = QToolButton()
        self.zoom_org_button = QToolButton()
        self.fit_window_button = QToolButton()
        self.fit_width_button = QToolButton()

        self.tb_files = [
            self.prev_button, self.next_button, self.play_button,
            self.zoom_org_button, self.fit_window_button, self.fit_width_button,
        ]
        for self.tb_file in self.tb_files:
            self.tb_file.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
            self.tb_file.setStyleSheet("QToolButton{margin:2px 5px 2px 0px;padding:2px;}")  # 上右下左

        self.hb_file_control = QHBoxLayout()
        self.hb_file_control.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.hb_file_control.addWidget(self.prev_button)
        self.hb_file_control.addWidget(self.next_button)
        self.hb_file_control.addWidget(self.play_button)
        self.hb_file_control.addWidget(self.zoom_org_button)
        self.hb_file_control.addWidget(self.fit_window_button)
        self.hb_file_control.addWidget(self.fit_width_button)
        # self.hb_file_control.addStretch(1)

        # ================搜索框================
        self.fileSearch = QLineEdit()
        self.fileSearch.setPlaceholderText(get_str("Search Filename"))
        self.fileSearch.textChanged.connect(self.fileSearchChanged)
        # ================文件列表================
        self.lw_file = QListWidget()
        self.md_file = self.lw_file.model()
        self.sm_file = self.lw_file.selectionModel()
        # self.sm_file.currentChanged.connect(self.fileCurrentChanged)
        self.lw_file.itemSelectionChanged.connect(self.fileSelectionChanged)
        # self.lw_file.itemDoubleClicked.connect(self.file_item_double_clicked)
        # self.lw_file.itemClicked.connect(self.file_item_clicked)

        self.zoom_widget = ZoomWidget()
        self.light_widget = LightWidget(get_str('lightWidgetTitle'))
        self.color_dialog = ColorDialog(parent=self)

        self.canvas = Canvas(parent=self)
        self.canvas.zoomRequest.connect(self.zoom_request)
        self.canvas.set_drawing_shape_to_square(app_settings.get(SETTING_DRAW_SQUARE, False))

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.canvas)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_bars = {
            Qt.Orientation.Vertical: self.scroll_area.verticalScrollBar(),
            Qt.Orientation.Horizontal: self.scroll_area.horizontalScrollBar()
        }
        self.canvas.scrollRequest.connect(self.scroll_request)

        self.canvas.newShape.connect(self.new_shape)
        self.canvas.shapeMoved.connect(self.set_dirty)
        self.canvas.selectionChanged.connect(self.shape_selection_changed)
        self.canvas.drawingPolygon.connect(self.toggle_drawing_sensitive)

        # ================区块的标签================
        hb_use_default_label = QHBoxLayout()
        hb_use_default_label.addWidget(self.cb_use_default_label)
        hb_use_default_label.addWidget(self.le_default_label)

        vb_label_edit = QVBoxLayout()
        vb_label_edit.addWidget(self.edit_button)
        vb_label_edit.addWidget(self.diffc_button)
        vb_label_edit.addLayout(hb_use_default_label)
        vb_label_edit.addStretch(1)
        vb_label_edit.setContentsMargins(0, 5, 0, 5)
        vb_label_edit.setSpacing(5)
        w_label_edit = QWidget()
        w_label_edit.setLayout(vb_label_edit)

        vb_cb = QVBoxLayout()
        vb_cb.addWidget(self.cb_text_list)
        vb_cb.addWidget(self.label_list)
        vb_cb.setContentsMargins(0, 5, 0, 5)
        vb_cb.setSpacing(0)
        w_cb = QWidget()
        w_cb.setLayout(vb_cb)

        vb_file = QVBoxLayout()
        vb_file.addLayout(self.hb_file_control)
        vb_file.addWidget(self.fileSearch)
        vb_file.addWidget(self.lw_file)
        vb_file.setContentsMargins(0, 0, 0, 0)
        vb_file.setSpacing(0)
        w_file = QWidget()
        w_file.setLayout(vb_file)

        self.dock_label = QDockWidget(get_str('boxLabelEditText'), self)
        self.dock_label.setObjectName(get_str('labeledit'))
        self.dock_label.setWidget(w_label_edit)
        self.dock_label.setMaximumHeight(150)
        # self.dock_label.setFixedHeight(160)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dock_label.sizePolicy().hasHeightForWidth())
        self.dock_label.setSizePolicy(sizePolicy)

        self.dock_magnifier = QDockWidget(get_str('magnifierAreaText'), self)
        self.dock_magnifier.setObjectName(get_str('magnifierarea'))
        self.dock_magnifier.setWidget(self.lb_magnifier)

        self.dock_cb = QDockWidget(get_str('boxLabelText'), self)
        self.dock_cb.setObjectName(get_str('labels'))
        self.dock_cb.setWidget(w_cb)

        self.file_dock = QDockWidget(get_str('fileList'), self)
        self.file_dock.setObjectName(get_str('files'))
        self.file_dock.setWidget(w_file)

        # ================中心组件================
        self.setCentralWidget(self.scroll_area)
        # ================区块标签编辑================
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_label)
        # ================放大镜区域================
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_magnifier)
        # ================区块的标签================
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock_cb)
        # ================文件列表================
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.file_dock)

        # 常量                                      | 描述
        # --------------------------------------- | --------------
        # QDockWidget::DockWidgetClosable         | 可关闭
        # QDockWidget::DockWidgetMovable          | 可移动
        # QDockWidget::DockWidgetFloatable        | 可漂浮
        # QDockWidget::DockWidgetVerticalTitleBar | 在左边显示垂直的标签栏
        # QDockWidget::AllDockWidgetFeatures      | 具有1,2,3的所有功能
        # QDockWidget::NoDockWidgetFeatures       | 无法关闭，不能移动，不能漂浮

        # self.file_dock.setFeatures(QDockWidget.DockWidgetFloatable)
        # 可关闭、可漂浮
        # self.dock_features = QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetFloatable
        # self.dock_label.setFeatures(self.dock_label.features() ^ self.dock_features)
        # self.dock_magnifier.setFeatures(self.dock_magnifier.features() ^ self.dock_features)
        # self.dock_cb.setFeatures(self.dock_cb.features() ^ self.dock_features)

        self.displayTimer = QTimer(self)
        self.displayTimer.setInterval(mc.play_interval * 1000)
        self.displayTimer.timeout.connect(self.auto_next)

        self.image_playing = False

    def a3_statusbar(self):
        # ================状态栏================
        self.statusbar_main = QStatusBar()
        self.statusbar_main.showMessage(self.tr('Ready'))
        # 设置状态栏，类似布局设置
        self.setStatusBar(self.statusbar_main)

    def a4_menubar(self):
        # ================菜单栏================

        # Actions
        action = partial(new_action, self)
        #  new_action(parent, text, slot=None, shortcut=None, icon=None, tip=None, checkable=False, enabled=True)
        action_quit = action(get_str('quit'), self.close,
                             'Ctrl+Q', 'quit', get_str('quitApp'))

        # 打开目录
        open_dir = action(get_str('openDir'), self.open_dir_dialog, 'Ctrl+u', 'open_dir', get_str('openDir'))

        # 开启标签
        open_annotation = action(get_str('openAnnotation'), self.open_annotation_dialog, 'Ctrl+Shift+O',
                                 'open_annotation', get_str('openAnnotationDetail'))

        copy_prev_bounding = action(get_str('copyPrevBounding'), self.copy_previous_bounding_boxes, 'Ctrl+v', 'copy',
                                    get_str('copyPrevBounding'))
        open_next_image = action(get_str('nextImg'), self.open_next_image, 'd', 'next', get_str('nextImgDetail'))
        open_prev_image = action(get_str('prevImg'), self.open_prev_image, 'a', 'prev', get_str('prevImgDetail'))

        play_image = action(get_str('Play'), self.play_start,
                            'Ctrl+Shift+P', 'play', get_str('auto next'),
                            checkable=True, enabled=True)

        verify = action(get_str('verifyImg'), self.verify_image,
                        'space', 'verify', get_str('verifyImgDetail'))

        save = action(get_str('save'), self.save_file,
                      'Ctrl+S', 'save', get_str('saveDetail'), enabled=False)

        format_meta = get_format_meta(self.label_file_format)
        save_format = action(format_meta[0],
                             self.change_format, 'Ctrl+',
                             get_format_meta(self.label_file_format)[1],
                             get_str('changeSaveFormat'), enabled=True)

        save_as = action(get_str('saveAs'), self.save_file_as,
                         'Ctrl+Shift+S', 'save-as', get_str('saveAsDetail'), enabled=False)

        close_cur = action(get_str('closeCur'), self.close_file, 'Ctrl+W', 'close', get_str('closeCurDetail'))

        delete_image = action(get_str('deleteImg'), self.delete_image, 'Ctrl+Shift+D', 'delete-icon-hover',
                              get_str('deleteImgDetail'))

        reset_all = action(get_str('resetAll'), self.reset_all, None, 'resetall', get_str('resetAllDetail'))

        color1 = action(get_str('boxLineColor'), self.choose_color1,
                        'Ctrl+L', 'color_line', get_str('boxLineColorDetail'))

        create_mode = action(get_str('crtBox'), self.set_create_mode,
                             'w', 'new', get_str('crtBoxDetail'), enabled=False)
        edit_mode = action(get_str('editBox'), self.set_edit_mode,
                           'Ctrl+J', 'edit', get_str('editBoxDetail'), enabled=False)

        create = action(get_str('crtBox'), self.create_shape,
                        'w', 'new', get_str('crtBoxDetail'), enabled=False)
        delete = action(get_str('delBox'), self.delete_selected_shape,
                        'Delete', 'delete', get_str('delBoxDetail'), enabled=False)
        copy = action(get_str('dupBox'), self.copy_selected_shape,
                      'Ctrl+D', 'copy', get_str('dupBoxDetail'),
                      enabled=False)

        advanced_mode = action(get_str('advancedMode'), self.toggle_advanced_mode,
                               'Ctrl+Shift+A', 'expert', get_str('advancedModeDetail'),
                               checkable=True)

        hide_all = action(get_str('hideAllBox'), partial(self.toggle_polygons, False),
                          'Ctrl+H', 'hide_all', get_str('hideAllBoxDetail'),
                          enabled=False)
        show_all = action(get_str('showAllBox'), partial(self.toggle_polygons, True),
                          'Ctrl+A', 'show_all', get_str('showAllBoxDetail'),
                          enabled=False)

        help_default = action(get_str('tutorialDefault'), self.show_default_tutorial_dialog, None, 'help',
                              get_str('tutorialDetail'))
        show_info = action(get_str('info'), self.show_info_dialog, None, 'help', get_str('info'))
        show_shortcut = action(get_str('shortcut'), self.show_shortcuts_dialog, None, 'help', get_str('shortcut'))

        zoom = QWidgetAction(self)
        zoom.setDefaultWidget(self.zoom_widget)
        self.zoom_widget.setWhatsThis(
            u"Zoom in or out of the image. Also accessible with"
            " %s and %s from the canvas." % (format_shortcut("Ctrl+[-+]"),
                                             format_shortcut("Ctrl+Wheel")))
        self.zoom_widget.setEnabled(False)

        zoom_in = action(get_str('zoomin'), partial(self.add_zoom, 10),
                         'Ctrl++', 'zoom-in', get_str('zoominDetail'), enabled=False)
        zoom_out = action(get_str('zoomout'), partial(self.add_zoom, -10),
                          'Ctrl+-', 'zoom-out', get_str('zoomoutDetail'), enabled=False)
        zoom_org = action(get_str('originalsize'), partial(self.set_zoom, 100),
                          'Ctrl+0', 'zoom', get_str('originalsizeDetail'),
                          checkable=True, enabled=False)
        fit_window = action(get_str('fitWin'), self.set_fit_window,
                            'Ctrl+F', 'fit-window', get_str('fitWinDetail'),
                            checkable=True, enabled=False)
        fit_width = action(get_str('fitWidth'), self.set_fit_width,
                           'Ctrl+Shift+F', 'fit-width', get_str('fitWidthDetail'),
                           checkable=True, enabled=False)
        # Group zoom controls into a list for easier toggling.
        zoom_actions = (self.zoom_widget, zoom_in, zoom_out,
                        zoom_org, fit_window, fit_width)
        self.zoom_mode = self.MANUAL_ZOOM
        self.scalers = {
            self.FIT_WINDOW: self.scale_fit_window,
            self.FIT_WIDTH: self.scale_fit_width,
            # Set to one to scale to 100% when loading files.
            self.MANUAL_ZOOM: lambda: 1,
        }

        light = QWidgetAction(self)
        light.setDefaultWidget(self.light_widget)
        self.light_widget.setWhatsThis(
            u"Brighten or darken current image. Also accessible with"
            " %s and %s from the canvas." % (format_shortcut("Ctrl+Shift+[-+]"),
                                             format_shortcut("Ctrl+Shift+Wheel")))
        self.light_widget.setEnabled(False)

        light_brighten = action(get_str('lightbrighten'), partial(self.add_light, 10),
                                'Ctrl+Shift++', 'light_lighten', get_str('lightbrightenDetail'), enabled=False)
        light_darken = action(get_str('lightdarken'), partial(self.add_light, -10),
                              'Ctrl+Shift+-', 'light_darken', get_str('lightdarkenDetail'), enabled=False)
        light_org = action(get_str('lightreset'), partial(self.set_light, 50),
                           'Ctrl+Shift+0', 'light_reset', get_str('lightresetDetail'), checkable=True, enabled=False)
        light_org.setChecked(True)

        # Group light controls into a list for easier toggling.
        light_actions = (self.light_widget, light_brighten,
                         light_darken, light_org)

        edit = action(get_str('editLabel'), self.edit_label,
                      'Ctrl+E', 'edit', get_str('editLabelDetail'),
                      enabled=False)
        self.edit_button.setDefaultAction(edit)

        shape_line_color = action(get_str('shapeLineColor'), self.choose_shape_line_color,
                                  icon='color_line', tip=get_str('shapeLineColorDetail'),
                                  enabled=False)
        shape_fill_color = action(get_str('shapeFillColor'), self.choose_shape_fill_color,
                                  icon='color', tip=get_str('shapeFillColorDetail'),
                                  enabled=False)

        self.prev_button.setDefaultAction(open_prev_image)
        self.next_button.setDefaultAction(open_next_image)
        self.play_button.setDefaultAction(play_image)
        self.zoom_org_button.setDefaultAction(zoom_org)
        self.fit_window_button.setDefaultAction(fit_window)
        self.fit_width_button.setDefaultAction(fit_width)

        # Label list context menu.
        label_menu = QMenu()
        add_actions(label_menu, (edit, delete))
        self.label_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.label_list.customContextMenuRequested.connect(self.pop_label_list_menu)

        # Draw squares/rectangles
        self.draw_squares_option = QAction(get_str('drawSquares'), self)
        self.draw_squares_option.setShortcut('Ctrl+Shift+R')
        self.draw_squares_option.setCheckable(True)
        self.draw_squares_option.setChecked(app_settings.get(SETTING_DRAW_SQUARE, False))
        self.draw_squares_option.triggered.connect(self.toggle_draw_square)

        # Store actions for further handling.
        self.actions = Struct(
            save=save, save_format=save_format, saveAs=save_as, close_cur=close_cur, resetAll=reset_all,
            deleteImg=delete_image,
            lineColor=color1, create=create, delete=delete, edit=edit, copy=copy,
            createMode=create_mode, editMode=edit_mode, advancedMode=advanced_mode,
            shapeLineColor=shape_line_color, shapeFillColor=shape_fill_color,
            zoom=zoom, zoomIn=zoom_in, zoomOut=zoom_out, zoomOrg=zoom_org,
            fitWindow=fit_window, fitWidth=fit_width,
            zoomActions=zoom_actions,
            lightBrighten=light_brighten, lightDarken=light_darken, lightOrg=light_org,
            lightActions=light_actions,
            fileMenuActions=(
                open_dir, save, save_as, close_cur, reset_all, action_quit),
            beginner=(), advanced=(),
            editMenu=(edit, copy, delete,
                      None, color1, self.draw_squares_option),
            beginnerContext=(create, edit, copy, delete),
            advancedContext=(create_mode, edit_mode, edit, copy,
                             delete, shape_line_color, shape_fill_color),
            onLoadActive=(
                close_cur, create, create_mode, edit_mode),
            onShapesPresent=(save_as, hide_all, show_all))

        menu_file = self.menuBar().addMenu(get_str('menu_file'))
        menu_edit = self.menuBar().addMenu(get_str('menu_edit'))
        menu_view = self.menuBar().addMenu(get_str('menu_view'))
        menu_help = self.menuBar().addMenu(get_str('menu_help'))
        self.menus = Struct(
            file=menu_file,
            edit=menu_edit,
            view=menu_view,
            help=menu_help,
            recentFiles=QMenu(get_str('menu_openRecent')),
            labelList=label_menu)

        self.use_magnifying_glass = QAction(get_str('Magnifying Glass'), self)
        self.use_magnifying_glass.setCheckable(True)
        self.use_magnifying_glass.setChecked(app_settings.get(SETTING_Magnifying_Lens, False))
        # Auto saving : Enable auto saving if pressing next
        self.auto_saving = QAction(get_str('autoSaveMode'), self)
        self.auto_saving.setCheckable(True)
        self.auto_saving.setChecked(app_settings.get(SETTING_AUTO_SAVE, False))
        # Sync single class mode from PR#106
        self.single_class_mode = QAction(get_str('singleClsMode'), self)
        self.single_class_mode.setShortcut("Ctrl+Shift+G")
        self.single_class_mode.setCheckable(True)
        self.single_class_mode.setChecked(app_settings.get(SETTING_SINGLE_CLASS, False))
        self.lastLabel = None
        # Add option to enable/disable labels being displayed at the top of bounding boxes
        self.display_label_option = QAction(get_str('displayLabel'), self)
        self.display_label_option.setShortcut("Ctrl+Shift+P")
        self.display_label_option.setCheckable(True)
        self.display_label_option.setChecked(app_settings.get(SETTING_PAINT_LABEL, False))
        self.display_label_option.triggered.connect(self.toggle_paint_labels_option)

        add_actions(self.menus.file,
                    (
                        open_dir, open_annotation, copy_prev_bounding,
                        self.menus.recentFiles,
                        save,
                        save_format, save_as, close_cur, reset_all, delete_image, action_quit
                    ))
        add_actions(self.menus.help, (help_default, show_info, show_shortcut))
        add_actions(self.menus.view, (
            self.dock_label.toggleViewAction(),
            self.dock_magnifier.toggleViewAction(),
            self.dock_cb.toggleViewAction(),
            self.file_dock.toggleViewAction(),
            None,
            self.use_magnifying_glass,
            self.auto_saving,
            self.single_class_mode,
            self.display_label_option,
            advanced_mode, None,
            hide_all, show_all, None,
            zoom_in, zoom_out, None,
            zoom_org, fit_window, fit_width, None,
            light_brighten, light_darken, light_org))

        self.dock_label.toggleViewAction().setShortcut('Ctrl+1')
        self.dock_magnifier.toggleViewAction().setShortcut('Ctrl+2')
        self.dock_cb.toggleViewAction().setShortcut('Ctrl+3')
        self.file_dock.toggleViewAction().setShortcut('Ctrl+4')

        self.menus.file.aboutToShow.connect(self.update_file_menu)

        # Custom context menu for the canvas widget:
        add_actions(self.canvas.menus[0], self.actions.beginnerContext)
        add_actions(self.canvas.menus[1], (
            action('&Copy here', self.copy_shape),
            action('&Move here', self.move_shape)))

        self.actions.beginner = (
            open_dir, verify, save, save_format, None,
            create,
            copy, delete, None,
            zoom_in, zoom, zoom_out, None,
            # zoom_org, fit_window, fit_width, None,
            light_brighten, light, light_darken, light_org, None,
            hide_all, show_all)

        self.actions.advanced = (
            open_dir, open_next_image, open_prev_image, play_image, save, save_format, None,
            create_mode, edit_mode, None,
            hide_all, show_all)

    def a5_toolbar(self):
        self.tb_main = QToolBar('Tools')
        self.tb_main.setObjectName(u'ToolsToolBar')
        self.tb_main.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        # self.tb_main.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        if SYSTEM == 'WINDOWS':
            self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.tb_main)
        else:
            self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tb_main)

        self.statusbar_main.showMessage(f'{__appname__} started.')

    def a6_btngroup(self):
        # ================多选框组================
        pass

    def a7_widgets(self):
        pass

    def a8_layout(self):
        pass

    def a9_set(self):
        # Fix the compatible issue for qt4 and qt5. Convert the QStringList to python list
        if app_settings.get(SETTING_RECENT_FILES):
            self.recent_files = app_settings.get(SETTING_RECENT_FILES)

        size = app_settings.get(SETTING_WIN_SIZE, QSize(600, 500))
        position = QPoint(0, 0)

        saved_position = app_settings.get(SETTING_WIN_POSE, position)
        # Fix the multiple monitors issue
        if SYSTEM == 'M1':
            for i in range(len(QApplication.screens())):
                if QApplication.screens()[i].availableGeometry().contains(saved_position):
                    position = saved_position
                    break
        else:
            for i in range(QApplication.desktop().screenCount()):
                if QApplication.desktop().availableGeometry(i).contains(saved_position):
                    position = saved_position
                    break
        self.resize(size)
        self.move(position)

        self.restoreState(app_settings.get(SETTING_WIN_STATE, QByteArray()))
        Shape.line_color = self.line_color = QColor(app_settings.get(SETTING_LINE_COLOR, DEFAULT_LINE_COLOR))
        Shape.fill_color = self.fill_color = QColor(app_settings.get(SETTING_FILL_COLOR, DEFAULT_FILL_COLOR))
        self.canvas.set_drawing_color(self.line_color)
        # Add chris
        Shape.difficult = self.difficult

        if SYSTEM != 'M1':
            def xbool(x):
                if isinstance(x, QVariant):
                    return x.toBool()
                return bool(x)

            if xbool(app_settings.get(SETTING_ADVANCE_MODE, False)):
                self.actions.advancedMode.setChecked(True)
                self.toggle_advanced_mode()

        # Populate the File menu dynamically.
        self.update_file_menu()

        # Since loading the file may take some time, make sure it runs in the background.
        if self.file_path and os.path.isdir(self.file_path):
            self.queue_event(partial(self.import_dir_images, self.file_path or ""))
        elif self.file_path:
            self.queue_event(partial(self.qload_file, self.file_path or ""))

        # Callbacks:
        self.zoom_widget.valueChanged.connect(self.paint_canvas)
        self.light_widget.valueChanged.connect(self.paint_canvas)

        self.populate_mode_actions()

        # Display cursor coordinates at the right of status bar
        self.label_coordinates = QLabel('')
        self.statusbar_main.addPermanentWidget(self.label_coordinates)

        # Open Dir if default file
        # if self.file_path and os.path.isdir(self.file_path):
        #     self.open_dir_dialog(dir_path=self.file_path, silent=True)

        # ================窗口设置================
        self.center()
        self.show()

    # ================控制窗口显示在屏幕中心的方法================
    def center(self):
        # # 获得窗口
        # qr = self.frameGeometry()
        # # 获得屏幕中心点
        # cp = QDesktopWidget().availableGeometry().center()
        # # 显示到屏幕中心
        # qr.moveCenter(cp)
        #
        # self.move(qr.topLeft())
        self.move(10, 10)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Control:
            self.canvas.set_drawing_shape_to_square(False)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Control:
            # Draw rectangle if Ctrl is pressed
            self.canvas.set_drawing_shape_to_square(True)

    # Support Functions #
    def set_format(self, save_format):
        if save_format == FORMAT_PASCALVOC:
            self.actions.save_format.setText(FORMAT_PASCALVOC)
            self.actions.save_format.setIcon(new_icon("format_voc"))
            self.label_file_format = LabelFileFormat.PASCAL_VOC
            LabelFile.suffix = XML_EXT

        elif save_format == FORMAT_YOLO:
            self.actions.save_format.setText(FORMAT_YOLO)
            self.actions.save_format.setIcon(new_icon("format_yolo"))
            self.label_file_format = LabelFileFormat.YOLO
            LabelFile.suffix = TXT_EXT

        elif save_format == FORMAT_CREATEML:
            self.actions.save_format.setText(FORMAT_CREATEML)
            self.actions.save_format.setIcon(new_icon("format_createml"))
            self.label_file_format = LabelFileFormat.CREATE_ML
            LabelFile.suffix = JSON_EXT

    def change_format(self):
        if self.label_file_format == LabelFileFormat.PASCAL_VOC:
            self.set_format(FORMAT_YOLO)
        elif self.label_file_format == LabelFileFormat.YOLO:
            self.set_format(FORMAT_CREATEML)
        elif self.label_file_format == LabelFileFormat.CREATE_ML:
            self.set_format(FORMAT_PASCALVOC)
        else:
            raise ValueError('Unknown label file format.')
        self.set_dirty()

    def no_shapes(self):
        return not self.items_to_shapes

    def toggle_advanced_mode(self, value=True):
        self._beginner = not value
        self.canvas.set_editing(True)
        self.populate_mode_actions()
        self.edit_button.setVisible(not value)
        if value:
            self.actions.createMode.setEnabled(True)
            self.actions.editMode.setEnabled(False)
            # self.dock_label.setFeatures(self.dock_label.features() | self.dock_features)
        else:
            pass
            # self.dock_label.setFeatures(self.dock_label.features() ^ self.dock_features)

    def populate_mode_actions(self):
        if self.beginner():
            tool, menu = self.actions.beginner, self.actions.beginnerContext
        else:
            tool, menu = self.actions.advanced, self.actions.advancedContext
        self.tb_main.clear()
        add_actions(self.tb_main, tool)
        self.canvas.menus[0].clear()
        add_actions(self.canvas.menus[0], menu)
        self.menus.edit.clear()
        actions = (self.actions.create,) if self.beginner() else (self.actions.createMode, self.actions.editMode)
        add_actions(self.menus.edit, actions + self.actions.editMenu)

    def set_beginner(self):
        self.tb_main.clear()
        add_actions(self.tb_main, self.actions.beginner)

    def set_advanced(self):
        self.tb_main.clear()
        add_actions(self.tb_main, self.actions.advanced)

    def set_dirty(self):
        self.dirty = True
        self.actions.save.setEnabled(True)

    def set_clean(self):
        self.dirty = False
        self.actions.save.setEnabled(False)
        self.actions.create.setEnabled(True)

    def toggle_actions(self, value=True):
        """Enable/Disable widgets which depend on an opened image."""
        for z in self.actions.zoomActions:
            z.setEnabled(value)
        for z in self.actions.lightActions:
            z.setEnabled(value)
        for action in self.actions.onLoadActive:
            action.setEnabled(value)

    def queue_event(self, function):
        QTimer.singleShot(0, function)

    def status(self, message, delay=5000):
        self.statusbar_main.showMessage(message, delay)

    def reset_state(self):
        self.items_to_shapes.clear()
        self.shapes_to_items.clear()
        self.label_list.clear()
        self.file_path = None
        self.image_data = None
        self.label_file = None
        self.canvas.reset_state()
        self.label_coordinates.clear()
        self.cb_text_list.clear()

    def current_item(self):
        items = self.label_list.selectedItems()
        if items:
            return items[0]
        return None

    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        elif len(self.recent_files) >= self.max_recent:
            self.recent_files.pop()
        self.recent_files.insert(0, file_path)

    def beginner(self):
        return self._beginner

    def advanced(self):
        return not self.beginner()

    def show_tutorial_dialog(self, browser='default', link=None):
        if link is None:
            link = self.screencast

        if browser.lower() == 'default':
            webbrowser.open(link, new=2)
        elif browser.lower() == 'chrome' and SYSTEM == 'WINDOWS':
            if shutil.which(browser.lower()):  # 'chrome' not in wb._browsers in windows
                webbrowser.register('chrome', None, webbrowser.BackgroundBrowser('chrome'))
            else:
                chrome_path = "D:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
                if os.path.isfile(chrome_path):
                    webbrowser.register('chrome', None, webbrowser.BackgroundBrowser(chrome_path))
            try:
                webbrowser.get('chrome').open(link, new=2)
            except:
                webbrowser.open(link, new=2)
        elif browser.lower() in webbrowser._browsers:
            webbrowser.get(browser.lower()).open(link, new=2)

    def show_default_tutorial_dialog(self):
        self.show_tutorial_dialog(browser='default')

    def show_info_dialog(self):
        msg = f'{get_str("Name")}:{__appname__} \n{sys.version_info}'
        QMessageBox.information(self, get_str('Information'), msg)

    def show_shortcuts_dialog(self):
        msg = keysInfo(locale_str)
        QMessageBox.information(self, get_str('Information'), msg)
        # self.show_tutorial_dialog(browser='default', link='https://github.com/tzutalin/labelImg#Hotkeys')

    def create_shape(self):
        assert self.beginner()
        self.canvas.set_editing(False)
        self.actions.create.setEnabled(False)

    def toggle_drawing_sensitive(self, drawing=True):
        """In the middle of drawing, toggling between modes should be disabled."""
        self.actions.editMode.setEnabled(not drawing)
        if not drawing and self.beginner():
            # Cancel creation.
            print('Cancel creation.')
            self.canvas.set_editing(True)
            self.canvas.restore_cursor()
            self.actions.create.setEnabled(True)

    def toggle_draw_mode(self, edit=True):
        self.canvas.set_editing(edit)
        self.actions.createMode.setEnabled(edit)
        self.actions.editMode.setEnabled(not edit)

    def set_create_mode(self):
        assert self.advanced()
        self.toggle_draw_mode(False)

    def set_edit_mode(self):
        assert self.advanced()
        self.toggle_draw_mode(True)
        self.label_selection_changed()

    def update_file_menu(self):
        curr_file_path = self.file_path

        menu = self.menus.recentFiles
        menu.clear()
        files = [f for f in self.recent_files if f !=
                 curr_file_path and exists(f)]
        for i, f in enumerate(files):
            icon = new_icon('labels')
            action = QAction(
                icon, '&%d %s' % (i + 1, QFileInfo(f).fileName()), self)
            action.triggered.connect(partial(self.load_recent, f))
            menu.addAction(action)

    def pop_label_list_menu(self, point):
        self.menus.labelList.exec(self.label_list.mapToGlobal(point))

    def edit_label(self):
        if not self.canvas.editing():
            return
        item = self.current_item()
        if not item:
            return
        text = self.label_dialog.pop_up(item.text())
        if text is not None:
            item.setText(text)
            item.setBackground(generate_color_by_text(text))
            self.set_dirty()
            self.update_combo_box()

    def fileSearchChanged(self):
        self.import_dir_images(
            mc.file_dir,
            pattern=self.fileSearch.text(),
            load=False,
        )

    def fileCurrentChanged(self, current, previous):
        pass
        # filename = self.md_file.data(current, Qt.EditRole)
        # loge(f'{filename=}', 'debug')
        #
        # items = self.lw_file.selectedItems()
        # if not items:
        #     return
        # item = items[0]
        # # loge(f'{item.text()=}', 'debug')
        #
        # self.cur_img_idx = mc.imgRelPaths.index(item.text())
        # # loge(f'{self.cur_img_idx=}', 'debug')
        # # loge(f'{len(mc.imgRelPaths)=}', 'debug')
        # if 0 <= self.cur_img_idx < len(mc.imgRelPaths):
        #     filename = mc.image_list[self.cur_img_idx]
        #     # loge(f'{filename=}', 'debug')
        #     if filename:
        #         self.qload_file(filename)

    def fileSelectionChanged(self):
        # pass
        items = self.lw_file.selectedItems()
        if not items:
            return
        item = items[0]
        # loge(f'{item.text()=}', 'debug')

        self.cur_img_idx = mc.imgRelPaths.index(item.text())
        # loge(f'{self.cur_img_idx=}', 'debug')
        # loge(f'{len(mc.imgRelPaths)=}', 'debug')
        if 0 <= self.cur_img_idx < len(mc.imgRelPaths):
            filename = mc.image_list[self.cur_img_idx]
            # loge(f'{filename=}', 'debug')
            if filename:
                self.qload_file(filename)

    # Tzutalin 20160906 : Add file list and dock to move faster
    def file_item_double_clicked(self, item=None):
        pass

    def file_item_clicked(self, item=None):
        pass

    # TODO auto_next
    def auto_next(self):
        if self.image_playing:
            suc = self.open_next_image()
            if not suc:
                self.actions.play.triggered.emit(False)
                self.actions.play.setChecked(False)

    def play_start(self, value=True):
        if value:
            self.image_playing = True
            self.displayTimer.start()
        else:
            self.image_playing = False
            self.displayTimer.stop()

    # Add chris
    def button_state(self, item=None):
        """ Function to handle difficult examples
        Update on each object """
        if not self.canvas.editing():
            return

        item = self.current_item()
        if not item:  # If not selected Item, take the first one
            item = self.label_list.item(self.label_list.count() - 1)

        difficult = self.diffc_button.isChecked()

        try:
            shape = self.items_to_shapes[item]
        except:
            pass
        # Checked and Update
        try:
            if difficult != shape.difficult:
                shape.difficult = difficult
                self.set_dirty()
            else:  # User probably changed item visibility
                self.canvas.set_shape_visible(shape, item.checkState() == Qt.CheckState.Checked)
        except:
            pass

    # React to canvas signals.
    def shape_selection_changed(self, selected=False):
        if self._no_selection_slot:
            self._no_selection_slot = False
        else:
            shape = self.canvas.selected_shape
            if shape:
                self.shapes_to_items[shape].setSelected(True)
            else:
                self.label_list.clearSelection()
        self.actions.delete.setEnabled(selected)
        self.actions.copy.setEnabled(selected)
        self.actions.edit.setEnabled(selected)
        self.actions.shapeLineColor.setEnabled(selected)
        self.actions.shapeFillColor.setEnabled(selected)

    def add_label(self, shape):
        shape.paint_label = self.display_label_option.isChecked()
        item = HashableQListWidgetItem(f'{shape.label}')
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
        item.setCheckState(Qt.CheckState.Checked)
        item.setBackground(generate_color_by_text(shape.label))
        self.items_to_shapes[item] = shape
        self.shapes_to_items[shape] = item
        self.label_list.addItem(item)
        for action in self.actions.onShapesPresent:
            action.setEnabled(True)
        self.update_combo_box()

    def remove_label(self, shape):
        if shape is None:
            # print('rm empty label')
            return
        item = self.shapes_to_items[shape]
        self.label_list.takeItem(self.label_list.row(item))
        del self.shapes_to_items[shape]
        del self.items_to_shapes[item]
        self.update_combo_box()

    def load_labels(self, shapes):
        s = []
        for label, points, line_color, fill_color, difficult in shapes:
            shape = Shape(label=label)
            for x, y in points:

                # Ensure the labels are within the bounds of the image. If not, fix them.
                x, y, snapped = self.canvas.snap_point_to_canvas(x, y)
                if snapped:
                    self.set_dirty()

                shape.add_point(QPointF(x, y))
            shape.difficult = difficult
            shape.close()
            s.append(shape)

            if line_color:
                shape.line_color = QColor(*line_color)
            else:
                shape.line_color = generate_color_by_text(label)

            if fill_color:
                shape.fill_color = QColor(*fill_color)
            else:
                shape.fill_color = generate_color_by_text(label)

            self.add_label(shape)
        self.update_combo_box()
        self.canvas.load_shapes(s)

    def update_combo_box(self):
        # Get the unique labels and add them to the Combobox.
        items_text_list = [str(self.label_list.item(i).text()) for i in range(self.label_list.count())]

        unique_text_list = list(set(items_text_list))
        # Add a null row for showing all the labels
        unique_text_list.append("")
        unique_text_list.sort()

        self.cb_text_list.clear()
        self.cb_text_list.addItems(unique_text_list)

    def save_labels(self, annotation_file_path):
        if self.label_file is None:
            self.label_file = LabelFile()
            self.label_file.verified = self.canvas.verified

        shapes = [format_shape(shape) for shape in self.canvas.shapes]
        # Can add different annotation formats here
        try:
            if self.label_file_format == LabelFileFormat.PASCAL_VOC:
                if annotation_file_path[-4:].lower() != ".xml":
                    annotation_file_path += XML_EXT
                self.label_file.save_pascal_voc_format(annotation_file_path, shapes, self.file_path, self.image_data,
                                                       self.line_color.getRgb(), self.fill_color.getRgb())
            elif self.label_file_format == LabelFileFormat.YOLO:
                if annotation_file_path[-4:].lower() != ".txt":
                    annotation_file_path += TXT_EXT
                self.label_file.save_yolo_format(annotation_file_path, shapes, self.file_path, self.image_data,
                                                 self.classes,
                                                 self.line_color.getRgb(), self.fill_color.getRgb())
            elif self.label_file_format == LabelFileFormat.CREATE_ML:
                if annotation_file_path[-5:].lower() != ".json":
                    annotation_file_path += JSON_EXT
                self.label_file.save_create_ml_format(annotation_file_path, shapes, self.file_path, self.image_data,
                                                      self.classes, self.line_color.getRgb(),
                                                      self.fill_color.getRgb())
            else:
                self.label_file.save(annotation_file_path, shapes, self.file_path, self.image_data,
                                     self.line_color.getRgb(), self.fill_color.getRgb())
            loge(f'Image: {self.file_path} -> Annotation: {annotation_file_path}', 'debug')
            return True
        except LabelFileError as e:
            self.error_message(u'Error saving label data', u'<b>%s</b>' % e)
            return False

    def copy_selected_shape(self):
        self.add_label(self.canvas.copy_selected_shape())
        # fix copy and delete
        self.shape_selection_changed(True)

    def combo_selection_changed(self, index):
        text = self.cb_text_list.itemText(index)
        for i in range(self.label_list.count()):
            if text == "":
                self.label_list.item(i).setCheckState(Qt.CheckState(2))
            elif text != self.label_list.item(i).text():
                self.label_list.item(i).setCheckState(Qt.CheckState(0))
            else:
                self.label_list.item(i).setCheckState(Qt.CheckState(2))

    def label_selection_changed(self):
        item = self.current_item()
        if item and self.canvas.editing():
            self._no_selection_slot = True
            self.canvas.select_shape(self.items_to_shapes[item])
            shape = self.items_to_shapes[item]
            # Add Chris
            self.diffc_button.setChecked(shape.difficult)

    def label_item_changed(self, item):
        shape = self.items_to_shapes[item]
        label = item.text()
        if label != shape.label:
            shape.label = item.text()
            shape.line_color = generate_color_by_text(shape.label)
            self.set_dirty()
        else:  # User probably changed item visibility
            self.canvas.set_shape_visible(shape, item.checkState() == Qt.CheckState.Checked)

    # Callback functions:
    def new_shape(self):
        """Pop-up and give focus to the label editor.

        position MUST be in global coordinates.
        """
        if not self.cb_use_default_label.isChecked() or not self.le_default_label.text():
            self.par_dir = Path(self.file_path).parent
            self.classes = get_classes(self.par_dir)
            list_item = self.classes
            if not list_item:
                if len(mc.label_hist) > 0:
                    list_item = mc.label_hist
            self.label_dialog = LabelDialog(parent=self, list_item=list_item)

            # Sync single class mode from PR#106
            if self.single_class_mode.isChecked() and self.lastLabel:
                text = self.lastLabel
            else:
                text = self.label_dialog.pop_up(text=self.prev_label_text)
                self.lastLabel = text
        else:
            text = self.le_default_label.text()

        # Add Chris
        self.diffc_button.setChecked(False)
        if text is not None:
            self.prev_label_text = text
            generate_color = generate_color_by_text(text)
            shape = self.canvas.set_last_label(text, generate_color, generate_color)
            self.add_label(shape)
            if self.beginner():  # Switch to edit mode.
                self.canvas.set_editing(True)
                self.actions.create.setEnabled(True)
            else:
                self.actions.editMode.setEnabled(True)
            self.set_dirty()

            if text not in mc.label_hist:
                mc.label_hist.append(text)
        else:
            # self.canvas.undoLastLine()
            self.canvas.reset_all_lines()

    @logger.catch
    def scroll_request(self, h_delta, v_delta):
        # TODO scroll_request
        # loge(f'{h_delta=},{v_delta=}', 'debug')

        if h_delta != 0:
            orientation = Qt.Orientation.Horizontal
            delta = h_delta
        else:
            orientation = Qt.Orientation.Vertical
            delta = v_delta

        if SYSTEM == 'M1':
            pass
            # loge(f'{delta=},{orientation=}', 'debug')

        units = - delta / (8 * 15)
        # orientation属性缺省是水平方向（Qt.Horizontal,值为0x1），
        # 可以使用orientation()、setOrientation(Qt.Orientation orientation)来访问，
        # 垂直方向的为Qt.Vertical，值为0x2。
        bar = self.scroll_bars[orientation]
        # 移动相应距离
        bar.setValue(int(bar.value() + bar.singleStep() * units))

    def set_zoom(self, value):
        self.actions.fitWidth.setChecked(False)
        self.actions.fitWindow.setChecked(False)
        # self.actions.zoomOrg.setChecked(False)
        # 如果大小为100%则选中原始大小
        self.actions.zoomOrg.setChecked(int(value) == 100)

        self.zoom_mode = self.MANUAL_ZOOM
        # Arithmetic on scaling factor often results in float
        # Convert to int to avoid type errors
        self.zoom_widget.setValue(int(value))

    def add_zoom(self, increment=10):
        self.set_zoom(self.zoom_widget.value() + increment)

    def zoom_request(self, delta):
        # get the current scrollbar positions
        # calculate the percentages ~ coordinates
        h_bar = self.scroll_bars[Qt.Orientation.Horizontal]
        v_bar = self.scroll_bars[Qt.Orientation.Vertical]

        # get the current maximum, to know the difference after zooming
        h_bar_max = h_bar.maximum()
        v_bar_max = v_bar.maximum()

        # get the cursor position and canvas size
        # calculate the desired movement from 0 to 1
        # where 0 = move left
        #       1 = move right
        # up and down analogous
        cursor = QCursor()
        pos = cursor.pos()
        relative_pos = QWidget.mapFromGlobal(self, pos)

        cursor_x = relative_pos.x()
        cursor_y = relative_pos.y()

        w = self.scroll_area.width()
        h = self.scroll_area.height()

        # the scaling from 0 to 1 has some padding
        # you don't have to hit the very leftmost pixel for a maximum-left movement
        margin = 0.1
        move_x = (cursor_x - margin * w) / (w - 2 * margin * w)
        move_y = (cursor_y - margin * h) / (h - 2 * margin * h)

        # clamp the values from 0 to 1
        move_x = min(max(move_x, 0), 1)
        move_y = min(max(move_y, 0), 1)

        # zoom in
        units = delta // (8 * 15)
        scale = 10
        self.add_zoom(scale * units)

        # get the difference in scrollbar values
        # this is how far we can move
        d_h_bar_max = h_bar.maximum() - h_bar_max
        d_v_bar_max = v_bar.maximum() - v_bar_max

        # get the new scrollbar values
        new_h_bar_value = int(h_bar.value() + move_x * d_h_bar_max)
        new_v_bar_value = int(v_bar.value() + move_y * d_v_bar_max)

        h_bar.setValue(new_h_bar_value)
        v_bar.setValue(new_v_bar_value)

    def light_request(self, delta):
        self.add_light(5 * delta // (8 * 15))

    def set_fit_window(self, value=True):
        if value:
            self.actions.fitWidth.setChecked(False)
            self.actions.zoomOrg.setChecked(False)

        self.zoom_mode = self.FIT_WINDOW if value else self.MANUAL_ZOOM
        self.adjust_scale()

    def set_fit_width(self, value=True):
        if value:
            self.actions.fitWindow.setChecked(False)
            self.actions.zoomOrg.setChecked(False)

        self.zoom_mode = self.FIT_WIDTH if value else self.MANUAL_ZOOM
        self.adjust_scale()

    def set_light(self, value):
        # 如果亮度为50则选中原始亮度
        self.actions.lightOrg.setChecked(int(value) == 50)
        # Arithmetic on scaling factor often results in float
        # Convert to int to avoid type errors
        self.light_widget.setValue(int(value))

    def add_light(self, increment=10):
        self.set_light(self.light_widget.value() + increment)

    def toggle_polygons(self, value):
        for item, shape in self.items_to_shapes.items():
            item.setCheckState(Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)

    def qload_file(self, file_path=None):
        # TODO qload_file
        """Load the specified file, or the last opened file if None."""
        # changing fileListWidget loads file
        if file_path in mc.image_list and (self.lw_file.currentRow() != mc.image_list.index(file_path)):
            # 改变所选行数
            self.lw_file.setCurrentRow(mc.image_list.index(file_path))
            self.lw_file.repaint()
            return

        self.reset_state()
        self.canvas.setEnabled(False)

        # Make sure that filePath is a regular python string, rather than QString
        # Fix bug: An  index error after select a directory when open a new file.
        unicode_file_path = os.path.abspath(file_path)
        # Tzutalin 20160906 : Add file list and dock to move faster
        # Highlight the file item
        if self.lw_file.count() > 0:
            if file_path in mc.image_list:
                index = mc.image_list.index(file_path)
                file_widget_item = self.lw_file.item(index)
                file_widget_item.setSelected(True)
            else:
                self.lw_file.clear()
                mc.image_list.clear()

        if Path(file_path).exists():
            if LabelFile.is_label_file(unicode_file_path):
                try:
                    self.label_file = LabelFile(unicode_file_path)
                except LabelFileError as e:
                    self.error_message(
                        get_str('Error opening file'),
                        (
                            f"<p><b>{e}</b></p><p>{get_str('Make sure')} <i>{unicode_file_path}</i> {get_str('is a valid label file.')}")
                    )
                    self.status(f"{get_str('Error reading')} {unicode_file_path}")
                    return False
                self.image_data = self.label_file.image_data
                self.line_color = QColor(*self.label_file.lineColor)
                self.fill_color = QColor(*self.label_file.fillColor)
                self.canvas.verified = self.label_file.verified
            else:
                # Load image:
                # read data first and store for saving into label file.
                self.image_data = qread(unicode_file_path, None)
                self.label_file = None
                self.canvas.verified = False

            if isinstance(self.image_data, QImage):
                image = self.image_data
            else:
                image = QImage.fromData(self.image_data)
            if image.isNull():
                self.error_message(u'Error opening file',
                                   u"<p>Make sure <i>%s</i> is a valid image file." % unicode_file_path)
                self.status("Error reading %s" % unicode_file_path)
                return False
            self.status(f"{get_str('Loaded')} {os.path.basename(unicode_file_path)}")
            self.qimage = image
            self.file_path = unicode_file_path
            self.qpix = QPixmap.fromImage(image)
            self.qpix.setDevicePixelRatio(1)
            self.canvas.load_pixmap(self.qpix)
            if self.label_file:
                self.load_labels(self.label_file.shapes)
            self.set_clean()
            self.canvas.setEnabled(True)
            self.adjust_scale(initial=True)
            self.paint_canvas()
            self.add_recent_file(self.file_path)
            self.toggle_actions(True)
            self.show_bounding_box_from_annotation_file(self.file_path)

            counter = f'[{self.cur_img_idx + 1}/{len(mc.image_list)}]'
            if Path(file_path).as_posix().startswith(ImageData.as_posix()):
                imgRelPath = Path(file_path).relative_to(ImageData).as_posix()
            elif Path(file_path).as_posix().startswith(MomoYolo.as_posix()):
                imgRelPath = Path(file_path).relative_to(MomoYolo).as_posix()
            else:
                imgRelPath = Path(file_path).as_posix()
            path_str = imgRelPath

            # 直接打印rect得不到长宽
            rect = self.qimage.rect()
            # 第1种获取长宽的方法
            w = rect.width()
            h = rect.height()
            # 第2种获取长宽的方法
            w_ = self.qimage.width()
            h_ = self.qimage.height()
            # print(rect, (w, h), (w_, h_))
            # 运行结果：PyQt5.QtCore.QRect(0, 0, 536, 868) (536, 868) (536, 868)

            if SYSTEM == 'MAC':
                max_path_len = cg.mac_max_path_len
            else:
                max_path_len = cg.win_max_path_len
            # ================路径过长则仅使用文件名================
            if len(imgRelPath) >= max_path_len:
                path_str = Path(file_path).name
            window_title = f'{__appname__} {counter} {path_str} [{w_}x{h_}]'
            # TODO setWindowTitle
            self.setWindowTitle(window_title)

            # Default : select last item if there is at least one item
            if self.label_list.count():
                self.label_list.setCurrentItem(self.label_list.item(self.label_list.count() - 1))
                self.label_list.item(self.label_list.count() - 1).setSelected(True)

            # self.canvas.setFocus(True)
            self.canvas.setFocus()
            return True
        return False

    @logger.catch
    def show_bounding_box_from_annotation_file(self, file_path):
        loge(f'{file_path=}', 'debug')
        file_path = Path(file_path)
        has_annotation = False
        label_dirs = get_label_dirs(file_path)

        for d in range(len(label_dirs)):
            label_dir = label_dirs[d]
            label_dir = Path(label_dir)
            xml_path = label_dir / f'{file_path.stem}{XML_EXT}'
            txt_path = label_dir / f'{file_path.stem}{TXT_EXT}'
            json_path = label_dir / f'{file_path.stem}{JSON_EXT}'

            """Annotation file priority:
            PascalXML > YOLO
            """
            if xml_path.exists():
                self.load_pascal_xml_by_filename(xml_path)
                has_annotation = True
            elif txt_path.exists():
                if debug:
                    loge(f'{txt_path.as_posix()=}', 'debug')
                self.load_yolo_txt_by_filename(txt_path)
                has_annotation = True
            elif json_path.exists():
                self.load_create_ml_json_by_filename(json_path, file_path)
                has_annotation = True

            if has_annotation:
                break

    def resizeEvent(self, event):
        if self.canvas and not self.qimage.isNull() and self.zoom_mode != self.MANUAL_ZOOM:
            self.adjust_scale()
        super(LabelImgWindow, self).resizeEvent(event)

    def paint_canvas(self):
        assert not self.qimage.isNull(), "cannot paint null image"
        self.canvas.scale = 0.01 * self.zoom_widget.value()
        self.canvas.overlay_color = self.light_widget.light_color()
        self.canvas.label_font_size = int(0.02 * max(self.qimage.width(), self.qimage.height()))
        self.canvas.adjustSize()
        self.canvas.update()

    def adjust_scale(self, initial=False):
        value = self.scalers[self.FIT_WINDOW if initial else self.zoom_mode]()
        self.zoom_widget.setValue(int(100 * value))

    def scale_fit_window(self):
        """Figure out the size of the pixmap in order to fit the main widget."""
        e = 2.0  # So that no scrollbars are generated.
        w1 = self.centralWidget().width() - e
        h1 = self.centralWidget().height() - e
        a1 = w1 / h1
        # Calculate a new scale value based on the pixmap's aspect ratio.
        w2 = self.canvas.pixmap.width() - 0.0
        h2 = self.canvas.pixmap.height() - 0.0
        a2 = w2 / h2
        return w1 / w2 if a2 >= a1 else h1 / h2

    def scale_fit_width(self):
        # The epsilon does not seem to work too well here.
        w = self.centralWidget().width() - 2.0
        return w / self.canvas.pixmap.width()

    def closeEvent(self, event):
        if not self.may_continue():
            event.ignore()
        app_settings[SETTING_WIN_SIZE] = self.size()
        app_settings[SETTING_WIN_POSE] = self.pos()
        app_settings[SETTING_WIN_STATE] = self.saveState()
        app_settings[SETTING_LINE_COLOR] = self.line_color
        app_settings[SETTING_FILL_COLOR] = self.fill_color
        app_settings[SETTING_RECENT_FILES] = self.recent_files
        app_settings[SETTING_ADVANCE_MODE] = not self._beginner
        app_settings[SETTING_AUTO_SAVE] = self.auto_saving.isChecked()
        app_settings[SETTING_SINGLE_CLASS] = self.single_class_mode.isChecked()
        app_settings[SETTING_PAINT_LABEL] = self.display_label_option.isChecked()
        app_settings[SETTING_DRAW_SQUARE] = self.draw_squares_option.isChecked()
        app_settings[SETTING_Magnifying_Lens] = self.use_magnifying_glass.isChecked()
        app_settings[SETTING_LABEL_FILE_FORMAT] = self.label_file_format
        app_settings.save()

    def load_recent(self, filename):
        if self.may_continue():
            self.qload_file(filename)

    def open_annotation_dialog(self, _value=False):
        if self.file_path is None:
            self.statusbar_main.showMessage(get_str('Please select image first'))
            return

        path = os.path.dirname(self.file_path) if self.file_path else '.'
        if self.label_file_format == LabelFileFormat.PASCAL_VOC:
            filters = "Open Annotation XML file (%s)" % ' '.join(['*.xml'])
            filename = QFileDialog.getOpenFileName(self, f'{__appname__} - {get_str("Choose a xml file")}', path,
                                                   filters)
            if filename:
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]
            self.load_pascal_xml_by_filename(filename)

        elif self.label_file_format == LabelFileFormat.CREATE_ML:
            filters = "Open Annotation JSON file (%s)" % ' '.join(['*.json'])
            filename = QFileDialog.getOpenFileName(self, f'{__appname__} - {get_str("Choose a json file")}', path,
                                                   filters)
            if filename:
                if isinstance(filename, (tuple, list)):
                    filename = filename[0]

            self.load_create_ml_json_by_filename(filename, self.file_path)

    @logger.catch
    def open_dir_dialog(self, _value=False):
        if not self.may_continue():
            return

        # ================打开文件夹================
        target_dir_path = QFileDialog.getExistingDirectory(self,
                                                           f'{__appname__} - {get_str("Open Directory")}',
                                                           str(mc.file_dir),  # 起始路径
                                                           QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks)

        # ================取消选择================
        if target_dir_path == "":
            loge(f'{get_str("Cancel Selection")}', 'warning')
            # 否则取消选择会选择程序所在文件夹
            return

        loge(f'{target_dir_path=}', 'warning')
        self.import_dir_images(target_dir_path)

    def import_dir_images(self, dir_path, pattern=None, load=True):
        # ================导入文件夹================
        # TODO import_dir_images
        dir_path = Path(dir_path)
        loge(f'{dir_path=}', 'debug')
        if not self.may_continue() or not dir_path:
            return

        same_dir_path = (Path(dir_path) == mc.file_dir)
        same_pattern = (pattern == mc.pattern)
        # 如果是同一个文件夹且未改搜索关键词，不处理
        if same_dir_path and same_pattern:
            return

        self.file_path = None
        self.lw_file.clear()
        mc.put_file_dir(dir_path, pattern)

        self.classes = get_classes(mc.file_dir)
        list_item = self.classes
        if not list_item:
            if len(mc.label_hist) > 0:
                list_item = mc.label_hist
        self.label_dialog = LabelDialog(parent=self, list_item=list_item)

        for i in range(len(mc.image_list)):
            imgPath = mc.image_list[i]
            imgRelPath = mc.imgRelPaths[i]
            # loge(f'[{i+1}/{len(mc.image_list)}]{imgRelPath=}', 'debug')
            imgCheck = mc.imgChecks[i]
            imgItem = QListWidgetItem(imgRelPath)
            imgItem.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
            if imgCheck:
                imgItem.setCheckState(Qt.CheckState.Checked)
                if len(mc.no_labels) >= 0.8 * len(mc.image_list):
                    # 给有标签文件的图片名称显示为彩色
                    imgItem.setBackground(generate_color_by_text(imgPath.stem))
            else:
                imgItem.setCheckState(Qt.CheckState.Unchecked)
                if len(mc.no_labels) <= 0.2 * len(mc.image_list):
                    # 给没有标签文件的图片名称显示为彩色
                    imgItem.setBackground(generate_color_by_text(imgPath.stem))

            self.lw_file.addItem(imgItem)

        loge(get_str(f'label_files loaded'), 'debug')
        # 如果是同一个文件夹且改了搜索关键词，不加载图片
        if same_dir_path and not same_pattern:
            pass
        self.open_next_image(load=load)

    def verify_image(self, _value=False):
        # Proceeding next image without dialog if having any label
        if self.file_path is not None:
            try:
                self.label_file.toggle_verify()
            except AttributeError:
                # If the labelling file does not exist yet, create if and
                # re-save it with the verified attribute.
                self.save_file()
                if self.label_file is not None:
                    self.label_file.toggle_verify()
                else:
                    return

            self.canvas.verified = self.label_file.verified
            self.paint_canvas()
            self.save_file()

    def open_prev_image(self, _value=False):
        # TODO open_prev_image
        # Proceeding prev image without dialog if having any label
        if self.auto_saving.isChecked():
            if cg.default_save_dir is not None:
                if self.dirty is True:
                    self.save_file()
            else:
                return

        if not self.may_continue():
            return

        if len(mc.image_list) <= 0:
            return

        if self.file_path is None:
            return

        currIndex = self.sm_file.currentIndex()
        if currIndex.row() <= 0:
            # 第一张没有更前面
            return False

        prevIndexInt = currIndex.row() - 1
        prevIndex = self.md_file.index(prevIndexInt)
        # self.sm_file.setCurrentIndex(prevIndex, QItemSelectionModel.SelectCurrent)

        self.file_path = mc.image_list[prevIndexInt]
        if self.file_path:
            self.qload_file(self.file_path)
        return

    @logger.catch
    def open_next_image(self, _value=False, load=True):
        # TODO open_next_image
        # Proceeding next image without dialog if having any label
        if self.auto_saving.isChecked():
            if cg.default_save_dir is not None:
                if self.dirty is True:
                    self.save_file()
            else:
                return

        if not self.may_continue():
            return

        if len(mc.image_list) <= 0:
            return

        if not mc.image_list:
            return

        currIndex = self.sm_file.currentIndex()
        if currIndex.row() >= self.md_file.rowCount() - 1:
            # 最后一张没有更后面
            return False

        nextIndexInt = currIndex.row() + 1
        nextIndex = self.md_file.index(nextIndexInt)
        # self.sm_file.setCurrentIndex(nextIndex, QItemSelectionModel.SelectCurrent)

        self.file_path = mc.image_list[nextIndexInt]
        if self.file_path and load:
            self.qload_file(self.file_path)
        return True

    def save_file(self, _value=False):
        if cg.default_save_dir is not None and len(str(cg.default_save_dir)):
            if self.file_path:
                image_file_name = os.path.basename(self.file_path)
                saved_file_name = os.path.splitext(image_file_name)[0]
                saved_path = os.path.join(cg.default_save_dir, saved_file_name)
                self._save_file(saved_path)
        else:
            image_file_dir = os.path.dirname(self.file_path)
            image_file_name = os.path.basename(self.file_path)
            saved_file_name = os.path.splitext(image_file_name)[0]
            saved_path = os.path.join(image_file_dir, saved_file_name)
            self._save_file(saved_path if self.label_file
                            else self.save_file_dialog(remove_ext=False))

    def save_file_as(self, _value=False):
        assert not self.qimage.isNull(), "cannot save empty image"
        self._save_file(self.save_file_dialog())

    def save_file_dialog(self, remove_ext=True):
        caption = f'{__appname__} - {get_str("Choose File")}'
        filters = f'{get_str("File")} (*{LabelFile.suffix})'
        open_dialog_path = self.current_path()
        dlg = QFileDialog(self, caption, open_dialog_path, filters)
        dlg.setDefaultSuffix(LabelFile.suffix[1:])
        dlg.setAcceptMode(QFileDialog.AcceptSave)
        filename_without_extension = os.path.splitext(self.file_path)[0]
        dlg.selectFile(filename_without_extension)
        dlg.setOption(QFileDialog.DontUseNativeDialog, False)
        if dlg.exec():
            full_file_path = dlg.selectedFiles()[0]
            if remove_ext:
                return os.path.splitext(full_file_path)[0]  # Return file path without the extension.
            else:
                return full_file_path
        return ''

    def _save_file(self, annotation_file_path):
        if annotation_file_path and self.save_labels(annotation_file_path):
            self.set_clean()
            self.statusbar_main.showMessage(f'Saved to  {annotation_file_path}')

    def close_file(self, _value=False):
        if not self.may_continue():
            return
        self.reset_state()
        self.set_clean()
        self.toggle_actions(False)
        self.canvas.setEnabled(False)
        self.actions.saveAs.setEnabled(False)

    def delete_image(self):
        # TODO 【delete_image】
        delete_path = Path(self.file_path)
        loge(f'{delete_path=}', 'debug')
        items = self.lw_file.selectedItems()
        if not items:
            return
        item = items[0]
        self.cur_img_idx = mc.imgRelPaths.index(item.text())
        if delete_path is not None:
            idx = self.cur_img_idx
            if os.path.exists(delete_path):
                new_file_path = Trash / delete_path.name
                # 移动文件或目录都是使用这条命令
                shutil.move(delete_path, new_file_path)
                # os.remove(delete_path)
            self.import_dir_images(mc.file_dir)
            if self.cur_img_idx > 0:
                self.new_cur_img_idx = max(0, self.cur_img_idx - 1)
                filename = mc.image_list[self.new_cur_img_idx]
                if filename:
                    self.qload_file(filename)
            else:
                self.close_file()

    def reset_all(self):
        app_settings.reset()
        self.close()
        process = QProcess()
        process.startDetached(os.path.abspath(__file__))

    def may_continue(self):
        if not self.dirty:
            return True
        else:
            discard_changes = self.discard_changes_dialog()
            if discard_changes == QMessageBox.StandardButton.No:
                return True
            elif discard_changes == QMessageBox.StandardButton.Yes:
                self.save_file()
                return True
            else:
                return False

    def discard_changes_dialog(self):
        yes, no, cancel = QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No, QMessageBox.StandardButton.Cancel
        key = u'You have unsaved changes, would you like to save them and proceed?\nClick "No" to undo all changes.'
        msg = get_str(key)
        return QMessageBox.warning(self, get_str('Attention'), msg, yes | no | cancel)

    def error_message(self, title, message):
        return QMessageBox.critical(self, title,
                                    '<p><b>%s</b></p>%s' % (title, message))

    def current_path(self):
        return os.path.dirname(self.file_path) if self.file_path else '.'

    def choose_color1(self):
        color = self.color_dialog.getColor(self.line_color, get_str('Choose line color'),
                                           default=DEFAULT_LINE_COLOR)
        if color:
            self.line_color = color
            Shape.line_color = color
            self.canvas.set_drawing_color(color)
            self.canvas.update()
            self.set_dirty()

    def delete_selected_shape(self):
        self.remove_label(self.canvas.delete_selected())
        self.set_dirty()
        if self.no_shapes():
            for action in self.actions.onShapesPresent:
                action.setEnabled(False)

    def choose_shape_line_color(self):
        color = self.color_dialog.getColor(self.line_color, get_str('Choose line color'),
                                           default=DEFAULT_LINE_COLOR)
        if color:
            self.canvas.selected_shape.line_color = color
            self.canvas.update()
            self.set_dirty()

    def choose_shape_fill_color(self):
        color = self.color_dialog.getColor(self.fill_color, get_str('Choose Fill Color'),
                                           default=DEFAULT_FILL_COLOR)
        if color:
            self.canvas.selected_shape.fill_color = color
            self.canvas.update()
            self.set_dirty()

    def copy_shape(self):
        if self.canvas.selected_shape is None:
            # True if one accidentally touches the left mouse button before releasing
            return
        self.canvas.end_move(copy=True)
        self.add_label(self.canvas.selected_shape)
        self.set_dirty()

    def move_shape(self):
        self.canvas.end_move(copy=False)
        self.set_dirty()

    def load_pascal_xml_by_filename(self, xml_path):
        if self.file_path is None:
            return
        if os.path.isfile(xml_path) is False:
            return

        self.set_format(FORMAT_PASCALVOC)

        t_voc_parse_reader = PascalVocReader(xml_path)
        shapes = t_voc_parse_reader.get_shapes()
        self.load_labels(shapes)
        self.canvas.verified = t_voc_parse_reader.verified

    def load_yolo_txt_by_filename(self, txt_path):
        if self.file_path is None:
            return
        if os.path.isfile(txt_path) is False:
            return

        self.set_format(FORMAT_YOLO)
        t_yolo_parse_reader = YoloReader(txt_path, self.qimage)
        shapes = t_yolo_parse_reader.get_shapes()
        for s in range(len(shapes)):
            shape = shapes[s]
            loge(f'{shape=}', 'warning')
        self.load_labels(shapes)
        self.canvas.verified = t_yolo_parse_reader.verified

    def load_create_ml_json_by_filename(self, json_path, file_path):
        if self.file_path is None:
            return
        if os.path.isfile(json_path) is False:
            return

        self.set_format(FORMAT_CREATEML)

        create_ml_parse_reader = CreateMLReader(json_path, file_path)
        shapes = create_ml_parse_reader.get_shapes()
        self.load_labels(shapes)
        self.canvas.verified = create_ml_parse_reader.verified

    def copy_previous_bounding_boxes(self):
        current_index = mc.image_list.index(self.file_path)
        if current_index - 1 >= 0:
            prev_file_path = mc.image_list[current_index - 1]
            self.show_bounding_box_from_annotation_file(prev_file_path)
            self.save_file()

    def toggle_paint_labels_option(self):
        for shape in self.canvas.shapes:
            shape.paint_label = self.display_label_option.isChecked()

    def toggle_draw_square(self):
        self.canvas.set_drawing_shape_to_square(self.draw_squares_option.isChecked())


@logger.catch
def get_locale_str():
    try:
        locale = getlocale()
        defaultlocale = getdefaultlocale()
        qloca = QLocale.system().name()
        os_lang = os.getenv('LANG')
        loge(f'{locale=}', 'debug')
        loge(f'{defaultlocale=}', 'debug')
        loge(f'{qloca=}', 'debug')
        loge(f'{os_lang=}', 'debug')
        if defaultlocale and len(defaultlocale) > 0:
            locale_str = defaultlocale[0]
        else:
            locale_str = os_lang
    except:
        print('Invalid locale')
        locale_str = 'en'
        locale_str = None

    if locale_str is None:
        locale_str = 'zh-CN'
        locale_str = 'en'
    elif 'zh' in locale_str:
        locale_str = 'zh-CN'
    elif 'en' in locale_str:
        locale_str = 'en'
    if SYSTEM in ['MAC', 'M1']:
        # locale_str = 'zh-CN'
        pass

    # locale_str = 'en'
    return locale_str


@logger.catch
def get_id_to_message(app_name, app_names):
    id_to_message = {}
    locale_paths = []
    custom_app_names = [x for x in app_names if x != app_name]
    custom_app_names = [app_name] + custom_app_names

    for a in range(len(custom_app_names)):
        appname = custom_app_names[a]
        locale_path = Translation / f'{appname}-{locale_str}.txt'
        if locale_path not in locale_paths and locale_path.exists():
            locale_paths.append(locale_path)

    for n in range(len(locale_paths)):
        locale_path = locale_paths[n]
        loge(f'{locale_path=}', 'debug')
        if locale_path.exists():
            trans_text = read_txt(locale_path)
            trans_lines = trans_text.splitlines()
            for t in range(len(trans_lines)):
                trans_line = trans_lines[t]
                key_value = trans_line.split(PROP_SEPERATOR)
                key = key_value[0].strip()
                value = PROP_SEPERATOR.join(key_value[1:]).strip().strip('"')
                if key not in id_to_message:
                    id_to_message[key] = value

    # ================补充================
    if locale_str == 'zh-CN':
        key = u'You have unsaved changes, would you like to save them and proceed?\nClick "No" to undo all changes.'
        value = '您有未保存的更改，是否要保存并继续？\n单击“否”以撤消所有更改。'
        id_to_message[key] = value
    return id_to_message


@logger.catch
def get_str(string_id):
    untranslated_txt = UserDataFolder / f'{app_name}_strings.txt'

    if string_id in id_to_message:
        trans_str = id_to_message[string_id]
    else:
        trans_str = string_id
        loge(f'{string_id=}', 'warning')

        if untranslated_txt.exists():
            page_text = read_txt(untranslated_txt)
            rows = page_text.splitlines()
        else:
            rows = []
        if string_id not in rows:
            rows.append(string_id)
            untranslated_text = lf.join(rows)
            write_txt(untranslated_txt, untranslated_text)
    return trans_str


def z_nuitka():
    pass


# 使用带命令行
# nuitka --standalone --mingw64 --show-memory --show-progress --nofollow-imports --recurse-all --plugin-enable=qt-plugins --plugin-enable=numpy --output-dir=o pyqt5_momolabelimg.py
# nuitka --standalone --mingw64 --show-memory --show-progress --nofollow-imports --plugin-enable=pyqt5,numpy --output-dir=o pyqt5_momolabelimg.py
# 使用不带命令行
# nuitka --standalone --windows-disable-console --mingw64 --show-memory --show-progress --nofollow-imports --recurse-all --plugin-enable=qt-plugins --plugin-enable=numpy --output-dir=o pyqt5_momolabelimg.py

# anti-bloat            Patch stupid imports out of widely used qt_lib modules source codes.
# data-files
# data-hiding           Commercial: Hide program constant Python data from offline inspection of created binaries.
# datafile-inclusion    Commercial: Load file trusted file contents at compile time.
# dill-compat
# enum-compat
# ethereum              Commercial: Required for ethereum packages in standalone mode
# eventlet              Support for including 'eventlet' dependencies and its need for 'dns' package monkey patching
# gevent                Required by the gevent package
# gi                    Support for GI dependencies
# glfw                  Required for glfw in standalone mode
# implicit-imports
# multiprocessing       Required by Python's multiprocessing module
# numpy                 Required for numpy, scipy, pandas, matplotlib, etc.
# pbr-compat
# pkg-resources         Resolve version numbers at compile time.
# pmw-freezer           Required by the Pmw package
# pylint-warnings       Support PyLint / PyDev linting source markers
# pyqt5                 Required by the PyQt5 package.
# pyside2               Required by the PySide2 package.
# pyside6               Required by the PySide6 package for standalone mode.
# pyzmq                 Required for pyzmq in standalone mode
# tensorflow            Required by the tensorflow package
# tk-inter              Required by Python's Tk modules
# torch                 Required by the torch / torchvision packages
# traceback-encryption  Commercial: Encrypt tracebacks (de-Jong-Stacks).
# windows-service       Commercial: Create Windows Service files

def z_hotkey():
    pass


# 快捷键      | 功能
# -------- | ------------
# Ctrl + u | 从目录加载所有图像
# Ctrl + R | 更改默认注释目标目录
# Ctrl + s | 储存
# Ctrl + d | 复制当前标签和矩形框
# space    | 将当前图像标记为已验证
# w        | 创建一个矩形框
# d        | 下一张图片
# a        | 上一张图片
# del      | 删除选定的矩形框
# Ctrl ++  | 放大
# Ctrl–    | 缩小
# ↑→↓←     | 键盘箭头移动选定的矩形框

def z():
    pass


@logger.catch
def main_pyqt():
    win = LabelImgWindow()
    sys.exit(appgui.exec())


if __name__ == '__main__':
    global_start_time = time()

    MomoYolo = DOCUMENTS / '默墨智能'
    Storage = MomoYolo / 'Storage'
    ConfigData = MomoYolo / 'ConfigData'
    ImageData = MomoYolo / 'ImageData'
    InputData = MomoYolo / 'InputData'
    Output = MomoYolo / 'Output'
    SaveData = MomoYolo / 'SaveData'
    Screenshot = MomoYolo / 'Screenshot'
    Trash = MomoYolo / 'Trash'
    Log = MomoYolo / 'Log'

    ComicBubble = ImageData / 'Comic Bubble'
    GIC = ImageData / 'Genshin Impact Character'
    COCO128 = ImageData / 'coco128'
    COCO = ImageData / 'coco'

    ComicBubble_Source = ComicBubble / 'Produce'
    GIC_Source = GIC / 'Produce'

    ImgResource = UserDataFolder / 'ImgResource'
    Translation = UserDataFolder / 'Translation'

    make_dir(MomoYolo)
    make_dir(Storage)
    make_dir(ConfigData)
    make_dir(ImageData)
    make_dir(InputData)
    make_dir(Output)
    make_dir(SaveData)
    make_dir(Screenshot)
    make_dir(Trash)
    make_dir(Log)

    make_dir(ImgResource)

    date_str = strftime('%Y_%m_%d')
    log_path = Log / f'日志-{date_str}.log'
    logger.add(
        log_path.as_posix(),
        rotation='500MB',
        encoding='utf-8',
        enqueue=True,
        compression='zip',
        retention='10 days',
        # backtrace=True,
        # diagnose=True,
        # colorize=True,
        # format="<green>{time}</green> <level>{message}</level>",
    )

    my_config = Config()
    mc = my_config

    loge('程序开始', 'info')

    momolabelimg_pkl = MomoYolo / 'momolabelimg.pkl'
    # labelimg_yml = MomoYolo / 'labelimg.yml'

    appgui = QApplication(sys.argv)

    pxrt = QWindow().devicePixelRatio()

    appgui.setStyle('Fusion')
    appgui.setApplicationName(__appname__)
    appgui.setWindowIcon(new_icon("app"))

    if SYSTEM != 'M1':
        QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    if SYSTEM == 'WINDOWS':
        # Needed for Qt WebEngine on Windows
        QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
        QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)

    # ================默认打开目录================
    image_dirs = [
        # GIC / 'Produce',
        # GIC / 'all',
        # COCO128,
        Output / mc.source_pic_dir_name,
        COCO / 'train',
        COCO,
        GIC / 'train',
        ComicBubble / 'train',
    ]

    # ================添加默认打开目录================
    if cg.default_open_dir is not None and len(str(cg.default_open_dir)):
        image_dirs.append(Path(cg.default_open_dir))

    image_dirs.append(ImageData)

    image_e_dirs = []
    # image_e_dirs = image_dirs
    for d in range(len(image_dirs)):
        image_dir = image_dirs[d]
        if image_dir.exists():
            image_e_dirs.append(image_dir)
            # all_pics = get_files(image_dir, 'pic', False)
            # if all_pics:
            #     image_e_dirs.append(image_dir)

    if image_e_dirs:
        image_dir = image_e_dirs[0]
    else:
        image_dir = None

    # ================添加默认存储目录================
    if cg.default_save_dir is not None and len(str(cg.default_save_dir)):
        pass
    else:
        cg.put_default_save_dir(SaveData)

    debug = True
    # debug = False

    # ================获取界面语言================
    locale_str = get_locale_str()
    loge(f'{locale_str=}', 'debug')

    # ================获取语言字典================
    app_name = 'momolabelimg'
    app_names = [
        'agentocrlabeling',
        'autolabelimg',
        'momolabelimg',
        'momolabelimg2',
        'momolabelme',
    ]
    id_to_message = get_id_to_message(app_name, app_names)

    # ================通过QSS样式的方式设置按钮文字================
    qss_style = read_txt(style_qss)
    if locale_str == 'zh-CN':
        qss_style = qss_cn + qss_style
    appgui.setStyleSheet(qss_style)


    def steps():
        pass


    # Load setting in the main thread
    app_settings = Settings()
    app_settings.load()

    main_pyqt()
