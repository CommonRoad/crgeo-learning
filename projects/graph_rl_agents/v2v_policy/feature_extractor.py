from typing import Type
from torch import Tensor, nn
from torch_geometric.nn import GCN, GAT
import torch
import gym
import warnings
import numpy as np
from torch_geometric.data import HeteroData
from crgeo.common.logging import stdout
from crgeo.dataset.commonroad_data import CommonRoadData
from crgeo.dataset.extraction.traffic.feature_computers.implementations.types import V2V_Feature, V_Feature
from crgeo_learning.reinforcement.base_geometric_feature_extractor import BaseGeometricFeatureExtractor
from torch_geometric.nn import MessagePassing, BatchNorm, LayerNorm, GraphNorm
from torch_geometric.nn.inits import reset
from torch_geometric.utils import remove_self_loops, add_self_loops, softmax

from typing import Type, TypeVar
from torch import nn, Tensor
import torch
from torch_geometric.nn import MessagePassing, MessageNorm, BatchNorm


class EdgeConv(MessagePassing):
    def __init__(
        self,
        x_dim: int,
        edge_dim: int,
        hidden_dim: int,
        aggr: str,
        activation_fn: Type[nn.Module],
        normalization: bool,
        **kwargs
    ) -> None:
        super(EdgeConv, self).__init__(aggr=aggr, **kwargs)
        self.lin1 = torch.nn.Linear(2 * x_dim + edge_dim, hidden_dim)
        self.normalization = normalization
        self.norm = MessageNorm(learn_scale=True) if normalization else torch.nn.Identity()
        self.act = activation_fn()

    def forward(self, x: Tensor, edge_index: Tensor, edge_attr: Tensor) -> Tensor:
        """"""
        return self.propagate(edge_index, x=x, edge_attr=edge_attr, size=None)

    def message(self, x_i: Tensor, x_j: Tensor, edge_attr: Tensor) -> Tensor:
        x = torch.cat([x_i, x_j, edge_attr], dim=-1)
        h1 = self.lin1(x)
        if self.normalization:
            z = self.act(self.norm(x, h1))
        else:
            z = self.act(h1)
        return z


def get_ego_features(data: CommonRoadData) -> Tensor:
    ego_features = torch.cat([
        (data.v[V_Feature.Velocity.value] - 15.0)/20.0,
        data.v[V_Feature.Acceleration.value] / 10.0,
        torch.clip(data.v[V_Feature.YawRate.value], -1.0, 1.0),
    ], dim=-1)
    return ego_features


def get_v_node_features(data: CommonRoadData) -> Tensor:
    position_ego_frame = data.v.position_ego_frame
    node_features = torch.cat([
        position_ego_frame[:, 0].unsqueeze(1) / 50.0,
        position_ego_frame[:, 1].unsqueeze(1) / 50.0,
        (data.v[V_Feature.Velocity.value] - 15) / 20.0
    ], dim=-1)
    return node_features


def get_v_edge_features(data: CommonRoadData) -> Tensor:
    edge_features = torch.cat([
        data.v2v[V2V_Feature.RelativePositionEgo.value] / 50.0
    ], dim=-1)
    return edge_features


class VehicleGraphFeatureExtractor(BaseGeometricFeatureExtractor):
    """
    GNN feature extractor with V2V interactions.
    """

    NUM_NODE_FEATURES = 4
    NUM_EDGE_FEATURES = 2
    NUM_EGO_FEATURES = 5

    def __init__(
        self,
        observation_space: gym.Space,
        gnn_hidden_dim: int,
        gnn_layers: int,
        gnn_out_dim: int,
        concat_ego_features: bool,
        self_loops: bool,
        aggr: str,
        activation_fn: Type[nn.Module],
        normalization: bool,
        **_
    ):
        self._gnn_layers = gnn_layers
        self._gnn_hidden_dim = gnn_hidden_dim
        self._gnn_out_dim = gnn_out_dim = 0 if gnn_layers == 0 else gnn_out_dim
        self._concat_ego_features = concat_ego_features
        self._self_loops = self_loops
        self._aggr = aggr
        self._activation_fn = activation_fn
        self._normalization = normalization
        super().__init__(observation_space)

    def _build(self, observation_space: gym.Space) -> None:
        if self._gnn_layers > 0:
            self.convs = []
            for i in range(self._gnn_layers):
                x_dim = VehicleGraphFeatureExtractor.NUM_NODE_FEATURES if i == 0 else self._gnn_hidden_dim
                edge_conv = EdgeConv(
                    x_dim=x_dim,
                    edge_dim=VehicleGraphFeatureExtractor.NUM_EDGE_FEATURES,
                    hidden_dim=self._gnn_hidden_dim,
                    aggr=self._aggr,
                    activation_fn=self._activation_fn,
                    normalization=self._normalization
                )
                layer = [
                    edge_conv,
                    self._activation_fn(),
                    nn.BatchNorm1d(self._gnn_hidden_dim) if self._normalization else nn.Identity()
                ]
                self.convs.append(layer)
                # TODO use sequential
            self.embedder = nn.Linear(
                self._gnn_hidden_dim + int(self._concat_ego_features) * VehicleGraphFeatureExtractor.NUM_EGO_FEATURES,
                self._gnn_out_dim
            )
            self.embed_act = self._activation_fn()
            self.out_norm = nn.BatchNorm1d(self.output_dim) if self._normalization else nn.Identity()
            #self.ego_features_norm = BatchNorm(VehicleGraphFeatureExtractor.NUM_EGO_FEATURES) if self._normalization else nn.Identity()
            #self.x_norm = BatchNorm(VehicleGraphFeatureExtractor.NUM_NODE_FEATURES) if self._normalization else nn.Identity()
            #self.edge_attr_norm = BatchNorm(VehicleGraphFeatureExtractor.NUM_EDGE_FEATURES) if self._normalization else nn.Identity()

    @property
    def output_dim(self) -> int:
        if self._gnn_layers == 0:
            return VehicleGraphFeatureExtractor.NUM_EGO_FEATURES
        elif self._concat_ego_features:
            return self._gnn_out_dim # + VehicleGraphFeatureExtractor.NUM_EGO_FEATURES
        else:
            return self._gnn_out_dim

    def _forward(self, data: CommonRoadData) -> Tensor:
        # Converting the flattened observation dict back into a PyTorch Geometric data instance.

        #data.to(self.convs[0].w)
        # TODO hack......
        device = self.convs[0][0].lin1.weight.device
        data.to(device)

        ego_mask = data['vehicle'].is_ego_mask.bool().squeeze(-1)

        # Creating ego feature tensor
        ego_features = get_ego_features(data)[ego_mask, :]

        if not torch.isfinite(ego_features).all():
            warnings.warn(f"ego_features tensor has nan values: {ego_features} - setting to zero")
            ego_features = torch.nan_to_num(ego_features)

        if torch.any(torch.abs(ego_features) > 10.0).item():
            pass
            warnings.warn(f"ego_features contains columns with large absolute values: {ego_features}")

        if self._gnn_layers == 0:
            y = ego_features
        else:
            x_raw = get_v_node_features(data)

            # Defining edge features
            edge_attr_raw = get_v_edge_features(data)

            # Extracting edge index
            edge_index = data['vehicle', 'vehicle'].edge_index

            # Adding self-loops
            if self._self_loops:
                edge_index, edge_attr_raw = add_self_loops(
                    edge_index,
                    edge_attr_raw,
                    fill_value=torch.zeros((VehicleGraphFeatureExtractor.NUM_EDGE_FEATURES, ), device=ego_mask.device, dtype=torch.float32),
                    num_nodes=x_raw.size(0)
                )

            x = x_raw # self.x_norm(x_raw)
            edge_attr = edge_attr_raw # self.edge_attr_norm(edge_attr_raw)

            if torch.any(torch.abs(x) > 10.0).item():
                warnings.warn(f"x contains columns with large absolute values: {x}")
            if torch.any(torch.abs(edge_attr) > 10.0).item():
                warnings.warn(f"edge_attr contains columns with large absolute values: {edge_attr}")
            # Computing node encodings

            z = x
            for layer in self.convs:
                for i, step in enumerate(layer):
                    if i == 0:
                        z = step(
                            z,
                            edge_index=edge_index,
                            edge_attr=edge_attr
                        )
                    else:
                        z = step(z)

            # Extracting the node encoding for the ego vehicle
            ego_z = z[ego_mask, :]

            if not torch.isfinite(ego_z).all():
                raise ValueError("ego_z tensor has nan values")

            if self._concat_ego_features:
                # Concatenating ego encoding with ego features
                y = torch.cat([
                    ego_features,
                    ego_z
                ], dim=-1)
            else:
                y = ego_z

        # Returning tensor to be fed into policy network
        out_0 = self.embedder(y.to(self.embedder.weight.device))
        out = self.embed_act(out_0)
        out_norm = self.out_norm(out)
        return out_norm
