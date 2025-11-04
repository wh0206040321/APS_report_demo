import shutil
from pathlib import Path

source = Path("report/allure_report")
target = Path("docs")

# 清空旧报告
if target.exists():
    shutil.rmtree(target)
    print("🧹 已清空旧的 docs/ 目录")

# 复制新报告
shutil.copytree(source, target)
print(f"✅ 成功复制报告：{source} → {target}")

# 添加 .nojekyll 文件
Path(target / ".nojekyll").touch()
print("✅ 已添加 .nojekyll 文件，确保 GitHub Pages 正确构建")
