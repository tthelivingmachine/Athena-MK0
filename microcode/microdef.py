FIRST_BYTE_FETCH = ["PC_INC", "MEM_OE", "IR0_READ_DBUS", "ABUS_WRITE_DEVICE=1", "DBUS_WRITE_DEVICE=7"]
SECOND_BYTE_FETCH = ["PC_INC", "MEM_OE", "IR1_READ_DBUS", "ABUS_WRITE_DEVICE=1", "DBUS_WRITE_DEVICE=7"]
THIRD_BYTE_FETCH = ["PC_INC", "MEM_OE", "IR2_READ_DBUS", "ABUS_WRITE_DEVICE=1", "DBUS_WRITE_DEVICE=7"]

MICROCODE = {
        0x38 : [ # RET, implement later as I figure out the stack.
        FIRST_BYTE_FETCH,
    ],
        0x39 : [ # NOP
        FIRST_BYTE_FETCH,
    ]
}


# MOV R[vvv], ACC
for vvv in range(8):
    op = 0x00 | vvv

    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        ["STORE_FLAG", "DBUS_WRITE_DEVICE=4", "DBUS_READ_DEVICE=1", "uPC_CLR"]
    ]

# Implementing all ALU in one go
for prefix in [0b00010, 0b00011, 0b00100, 0b00101, 0b00110]:
    for vvv in range(8):
        op = (prefix << 3) | vvv  # shift prefix into top 5 bits
        MICROCODE[op] = [
            FIRST_BYTE_FETCH,
            ["STORE_FLAG", "STORE_ACC", "uPC_CLR"]
        ]

# NOP
MICROCODE[0x39] = [
    FIRST_BYTE_FETCH
]

# RET
MICROCODE[0x38] = [
    FIRST_BYTE_FETCH
    ["SP_DEC"],
    ["ABUS_WRITE_DEVICE=2", "MEM_OE", "PC_HI_WE", "PC_SOURCE=0"],
    ["SP_DEC"],
    ["ABUS_WRITE_DEVICE=2", "MEM_OE", "PC_LO_WE", "PC_SOURCE=0", "uPC_CLR"]
]

# MOV ACC, #imm8
for vvv in range(8):
    op = (0b01001000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        ["STORE_FLAG", "STORE_ACC", "uPC_CLR"]
    ]

# ADD ACC, #imm8
for vvv in range(8):
    op = (0b01010000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        ["STORE_FLAG", "STORE_ACC", "uPC_CLR"]
    ]

# POP R[vvv]
for vvv in range(8):
    op = (0b01011000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        ["SP_DEC"],
        ["ABUS_WRITE_DEVICE=2", "DBUS_READ_DEVICE=1", "DBUS_WRITE_DEVICE=7", "MEM_OE", "uPC_CLR"]
    ]

# PUSH R[vvv]
for vvv in range(8):
    op = (0b01100000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        ["ABUS_WRITE_DEVICE=2", "SP_INC", "DBUS_WRITE_DEVICE=1", "MEM_WE", "uPC_CLR"]
    ]

# Branch rel #imm if (vvv)
for vvv in range(8):
    op = (0b01101000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH + ["uPC_COND_CLR"],
        # load 16 bit (pc + #imm8)
        # 1 - rel low
        # 2 - rel high
        ["PC_SOURCE=2", "PC_HI_WE"],
        ["PC_SOURCE=1", "PC_LO_WE", "uPC_CLR"]
    ]

# Load R[vvv], [rs0:rs1]
for vvv in range(8):
    op = (0b01110000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        ["ABUS_WRITE_DEVICE=3", "DBUS_WRITE_DEVICE=7", "DBUS_READ_DEVICE=1", "MEM_OE", "uPC_CLR"]
    ]

# Store R[vvv], [rs0:rs1]
for vvv in range(8):
    op = (0b01111000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        ["ABUS_WRITE_DEVICE=3", "DBUS_WRITE_DEVICE=1", "MEM_WE", "uPC_CLR"]
    ]

# Load R[vvv], #imm16
for vvv in range(8):
    op = (0b10000000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        THIRD_BYTE_FETCH,
        ["ABUS_WRITE_DEVICE=4", "DBUS_WRITE_DEVICE=7", "DBUS_READ_DEVICE=1", "MEM_OE", "uPC_CLR"]
    ]

# Store R[vvv], #imm16
for vvv in range(8):
    op = (0b10001000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        THIRD_BYTE_FETCH,
        ["ABUS_WRITE_DEVICE=4", "DBUS_WRITE_DEVICE=1", "MEM_WE", "uPC_CLR"]
    ]

# Call #imm16
for vvv in range(8):
    op = (0b10010000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH,
        THIRD_BYTE_FETCH,
        # 3 is low
        # 4 is high
        # 5 is write PC+1 Lo
        # 6 is write PC+1 Hi
        ["ABUS_WRITE_DEVICE=2", "SP_INC", "DBUS_WRITE_DEVICE=5", "MEM_WE"],
        ["ABUS_WRITE_DEVICE=2", "SP_INC", "DBUS_WRITE_DEVICE=6", "MEM_WE"],
        ["PC_SOURCE=4", "PC_HI_WE"],
        ["PC_SOURCE=3", "PC_LO_WE", "uPC_CLR"]

    ]

# Branch #imm16 if (vvv)
for vvv in range(8):
    op = (0b10011000) | vvv
    MICROCODE[op] = [
        FIRST_BYTE_FETCH,
        SECOND_BYTE_FETCH + ["uPC_COND_CLR"],
        THIRD_BYTE_FETCH,
        ["PC_SOURCE=4", "PC_HI_WE"],
        ["PC_SOURCE=3", "PC_LO_WE", "uPC_CLR"]
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
    "ABUS_WRITE_DEVICE": {"bits": (13, 15), "value": 0},  # 2 bits
    "DBUS_READ_DEVICE": {"bits": (16, 18), "value": 0},     # 3 bits
    "DBUS_WRITE_DEVICE": {"bits": (19, 21), "value": 0}, # 3 bits
    "STORE_FLAG": {"bits": (22, 22), "value": 1},
    "STORE_ACC": {"bits": (23, 23), "value": 1},
    "MEM_WE": {"bits": (30,30), "value":1},
    "MEM_OE": {"bits": (31,31), "value":1},
}
