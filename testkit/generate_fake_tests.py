import random
import string
import typing as T


def write_file() -> None:
    path = "test_" + random_str() + ".py"
    content = generate_class()
    with open(path, "w") as file:
        file.write(content)
    print("File %s created" % path)


def generate_class() -> str:
    chunks: T.List[str] = []
    chunks.append("import unittest\n\n")
    chunks.append("class Test" + random_str() + "(unittest.TestCase):")
    chunks.append(generate_methods(100))
    return "\n".join(chunks)


def generate_methods(count: int) -> str:
    chunks: T.List[str] = []
    for _ in range(count):
        chunks.append("    def test_" + random_str() + "(self):")
        chunks.append("        self.assertTrue(True)")
        chunks.append("        self.assertFalse(False)\n")
    return "\n".join(chunks)


def random_str(count=10):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(count))


if __name__ == "__main__":
    for _ in range(10):
        write_file()
