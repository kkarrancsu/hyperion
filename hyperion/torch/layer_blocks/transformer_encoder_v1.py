"""
 Copyright 2019 Johns Hopkins University  (Author: Jesus Villalba)
 Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)
"""
from __future__ import absolute_import

import torch
import torch.nn as nn

from ..layers.transformer_feedforward import *
from ..layers.attention import *

class TransformerEncoderBlockV1(nn.Module):
    """Building block for transformer encoder.

    Attributes:
      num_feats: input/output feat. dimension (aka d_model)
      self_attn: attention nn.Module or string in ['scaled-dot-prod-att-v1', 'local-scaled-dot-prod-att-v1']
      num_heads: number of heads
      feed_forward: position-wise feed-forward nn.Module or string in ['linear', 'conv1dx2', 'conv1d-linear']
      d_ff: dimension of middle layer in feed_forward block
      ff_kernel_size: kernel size for convolutional versions of ff block
      ff_dropout_rate: dropout rate for ff block
      att_context: maximum context range for local attention
      att_dropout_rate: dropout rate for attention block
      norm_before: if True, use layer norm before layers, otherwise after
      concat_after: if True, if concats attention input and output and apply linear transform, i.e.,
                             y = x + linear(concat(x, att(x)))
                    if False, y = x + att(x)
    """

    def __init__(self, num_feats, self_attn, num_heads, feed_forward, d_ff, ff_kernel_size, ff_dropout_rate=0,
                 att_context=25, att_dropout_rate=0, norm_before=True, concat_after=False):

        super(TransformerEncoderBlockV1, self).__init__()
        if isinstance(self_attn, str):
            self.self_attn = self._make_att(self_attn, num_feats, num_heads, att_context, att_dropout_rate)
        else:
            self.self_attn = self_attn

        if isinstance(feed_forward, str):
            self.feed_forward = self._make_ff(feed_forward, num_feats, d_ff, ff_kernel_size, ff_dropout_rate)
        else:
            self.feed_forward = feed_forward

        self.norm1 = nn.LayerNorm(num_feats)
        self.norm2 = nn.LayerNorm(num_feats)
        self.dropout_rate = ff_dropout_rate
        if self.dropout_rate > 0:
            self.dropout = nn.Dropout(self.dropout_rate)

        self.norm_before = norm_before
        self.concat_after = concat_after
        if self.concat_after:
            self.concat_linear = nn.Linear(num_feats + num_feats, num_feats)


    @staticmethod
    def _make_att(att_type, num_feats, num_heads, context, dropout_rate):
        """Creates multihead attention block from att_type string

        Args:
           att_type: string in ['scaled-dot-prod-att-v1', 'local-scaled-dot-prod-att-v1']
           num_feats: input/output feat. dimension (aka d_model)
           num_heads: number of heads
           dropout_rate: dropout rate for attention block

        Returns:
           Attention nn.Module
        """
        
        assert num_feats % num_heads == 0
        d_k = num_feats // num_heads

        if att_type == 'scaled-dot-prod-v1':
            return ScaledDotProdAttV1(
                num_feats, num_feats, num_heads, d_k, d_k, 
                dropout_rate, time_dim=1)

        if att_type == 'local-scaled-dot-prod-v1':
            return LocalScaledDotProdAttV1(
                num_feats, num_feats, num_heads, d_k, d_k, 
                context, dropout_rate, time_dim=1)

        
    @staticmethod
    def _make_ff(ff_type, num_feats, hid_feats, kernel_size, dropout_rate):
        """Creates position-wise feed forward block from ff_type string

        Args:
          ff_type: string in ['linear', 'conv1dx2', 'conv1d-linear']
          num_feats: input/output feat. dimension (aka d_model)
          hid_feats: dimension of middle layer in feed_forward block
          kernel_size: kernel size for convolutional versions of ff block
          dropout_rate: dropout rate for ff block
        
        Returns:
          Position-wise feed-forward nn.Module 

        """
        if ff_type == 'linear':
            return PositionwiseFeedForward(
                num_feats, hid_feats, dropout_rate, time_dim=1)

        if ff_type == 'conv1dx2':
            return Conv1dx2(
                num_feats, hid_feats, kernel_size, dropout_rate, time_dim=1)

        if ff_type == 'conv1d-linear':
            return Conv1dLinear(
                num_feats, hid_feats, kernel_size, dropout_rate, time_dim=1)



    def forward(self, x, mask=None):
        """Forward pass function

        Args:
          x: input tensor with size=(batch, time, num_feats)
          mask: mask to indicate valid time steps for x (batch, time)

        Returns:
           Tensor with output features
           Tensor with mask
        """
        residual = x
        if self.norm_before:
            x = self.norm1(x)

        x_att = self.self_attn(x, x, x, mask)
        if self.concat_after:
            x = torch.cat((x, x_att), dim=-1)
            x = self.concat_linear(x)
        else:
            x = x_att

        if self.dropout_rate > 0:
            x = self.dropout(x)

        x = residual + x
        if not self.norm_before:
            x = self.norm1(x)

        residual = x
        if self.norm_before:
            x = self.norm2(x)

        x =self.feed_forward(x)
        if self.dropout_rate > 0:
            x = self.dropout(x)

        x = residual + x
        if not self.norm_before:
            x = self.norm2(x)

        return x, mask