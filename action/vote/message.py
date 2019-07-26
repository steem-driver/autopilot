# -*- coding:utf-8 -*-

import traceback

from bs4 import BeautifulSoup
from markdown import markdown

from utils.logging.logger import logger


def get_message(id):
    return build_message(id)

def build_message(id):
    return MESSAGES[id] + MESSAGE_ID.format(message_id=id)

def verify_message(id, body):
    try:
        html = markdown(body)
        soup = BeautifulSoup(html, "html.parser")
        msg_div = soup.find("div", {"message_id": id})
        if msg_div:
            return True
    except:
        logger.info("Failed when verifying message, with error: {}".format(traceback.format_exc()))

    return False

TABLE_TEMPLATE = """
<table>
<thead>
<tr>
{head}
</tr>
</thead>
<tbody>
{body}
</tbody>
</table>
"""

def build_table(head, data):
    if head and data and len(head) > 0 and len(data) > 0:
        head = "\n".join(["  <th>{}</th>".format(c) for c in head])
        rows = []
        for row in data:
            row_md = "\n".join(["<tr>", "\n".join(["  <td>{}</td>".format(c) for c in row]), "</tr>"])
            rows.append(row_md)
        body = "\n".join(rows)
        table = TABLE_TEMPLATE.format(head=head, body=body)
        return table
    return ""


MESSAGE_ID = """
<div message_id=\"{message_id}\"></div>
"""
