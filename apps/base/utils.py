# @Time    : 2023/8/14 01:10
# @Author  : Lan
# @File    : utils.py
# @Software: PyCharm
import datetime
import uuid
import os
from fastapi import UploadFile

from apps.base.depends import IPRateLimit
from apps.base.models import FileCodes
from core.settings import settings
from core.utils import get_random_num, get_random_string


async def get_file_path_name(file: UploadFile):
    """
    获取文件路径和文件名
    :param file:
    :return: {
        'path': 'share/data/2021/08/13',
        'suffix': '.jpg',
        'prefix': 'test',
        'file_uuid': '44a83bbd70e04c8aa7fd93bfd8c88249',
        'uuid_file_name': '44a83bbd70e04c8aa7fd93bfd8c88249.jpg',
        'save_path': 'share/data/2021/08/13/44a83bbd70e04c8aa7fd93bfd8c88249.jpg'
    }
    """
    today = datetime.datetime.now()
    path = f"share/data/{today.strftime('%Y/%m/%d')}"
    prefix, suffix = os.path.splitext(file.filename)
    file_uuid = f"{uuid.uuid4().hex}"
    uuid_file_name = f"{file_uuid}{suffix}"
    save_path = f"{path}/{uuid_file_name}"
    return path, suffix, prefix, uuid_file_name, save_path


async def get_expire_info(expire_value: int, expire_style: str):
    """
    获取过期信息
    :param expire_value:
    :param expire_style:
    :return: expired_at 过期时间, expired_count 可用次数, used_count 已用次数, code 随机码
    """
    expired_count, used_count, now, code = -1, 0, datetime.datetime.now(), None
    if expire_style == 'day':
        expired_at = now + datetime.timedelta(days=expire_value)
    elif expire_style == 'hour':
        expired_at = now + datetime.timedelta(hours=expire_value)
    elif expire_style == 'minute':
        expired_at = now + datetime.timedelta(minutes=expire_value)
    elif expire_style == 'count':
        expired_at = now + datetime.timedelta(days=1)
        expired_count = expire_value
    elif expire_style == 'forever':
        expired_at = None
        code = await get_random_code(style='string')
    else:
        expired_at = now + datetime.timedelta(days=1)
    if not code:
        code = await get_random_code()
    return expired_at, expired_count, used_count, code


async def get_random_code(style='num'):
    """
    获取随机字符串
    :return:
    """
    while True:
        code = await get_random_num() if style == 'num' else await get_random_string()
        if not await FileCodes.filter(code=code).exists():
            return code


# 错误IP限制器
error_ip_limit = IPRateLimit(count=settings.errorCount, minutes=settings.errorMinute)
# 上传文件限制器
upload_ip_limit = IPRateLimit(count=settings.uploadCount, minutes=settings.errorMinute)
