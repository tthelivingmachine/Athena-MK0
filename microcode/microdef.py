MICROCODE = {
    0x00: [  # FETCH
        ["PC_INC", "PC_LO_READ_DBUS", "ABUS_WRITE_DEVICE=1"],  # uPC=0
        ["uPC_CLR"]  # uPC=1
    ],
    0x01: [  # NOP
        ["uPC_CLR"]
    ],
}


