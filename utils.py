import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--learning-rate', type = float, action = 'store', default = 0.0001)
parser.add_argument('--num-epochs', type = int, action = 'store', default = 100)
parser.add_argument('--weight-decay', type = float, action = 'store', default = 0.98)
parser.add_argument('--batch-size', type = int, action = 'store', default = 32)
args = parser.parse_args()
