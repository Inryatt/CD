# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='chat.proto',
  package='',
  syntax='proto3',
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_pb=b'\n\nchat.proto\"6\n\x12TextMessageRequest\x12\x0f\n\x07\x63ontent\x18\x01 \x01(\t\x12\x0f\n\x07\x63hannel\x18\x02 \x01(\t\"%\n\x12\x43hannelJoinRequest\x12\x0f\n\x07\x63hannel\x18\x01 \x01(\t\" \n\x11ServerAcknowledge\x12\x0b\n\x03\x61\x63k\x18\x01 \x01(\x08\x32z\n\x04\x63hat\x12\x38\n\x0bTextMessage\x12\x13.TextMessageRequest\x1a\x12.ServerAcknowledge\"\x00\x12\x38\n\x0b\x43hannelJoin\x12\x13.ChannelJoinRequest\x1a\x12.ServerAcknowledge\"\x00\x62\x06proto3'
)




_TEXTMESSAGEREQUEST = _descriptor.Descriptor(
  name='TextMessageRequest',
  full_name='TextMessageRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='content', full_name='TextMessageRequest.content', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
    _descriptor.FieldDescriptor(
      name='channel', full_name='TextMessageRequest.channel', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=14,
  serialized_end=68,
)


_CHANNELJOINREQUEST = _descriptor.Descriptor(
  name='ChannelJoinRequest',
  full_name='ChannelJoinRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel', full_name='ChannelJoinRequest.channel', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=b"".decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=70,
  serialized_end=107,
)


_SERVERACKNOWLEDGE = _descriptor.Descriptor(
  name='ServerAcknowledge',
  full_name='ServerAcknowledge',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  create_key=_descriptor._internal_create_key,
  fields=[
    _descriptor.FieldDescriptor(
      name='ack', full_name='ServerAcknowledge.ack', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR,  create_key=_descriptor._internal_create_key),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=109,
  serialized_end=141,
)

DESCRIPTOR.message_types_by_name['TextMessageRequest'] = _TEXTMESSAGEREQUEST
DESCRIPTOR.message_types_by_name['ChannelJoinRequest'] = _CHANNELJOINREQUEST
DESCRIPTOR.message_types_by_name['ServerAcknowledge'] = _SERVERACKNOWLEDGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

TextMessageRequest = _reflection.GeneratedProtocolMessageType('TextMessageRequest', (_message.Message,), {
  'DESCRIPTOR' : _TEXTMESSAGEREQUEST,
  '__module__' : 'chat_pb2'
  # @@protoc_insertion_point(class_scope:TextMessageRequest)
  })
_sym_db.RegisterMessage(TextMessageRequest)

ChannelJoinRequest = _reflection.GeneratedProtocolMessageType('ChannelJoinRequest', (_message.Message,), {
  'DESCRIPTOR' : _CHANNELJOINREQUEST,
  '__module__' : 'chat_pb2'
  # @@protoc_insertion_point(class_scope:ChannelJoinRequest)
  })
_sym_db.RegisterMessage(ChannelJoinRequest)

ServerAcknowledge = _reflection.GeneratedProtocolMessageType('ServerAcknowledge', (_message.Message,), {
  'DESCRIPTOR' : _SERVERACKNOWLEDGE,
  '__module__' : 'chat_pb2'
  # @@protoc_insertion_point(class_scope:ServerAcknowledge)
  })
_sym_db.RegisterMessage(ServerAcknowledge)



_CHAT = _descriptor.ServiceDescriptor(
  name='chat',
  full_name='chat',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  create_key=_descriptor._internal_create_key,
  serialized_start=143,
  serialized_end=265,
  methods=[
  _descriptor.MethodDescriptor(
    name='TextMessage',
    full_name='chat.TextMessage',
    index=0,
    containing_service=None,
    input_type=_TEXTMESSAGEREQUEST,
    output_type=_SERVERACKNOWLEDGE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
  _descriptor.MethodDescriptor(
    name='ChannelJoin',
    full_name='chat.ChannelJoin',
    index=1,
    containing_service=None,
    input_type=_CHANNELJOINREQUEST,
    output_type=_SERVERACKNOWLEDGE,
    serialized_options=None,
    create_key=_descriptor._internal_create_key,
  ),
])
_sym_db.RegisterServiceDescriptor(_CHAT)

DESCRIPTOR.services_by_name['chat'] = _CHAT

# @@protoc_insertion_point(module_scope)
