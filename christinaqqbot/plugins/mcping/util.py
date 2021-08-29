from typing import Dict, Union, Tuple, Optional
import base64
import json
import os
import socket
import struct
import sys
import time

__author__ = "ntoskrnl4"
__version__ = "0.4"

# Sample ping packet data sent by the vanilla 1.15.2 client
# Captured by reading a raw Python socket

# 10 - Following packet's length
# 00 - This packet's ID
# c2 - VarInt: Client version (c204 = 578)
# 04 - VarInt: Client version
# 09 - Following string's length
# 31 - '1'
# 32 - '2'
# 37 - '7'
# 2e - '.'
# 30 - '0'
# 2e - '.'
# 30 - '0'
# 2e - '.'
# 31 - '1'
# 63 - Target port: high byte (63dd = 25565)
# dd - Target port: low byte
# 01 - Next state (01: Status)

# 01 - Following packet's length
# 00 - This packet's ID (00 w/o fields: Request)


# VarInts are a convoluted way of saving barely a few bytes of data on the
# network stream, by encoding a number alongside a bit ndicating if there's more
# bytes after it to that number. https://wiki.vg/Protocol#VarInt_and_VarLong
def decode_varint(sock) -> Union[int, Tuple[int, bytes]]:
	"""
	Read a VarInt from a socket or (string or string-like). Returns the number,
	alongside the rest of the data if string-like.
	
	:param sock: Socket to read a VarInt from.
	:raises ValueError: The VarInt we read exceeded int32 limits.
	:raises TypeError: We got back b''/EOF from a socket.
	:raises IndexError: We tried to read b'' from a string.
	:return: The number that was read.
	"""
	n_bytes = 0
	number = 0
	byte = 128  # The byte we are reading in from the socket
	while (byte & 0x80) != 0:
		if isinstance(sock, bytes):
			byte = sock[0]
			sock = sock[1:]
		else:
			byte = ord(sock.recv(1))
		value = byte & 0x7f
		number |= value << (7*n_bytes)  # In-place OR operation
		n_bytes += 1
		if n_bytes > 4:
			raise OverflowError("VarInt too large")
	if isinstance(sock, bytes):
		return number, sock
	else:
		return number


def encode_varint(number):
	"""
	Write a VarInt to a string.
	
	:param number: Number to encode as a VarInt.
	:return: The encoded VarInt.
	"""
	# Python ints are variable length, which means there's no fixed size.
	# Typical programming language implementation exploits the sign bit moving
	# when doing bitwise shifts, but that's not possible here.
	# To force an int32-like type, we use the `struct` module to make it fit.
	number = struct.unpack(">I", struct.pack(">i", number))[0]
	out = b""
	while True:
		part = number & 0x7f
		number = number >> 7
		if number != 0:
			part |= 0x80  # In-place OR operation
			out += part.to_bytes(1, byteorder="big")
		else:
			out += part.to_bytes(1, byteorder="big")
			return out


def write_packet(sock, data, packet_id):
	"""
	Write a Minecraft data packet to the socket.
	
	:param sock: Stream to write to.
	:param data: Data to be written.
	:param packet_id: Numeric packet ID.
	"""
	data = encode_varint(packet_id) + data
	length = encode_varint(len(data))
	# if debug: sys.stdout.write("<-- "+" ".join([hex(x | 0x100)[3:] for x in data])+"\n")
	sock.send(length + data)


def read_packet(sock) -> Tuple[int, bytes]:
	"""
	Read a packet into format (Packet ID, data).
	
	:param sock: Socket to read from.
	:return: Packet ID and corresponding data.
	"""
	packet_length = decode_varint(sock)
	packet_id = decode_varint(sock)
	data_length = packet_length - len(encode_varint(packet_id))
	data = b""
	while len(data) < data_length:
		data += sock.recv(data_length - len(data))
	# if debug: sys.stdout.write("--> "+" ".join([hex(x | 0x100)[3:] for x in data])+"\n")
	return packet_id, data


class MinecraftPing:
	def __init__(self, host: str, port: int):
		"""
		Create a new MinecraftPing representing a minecraft server to ping.
		
		:param host: Hostname or IP address of the server to ping.
		:param port: Port of the minecraft server.
		"""
		self.host = host
		self.port = port
		self.latency = None
	
	def ping(self) -> Tuple[bool, Optional[str]]:
		"""
		Ping the Minecraft server, and parse its response.
		
		:return: True if the server was connected to, otherwise False with an error string.
		"""
		try:
			s = socket.create_connection((self.host, self.port), timeout=5.0)
		except Exception as e:
			return False, f"{e.__class__.__name__}: {e}"
		
		proto = encode_varint(-1)  # Protocol will be -1/unknown (which is ok)
		if len(self.host) > 32767:
			raise OverflowError("Hostname too large: >32767 bytes in size")
		host = encode_varint(len(self.host)) + self.host.encode("UTF-8")
		port = struct.pack(">H", self.port)
		state = encode_varint(1)
		write_packet(s, packet_id=0x00, data=proto+host+port+state)
		write_packet(s, packet_id=0x00, data=b"")
		
		# Send Ping packet
		write_packet(s, packet_id=0x01, data=struct.pack(">q", time.time_ns()))
		start = time.perf_counter()
		end = None
		
		# We are expecting two packets back
		for _ in range(2):
			packet_id, data = read_packet(s)
			if packet_id == 0:  # Response packet
				self._handle_response(data)
		s.close()
		
		return True, None
	
	def _handle_response(self, data):
		"""
		Parse raw socket return data and set the attributes of the class.
		
		:param data: Raw socket data to parse.
		"""
		length, data = decode_varint(data)
		if len(data) != length:
			raise RuntimeError("Return data length mismatch")
		status = json.loads(data.decode())
		self.description = status["description"]["text"]
		self.player_limit = status["players"]["max"]
		self.player_count = status["players"]["online"]
		if self.player_count:
			self.players = [x["name"] for x in status["players"]["sample"]]
		else:
			self.players = []
		self.version = status["version"]["name"]
		self.version_id = status["version"]["protocol"]
		self.icon = status.get("favicon", "")