import argparse


def main():
    parser = argparse.ArgumentParser(description="Say hello to a name.")
    parser.add_argument("name", help="The name to greet")
    parser.add_argument("age", type=int, help="The age of the person")
    args = parser.parse_args()
    print(f"Hello, {args.name}! You are {args.age} years old.")


if __name__ == "__main__":
    main()
