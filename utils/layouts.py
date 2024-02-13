from construct import Int8ul, Int64ul
from construct import Struct as cStruct


LIQ_LAYOUT = cStruct("instruction" / Int8ul, "amount_in" / Int64ul)