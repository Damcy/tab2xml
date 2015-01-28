# -*- encoding=utf-8 -*-
#
# author: mayue<mayue07@baidu.com>
# create on: 2014-08-14

import sys
import json
import os
from optparse import OptionParser
import xml.dom.minidom
import traceback

sys.path.append("%s/../utility" %(os.path.abspath(os.path.dirname(__file__))))
import mylogging

log = None

def getFormat(type, readConf):
    """
    根据type读取readConf中的规范
    """
    if not os.path.isfile(readConf):
        log.error("table dataFormat file ERROR!")
        exit(1)
    try:
        ret = dict()
        doc = xml.dom.minidom.parse(readConf)
        root = doc.documentElement
        dataFormat = root.getElementsByTagName("tab")[0]
        domainNode = dataFormat.getElementsByTagName(type)[0]
        colNodes = domainNode.getElementsByTagName("col")
        for node in colNodes:
            col_id = int(node.getAttribute("id"))
            col_name = node.childNodes[0].data
            ret[int(col_id) - 1] = col_name
    except Exception, e:
        log.error("read input dataFormat failed! traceback info: " + str(traceback.format_exc()))
        exit(1)

    return ret


def read_opts():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-i", "--id", dest="id", \
                type="string", help="task id")
    parser.add_option("-t", "--type", dest="type", \
                type="string", help="task data type")
    parser.add_option("-l", "--logConf", dest="logConf", \
                type="string", help="log conf path")
    parser.add_option("-r", "--readConf", dest="readConf", \
                type="string", help="read inputFormat")
    parser.add_option("-x", "--xmlConf", dest="xmlConf", \
                type="string", help="xml transfer Format")
    parser.add_option("-c", "--tagConf", dest="tagConf", \
                type="string", help="element and tag pair")
    (options, args) = parser.parse_args()
    if not options.logConf or not options.id or not options.type or not options.readConf \
            or not options.xmlConf:
        sys.stderr.write("incorrect number of arguments" + os.linesep)
        exit(1)
    rdict = dict()
    rdict["id"] = options.id
    rdict["type"] = options.type
    rdict["logConf"] = options.logConf
    rdict["readConf"] = options.readConf
    rdict["xmlConf"] = options.xmlConf
    rdict["tagConf"] = options.tagConf
    return rdict


def convert_dict(formatDict, inLine, xmlStr, tagDict):
    """
    将tab line按照格式转成dict
    """
    ret = dict()
    line_content = inLine.split('\t')
    if len(line_content) < len(formatDict):
        raise Exception("dataERROR")
    for i in range(0, len(line_content)):
        ret[formatDict[i]] = line_content[i]
    replace_str = xmlStr
    for item in ret:
        if not ret.get(item, 0):
            re_str = "<" + tagDict[item] + "><![CDATA[##" + item + "##]]></" + tagDict[item] + ">"
            replace_str = replace_str.replace(re_str, ret[item])
        else:
            re_str = "##" + item + "##"
            replace_str = replace_str.replace(re_str, ret[item])
    return replace_str


def getXml(xmlConf):
    """
    读取当前类别的xml schema
    """
    if not os.path.isfile(xmlConf):
        log.error("xmlFormat file ERROR!")
        exit(1)
    try:
        fp = open(xmlConf, 'r')
        data = fp.read().decode("utf-8")
        fp.close()
    except Exception as e:
        log.error("read xml format failed! traceback info: " + str(traceback.format_exc()))
        fp.close()
        exit(1)
    return data


def load_tag(tagConf):
    """
    读取tag dict，反应每一个element处于的tag
    """
    if not os.path.isfile(tagConf):
        log.error("tag conf file ERROR!")
        exit(1)
    try:
        fp = open(tagConf, 'r')
        data = fp.read().decode("utf-8")
        fp.close()
        tagDict = json.loads(data)
    except:
        log.error("read tag conf failed! traceback info: " + str(traceback.format_exc()))
        fp.close()
        exit(1)
    return tagDict


if __name__ == "__main__":

    _INCODE = "utf-8"
    _OUTCODE = "utf-8"
    try:
        optDict = read_opts()
        id = optDict["id"]
        type = optDict["type"]
        logConf = optDict["logConf"]
        readConf = optDict["readConf"]
        xmlConf = optDict["xmlConf"]
        tagConf = optDict["tagConf"]
    except:
        msg = "table2xml get options ERROR!"
        sys.stderr.write(msg)
        exit(1)

    log = mylogging.getLogger(logConf)
    log.setTaskId(id)
    log.setType(type)

 
    try:
        formatDict = getFormat(type, readConf)
    except Exception as ex:
        msg = "table2xml read data format fail. traceback info: " + str(traceback.format_exc())
        log.error(msg)
        exit(1)

    try:
        xmlStr = getXml(xmlConf)
    except Exception as ex:
        msg = "table2xml read xml format fail. traceback info: " + str(traceback.format_exc())
        log.error(msg)
        exit(1)

    try:
        tagDict = load_tag(tagConf)
    except:
        msg = "table2xml read tag config file fail. traceback info: " + str(traceback.format_exc())
        log.error(msg)
        exit(1)

    # process each line
    for line in sys.stdin:
        try:
            result = convert_dict(formatDict, line.strip('\n').decode(_INCODE), xmlStr, tagDict)
            sys.stdout.write(result.encode(_OUTCODE))
            sys.stderr.write(line.strip('\n').split('\t')[0].decode(_INCODE).encode(_OUTCODE) + os.linesep)
        except:
            msg = "Line: " + line.strip('\n').decode(_INCODE) + " build XML ERROR! traceback info: " + str(traceback.format_exc()) + os.linesep
            log.error(msg)
            continue

