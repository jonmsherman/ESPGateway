from machine import Pin, SPI

CE_pin = 5
CS_pin = 4
IRQ_pin_number = 1
address_width = 3

hspi = None
chip_select = None
chip_enable = None
IRQ_pin = None
RXTX_ADDR = bytearray([0xE7, 0xE7, 0xE7]) # randomly chosen address


# Commands
R_REGISTER = 0x00
R_RX_PL_WID = 0x60
W_REGISTER = 0x20
R_RX_PAYLOAD = 0x61
W_TX_PAYLOAD = 0xA0
FLUSH_TX = 0xE1
FLUSH_RX = 0xE2
REUSE_TX_PL = 0xE3
NOP = 0xFF
R_RX_PL_WID = 0x60

# Register Addresses
CONFIG = 0x00
EN_AA = 0x01
EN_RXADDR = 0x02
SETUP_AW = 0x03
SETUP_RETR = 0x04
RF_CH = 0x05
RF_SETUP = 0x06
STATUS = 0x07
OBSERVE_TX = 0x08
CD = 0x09
RX_ADDR_P0 = 0x0A
RX_ADDR_P1 = 0x0B
RX_ADDR_P2 = 0x0C
RX_ADDR_P3 = 0x0D
RX_ADDR_P4 = 0x0E
RX_ADDR_P5 = 0x0F
TX_ADDR = 0x10
RX_PW_P0 = 0x11
RX_PW_P1 = 0x12
RX_PW_P2 = 0x13
RX_PW_P3 = 0x14
RX_PW_P4 = 0x15
RX_PW_P5 = 0x16
FIFO_STATUS = 0x17
DYNPD = 0x1C
FEATURE = 0x1D

def nrf_setup():
    SPI_init()



    write_register(EN_RXADDR, 0x01) # Enable data pipe 0

    write_register(SETUP_AW, 0x01) # 3 byte address

    write_register(SETUP_RETR, 0xFF) # 15 retries

    write_register(RF_CH, 0x09)  # Randomly chosen RF channel

    write_register(RF_SETUP, 0x26) # 250kbps, 0dBm

    write_register(RX_PW_P0, 0x20) # RX payload = 2 byte

    # # activate

    # global RXTX_ADDR
    write_address(RX_ADDR_P0, RXTX_ADDR);
    write_address(TX_ADDR, RXTX_ADDR);

    # print("Address RX, TX 2: ")
    print(read_address(RX_ADDR_P0))
    print(read_address(TX_ADDR))


    # enable dynamic payload
    write_register(FEATURE, 0x06)
    write_register(DYNPD, 0x01)
    write_register(EN_AA,0x01)
    print(read_register(DYNPD))
    print(read_register(FEATURE))
    # print(read_register(CONFIG))
    # # write the address to both 

    # # flush FIFO buffers
    flush_RX()
    flush_TX()
    write_register(CONFIG, 0x0B)  # 1 byte CRC, POWER UP, PRX
    print("nrf24L01 Initialized \n")

    # # setup IRQ
    # global IRQ_pin
    # IRQ_pin = Pin(IRQ_pin_number, Pin.IN)
    # IRQ_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_FALLING, handler=callback)



def RX_mode():
    write_register(CONFIG, 0x0B) # 1 byte CRC, POWER UP, PRX
    global chip_enable
    chip_enable.on()

def SPI_init():
    # initialize chip select to GPIO15 (D8)
    global chip_select
    chip_select = Pin(CS_pin,Pin.OUT)
    global chip_enable
    chip_enable = Pin(CE_pin,Pin.OUT)
    # initialize SPI to 8 MHz
    global hspi
    hspi = SPI(1, baudrate=4000000, polarity=0, phase=0)

def write_register(register, value):
    address = W_REGISTER | register
    data = bytearray(2)
    data[0] = address
    data[1] = value
    global chip_select
    chip_select.off()
    hspi.write(data)
    chip_select.on()

def read_address(address):
    address = R_REGISTER | address
    data = bytearray(1)
    data[0] = address
    global chip_select
    chip_select.off()
    hspi.write(data)
    value = hspi.read(5)
    chip_select.on()
    return value;

def activate_command():
    data = bytearray(2)
    data[0] = 0x50 
    data[1] = 0x73
    global chip_select
    chip_select.off()
    hspi.write(data)
    chip_select.on()

def R_RX_PL_WID_command():
    address = R_RX_PL_WID
    data = bytearray(1)
    data[0] = address
    global chip_select
    chip_select.off()
    hspi.write(data)
    value = hspi.read(1)
    chip_select.on()
    return value;

def read_register(register):
    address = R_REGISTER | register
    data = bytearray(1)
    data[0] = address
    global chip_select
    chip_select.off()
    hspi.write(data)
    value = hspi.read(1)
    chip_select.on()
    return value;

def write_address(register, address):
    register_address = W_REGISTER | register
    data = bytearray(6)
    data[0] = register_address
    data[1] = RXTX_ADDR[0]
    data[2] = RXTX_ADDR[1]
    data[3] = RXTX_ADDR[2]
    # data[4] = RXTX_ADDR[3]
    # data[5] = RXTX_ADDR[4]
    global chip_select
    chip_select.off()
    hspi.write(data)
    chip_select.on()

def send_command(command):
    data = bytearray(1)
    data[0] = command
    global chip_select
    chip_select.off()
    hspi.write(data)
    chip_select.on()

def flush_RX():
    write_register(STATUS,0x70) # clear interrupt bits and number of retransmits
    send_command(FLUSH_RX) # clear RX FIFO

def flush_TX():
    write_register(STATUS,0x70) # clear interrupt bits and number of retransmits
    send_command(FLUSH_TX) # clear RX FIFO

def can_read_data():
    STATUS_register = int.from_bytes(read_register(STATUS),'big')
    return (STATUS_register & 0x40) != 0

def read_status_register():
    data = bytearray(1)
    data[0] = NOP
    global chip_select
    chip_select.off()
    hspi.write(data)
    STATUS_register = hspi.read(1)
    chip_select.on()
    return STATUS_register

def read_payload(payload_length):
    rx_payload_command = bytearray(1)
    rx_payload_command[0] = R_RX_PAYLOAD
    i = 0
    rx_payload = bytearray(payload_length)
    global chip_select
    chip_select.off()
    hspi.write(rx_payload_command)
    while i < payload_length:
        rx_payload[i] = int.from_bytes(hspi.read(1),'big')
        i = i + 1
    chip_select.on()
    # print(value)
    return rx_payload

def send_read_command(command):
    data = bytearray(1)
    data[0] = command
    global chip_select
    chip_select.off()
    hspi.write(data)
    value = hspi.read(1)
    chip_select.on()
    return value


def receive_data():
    # grab payload length
    payload_length = send_read_command(R_RX_PL_WID)
    # print("Payload length:")
    # print(payload_length)
    # print("\n")
    print("PAYLOAD LENGTH:")
    print(payload_length)
    data = read_payload(2)
    # clear interrupt in status register
    write_register(STATUS,0x40)
    return data

def receive_dynamic_data():
    payload_length = int.from_bytes(R_RX_PL_WID_command(),'big')
    data = read_payload(payload_length)
    # clear interrupt in status register
    write_register(STATUS,0x40)
    return data


def callback(p):
    print("Got something...")
    value = receive_data()

    print(value)
