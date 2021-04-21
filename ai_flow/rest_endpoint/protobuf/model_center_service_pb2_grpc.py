#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import message_pb2 as message__pb2
from . import model_center_service_pb2 as model__center__service__pb2


class ModelCenterServiceStub(object):
    """AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
    Functions of ModelCenterService include:
    1.Create registered model
    2.Update registered model
    3.Delete registered model
    4.List registered models
    5.Get registered model detail
    6.Create model version
    7.Update model version
    8.Delete model version
    9.Get model version detail
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.createRegisteredModel = channel.unary_unary(
                '/service.ModelCenterService/createRegisteredModel',
                request_serializer=model__center__service__pb2.CreateRegisteredModelRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.updateRegisteredModel = channel.unary_unary(
                '/service.ModelCenterService/updateRegisteredModel',
                request_serializer=model__center__service__pb2.UpdateRegisteredModelRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.deleteRegisteredModel = channel.unary_unary(
                '/service.ModelCenterService/deleteRegisteredModel',
                request_serializer=model__center__service__pb2.DeleteRegisteredModelRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.listRegisteredModels = channel.unary_unary(
                '/service.ModelCenterService/listRegisteredModels',
                request_serializer=model__center__service__pb2.ListRegisteredModelsRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.getRegisteredModelDetail = channel.unary_unary(
                '/service.ModelCenterService/getRegisteredModelDetail',
                request_serializer=model__center__service__pb2.GetRegisteredModelDetailRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.createModelVersion = channel.unary_unary(
                '/service.ModelCenterService/createModelVersion',
                request_serializer=model__center__service__pb2.CreateModelVersionRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.updateModelVersion = channel.unary_unary(
                '/service.ModelCenterService/updateModelVersion',
                request_serializer=model__center__service__pb2.UpdateModelVersionRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.deleteModelVersion = channel.unary_unary(
                '/service.ModelCenterService/deleteModelVersion',
                request_serializer=model__center__service__pb2.DeleteModelVersionRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )
        self.getModelVersionDetail = channel.unary_unary(
                '/service.ModelCenterService/getModelVersionDetail',
                request_serializer=model__center__service__pb2.GetModelVersionDetailRequest.SerializeToString,
                response_deserializer=message__pb2.Response.FromString,
                )


class ModelCenterServiceServicer(object):
    """AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
    Functions of ModelCenterService include:
    1.Create registered model
    2.Update registered model
    3.Delete registered model
    4.List registered models
    5.Get registered model detail
    6.Create model version
    7.Update model version
    8.Delete model version
    9.Get model version detail
    """

    def createRegisteredModel(self, request, context):
        """Create registered model with metadata of RegisteredModel.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def updateRegisteredModel(self, request, context):
        """Update registered model with metadata of RegisteredModel.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def deleteRegisteredModel(self, request, context):
        """Delete registered model with metadata of RegisteredModel.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def listRegisteredModels(self, request, context):
        """List registered models about metadata of RegisteredModel.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getRegisteredModelDetail(self, request, context):
        """Get registered model detail including metadata of RegisteredModel.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def createModelVersion(self, request, context):
        """Create model version with metadata of ModelVersion.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def updateModelVersion(self, request, context):
        """Update model version with metadata of ModelVersion.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def deleteModelVersion(self, request, context):
        """Delete model version with metadata of ModelVersion.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def getModelVersionDetail(self, request, context):
        """Get model version detail with metadata of ModelVersion.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ModelCenterServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'createRegisteredModel': grpc.unary_unary_rpc_method_handler(
                    servicer.createRegisteredModel,
                    request_deserializer=model__center__service__pb2.CreateRegisteredModelRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'updateRegisteredModel': grpc.unary_unary_rpc_method_handler(
                    servicer.updateRegisteredModel,
                    request_deserializer=model__center__service__pb2.UpdateRegisteredModelRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'deleteRegisteredModel': grpc.unary_unary_rpc_method_handler(
                    servicer.deleteRegisteredModel,
                    request_deserializer=model__center__service__pb2.DeleteRegisteredModelRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'listRegisteredModels': grpc.unary_unary_rpc_method_handler(
                    servicer.listRegisteredModels,
                    request_deserializer=model__center__service__pb2.ListRegisteredModelsRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'getRegisteredModelDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.getRegisteredModelDetail,
                    request_deserializer=model__center__service__pb2.GetRegisteredModelDetailRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'createModelVersion': grpc.unary_unary_rpc_method_handler(
                    servicer.createModelVersion,
                    request_deserializer=model__center__service__pb2.CreateModelVersionRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'updateModelVersion': grpc.unary_unary_rpc_method_handler(
                    servicer.updateModelVersion,
                    request_deserializer=model__center__service__pb2.UpdateModelVersionRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'deleteModelVersion': grpc.unary_unary_rpc_method_handler(
                    servicer.deleteModelVersion,
                    request_deserializer=model__center__service__pb2.DeleteModelVersionRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
            'getModelVersionDetail': grpc.unary_unary_rpc_method_handler(
                    servicer.getModelVersionDetail,
                    request_deserializer=model__center__service__pb2.GetModelVersionDetailRequest.FromString,
                    response_serializer=message__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'service.ModelCenterService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ModelCenterService(object):
    """AIFlowService provides model registry service rest endpoint of ModelCenterService for Model Center component.
    Functions of ModelCenterService include:
    1.Create registered model
    2.Update registered model
    3.Delete registered model
    4.List registered models
    5.Get registered model detail
    6.Create model version
    7.Update model version
    8.Delete model version
    9.Get model version detail
    """

    @staticmethod
    def createRegisteredModel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/createRegisteredModel',
            model__center__service__pb2.CreateRegisteredModelRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def updateRegisteredModel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/updateRegisteredModel',
            model__center__service__pb2.UpdateRegisteredModelRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def deleteRegisteredModel(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/deleteRegisteredModel',
            model__center__service__pb2.DeleteRegisteredModelRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def listRegisteredModels(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/listRegisteredModels',
            model__center__service__pb2.ListRegisteredModelsRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def getRegisteredModelDetail(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/getRegisteredModelDetail',
            model__center__service__pb2.GetRegisteredModelDetailRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def createModelVersion(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/createModelVersion',
            model__center__service__pb2.CreateModelVersionRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def updateModelVersion(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/updateModelVersion',
            model__center__service__pb2.UpdateModelVersionRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def deleteModelVersion(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/deleteModelVersion',
            model__center__service__pb2.DeleteModelVersionRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def getModelVersionDetail(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/service.ModelCenterService/getModelVersionDetail',
            model__center__service__pb2.GetModelVersionDetailRequest.SerializeToString,
            message__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
