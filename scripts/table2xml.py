# -*- encoding=utf-8 -*-
#
# author: Damcy<stmayue@gmail.com>
# create on: 2014-08-14

import sys
import json
import os
from optparse import OptionParser
import xml.dom.minidom
import traceback

def getFormat(inputType, readConf):
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
        domainNode = dataFormat.getElementsByTagName(inputType)[0]
        colNodes = domainNode.getElementsByTagName("col")
        for node in colNodes:
            col_id = int(node.getAttribute("id"))
            col_name = node.childNodes[0].data
            ret[int(col_id) - 1] = col_name
    except Exception:
        sys.stderr.write("read input dataFormat failed! traceback info: " + str(traceback.format_exc()))
        exit(1)
    return ret


def read_opts():
    """ read input parameters
    """
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-t", "--type", dest="inputType", \
                type="string", help="task data type")
    parser.add_option("-r", "--readConf", dest="readConf", \
                type="string", help="read inputFormat")
    parser.add_option("-x", "--xmlConf", dest="xmlConf", \
                type="string", help="xml transfer Format")
    parser.add_option("-c", "--tagConf", dest="tagConf", \
                type="string", help="element and tag pair")
    (options, args) = parser.parse_args()
    if not options.inputType or not options.readConf \
        or not options.xmlConf or not options.tagConf:
        sys.stderr.write("incorrect number of arguments" + os.linesep)
        exit(1)
    rdict = {"type": options.inputType, "readConf": options.readConf, \
                "xmlConf": options.xmlConf, "tagConf": options.tagConf}
    return rdict


def convert_dict(formatDict, inLine, xmlStr, tagDict):
    """ trans tab line into dict according target format
    """
    ret = dict()
    line_content = inLine.split('\t')
    if len(line_content) < len(formatDict):
        raise Exception("dataERROR")
    for i in range(0, len(line_content)):
        ret[formatDict[i]] = line_content[i]
    replace_str = xmlStr
    for item in ret:
        # check replace or not
        if not ret.get(item, 0):
            re_str = "<" + tagDict[item] + "><![CDATA[##" + item + "##]]></" + tagDict[item] + ">"
            replace_str = replace_str.replace(re_str, ret[item])
        else:
            re_str = "##" + item + "##"
            replace_str = replace_str.replace(re_str, ret[item])
    return replace_str


def getXml(xmlConf):
    """ read xml schema
    """
    if not os.path.isfile(xmlConf):
        sys.stderr.write("xmlFormat file ERROR!")
        exit(1)
    try:
        with open(xmlConf, 'r') as fp:
            data = fp.read().decode("utf-8")
    except Exception:
        sys.stderr.write("read xml format failed! traceback info: " + str(traceback.format_exc()))
        exit(1)
    return data


def load_tag(tagConf):
    """ read tag dict, make element-tag pair
    """
    if not os.path.isfile(tagConf):
        sys.stderr.write("tag conf file ERROR!")
        exit(1)
    try:
        with open(tagConf, 'r') as fp:
            data = fp.read().decode("utf-8")
        tagDict = json.loads(data)
    except:
        sys.stderr.write("read tag conf failed! traceback info: " + str(traceback.format_exc()))
        exit(1)
    return tagDict


if __name__ == "__main__":
    _INCODE = "utf-8"
    _OUTCODE = "utf-8"
    try:
        optDict = read_opts()
        inputType = optDict["type"]
        readConf = optDict["readConf"]
        xmlConf = optDict["xmlConf"]
        tagConf = optDict["tagConf"]
    except:
        msg = "table2xml get options ERROR! info:" + str(traceback.format_exc())
        sys.stderr.write(msg)
        exit(1)

    try:
        formatDict = getFormat(inputType, readConf)
    except Exception as ex:
        msg = "table2xml read data format fail. traceback info: " + str(traceback.format_exc())
        sys.stderr.write(msg)
        exit(1)

    try:
        xmlStr = getXml(xmlConf)
    except Exception as ex:
        msg = "table2xml read xml format fail. traceback info: " + str(traceback.format_exc())
        sys.stderr.write(msg)
        exit(1)

    try:
        tagDict = load_tag(tagConf)
    except:
        msg = "table2xml read tag config file fail. traceback info: " + str(traceback.format_exc())
        sys.stderr.write(msg)
        exit(1)

    # process each line
    for line in sys.stdin:
        try:
            result = convert_dict(formatDict, line.strip('\n').decode(_INCODE), xmlStr, tagDict)
            sys.stdout.write(result.encode(_OUTCODE))
        except:
            msg = "Line: " + line.strip('\n').decode(_INCODE) + \
                    " build XML ERROR! traceback info: " + str(traceback.format_exc()) + os.linesep
            sys.stderr.write(msg)
            continue
