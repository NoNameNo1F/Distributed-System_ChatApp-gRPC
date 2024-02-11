# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2

import protobuf.ChatService.chat_pb2 as chat__pb2


class ChatServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendMessage = channel.unary_unary(
                '/chat.ChatService/SendMessage',
                request_serializer=chat__pb2.Message.SerializeToString,
                response_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                )
        self.CreateGroup = channel.unary_unary(
                '/chat.ChatService/CreateGroup',
                request_serializer=chat__pb2.CreateGroupRequest.SerializeToString,
                response_deserializer=chat__pb2.Metadata.FromString,
                )
        self.GetListUser = channel.unary_unary(
                '/chat.ChatService/GetListUser',
                request_serializer=chat__pb2.ListUsersRequest.SerializeToString,
                response_deserializer=chat__pb2.ListUsersResponse.FromString,
                )
        self.FetchMetadata = channel.unary_unary(
                '/chat.ChatService/FetchMetadata',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=chat__pb2.Metadata.FromString,
                )
        self.AddUserToGroup = channel.unary_unary(
                '/chat.ChatService/AddUserToGroup',
                request_serializer=chat__pb2.AddUserRequest.SerializeToString,
                response_deserializer=chat__pb2.Metadata.FromString,
                )


class ChatServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def CreateGroup(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetListUser(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def FetchMetadata(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AddUserToGroup(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'SendMessage': grpc.unary_unary_rpc_method_handler(
                    servicer.SendMessage,
                    request_deserializer=chat__pb2.Message.FromString,
                    response_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            ),
            'CreateGroup': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateGroup,
                    request_deserializer=chat__pb2.CreateGroupRequest.FromString,
                    response_serializer=chat__pb2.Metadata.SerializeToString,
            ),
            'GetListUser': grpc.unary_unary_rpc_method_handler(
                    servicer.GetListUser,
                    request_deserializer=chat__pb2.ListUsersRequest.FromString,
                    response_serializer=chat__pb2.ListUsersResponse.SerializeToString,
            ),
            'FetchMetadata': grpc.unary_unary_rpc_method_handler(
                    servicer.FetchMetadata,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=chat__pb2.Metadata.SerializeToString,
            ),
            'AddUserToGroup': grpc.unary_unary_rpc_method_handler(
                    servicer.AddUserToGroup,
                    request_deserializer=chat__pb2.AddUserRequest.FromString,
                    response_serializer=chat__pb2.Metadata.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'chat.ChatService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendMessage(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.ChatService/SendMessage',
            chat__pb2.Message.SerializeToString,
            google_dot_protobuf_dot_empty__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def CreateGroup(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.ChatService/CreateGroup',
            chat__pb2.CreateGroupRequest.SerializeToString,
            chat__pb2.Metadata.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetListUser(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.ChatService/GetListUser',
            chat__pb2.ListUsersRequest.SerializeToString,
            chat__pb2.ListUsersResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def FetchMetadata(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.ChatService/FetchMetadata',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            chat__pb2.Metadata.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def AddUserToGroup(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/chat.ChatService/AddUserToGroup',
            chat__pb2.AddUserRequest.SerializeToString,
            chat__pb2.Metadata.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
