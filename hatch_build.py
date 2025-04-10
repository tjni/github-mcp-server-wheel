import os
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


def download_binary(version: str, platform: str, arch: str):
    bin_dir = Path("bin")
    bin_dir.mkdir(exist_ok=True)

    binary_name = "github-mcp-server"
    if platform == "win":
        binary_name += ".exe"

    target_file = bin_dir / binary_name

    platform_part: str
    ext: str

    match platform:
        case "linux":
            platform_part = "Linux"
            ext = "tar.gz"
        case "macosx":
            platform_part = "Darwin"
            ext = "tar.gz"
        case "win":
            platform_part = "Windows"
            ext = "zip"
        case _:
            raise ValueError(f"Unsupported platform: {platform}")

    url = (
        "https://github.com/github/github-mcp-server/releases/download/"
        f"v{version}/github-mcp-server_{platform_part}_{arch}.{ext}"
    )

    with urllib.request.urlopen(url) as response:
        match ext:
            case "tar.gz":
                with tarfile.open(fileobj=response, mode="r|gz") as tar:
                    found = False
                    for member in tar:
                        if member.name == binary_name:
                            found = True
                            source = tar.extractfile(member)
                            if not source:
                                raise ValueError(
                                    f"Error extracting {binary_name} from tarball"
                                )

                            with target_file.open("wb") as target:
                                shutil.copyfileobj(source, target)

                            break

                    if not found:
                        raise ValueError(f"Binary {binary_name} not found in tarball")

                target_file.chmod(0o755)
            case "zip":
                with tempfile.NamedTemporaryFile() as temp_file:
                    shutil.copyfileobj(response, temp_file)
                    temp_file_path = temp_file.name

                    with zipfile.ZipFile(temp_file_path, "r") as zip:
                        info = zip.getinfo(binary_name)
                        with zip.open(info) as source, target_file.open("wb") as target:
                            shutil.copyfileobj(source, target)


def get_tag(platform: str, arch: str) -> str:
    platform_tag: str
    match platform:
        case "linux":
            if arch == "arm64":
                arch = "aarch64"
            platform_tag = f"manylinux_2_17_{arch}.manylinux2014_{arch}"
        case "macosx":
            if arch == "arm64":
                version = "11_0"
            else:
                version = "10_12"
            platform_tag = f"macosx_{version}_{arch}"
        case "win":
            if arch == "x86_64":
                arch = "amd64"
            platform_tag = f"win_{arch}"
        case _:
            raise ValueError(f"Unsupported platform: {platform}")

    return f"py3-none-{platform_tag}"


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        plat = os.environ["PLAT"]
        arch = os.environ["ARCH"]

        download_binary(self.metadata.version, plat, arch)
        build_data["tag"] = get_tag(plat, arch)
