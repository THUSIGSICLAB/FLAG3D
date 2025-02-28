import mindspore
import mindspore.nn as nn

class I3DHead(nn.Cell):
    """Classification head for I3D.

    Args:
        num_classes (int): Number of classes to be classified.
        in_channels (int): Number of channels in input feature.
        loss_cls (dict): Config for building loss.
            Default: dict(type='CrossEntropyLoss')
        spatial_type (str): Pooling type in spatial dimension. Default: 'avg'.
        dropout_ratio (float): Probability of dropout layer. Default: 0.5.
        init_std (float): Std value for Initiation. Default: 0.01.
        kwargs (dict, optional): Any keyword argument to be used to initialize
            the head.
    """

    def __init__(self,
                 num_classes,
                 in_channels_head,
                 spatial_type='avg',
                 dropout_ratio=0.5,
                 init_std=0.01):
        super().__init__()

        self.in_channels = in_channels_head
        self.num_classes = num_classes
        self.spatial_type = spatial_type
        self.dropout_ratio = dropout_ratio
        self.init_std = init_std
        if self.dropout_ratio != 0:
            self.dropout = nn.Dropout(p=self.dropout_ratio)
        else:
            self.dropout = None
        self.fc_cls = nn.Dense(self.in_channels, self.num_classes,
                                weight_init='normal',
                                bias_init='zeros',
                                has_bias=True)

        if self.spatial_type == 'avg':
            # use `nn.AdaptiveAvgPool3d` to adaptively match the in_channels.
            self.avg_pool = nn.AdaptiveAvgPool3d((1, 1, 1))
        else:
            self.avg_pool = None

    # def init_weights(self):
    #     initializer = mindspore.nn.initializer.Normal(std=self.init_std)
    #     initializer(self.fc_cls.weight)
    #     if self.fc_cls.bias is not None:
    #         initializer = mindspore.nn.initializer.Constant(0)
    #         initializer(self.fc_cls.bias)

    def construct(self, x):
        """Defines the computation performed at every call.

        Args:
            x (torch.Tensor): The input data.

        Returns:
            torch.Tensor: The classification scores for input samples.
        """
        # [N, in_channels, 4, 7, 7]
        if self.avg_pool is not None:
            x = self.avg_pool(x)
        # [N, in_channels, 1, 1, 1]
        if self.dropout is not None:
            x = self.dropout(x)
        # [N, in_channels, 1, 1, 1]
        x = x.reshape([x.shape[0], self.in_channels])
        # [N, in_channels]
        cls_score = self.fc_cls(x)
        # [N, num_classes]
        return cls_score

if __name__ == "__main__":
    head = I3DHead(num_classes=60, in_channels_head=512, spatial_type='avg', dropout_ratio=0.5)
    shape = (1, 512, 50, 8, 8)
    uniformreal = mindspore.ops.UniformReal(seed=2)
    x = uniformreal(shape)
    y = head(x)
    print(y.shape) # (1, 60)