import argparse


def main():
    parser = argparse.ArgumentParser(description="Say hi.")
    parser.add_argument("name", help="Your name")
    args = parser.parse_args()
    print(f"Hi, my name is {args.name}")


if __name__ == "__main__":
    main()
