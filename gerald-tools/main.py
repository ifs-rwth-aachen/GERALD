import argparse
import sys

import gerald_tools


def main(p: str):
    """
    Simply plots first image and annotations
    :param p: Command line argument for GERALD dataset path
    """
    gerald = gerald_tools.GERALDDataset(p)
    im, targets, idx = gerald[0]
    gerald_tools.plot_targets_over_im(im, targets)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="Path to GERALD dataset")
    args = parser.parse_args()

    sys.exit(main(p=args.path))
