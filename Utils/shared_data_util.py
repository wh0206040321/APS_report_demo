import json
from pathlib import Path


class SharedDataUtil:
    # 定义共享数据文件路径
    _data_file = Path(__file__).parent / "json" / "shared_data.json"

    @classmethod
    def save_data(cls, data):
        """
        保存共享数据到 JSON 文件中
        :param data: 要保存的字典数据
        """
        try:
            with open(cls._data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            print(f"[INFO] 共享数据已保存至 {cls._data_file}")
        except Exception as e:
            print(f"[ERROR] 写入共享数据失败: {e}")

    @classmethod
    def load_data(cls):
        """
        从 JSON 文件中加载共享数据
        :return: 字典类型数据
        """
        if not cls._data_file.exists():
            print(f"[WARN] 共享数据文件不存在: {cls._data_file}")
            return {}

        try:
            with open(cls._data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"[INFO] 成功加载共享数据: {data}")
            return data
        except Exception as e:
            print(f"[ERROR] 读取共享数据失败: {e}")
            return {}

    @classmethod
    def clear_data(cls):
        """清空共享数据文件内容"""
        try:
            # 清空文件内容，不删除文件
            with open(cls._data_file, "w", encoding="utf-8") as f:
                f.write("{}")  # 写入空对象
            print(f"[INFO] 共享数据已清空")
        except Exception as e:
            print(f"[ERROR] 清空共享数据失败: {e}")
