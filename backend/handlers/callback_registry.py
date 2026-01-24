from enum import Enum


class CallbackAction(str, Enum):
    EDIT = "act_edit"
    COMMENT = "act_comment"
    SAVE = "act_save"
    PERIOD = "act_period"
    HELP = "act_help"
    UPLOAD = "act_upload"
    ITEMS = "act_items"


class CallbackHeader(str, Enum):
    SUPPLIER = "hed:supplier"
    CLIENT = "hed:client"
    DATE = "hed:date"
    DOC_NUMBER = "hed:doc_number"
    TOTAL_SUM = "hed:total_sum"


HEADER_PREFIX = "hed:"

ITEMS_PAGE_PREFIX = "items_page"
ITEM_PICK_PREFIX = "item_pick"
ITEM_FIELD_PREFIX = "itm_field"


def make_items_page_callback(page: int) -> str:
    return f"{ITEMS_PAGE_PREFIX}:{page}"


def make_item_pick_callback(index: int) -> str:
    return f"{ITEM_PICK_PREFIX}:{index}"


def make_item_field_callback(index: int, key: str) -> str:
    return f"{ITEM_FIELD_PREFIX}:{index}:{key}"
