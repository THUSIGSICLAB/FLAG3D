

import mindspore
import mindspore.nn as nn

from model.tsagcn_mm.gcn_head import GCNHead
from model.tsagcn_mm.aagcn import AAGCN


class AAGCN_RECOGNIZER(nn.Cell):
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
                 in_channels=3,
                 num_person = 1,
                 graph_args = dict(layout='coco', mode='stgcn_spatial'),
                 num_classes=60,
                 in_channels_head=256,
                 kernel_size = (125, 17)):
        super().__init__()

        self.backbone = AAGCN(in_channels = in_channels, num_person = num_person, graph_args = graph_args)
        self.head = GCNHead(num_classes=num_classes,
                            in_channels_head=in_channels_head,
                            kernel_size=kernel_size
                            )



    def construct(self, x):
        x = self.backbone(x)
        x = self.head(x)
        return x


if __name__ == "__main__":
    model = AAGCN_RECOGNIZER(
        in_channels=3,
        num_person = 1,
        graph_args=dict(layout='coco', mode='stgcn_spatial'),
        num_classes=60,
        in_channels_head=256,
        kernel_size=(125, 17)
    )
    # b, num_clip(double), num_keypoint(in_channel), frame, h, w
    shape = (1, 1, 1, 500, 17, 3)
    uniformreal = mindspore.ops.UniformReal(seed=2)
    x = uniformreal(shape)
    y = model(x)
    print(y.shape) # (B*M, 60)