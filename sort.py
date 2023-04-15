from bs4 import BeautifulSoup
import collections
from collections import OrderedDict
from copy import deepcopy
import doctest
import functools
import gc
import getpass
import glob
from io import StringIO
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pathlib
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams, LTContainer, LTTextBox, LTTextLine, LTChar
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage
import re
import requests
import sys
import urllib
