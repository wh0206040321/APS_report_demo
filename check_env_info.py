import sys
import os
import subprocess

print("🔍 当前 Python 解释器路径：")
print(sys.executable)

print("\n📦 pip 路径：")
subprocess.call([sys.executable, "-m", "pip", "--version"])

print("\n🧪 pytest 来源：")
try:
    pytest_location = subprocess.check_output(["where", "pytest"], shell=True).decode()
    print(pytest_location.strip())
except Exception as e:
    print(f"获取失败：{e}")

print("\n💡 当前 Python 版本：")
print(sys.version)

print("\n🗂 当前虚拟环境根目录（如果有）：")
print(os.environ.get("VIRTUAL_ENV", "未启用虚拟环境"))