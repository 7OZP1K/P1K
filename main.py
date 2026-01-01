#!/usr/bin/env python3
"""
7OZP1K编程助手 vx:AE86-1w

现代化 MVC 架构：
├── config.py   - 配置常量
├── models.py   - 数据模型和持久化
├── services.py - 业务逻辑服务
├── views.py    - CustomTkinter UI
└── main.py     - 程序入口

依赖：
pip install customtkinter anthropic httpx
"""

import logging
import sys
from pathlib import Path

# 添加父目录到 sys.path，支持直接运行
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_dependencies(): 
    """检查依赖"""
    missing = []

    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    try:
        import anthropic
    except ImportError:
        missing.append("anthropic")

    try:
        import httpx
    except ImportError:
        missing.append("httpx")

    if missing:
        print("=" * 50)
        print("缺少必要的依赖库，请先安装：")
        print()
        print(f"  pip install {' '.join(missing)}")
        print()
        print("=" * 50)
        sys.exit(1)


def main():
    """主函数"""
    # 检查依赖
    check_dependencies()

    try:
        # 导入视图（依赖检查后再导入）
        try:
            from .views import MainApp
        except ImportError:
            from views import MainApp

        # 创建并运行应用
        logger.info("7OZP1K编程助手···...")
        app = MainApp()
        app.mainloop()

    except Exception as e:
        logger.exception("应用启动失败")
        print(f"\n错误: {e}")
        print("\n请检查：")
        print("1. 是否已安装所有依赖")
        print("2. Python 版本是否 >= 3.8")
        sys.exit(1)


if __name__ == "__main__":
    main()
