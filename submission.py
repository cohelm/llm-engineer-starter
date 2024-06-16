import argparse


def main():
    """Write the entrypoint to your submission here"""
    # TODO - import and execute your code here. Please put business logic into repo/src
    raise NotImplementedError


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path-to-case-pdf',
                        metavar='path',
                        type=str,
                        help='Path to local test case with which to run your code')
    args = parser.parse_args()
    main()
