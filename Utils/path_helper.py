import os


def get_report_dir(*subfolders) -> str:
    """
    返回项目根目录下的 report 子目录路径，可拼接子目录。
    例如：get_report_dir("screenshots") → <根目录>/report/screenshots
    """
    current_file = os.path.abspath(__file__)
    project_root = os.path.dirname(os.path.dirname(current_file))  # 两级上跳到根目录
    report_path = os.path.join(project_root, "report", *subfolders)
    os.makedirs(report_path, exist_ok=True)
    return report_path
