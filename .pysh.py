
# This is a sampe .pysh.py and is used when building/runniing in docker
PATH = [
    "/usr/local/bin",
    "/usr/local/sbin",
    "/usr/local/bin",
    "/usr/sbin",
    "/usr/bin",
    "/sbin",
    "/bin"
]

# PATH = "/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"


def test_func():
    print("This is a test function call")
