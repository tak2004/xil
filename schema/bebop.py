from enum import Enum
from python_bebop import BebopWriter, BebopReader, UnionType, UnionDefinition
from uuid import UUID
import math
import json
from datetime import datetime

class EdgeType(Enum):
    UNKNOWN = 0
    PARENTCHILD = 1
    STRING = 2
    TEXTVIEW = 3
    CONSTANT = 4

class NodeType(Enum):
    UNKNOWN = 0
    UNIT = 1
    MODULE = 2
    USE = 3
    FUNCTION = 4
    TYPE = 5
    FUNCTIONARGUMENT = 6
    STATEMENT = 7
    ID = 8
    FFI = 9
    LIBRARY = 14
    IMPORTLIBRARY = 15
    NUMBER = 12
    BOOLEAN = 13
    INTEGER8 = 17
    INTEGER16 = 18
    INTEGER32 = 19
    INTEGER64 = 20
    UNSIGNEDINTEGER8 = 21
    UNSIGNEDINTEGER16 = 22
    UNSIGNEDINTEGER32 = 23
    UNSIGNEDINTEGER64 = 24
    FLOAT32 = 25
    FLOAT64 = 26
    STRING = 27
    OPIF = 246
    OPLABEL = 247
    OPCMP = 249
    OPCALL = 255

class Edge:
    _src_id: int

    _sink_id: int

    _src_type: NodeType

    _sink_type: NodeType

    _type: EdgeType


    def __init__(self,     src_id: int, sink_id: int, src_type: NodeType, sink_type: NodeType, type: EdgeType    ):
        self.encode = self._encode
        self._src_id = src_id
        self._sink_id = sink_id
        self._src_type = src_type
        self._sink_type = sink_type
        self._type = type

    @property
    def src_id(self):
        return self._src_id

    @property
    def sink_id(self):
        return self._sink_id

    @property
    def src_type(self):
        return self._src_type

    @property
    def sink_type(self):
        return self._sink_type

    @property
    def type(self):
        return self._type

    def _encode(self):
        """Fake class method for allowing instance encode"""
        writer = BebopWriter()
        Edge.encode_into(self, writer)
        return writer.to_list()


    @staticmethod
    def encode(message: "Edge"):
        writer = BebopWriter()
        Edge.encode_into(message, writer)
        return writer.to_list()


    @staticmethod
    def encode_into(message: "Edge", writer: BebopWriter):
        writer.write_uint16(message.src_id)

        writer.write_uint16(message.sink_id)

        writer.write_byte(message.src_type.value)

        writer.write_byte(message.sink_type.value)

        writer.write_byte(message.type.value)

    @classmethod
    def read_from(cls, reader: BebopReader):
        field0 = reader.read_uint16()

        field1 = reader.read_uint16()

        field2 = NodeType(reader.read_byte())

        field3 = NodeType(reader.read_byte())

        field4 = EdgeType(reader.read_byte())

        return Edge(src_id=field0, sink_id=field1, src_type=field2, sink_type=field3, type=field4)

    @staticmethod
    def decode(buffer) -> "Edge":
        return Edge.read_from(BebopReader(buffer))

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else dict(sorted(o.__dict__.items())) if hasattr(o, "__dict__") else str(o))



class TextView:
    _row: int

    _column: int


    def __init__(self,     row: int, column: int    ):
        self.encode = self._encode
        self._row = row
        self._column = column

    @property
    def row(self):
        return self._row

    @property
    def column(self):
        return self._column

    def _encode(self):
        """Fake class method for allowing instance encode"""
        writer = BebopWriter()
        TextView.encode_into(self, writer)
        return writer.to_list()


    @staticmethod
    def encode(message: "TextView"):
        writer = BebopWriter()
        TextView.encode_into(message, writer)
        return writer.to_list()


    @staticmethod
    def encode_into(message: "TextView", writer: BebopWriter):
        writer.write_uint32(message.row)

        writer.write_uint32(message.column)

    @classmethod
    def read_from(cls, reader: BebopReader):
        field0 = reader.read_uint32()

        field1 = reader.read_uint32()

        return TextView(row=field0, column=field1)

    @staticmethod
    def decode(buffer) -> "TextView":
        return TextView.read_from(BebopReader(buffer))

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else dict(sorted(o.__dict__.items())) if hasattr(o, "__dict__") else str(o))



class EdgeList:
    _elements: list[Edge]


    def __init__(self,     elements: list[Edge]    ):
        self.encode = self._encode
        self._elements = elements

    @property
    def elements(self):
        return self._elements

    def _encode(self):
        """Fake class method for allowing instance encode"""
        writer = BebopWriter()
        EdgeList.encode_into(self, writer)
        return writer.to_list()


    @staticmethod
    def encode(message: "EdgeList"):
        writer = BebopWriter()
        EdgeList.encode_into(message, writer)
        return writer.to_list()


    @staticmethod
    def encode_into(message: "EdgeList", writer: BebopWriter):
        length0 = len(message.elements)
        writer.write_uint32(length0)
        for i0 in range(length0):
            Edge.encode_into(message.elements[i0], writer)

    @classmethod
    def read_from(cls, reader: BebopReader):
        length0 = reader.read_uint32()
        field0 = []
        for i0 in range(length0):
            x0 = Edge.read_from(reader)
            field0.append(x0)

        return EdgeList(elements=field0)

    @staticmethod
    def decode(buffer) -> "EdgeList":
        return EdgeList.read_from(BebopReader(buffer))

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else dict(sorted(o.__dict__.items())) if hasattr(o, "__dict__") else str(o))



class TextViewList:
    _elements: list[TextView]


    def __init__(self,     elements: list[TextView]    ):
        self.encode = self._encode
        self._elements = elements

    @property
    def elements(self):
        return self._elements

    def _encode(self):
        """Fake class method for allowing instance encode"""
        writer = BebopWriter()
        TextViewList.encode_into(self, writer)
        return writer.to_list()


    @staticmethod
    def encode(message: "TextViewList"):
        writer = BebopWriter()
        TextViewList.encode_into(message, writer)
        return writer.to_list()


    @staticmethod
    def encode_into(message: "TextViewList", writer: BebopWriter):
        length0 = len(message.elements)
        writer.write_uint32(length0)
        for i0 in range(length0):
            TextView.encode_into(message.elements[i0], writer)

    @classmethod
    def read_from(cls, reader: BebopReader):
        length0 = reader.read_uint32()
        field0 = []
        for i0 in range(length0):
            x0 = TextView.read_from(reader)
            field0.append(x0)

        return TextViewList(elements=field0)

    @staticmethod
    def decode(buffer) -> "TextViewList":
        return TextViewList.read_from(BebopReader(buffer))

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else dict(sorted(o.__dict__.items())) if hasattr(o, "__dict__") else str(o))



class StringList:
    _elements: list[str]


    def __init__(self,     elements: list[str]    ):
        self.encode = self._encode
        self._elements = elements

    @property
    def elements(self):
        return self._elements

    def _encode(self):
        """Fake class method for allowing instance encode"""
        writer = BebopWriter()
        StringList.encode_into(self, writer)
        return writer.to_list()


    @staticmethod
    def encode(message: "StringList"):
        writer = BebopWriter()
        StringList.encode_into(message, writer)
        return writer.to_list()


    @staticmethod
    def encode_into(message: "StringList", writer: BebopWriter):
        length0 = len(message.elements)
        writer.write_uint32(length0)
        for i0 in range(length0):
            writer.write_string(message.elements[i0])

    @classmethod
    def read_from(cls, reader: BebopReader):
        length0 = reader.read_uint32()
        field0 = []
        for i0 in range(length0):
            x0 = reader.read_string()
            field0.append(x0)

        return StringList(elements=field0)

    @staticmethod
    def decode(buffer) -> "StringList":
        return StringList.read_from(BebopReader(buffer))

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else dict(sorted(o.__dict__.items())) if hasattr(o, "__dict__") else str(o))



class AbstractSyntaxGraph:
    _EdgeListBytes: int

    _TextViewListBytes: int

    _StringListBytes: int


    def __init__(self,     EdgeListBytes: int, TextViewListBytes: int, StringListBytes: int    ):
        self.encode = self._encode
        self._EdgeListBytes = EdgeListBytes
        self._TextViewListBytes = TextViewListBytes
        self._StringListBytes = StringListBytes

    @property
    def EdgeListBytes(self):
        return self._EdgeListBytes

    @property
    def TextViewListBytes(self):
        return self._TextViewListBytes

    @property
    def StringListBytes(self):
        return self._StringListBytes

    def _encode(self):
        """Fake class method for allowing instance encode"""
        writer = BebopWriter()
        AbstractSyntaxGraph.encode_into(self, writer)
        return writer.to_list()


    @staticmethod
    def encode(message: "AbstractSyntaxGraph"):
        writer = BebopWriter()
        AbstractSyntaxGraph.encode_into(message, writer)
        return writer.to_list()


    @staticmethod
    def encode_into(message: "AbstractSyntaxGraph", writer: BebopWriter):
        writer.write_uint32(message.EdgeListBytes)

        writer.write_uint32(message.TextViewListBytes)

        writer.write_uint32(message.StringListBytes)

    @classmethod
    def read_from(cls, reader: BebopReader):
        field0 = reader.read_uint32()

        field1 = reader.read_uint32()

        field2 = reader.read_uint32()

        return AbstractSyntaxGraph(EdgeListBytes=field0, TextViewListBytes=field1, StringListBytes=field2)

    @staticmethod
    def decode(buffer) -> "AbstractSyntaxGraph":
        return AbstractSyntaxGraph.read_from(BebopReader(buffer))

    def __repr__(self):
        return json.dumps(self, default=lambda o: o.value if isinstance(o, Enum) else dict(sorted(o.__dict__.items())) if hasattr(o, "__dict__") else str(o))