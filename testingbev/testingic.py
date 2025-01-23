import board
import busio
from adafruit_mcp230xx.mcp23017 import MCP23017

i2c = busio.I2C(board.SCL, board.SDA)
print("Initializing MCP23017...")
mcp = MCP23017(i2c, address=0x24)
print("MCP23017 detected and initialized.")
