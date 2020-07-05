import torch
import torch.nn as nn
import torch.nn.functional as F
import time


def conv3x3(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=3, stride=stride,
                     padding=(1,1))


def conv1x1(in_planes, out_planes, stride=1):
    return nn.Conv2d(in_planes, out_planes, kernel_size=1, stride=stride, bias=False)

class PokerNet(nn.Module):
    def __init__(self,filters):
        super(PokerNet, self).__init__()
        #device = torch.device("CPU")
        self.conv1 =conv3x3(113, filters)
        self.bn1 = nn.BatchNorm2d(filters)
        self.block1 = ResidualBlock(filters,filters)
        self.block2 = ResidualBlock(filters,filters)
        self.block3 = ResidualBlock(filters,filters)
        self.block4 = ResidualBlock(filters,filters)
        #self.block5 = ResidualBlock(filters,filters)
        #self.block6 = ResidualBlock(filters,filters)
        #self.block7 = ResidualBlock(filters,filters)
        #self.block8 = ResidualBlock(filters,filters)
        self.phead_convout = conv1x1(filters, filters)
        self.phead_bn = nn.BatchNorm2d(filters)
        self.phead_out = nn.Linear(filters*13*4, 52)
        self.filters = filters


    def forward(self, x):
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.block1(x)
        x = self.block2(x)
        x = self.block3(x)
        x = self.block4(x)
        #x = self.block5(x)
        #x = self.block6(x)
        #x = self.block7(x)
        #x = self.block8(x)
        phead = self.phead_convout(x)
        phead = self.phead_bn(phead)
        phead = F.relu(phead)
        phead = phead.view(-1, self.filters*13*4)  # batch_size X channel X height X width
        phead = self.phead_out(phead)

        return phead

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, filters, stride=1):
        super(ResidualBlock, self).__init__()
        self.conv1 = conv3x3(in_channels, filters, stride)
        self.bn1 = nn.BatchNorm2d(filters)
        self.relu = nn.ReLU(inplace=True)
        self.conv2 = conv3x3(filters, filters)
        self.bn2 = nn.BatchNorm2d(filters)

    def forward(self, x):
        residual = x
        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)
        out = self.conv2(out)
        out = self.bn2(out)
        out += residual
        out = self.relu(out)
        return out
