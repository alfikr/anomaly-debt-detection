# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import anomaly_pb2 as anomaly__pb2

GRPC_GENERATED_VERSION = '1.73.0'
GRPC_VERSION = grpc.__version__
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    raise RuntimeError(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in anomaly_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
    )


class AnomalyServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Detect = channel.unary_unary(
                '/AnomalyService/Detect',
                request_serializer=anomaly__pb2.AnomalyRequest.SerializeToString,
                response_deserializer=anomaly__pb2.AnomalyResponse.FromString,
                _registered_method=True)
        self.SubmitFeedback = channel.unary_unary(
                '/AnomalyService/SubmitFeedback',
                request_serializer=anomaly__pb2.FeedbackRequest.SerializeToString,
                response_deserializer=anomaly__pb2.FeedbackResponse.FromString,
                _registered_method=True)


class AnomalyServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Detect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SubmitFeedback(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AnomalyServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Detect': grpc.unary_unary_rpc_method_handler(
                    servicer.Detect,
                    request_deserializer=anomaly__pb2.AnomalyRequest.FromString,
                    response_serializer=anomaly__pb2.AnomalyResponse.SerializeToString,
            ),
            'SubmitFeedback': grpc.unary_unary_rpc_method_handler(
                    servicer.SubmitFeedback,
                    request_deserializer=anomaly__pb2.FeedbackRequest.FromString,
                    response_serializer=anomaly__pb2.FeedbackResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'AnomalyService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('AnomalyService', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class AnomalyService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Detect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/AnomalyService/Detect',
            anomaly__pb2.AnomalyRequest.SerializeToString,
            anomaly__pb2.AnomalyResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def SubmitFeedback(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/AnomalyService/SubmitFeedback',
            anomaly__pb2.FeedbackRequest.SerializeToString,
            anomaly__pb2.FeedbackResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
