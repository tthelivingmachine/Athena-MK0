MICROCODE = {
    0x00: [  # FETCH
        ["PC_INC", "PC_LO_READ_DBUS", "ABUS_WRITE_DEVICE=1"],  # uPC=0
        ["uPC_CLR"]  # uPC=1
    ],
    0x01: [  # NOP
        ["uPC_CLR"]
    ],
}

# Define the field mappings based on your specification
FIELD_DEFINITIONS = {
    # Field definitions with their bit positions
    "uPC_CLR": {"bits": (0, 0), "value": 1},
    "PC_INC": {"bits": (1, 1), "value": 1},
    "PC_LO_READ_DBUS": {"bits": (2, 2), "value": 1},
    "PC_HI_READ_DBUS": {"bits": (3, 3), "value": 1},
    "IR0_READ_DBUS": {"bits": (4, 4), "value": 1},
    "IR1_READ_DBUS": {"bits": (5, 5), "value": 1},
    "IR2_READ_DBUS": {"bits": (6, 6), "value": 1},
    "SP_INC": {"bits": (7, 7), "value": 1},
    "SP_DEC": {"bits": (8, 8), "value": 1},
    "ABUS_WRITE_DEVICE": {"bits": (9, 10), "value": 0},  # 2 bits
    "REG_READ_DBUS": {"bits": (11, 13), "value": 0},     # 3 bits
    "DBUS_WRITE_DEVICE": {"bits": (14, 16), "value": 0}, # 3 bits
    "STORE_FLAG": {"bits": (17, 17), "value": 1),
    "STORE_ACC": {"bits": (18, 18), "value": 1),
}
