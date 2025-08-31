
FIRST_BYTE_FETCH = ["PC_INC", "MEM_OE", "IR0_READ_DBUS", "ABUS_WRITE_DEVICE=1", "DBUS_WRITE_DEVICE=7"]
SECOND_BYTE_FETCH = ["PC_INC", "MEM_OE", "IR1_READ_DBUS", "ABUS_WRITE_DEVICE=1"]
THIRD_BYTE_FETCH = ["PC_INC", "MEM_OE", "IR2_READ_DBUS", "ABUS_WRITE_DEVICE=1"]


MICROCODE = {
    0x00: [  # MOV ACC, R[vvv]
        FIRST_BYTE_FETCH,
        ["STORE_ACC", "uPC_CLR"]  # uPC=1
    ],
    0x01: [
        FIRST_BYTE_FETCH,
        ["STORE_ACC", "uPC_CLR"]  # uPC=1
    ],
}

for vvv in range(8):
    op = 0x00 | vvv

    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        ["STORE_ACC", "uPC_CLR"]
    ]

# Define the field mappings based on your specification
FIELD_DEFINITIONS = {
    # Field definitions with their bit positions
    "uPC_CLR": {"bits": (0, 0), "value": 1},
    "uPC_COND_CLR": {"bits": (1, 1), "value": 1},
    "PC_INC": {"bits": (2, 2), "value": 1},
    "PC_LO_WE": {"bits": (3, 3), "value": 1},
    "PC_HI_WE": {"bits": (4, 4), "value": 1},
    "PC_SOURCE": { "bits": (5,7), "value": 0},
    "IR0_READ_DBUS": {"bits": (8, 8), "value": 1},
    "IR1_READ_DBUS": {"bits": (9, 9), "value": 1},
    "IR2_READ_DBUS": {"bits": (10, 10), "value": 1},
    "SP_INC": {"bits": (11, 11), "value": 1},
    "SP_DEC": {"bits": (12, 12), "value": 1},
    "ABUS_WRITE_DEVICE": {"bits": (13, 14), "value": 0},  # 2 bits
    "DBUS_READ_DEVICE": {"bits": (15, 17), "value": 0},     # 3 bits
    "DBUS_WRITE_DEVICE": {"bits": (18, 20), "value": 0}, # 3 bits
    "STORE_FLAG": {"bits": (21, 21), "value": 1},
    "STORE_ACC": {"bits": (22, 22), "value": 1},
    "MEM_WE": {"bits": (23,23), "value":1},
    "MEM_OE": {"bits": (24,24), "value":1},
}
