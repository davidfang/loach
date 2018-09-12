# -*- coding: utf-8 -*-
from flask import Blueprint


douyin = Blueprint('douyin', __name__, url_prefix='/douyin')
kuaishou = Blueprint('kuaishou', __name__, url_prefix='/kuaishou')

from loach.api import douyinview
from loach.api import kuaishouview