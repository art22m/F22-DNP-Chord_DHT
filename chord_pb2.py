# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chord.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0b\x63hord.proto\"/\n\x0fRegisterRequest\x12\x0e\n\x06ipaddr\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\t\"1\n\rRegisterReply\x12\x0f\n\x07node_id\x18\x01 \x01(\x03\x12\x0f\n\x07message\x18\x02 \x01(\t\"$\n\x11\x44\x65registerRequest\x12\x0f\n\x07node_id\x18\x01 \x01(\x03\"2\n\x0f\x44\x65registerReply\x12\x0e\n\x06result\x18\x01 \x01(\x08\x12\x0f\n\x07message\x18\x02 \x01(\t\"-\n\x1aPopulateFingerTableRequest\x12\x0f\n\x07node_id\x18\x01 \x01(\x03\"H\n\x18PopulateFingerTableReply\x12\x0f\n\x07node_id\x18\x01 \x01(\x03\x12\x1b\n\x0c\x66inger_table\x18\x02 \x03(\x0b\x32\x05.Node\"\x15\n\x13GetChordInfoRequest\")\n\x11GetChordInfoReply\x12\x14\n\x05nodes\x18\x01 \x03(\x0b\x32\x05.Node\"\'\n\x04Node\x12\n\n\x02id\x18\x01 \x01(\x03\x12\x13\n\x0bsocket_addr\x18\x02 \x01(\t\"\x17\n\x15GetFingerTableRequest\"2\n\x13GetFingerTableReply\x12\x1b\n\x0c\x66inger_table\x18\x01 \x03(\x0b\x32\x05.Node2\x88\x02\n\x0fRegistryService\x12.\n\x08register\x12\x10.RegisterRequest\x1a\x0e.RegisterReply\"\x00\x12\x34\n\nderegister\x12\x12.DeregisterRequest\x1a\x10.DeregisterReply\"\x00\x12Q\n\x15populate_finger_table\x12\x1b.PopulateFingerTableRequest\x1a\x19.PopulateFingerTableReply\"\x00\x12<\n\x0eget_chord_info\x12\x14.GetChordInfoRequest\x1a\x12.GetChordInfoReply\"\x00\x32Q\n\x0bNodeService\x12\x42\n\x10get_finger_table\x12\x16.GetFingerTableRequest\x1a\x14.GetFingerTableReply\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'chord_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _REGISTERREQUEST._serialized_start=15
  _REGISTERREQUEST._serialized_end=62
  _REGISTERREPLY._serialized_start=64
  _REGISTERREPLY._serialized_end=113
  _DEREGISTERREQUEST._serialized_start=115
  _DEREGISTERREQUEST._serialized_end=151
  _DEREGISTERREPLY._serialized_start=153
  _DEREGISTERREPLY._serialized_end=203
  _POPULATEFINGERTABLEREQUEST._serialized_start=205
  _POPULATEFINGERTABLEREQUEST._serialized_end=250
  _POPULATEFINGERTABLEREPLY._serialized_start=252
  _POPULATEFINGERTABLEREPLY._serialized_end=324
  _GETCHORDINFOREQUEST._serialized_start=326
  _GETCHORDINFOREQUEST._serialized_end=347
  _GETCHORDINFOREPLY._serialized_start=349
  _GETCHORDINFOREPLY._serialized_end=390
  _NODE._serialized_start=392
  _NODE._serialized_end=431
  _GETFINGERTABLEREQUEST._serialized_start=433
  _GETFINGERTABLEREQUEST._serialized_end=456
  _GETFINGERTABLEREPLY._serialized_start=458
  _GETFINGERTABLEREPLY._serialized_end=508
  _REGISTRYSERVICE._serialized_start=511
  _REGISTRYSERVICE._serialized_end=775
  _NODESERVICE._serialized_start=777
  _NODESERVICE._serialized_end=858
# @@protoc_insertion_point(module_scope)
