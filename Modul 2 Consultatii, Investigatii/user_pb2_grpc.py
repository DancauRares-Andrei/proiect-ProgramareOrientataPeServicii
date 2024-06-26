# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import user_pb2 as user__pb2


class AuthServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Authenticate = channel.unary_unary(
                '/users.AuthService/Authenticate',
                request_serializer=user__pb2.AuthRequest.SerializeToString,
                response_deserializer=user__pb2.AuthResponse.FromString,
                )
        self.ValidateToken = channel.unary_unary(
                '/users.AuthService/ValidateToken',
                request_serializer=user__pb2.TokenRequest.SerializeToString,
                response_deserializer=user__pb2.TokenResponse.FromString,
                )
        self.DestroyToken = channel.unary_unary(
                '/users.AuthService/DestroyToken',
                request_serializer=user__pb2.TokenRequest.SerializeToString,
                response_deserializer=user__pb2.DestroyTokenResponse.FromString,
                )


class AuthServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Authenticate(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ValidateToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def DestroyToken(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AuthServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Authenticate': grpc.unary_unary_rpc_method_handler(
                    servicer.Authenticate,
                    request_deserializer=user__pb2.AuthRequest.FromString,
                    response_serializer=user__pb2.AuthResponse.SerializeToString,
            ),
            'ValidateToken': grpc.unary_unary_rpc_method_handler(
                    servicer.ValidateToken,
                    request_deserializer=user__pb2.TokenRequest.FromString,
                    response_serializer=user__pb2.TokenResponse.SerializeToString,
            ),
            'DestroyToken': grpc.unary_unary_rpc_method_handler(
                    servicer.DestroyToken,
                    request_deserializer=user__pb2.TokenRequest.FromString,
                    response_serializer=user__pb2.DestroyTokenResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'users.AuthService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AuthService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Authenticate(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/users.AuthService/Authenticate',
            user__pb2.AuthRequest.SerializeToString,
            user__pb2.AuthResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ValidateToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/users.AuthService/ValidateToken',
            user__pb2.TokenRequest.SerializeToString,
            user__pb2.TokenResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def DestroyToken(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/users.AuthService/DestroyToken',
            user__pb2.TokenRequest.SerializeToString,
            user__pb2.DestroyTokenResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)