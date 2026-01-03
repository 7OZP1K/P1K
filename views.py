"""
视图层 - CustomTkinter 现代化 UI
"""

import logging
import os
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from typing import Optional

import customtkinter as ctk

try:
    from .config import (
        LANGUAGE_FRAMEWORKS,
        THEMES,
        AVAILABLE_MODELS,
        DEFAULT_TEMPLATES,
        SNIPPET_CATEGORIES,
        ADMIN_PASSWORD,
        DEFAULT_PRIORITIES,
        DEFAULT_AI_WEBSITES,
    )
    from .models import (
        APIConfig,
        ProjectInfo,
        HistoryRecord,
        FavoriteRecord,
        DataManager,
    )
    from .services import (
        PromptGeneratorService,
        PyInstallerService,
        FileService,
        AIPackageAnalyzer,
    )
    from .code_system import get_code_manager, PACKAGES, FEATURES
except ImportError:
    from config import (
        LANGUAGE_FRAMEWORKS,
        THEMES,
        AVAILABLE_MODELS,
        DEFAULT_TEMPLATES,
        SNIPPET_CATEGORIES,
        ADMIN_PASSWORD,
        DEFAULT_PRIORITIES,
        DEFAULT_AI_WEBSITES,
    )
    from models import (
        APIConfig,
        ProjectInfo,
        HistoryRecord,
        FavoriteRecord,
        DataManager,
    )
    from services import (
        PromptGeneratorService,
        PyInstallerService,
        FileService,
        AIPackageAnalyzer,
    )
    from code_system import get_code_manager, PACKAGES, FEATURES

logger = logging.getLogger(__name__)


# ============================================================
#                      主应用视图
# ============================================================

class MainApp(ctk.CTk):
    """主应用程序 - 专业SaaS设计"""

    def __init__(self):
        super().__init__()

        # 管理员模式标志
        self.is_admin = False

        # 兑换码管理器
        self.code_manager = get_code_manager()

        # 加载设置
        self.settings = DataManager.load_settings()

        # 设置主题
        theme_key = self.settings.get("theme", "dark")
        self._current_theme = THEMES.get(theme_key, THEMES["dark"])
        ctk.set_appearance_mode(self._current_theme["mode"])
        ctk.set_default_color_theme(self._current_theme["color_theme"])

        # 窗口配置 - 现代化尺寸
        self.title("7OZP1K 编程助手")
        self.geometry("1440x900")
        self.minsize(1280, 720)

        # 统一配色方案 - 高端紫色主题
        self.colors = {
            # 主色 - 深邃紫色
            "primary": "#7C3AED",        # Violet 600
            "primary_hover": "#6D28D9",  # Violet 700
            "primary_light": "#A78BFA",  # Violet 400
            "primary_subtle": "#EDE9FE", # Violet 50

            # 强调色 - AI功能专用
            "accent": "#EC4899",         # Pink 500
            "accent_hover": "#DB2777",   # Pink 600

            # 功能色
            "success": "#10B981",        # Emerald 500
            "error": "#EF4444",          # Red 500
            "warning": "#F59E0B",        # Amber 500

            # 背景层次 (浅色模式)
            "bg_base": "#FAFAFA",        # 最底层
            "bg_elevated": "#FFFFFF",    # 抬升背景
            "bg_hover": "#F4F4F5",       # 悬停背景

            # 背景层次 (深色模式)
            "bg_base_dark": "#09090B",   # Zinc 950
            "bg_elevated_dark": "#18181B", # Zinc 900
            "bg_hover_dark": "#27272A",  # Zinc 800

            # 文字颜色
            "text_primary": "#18181B",   # 主文字
            "text_secondary": "#52525B", # 次要文字
            "text_muted": "#A1A1AA",     # 弱化文字
            "text_primary_dark": "#FAFAFA",
            "text_secondary_dark": "#A1A1AA",
            "text_muted_dark": "#71717A",

            # 边框
            "border": "#E4E4E7",         # Zinc 200
            "border_dark": "#27272A",    # Zinc 800

            # 兼容旧代码的别名
            "bg_light": "#FAFAFA",
            "bg_dark": "#09090B",
            "surface_light": "#FFFFFF",
            "surface_dark": "#18181B",
            "text_light": "#18181B",
            "text_dark": "#FAFAFA",
            "text_muted_light": "#71717A",
            "text_muted_dark": "#A1A1AA",
            "border_light": "#E4E4E7",
            "primary_dark": "#6D28D9",
        }

        # 初始化服务
        self.api_config = APIConfig(
            api_key=self.settings.get("api_key", ""),
            base_url=self.settings.get("base_url", "https://api.anthropic.com"),
            model=self.settings.get("model", "claude-haiku-4-5-20251001"),
        )
        self.prompt_service = PromptGeneratorService(self.api_config)
        self.ai_analyzer = AIPackageAnalyzer(self.api_config)

        # 状态变量
        self.current_prompt = ""
        self.current_project_info: Optional[ProjectInfo] = None
        self._generating = False
        self.uploaded_files: list = []
        self.conversation_pages: list = []
        self.current_page_index = 0

        # 应用专业背景
        self.configure(fg_color=(self.colors["bg_light"], self.colors["bg_dark"]))

        # 显示加载页面
        self._show_splash_screen()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _show_splash_screen(self):
        """显示启动加载页面 - 极简设计"""
        # 创建加载容器
        self.splash_frame = ctk.CTkFrame(
            self,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            corner_radius=0
        )
        self.splash_frame.pack(fill="both", expand=True)

        # 中心内容
        center_container = ctk.CTkFrame(
            self.splash_frame,
            fg_color="transparent"
        )
        center_container.place(relx=0.5, rely=0.5, anchor="center")

        # Logo区域 - 渐变圆形
        logo_frame = ctk.CTkFrame(
            center_container,
            width=120,
            height=120,
            corner_radius=60,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            border_width=0
        )
        logo_frame.pack(pady=(0, 35))
        logo_frame.pack_propagate(False)

        # Logo文字 - 修正为7OZP1K
        ctk.CTkLabel(
            logo_frame,
            text="7OZP1K",
            font=ctk.CTkFont(size=21, weight="bold", family="Arial"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 应用标题
        ctk.CTkLabel(
            center_container,
            text="7OZP1K 编程助手vx:AE86-1w",
            font=ctk.CTkFont(size=32, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(pady=(0, 10))

        # 副标题
        ctk.CTkLabel(
            center_container,
            text="AI智能开发工具",
            font=ctk.CTkFont(size=14, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        ).pack(pady=(0, 45))

        # 进度条容器 - 极简设计
        progress_container = ctk.CTkFrame(
            center_container,
            fg_color="transparent",
            width=380,
            height=60
        )
        progress_container.pack(pady=(0, 20))
        progress_container.pack_propagate(False)

        # 加载文字
        self.loading_label = ctk.CTkLabel(
            progress_container,
            text="正在初始化...",
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        )
        self.loading_label.pack(pady=(0, 10))

        # 进度条 - 渐变色
        self.progress_bar = ctk.CTkProgressBar(
            progress_container,
            width=380,
            height=8,
            corner_radius=4,
            fg_color=(self.colors["border_light"], self.colors["border_dark"]),
            progress_color=(self.colors["primary"], self.colors["primary_light"]),
            border_width=0
        )
        self.progress_bar.pack()
        self.progress_bar.set(0)

        # 版本信息
        ctk.CTkLabel(
            center_container,
            text="v3.0",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        ).pack(pady=(25, 0))

        # 开始加载动画
        self._animate_loading()

    def _animate_loading(self):
        """加载动画"""
        steps = [
            (0.2, "检查环境配置..."),
            (0.4, "加载AI服务..."),
            (0.6, "初始化界面..."),
            (0.8, "准备就绪..."),
            (1.0, "启动完成！")
        ]

        def update_progress(step_index):
            if step_index < len(steps):
                progress, text = steps[step_index]
                self.progress_bar.set(progress)
                self.loading_label.configure(text=text)
                self.after(400, lambda: update_progress(step_index + 1))
            else:
                # 加载完成，显示主界面或激活界面
                self.after(300, self._finish_loading)

        update_progress(0)

    def _finish_loading(self):
        """完成加载，进入主界面"""
        # 销毁加载页面
        if hasattr(self, 'splash_frame'):
            self.splash_frame.destroy()

        # 检查是否已激活或管理员模式
        if not self.code_manager.get_unlocked_features() and not self.is_admin:
            # 未激活，显示兑换码输入界面
            self._show_activation_screen()
        else:
            # 已激活或管理员模式，构建主界面
            self._build_ui()

    def _show_activation_screen(self):
        """显示激活界面 - 极简紫色主题"""
        # 清空窗口
        for widget in self.winfo_children():
            widget.destroy()

        self.geometry("680x800")
        self.minsize(680, 800)

        # 背景容器
        container = ctk.CTkFrame(
            self,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            corner_radius=0
        )
        container.pack(fill="both", expand=True)

        # 主卡片
        main_card = ctk.CTkFrame(
            container,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=20,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            width=540,
            height=720
        )
        main_card.place(relx=0.5, rely=0.5, anchor="center")
        main_card.pack_propagate(False)

        # Logo - 紫色渐变圆形
        logo_container = ctk.CTkFrame(
            main_card,
            width=90,
            height=90,
            corner_radius=45,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            border_width=0
        )
        logo_container.pack(pady=(50, 25))
        logo_container.pack_propagate(False)

        ctk.CTkLabel(
            logo_container,
            text="🔐",
            font=ctk.CTkFont(size=48)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 标题
        ctk.CTkLabel(
            main_card,
            text="7OZP1K 编程助手",
            font=ctk.CTkFont(size=28, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(pady=(0, 8))

        # 副标题
        ctk.CTkLabel(
            main_card,
            text="请输入兑换码激活软件功能",
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"]),
        ).pack(pady=(0, 35))

        # 兑换码输入框
        self.activation_code_var = ctk.StringVar()
        code_entry = ctk.CTkEntry(
            main_card,
            textvariable=self.activation_code_var,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(family="Consolas", size=15, weight="bold"),
            width=400,
            height=52,
            justify="center",
            corner_radius=10,
            border_width=2,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            fg_color=(self.colors["surface_light"], self.colors["bg_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            placeholder_text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        )
        code_entry.pack(pady=(0, 15))
        code_entry.bind("<Return>", lambda e: self._activate())

        # 消息标签
        self.activation_msg = ctk.CTkLabel(
            main_card,
            text="",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
        )
        self.activation_msg.pack(pady=(0, 20))

        # 激活按钮 - 紫色渐变
        activate_btn = ctk.CTkButton(
            main_card,
            text="立即激活",
            font=ctk.CTkFont(size=15, weight="bold", family="Microsoft YaHei UI"),
            width=240,
            height=48,
            corner_radius=10,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
            text_color="white",
            command=self._activate,
        )
        activate_btn.pack(pady=(0, 30))

        # 套餐说明
        info_card = ctk.CTkFrame(
            main_card,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            corner_radius=12,
            border_width=0
        )
        info_card.pack(pady=(0, 0), padx=30, fill="x")

        ctk.CTkLabel(
            info_card,
            text="📦 套餐说明",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(pady=(15, 12))

        # 套餐列表
        packages = [
            ("基础版", "提示词生成"),
            ("专业版", "提示词生成 • 复制跳转 • PyInstaller打包 • VIP视频解析")
        ]

        for title, desc in packages:
            pkg_row = ctk.CTkFrame(info_card, fg_color="transparent")
            pkg_row.pack(fill="x", padx=25, pady=3)

            ctk.CTkLabel(
                pkg_row,
                text="•",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=(self.colors["primary"], self.colors["primary_light"])
            ).pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                pkg_row,
                text=f"{title}：",
                font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
                text_color=(self.colors["text_light"], self.colors["text_dark"])
            ).pack(side="left")

            ctk.CTkLabel(
                pkg_row,
                text=desc,
                font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
                text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
            ).pack(side="left", padx=(5, 0))

        ctk.CTkFrame(info_card, fg_color="transparent", height=12).pack()

        # 分隔线
        ctk.CTkFrame(
            main_card,
            height=1,
            fg_color=(self.colors["border_light"], self.colors["border_dark"])
        ).pack(fill="x", padx=40, pady=(25, 20))

        # 管理员入口 - 更显眼的设计
        admin_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        admin_frame.pack(pady=(0, 10))

        ctk.CTkLabel(
            admin_frame,
            text="管理员?",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(0, 8))

        admin_btn = ctk.CTkButton(
            admin_frame,
            text="🔧 进入管理员模式",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["primary"], self.colors["primary"]),
            text_color=(self.colors["primary"], self.colors["primary_light"]),
            width=180,
            height=40,
            corner_radius=10,
            border_width=2,
            border_color=(self.colors["primary"], self.colors["primary"]),
            command=self._admin_login_from_activation,
        )
        admin_btn.pack(side="left")

        code_entry.focus()

    def _admin_login_from_activation(self):
        """从激活界面进入管理员模式 - 极简设计"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("管理员登录")
        dialog.geometry("440x300")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 440) // 2
        y = (dialog.winfo_screenheight() - 300) // 2
        dialog.geometry(f"+{x}+{y}")

        # 设置背景
        dialog.configure(fg_color=(self.colors["bg_light"], self.colors["bg_dark"]))

        # 主卡片
        frame = ctk.CTkFrame(
            dialog,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=16,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"])
        )
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # 图标
        icon_frame = ctk.CTkFrame(
            frame,
            width=60,
            height=60,
            corner_radius=30,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            border_width=0
        )
        icon_frame.pack(pady=(30, 20))
        icon_frame.pack_propagate(False)

        ctk.CTkLabel(
            icon_frame,
            text="🔧",
            font=ctk.CTkFont(size=30)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 标题
        ctk.CTkLabel(
            frame,
            text="管理员登录",
            font=ctk.CTkFont(size=20, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(pady=(0, 20))

        # 密码输入
        pwd_var = ctk.StringVar()
        pwd_entry = ctk.CTkEntry(
            frame,
            textvariable=pwd_var,
            placeholder_text="请输入管理员密码",
            show="●",
            width=320,
            height=46,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            corner_radius=10,
            border_width=2,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            fg_color=(self.colors["surface_light"], self.colors["bg_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        )
        pwd_entry.pack(pady=(0, 10))

        # 错误消息
        msg_label = ctk.CTkLabel(
            frame,
            text="",
            text_color=(self.colors["error"], self.colors["error"]),
            font=ctk.CTkFont(size=11, weight="bold", family="Microsoft YaHei UI")
        )
        msg_label.pack(pady=(0, 15))

        def do_login():
            if pwd_var.get() == ADMIN_PASSWORD:
                self.is_admin = True
                dialog.destroy()
                self._enter_main_app()
            else:
                msg_label.configure(text="❌ 密码错误，请重试")
                pwd_var.set("")
                pwd_entry.focus()

        pwd_entry.bind("<Return>", lambda e: do_login())

        # 登录按钮
        ctk.CTkButton(
            frame,
            text="登录",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            width=220,
            height=44,
            corner_radius=10,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
            command=do_login,
        ).pack(pady=(0, 25))

        pwd_entry.focus()

    def _activate(self):
        """激活软件"""
        code = self.activation_code_var.get().strip()

        if not code:
            self.activation_msg.configure(text="请输入兑换码", text_color="red")
            return

        success, message = self.code_manager.redeem_code(code)

        if success:
            self.activation_msg.configure(text=message, text_color="green")
            # 延迟后进入主界面
            self.after(1500, self._enter_main_app)
        else:
            self.activation_msg.configure(text=message, text_color="red")

    def _enter_main_app(self):
        """进入主应用界面"""
        # 清空激活界面
        for widget in self.winfo_children():
            widget.destroy()

        # 恢复窗口大小
        self.geometry("1400x900")
        self.minsize(1200, 800)

        # 构建主界面
        self._build_ui()

    def _build_ui(self):
        """构建用户界面 - 全新单页导航布局"""
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)  # 内容区可扩展

        # 导航状态
        self.current_nav = "new_project"
        self.content_frames = {}

        # Row 0: 顶部栏 (Logo + 标题 + 工具按钮)
        self._build_header()

        # Row 1: 导航栏 (单行功能导航)
        self._build_navigation()

        # Row 2: 内容区域 (根据导航切换)
        self._build_content_area()

        # Row 3: 状态栏
        self._build_statusbar()

    # ----------------------------------------------------------
    #                       顶部栏 (Header)
    # ----------------------------------------------------------

    def _build_header(self):
        """构建顶部栏 - 极简高端设计"""
        header = ctk.CTkFrame(
            self,
            height=64,
            fg_color="transparent",
            corner_radius=0
        )
        header.grid(row=0, column=0, sticky="ew", padx=32, pady=(20, 0))
        header.grid_columnconfigure(1, weight=1)
        header.grid_propagate(False)

        # 左侧 - 品牌区
        brand_section = ctk.CTkFrame(header, fg_color="transparent")
        brand_section.grid(row=0, column=0, sticky="w")

        # Logo 紫色圆形
        logo_circle = ctk.CTkFrame(
            brand_section,
            width=36,
            height=36,
            corner_radius=18,
            fg_color=self.colors["primary"],
            border_width=0
        )
        logo_circle.pack(side="left", padx=(0, 12))
        logo_circle.pack_propagate(False)

        ctk.CTkLabel(
            logo_circle,
            text="7",
            font=ctk.CTkFont(size=14, weight="bold", family="Arial"),
            text_color="white"
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 标题
        ctk.CTkLabel(
            brand_section,
            text="7OZP1K 编程助手",
            font=ctk.CTkFont(size=18, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        # 右侧控件区 - Ghost风格按钮
        tools_section = ctk.CTkFrame(header, fg_color="transparent")
        tools_section.grid(row=0, column=2, sticky="e")

        # API状态指示
        self.api_status_label = ctk.CTkLabel(
            tools_section,
            text="",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
        )
        self.api_status_label.pack(side="left", padx=(0, 16))

        # 设置按钮 - Ghost风格
        ctk.CTkButton(
            tools_section,
            text="⚙",
            font=ctk.CTkFont(size=18),
            width=36,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            command=self._show_settings,
        ).pack(side="left", padx=2)

        # 主题切换 - Ghost风格
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        theme_btn = ctk.CTkButton(
            tools_section,
            text="◐",
            font=ctk.CTkFont(size=18),
            width=36,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            command=self._toggle_theme,
        )
        theme_btn.pack(side="left", padx=2)

        # 帮助按钮 - Ghost风格
        ctk.CTkButton(
            tools_section,
            text="?",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=36,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            command=self._show_help,
        ).pack(side="left", padx=2)

        # 更新API状态
        self._update_api_status()

    def _toggle_theme(self):
        """切换主题"""
        current = self.theme_var.get()
        themes = list(THEMES.keys())
        idx = themes.index(current) if current in themes else 0
        next_theme = themes[(idx + 1) % len(themes)]
        self.theme_var.set(next_theme)
        self._on_theme_changed(next_theme)

    # ----------------------------------------------------------
    #                       导航栏 (Navigation)
    # ----------------------------------------------------------

    def _build_navigation(self):
        """构建单行导航栏"""
        nav_container = ctk.CTkFrame(
            self,
            height=48,
            fg_color="transparent",
            corner_radius=0
        )
        nav_container.grid(row=1, column=0, sticky="ew", padx=32, pady=(16, 0))
        nav_container.grid_propagate(False)

        # 导航项目配置
        self.nav_items = [
            ("新建项目", "new_project"),
            ("模板库", "templates"),
            ("历史记录", "history"),
            ("生成结果", "output"),
            ("打包工具", "packager"),
            ("工具箱", "toolbox"),
        ]

        self.nav_buttons = {}

        for label, nav_id in self.nav_items:
            btn_container = ctk.CTkFrame(nav_container, fg_color="transparent")
            btn_container.pack(side="left", padx=(0, 8))

            # 导航按钮
            btn = ctk.CTkButton(
                btn_container,
                text=label,
                font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
                height=40,
                corner_radius=0,
                fg_color="transparent",
                hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
                text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
                command=lambda nid=nav_id: self._switch_content(nid),
            )
            btn.pack(side="top")

            # 下划线指示器
            indicator = ctk.CTkFrame(
                btn_container,
                height=2,
                fg_color="transparent",
                corner_radius=0
            )
            indicator.pack(side="top", fill="x", padx=8)

            self.nav_buttons[nav_id] = {
                "button": btn,
                "indicator": indicator
            }

        # 设置初始选中状态
        self._update_nav_styles()

    def _update_nav_styles(self):
        """更新导航按钮样式"""
        for nav_id, widgets in self.nav_buttons.items():
            btn = widgets["button"]
            indicator = widgets["indicator"]

            if nav_id == self.current_nav:
                # 选中状态
                btn.configure(
                    text_color=(self.colors["primary"], self.colors["primary_light"]),
                    font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI")
                )
                indicator.configure(fg_color=self.colors["primary"])
            else:
                # 未选中状态
                btn.configure(
                    text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
                    font=ctk.CTkFont(size=13, family="Microsoft YaHei UI")
                )
                indicator.configure(fg_color="transparent")

    def _switch_content(self, nav_id: str):
        """切换内容区域"""
        if nav_id == self.current_nav:
            return

        # 隐藏当前内容
        if self.current_nav in self.content_frames:
            self.content_frames[self.current_nav].grid_forget()

        # 显示新内容
        self.current_nav = nav_id
        if nav_id in self.content_frames:
            self.content_frames[nav_id].grid(row=0, column=0, sticky="nsew")

        # 更新导航样式
        self._update_nav_styles()

        # 更新状态栏
        nav_labels = dict(self.nav_items)
        self.status_label.configure(text=f"当前: {nav_labels.get(nav_id, '')}")

    # ----------------------------------------------------------
    #                       内容区域 (Content Area)
    # ----------------------------------------------------------

    def _build_content_area(self):
        """构建内容区域容器"""
        # 内容区容器
        self.content_container = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )
        self.content_container.grid(row=2, column=0, sticky="nsew", padx=32, pady=16)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # 构建所有内容页面
        self._build_new_project_content()
        self._build_templates_content()
        self._build_history_content()
        self._build_output_content()
        self._build_packager_content()
        self._build_toolbox_content()

        # 显示默认页面
        self.content_frames["new_project"].grid(row=0, column=0, sticky="nsew")

    def _build_new_project_content(self):
        """构建新建项目内容页 - UI-UX-PRO-MAX 高级风格"""
        frame = ctk.CTkFrame(
            self.content_container,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.content_frames["new_project"] = frame

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # ============ 页面标题 - 渐变风格 ============
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, sticky="ew", padx=24, pady=(24, 16))
        header.grid_columnconfigure(1, weight=1)

        title_group = ctk.CTkFrame(header, fg_color="transparent")
        title_group.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_group,
            text="创建新项目",
            font=ctk.CTkFont(size=22, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        # 状态徽章
        self.project_status_badge = ctk.CTkLabel(
            title_group,
            text="就绪",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color="white",
            fg_color=self.colors["success"],
            corner_radius=10,
            padx=10,
            pady=2
        )
        self.project_status_badge.pack(side="left", padx=(12, 0))

        # API 状态指示
        self.api_status_label = ctk.CTkLabel(
            header,
            text="",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.api_status_label.grid(row=0, column=1, sticky="e")

        # 左侧 - 项目配置
        left_panel = ctk.CTkFrame(frame, fg_color="transparent")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(24, 12), pady=(0, 24))
        left_panel.grid_columnconfigure(0, weight=1)
        left_panel.grid_rowconfigure(2, weight=1)

        # ============ 项目配置区 - Bento Grid 风格 ============
        config_card = ctk.CTkFrame(
            left_panel,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        config_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        config_card.grid_columnconfigure(1, weight=1)

        # 配置标题带图标
        config_header = ctk.CTkFrame(config_card, fg_color="transparent")
        config_header.grid(row=0, column=0, columnspan=4, sticky="ew", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            config_header,
            text="⚙",
            font=ctk.CTkFont(size=16),
            text_color=self.colors["primary"]
        ).pack(side="left")

        ctk.CTkLabel(
            config_header,
            text="项目配置",
            font=ctk.CTkFont(size=15, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(8, 0))

        # 分隔线
        ctk.CTkFrame(
            config_card,
            height=1,
            fg_color=(self.colors["border"], self.colors["border_dark"])
        ).grid(row=1, column=0, columnspan=4, sticky="ew", padx=16, pady=(0, 12))

        # ====== 语言选择行 - 紧凑布局 ======
        lang_row = ctk.CTkFrame(config_card, fg_color="transparent")
        lang_row.grid(row=2, column=0, columnspan=4, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            lang_row,
            text="编程语言",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).pack(side="left")

        # 语言图标芯片
        self.lang_icon_label = ctk.CTkLabel(
            lang_row,
            text="Py",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="white",
            fg_color=self.colors["primary"],
            corner_radius=6,
            width=32,
            height=32
        )
        self.lang_icon_label.pack(side="left", padx=(12, 6))

        self.language_var = ctk.StringVar(value=self.settings.get("last_language", "Python"))
        self.language_menu = ctk.CTkOptionMenu(
            lang_row,
            values=list(LANGUAGE_FRAMEWORKS.keys()),
            variable=self.language_var,
            command=self._on_language_changed,
            width=130,
            height=34,
            corner_radius=8,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=self.colors["primary"],
            button_hover_color=self.colors["primary_hover"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI")
        )
        self.language_menu.pack(side="left")

        # ====== 框架选择行 ======
        fw_row = ctk.CTkFrame(config_card, fg_color="transparent")
        fw_row.grid(row=3, column=0, columnspan=4, sticky="ew", padx=16, pady=8)
        fw_row.grid_columnconfigure(1, weight=1)
        fw_row.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(
            fw_row,
            text="框架类别",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=0, column=0, sticky="w")

        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(
            fw_row,
            values=[""],
            variable=self.category_var,
            command=self._on_category_changed,
            width=140,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")
        )
        self.category_menu.grid(row=0, column=1, sticky="w", padx=(12, 24))

        ctk.CTkLabel(
            fw_row,
            text="具体框架",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=0, column=2, sticky="w")

        self.framework_var = ctk.StringVar()
        self.framework_menu = ctk.CTkOptionMenu(
            fw_row,
            values=[""],
            variable=self.framework_var,
            width=140,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")
        )
        self.framework_menu.grid(row=0, column=3, sticky="w", padx=(12, 0))

        # ====== 开发优先级 - 芯片式选择 ======
        priority_row = ctk.CTkFrame(config_card, fg_color="transparent")
        priority_row.grid(row=4, column=0, columnspan=4, sticky="ew", padx=16, pady=(8, 16))

        ctk.CTkLabel(
            priority_row,
            text="开发优先级",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).pack(side="left")

        priority_chips = ctk.CTkFrame(priority_row, fg_color="transparent")
        priority_chips.pack(side="right")

        self.priority_var = ctk.StringVar(value="功能完整")
        priorities = [
            ("快速原型", "⚡"),
            ("功能完整", "✓"),
            ("生产就绪", "🚀"),
            ("最佳实践", "⭐")
        ]

        self.priority_buttons = {}
        for p_text, p_icon in priorities:
            btn = ctk.CTkButton(
                priority_chips,
                text=f"{p_icon} {p_text}",
                font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
                height=30,
                width=90,
                corner_radius=15,
                fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]) if p_text != "功能完整" else self.colors["primary"],
                hover_color=self.colors["primary_hover"],
                text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]) if p_text != "功能完整" else "white",
                command=lambda t=p_text: self._select_priority(t)
            )
            btn.pack(side="left", padx=3)
            self.priority_buttons[p_text] = btn

        # 初始化框架选项
        self._on_language_changed(self.language_var.get())

        # ============ 文件上传区 - 虚线边框风格 ============
        upload_card = ctk.CTkFrame(
            left_panel,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        upload_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        upload_card.grid_columnconfigure(0, weight=1)

        upload_header = ctk.CTkFrame(upload_card, fg_color="transparent")
        upload_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            upload_header,
            text="📎",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")

        ctk.CTkLabel(
            upload_header,
            text="附加文件",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(6, 0))

        ctk.CTkLabel(
            upload_header,
            text="可选",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            corner_radius=4,
            padx=6,
            pady=1
        ).pack(side="left", padx=(8, 0))

        btn_group = ctk.CTkFrame(upload_header, fg_color="transparent")
        btn_group.pack(side="right")

        ctk.CTkButton(
            btn_group,
            text="清空",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=60,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            command=self._clear_files,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_group,
            text="选择文件",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=85,
            height=28,
            corner_radius=6,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._select_files,
        ).pack(side="left")

        # 拖拽区域 - 虚线效果
        self.drop_frame = ctk.CTkFrame(
            upload_card,
            height=70,
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            corner_radius=10,
            border_width=2,
            border_color=(self.colors["border"], self.colors["border_dark"]),
        )
        self.drop_frame.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))
        self.drop_frame.grid_propagate(False)

        drop_content = ctk.CTkFrame(self.drop_frame, fg_color="transparent")
        drop_content.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            drop_content,
            text="📂",
            font=ctk.CTkFont(size=20)
        ).pack()

        self.drop_label = ctk.CTkLabel(
            drop_content,
            text="点击选择或拖拽文件到此处",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
        )
        self.drop_label.pack()

        self.drop_frame.bind("<Button-1>", lambda e: self._select_files())
        drop_content.bind("<Button-1>", lambda e: self._select_files())

        # 文件列表
        self.files_listbox = ctk.CTkTextbox(
            upload_card,
            height=45,
            font=ctk.CTkFont(size=10, family="Consolas"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=6
        )
        self.files_listbox.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 16))
        self.files_listbox.insert("1.0", "暂无文件")
        self.files_listbox.configure(state="disabled")

        # 尝试启用拖拽功能
        self._setup_drag_drop()

        # ============ 项目描述区 - 带智能提示 ============
        desc_card = ctk.CTkFrame(
            left_panel,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        desc_card.grid(row=2, column=0, sticky="nsew")
        desc_card.grid_columnconfigure(0, weight=1)
        desc_card.grid_rowconfigure(1, weight=1)

        desc_header = ctk.CTkFrame(desc_card, fg_color="transparent")
        desc_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))

        ctk.CTkLabel(
            desc_header,
            text="✏",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")

        ctk.CTkLabel(
            desc_header,
            text="项目描述",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(6, 0))

        self.char_count_label = ctk.CTkLabel(
            desc_header,
            text="0 字",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            corner_radius=4,
            padx=8,
            pady=2
        )
        self.char_count_label.pack(side="right")

        # AI优化按钮 - 渐变效果
        self.optimize_btn = ctk.CTkButton(
            desc_header,
            text="✨ AI优化",
            font=ctk.CTkFont(size=11, weight="bold", family="Microsoft YaHei UI"),
            width=85,
            height=28,
            corner_radius=14,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._optimize_input,
        )
        self.optimize_btn.pack(side="right", padx=(0, 12))

        self.idea_textbox = ctk.CTkTextbox(
            desc_card,
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            wrap="word",
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=8
        )
        self.idea_textbox.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        self.idea_textbox.bind("<KeyRelease>", self._update_char_count)

        # ============ 右侧 - 操作区 ============
        right_panel = ctk.CTkFrame(frame, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(12, 24), pady=(0, 24))
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        # ====== 生成按钮区 - 突出显示 ======
        action_card = ctk.CTkFrame(
            right_panel,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        action_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))

        action_header = ctk.CTkFrame(action_card, fg_color="transparent")
        action_header.pack(fill="x", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            action_header,
            text="🚀",
            font=ctk.CTkFont(size=16)
        ).pack(side="left")

        ctk.CTkLabel(
            action_header,
            text="生成提示词",
            font=ctk.CTkFont(size=15, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(8, 0))

        self.generate_btn = ctk.CTkButton(
            action_card,
            text="开始生成",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            height=48,
            corner_radius=10,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._generate_prompt,
        )
        self.generate_btn.pack(fill="x", padx=16, pady=(0, 12))

        self.progress_label = ctk.CTkLabel(
            action_card,
            text="",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
        )
        self.progress_label.pack(anchor="w", padx=16, pady=(0, 16))

        # ====== 快捷操作卡片 - 图标卡片风格 ======
        quick_card = ctk.CTkFrame(
            right_panel,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        quick_card.grid(row=1, column=0, sticky="nsew")
        quick_card.grid_columnconfigure(0, weight=1)

        quick_header = ctk.CTkFrame(quick_card, fg_color="transparent")
        quick_header.pack(fill="x", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            quick_header,
            text="⚡",
            font=ctk.CTkFont(size=14)
        ).pack(side="left")

        ctk.CTkLabel(
            quick_header,
            text="快捷操作",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(6, 0))

        # 快捷操作按钮 - 带图标
        quick_actions = [
            ("📚", "模板库", lambda: self._switch_content("templates")),
            ("📜", "历史记录", lambda: self._switch_content("history")),
            ("⚙", "打开设置", self._show_settings),
            ("🛠", "工具箱", lambda: self._switch_content("toolbox")),
        ]

        for icon, text, cmd in quick_actions:
            btn_frame = ctk.CTkFrame(quick_card, fg_color="transparent")
            btn_frame.pack(fill="x", padx=16, pady=3)

            btn = ctk.CTkButton(
                btn_frame,
                text="",
                width=0,
                height=40,
                corner_radius=8,
                fg_color="transparent",
                hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
                border_width=1,
                border_color=(self.colors["border"], self.colors["border_dark"]),
                command=cmd,
            )
            btn.pack(fill="x")

            # 内部布局
            inner = ctk.CTkFrame(btn, fg_color="transparent")
            inner.place(relx=0.02, rely=0.5, anchor="w")

            ctk.CTkLabel(
                inner,
                text=icon,
                font=ctk.CTkFont(size=14)
            ).pack(side="left", padx=(8, 0))

            ctk.CTkLabel(
                inner,
                text=text,
                font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
                text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
            ).pack(side="left", padx=(10, 0))

            # 箭头指示
            ctk.CTkLabel(
                btn,
                text="›",
                font=ctk.CTkFont(size=16),
                text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
            ).place(relx=0.95, rely=0.5, anchor="e")

        ctk.CTkFrame(quick_card, fg_color="transparent", height=16).pack()

    def _select_priority(self, priority: str):
        """选择开发优先级 - 更新芯片按钮样式"""
        self.priority_var.set(priority)
        for p_text, btn in self.priority_buttons.items():
            if p_text == priority:
                btn.configure(
                    fg_color=self.colors["primary"],
                    text_color="white"
                )
            else:
                btn.configure(
                    fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
                    text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
                )

    def _build_templates_content(self):
        """构建模板库内容页 - UI-UX-PRO-MAX 高级风格"""
        frame = ctk.CTkFrame(
            self.content_container,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.content_frames["templates"] = frame

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # 页面标题 - 带徽章
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        header.grid_columnconfigure(1, weight=1)

        title_group = ctk.CTkFrame(header, fg_color="transparent")
        title_group.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_group,
            text="📚",
            font=ctk.CTkFont(size=20)
        ).pack(side="left")

        ctk.CTkLabel(
            title_group,
            text="模板库",
            font=ctk.CTkFont(size=22, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(10, 0))

        # 模板数量徽章
        self.template_count_badge = ctk.CTkLabel(
            title_group,
            text="0 个模板",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color="white",
            fg_color=self.colors["primary"],
            corner_radius=10,
            padx=10,
            pady=2
        )
        self.template_count_badge.pack(side="left", padx=(12, 0))

        # 操作按钮组
        btn_group = ctk.CTkFrame(header, fg_color="transparent")
        btn_group.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            btn_group,
            text="🔄 刷新",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=80,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._refresh_templates,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_group,
            text="➕ 添加模板",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            width=110,
            height=34,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._add_template_dialog,
        ).pack(side="left")

        # 模板列表容器 - 带空状态提示
        self.templates_scroll_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.templates_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.templates_scroll_frame.grid_columnconfigure(0, weight=1)

        self._refresh_templates()

    def _build_history_content(self):
        """构建历史记录内容页 - UI-UX-PRO-MAX 高级风格"""
        frame = ctk.CTkFrame(
            self.content_container,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.content_frames["history"] = frame

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # 页面标题 - 带徽章
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        header.grid_columnconfigure(1, weight=1)

        title_group = ctk.CTkFrame(header, fg_color="transparent")
        title_group.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_group,
            text="📜",
            font=ctk.CTkFont(size=20)
        ).pack(side="left")

        ctk.CTkLabel(
            title_group,
            text="历史记录",
            font=ctk.CTkFont(size=22, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(10, 0))

        # 记录数量徽章
        self.history_count_badge = ctk.CTkLabel(
            title_group,
            text="0 条记录",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color="white",
            fg_color=self.colors["accent"],
            corner_radius=10,
            padx=10,
            pady=2
        )
        self.history_count_badge.pack(side="left", padx=(12, 0))

        # 操作按钮组
        btn_group = ctk.CTkFrame(header, fg_color="transparent")
        btn_group.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(
            btn_group,
            text="🔄 刷新",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=80,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._refresh_history,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_group,
            text="🗑 清空全部",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=100,
            height=34,
            corner_radius=8,
            fg_color=self.colors["error"],
            hover_color="#DC2626",
            command=self._clear_history,
        ).pack(side="left")

        # 历史列表容器
        self.history_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            corner_radius=0
        )
        self.history_frame.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.history_frame.grid_columnconfigure(0, weight=1)

        self._refresh_history()

    def _build_output_content(self):
        """构建生成结果内容页"""
        frame = ctk.CTkFrame(
            self.content_container,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.content_frames["output"] = frame

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # 页面标题和工具栏
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        header.grid_columnconfigure(1, weight=1)

        # 翻页控件
        page_frame = ctk.CTkFrame(header, fg_color="transparent")
        page_frame.grid(row=0, column=0, sticky="w")

        self.prev_page_btn = ctk.CTkButton(
            page_frame,
            text="◀",
            width=32,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            command=self._prev_page,
            state="disabled",
        )
        self.prev_page_btn.pack(side="left", padx=2)

        self.page_label = ctk.CTkLabel(
            page_frame,
            text="0 / 0",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        )
        self.page_label.pack(side="left", padx=8)

        self.next_page_btn = ctk.CTkButton(
            page_frame,
            text="▶",
            width=32,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            command=self._next_page,
            state="disabled",
        )
        self.next_page_btn.pack(side="left", padx=2)

        self.page_title_label = ctk.CTkLabel(
            page_frame,
            text="",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        )
        self.page_title_label.pack(side="left", padx=16)

        # 右侧按钮
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(
            btn_frame,
            text="复制",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=60,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._copy_prompt,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="收藏",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=60,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._add_favorite,
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="导出",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=60,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._export_prompt,
        ).pack(side="left", padx=2)

        # 复制并跳转
        self.jump_website_var = ctk.StringVar(value="跳转")
        self.jump_website_menu = ctk.CTkOptionMenu(
            btn_frame,
            values=self._get_website_names(),
            variable=self.jump_website_var,
            command=self._copy_and_jump,
            width=90,
            height=32,
            corner_radius=6,
            fg_color=self.colors["success"],
            button_color=self.colors["success"],
            button_hover_color="#059669",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI")
        )
        self.jump_website_menu.pack(side="left", padx=2)
        self.jump_website_menu.set("跳转")

        ctk.CTkButton(
            btn_frame,
            text="清空",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=60,
            height=32,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            command=self._clear_pages,
        ).pack(side="left", padx=2)

        # 输出文本框
        self.output_textbox = ctk.CTkTextbox(
            frame,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            state="disabled",
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=8
        )
        self.output_textbox.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 12))

        # 底部统计和追问
        bottom_frame = ctk.CTkFrame(frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=24, pady=(0, 24))
        bottom_frame.grid_columnconfigure(1, weight=1)

        # 统计信息
        stats_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        stats_frame.grid(row=0, column=0, sticky="w")

        self.word_count_label = ctk.CTkLabel(
            stats_frame,
            text="字数: 0",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.word_count_label.pack(side="left", padx=(0, 16))

        self.line_count_label = ctk.CTkLabel(
            stats_frame,
            text="行数: 0",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.line_count_label.pack(side="left")

        # 追问输入
        followup_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        followup_frame.grid(row=0, column=1, sticky="e")

        self.followup_entry = ctk.CTkEntry(
            followup_frame,
            placeholder_text="输入追问内容...",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=300,
            height=32,
            corner_radius=6,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.followup_entry.pack(side="left", padx=(0, 8))
        self.followup_entry.bind("<Return>", lambda e: self._send_followup())

        self.followup_btn = ctk.CTkButton(
            followup_frame,
            text="发送",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=60,
            height=32,
            corner_radius=6,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._send_followup,
        )
        self.followup_btn.pack(side="left")

    def _build_packager_content(self):
        """构建打包工具内容页"""
        frame = ctk.CTkFrame(
            self.content_container,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.content_frames["packager"] = frame

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # 页面标题
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="Python 打包工具",
            font=ctk.CTkFont(size=20, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).grid(row=0, column=0, sticky="w")

        # 模式切换
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            mode_frame,
            text="模式:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(0, 8))

        self.packager_mode_var = ctk.StringVar(value="beginner")
        self.packager_mode_menu = ctk.CTkSegmentedButton(
            mode_frame,
            values=["零基础用户", "独立开发"],
            variable=self.packager_mode_var,
            command=self._on_packager_mode_changed,
            selected_color=self.colors["primary"],
            selected_hover_color=self.colors["primary_hover"],
            unselected_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            unselected_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI")
        )
        self.packager_mode_menu.pack(side="left", padx=8)
        self.packager_mode_menu.set("零基础用户")

        self.pyinstaller_status = ctk.CTkLabel(
            mode_frame,
            text="检查中...",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
        )
        self.pyinstaller_status.pack(side="left", padx=10)

        # 主内容容器
        self.packager_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.packager_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.packager_container.grid_columnconfigure(0, weight=1)
        self.packager_container.grid_rowconfigure(0, weight=1)

        # 构建两种模式界面
        self._build_beginner_mode()
        self._build_developer_mode()

        # 默认显示零基础模式
        self._show_beginner_mode()

        # 检查 PyInstaller 状态
        self._check_pyinstaller()

    def _build_toolbox_content(self):
        """构建工具箱内容页 - Bento Grid 高级风格"""
        # 主框架
        frame = ctk.CTkFrame(
            self.content_container,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        self.content_frames["toolbox"] = frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # ============ 顶部导航栏 ============
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(20, 12))
        header.grid_columnconfigure(1, weight=1)

        # 标题
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_frame,
            text="工具箱",
            font=ctk.CTkFont(size=22, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        # 工具标签指示
        self.toolbox_tag = ctk.CTkLabel(
            title_frame,
            text="多功能工具集",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            corner_radius=6,
            padx=8,
            pady=2
        )
        self.toolbox_tag.pack(side="left", padx=(12, 0))

        # 分段按钮切换工具
        self.toolbox_segmented = ctk.CTkSegmentedButton(
            header,
            values=["视频解析", "系统配置"],
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            corner_radius=8,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            selected_color=self.colors["primary"],
            selected_hover_color=self.colors["primary_hover"],
            unselected_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            unselected_hover_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            command=self._switch_toolbox_tab
        )
        self.toolbox_segmented.grid(row=0, column=1, sticky="e")
        self.toolbox_segmented.set("视频解析")

        # ============ 工具内容容器 ============
        self.toolbox_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.toolbox_container.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        self.toolbox_container.grid_columnconfigure(0, weight=1)
        self.toolbox_container.grid_rowconfigure(0, weight=1)

        # 工具子页面
        self.toolbox_pages = {}
        self.current_toolbox_tab = "video_parser"

        # 构建视频解析工具
        self._build_video_parser_tool()

        # 构建配置管理工具
        self._build_config_tool()

        # 默认显示视频解析
        self.toolbox_pages["video_parser"].grid(row=0, column=0, sticky="nsew")

    def _switch_toolbox_tab(self, value: str):
        """切换工具箱标签页"""
        tab_map = {
            "视频解析": "video_parser",
            "系统配置": "config"
        }
        new_tab = tab_map.get(value, "video_parser")

        if new_tab == self.current_toolbox_tab:
            return

        # 隐藏当前页面
        if self.current_toolbox_tab in self.toolbox_pages:
            self.toolbox_pages[self.current_toolbox_tab].grid_forget()

        # 显示新页面
        self.current_toolbox_tab = new_tab
        if new_tab in self.toolbox_pages:
            self.toolbox_pages[new_tab].grid(row=0, column=0, sticky="nsew")

        # 检查视频解析权限
        if new_tab == "video_parser":
            self._check_video_parser_access()

    def _build_video_parser_tool(self):
        """构建视频解析工具 - 简约高级风格"""
        # 使用全局背景色
        bg_primary = (self.colors["bg_light"], self.colors["bg_dark"])
        bg_secondary = (self.colors["surface_light"], self.colors["surface_dark"])
        bg_tertiary = (self.colors["bg_hover"], self.colors["bg_hover_dark"])
        text_primary = (self.colors["text_light"], self.colors["text_dark"])
        text_secondary = (self.colors["text_secondary"], self.colors["text_secondary_dark"])
        text_muted = (self.colors["text_muted_light"], self.colors["text_muted_dark"])
        border_color = (self.colors["border"], self.colors["border_dark"])
        accent = self.colors["primary"]
        accent_hover = self.colors["primary_hover"]

        # 视频解析页面框架 - 放入工具箱容器
        frame = ctk.CTkFrame(
            self.toolbox_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.toolbox_pages["video_parser"] = frame
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # ============ 解锁检查容器 ============
        self.video_unlock_frame = ctk.CTkFrame(frame, fg_color=bg_secondary, corner_radius=16)
        self.video_unlock_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=24, pady=24)
        self.video_unlock_frame.grid_columnconfigure(0, weight=1)
        self.video_unlock_frame.grid_rowconfigure(0, weight=1)

        unlock_content = ctk.CTkFrame(self.video_unlock_frame, fg_color="transparent")
        unlock_content.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkFrame(unlock_content, width=80, height=80, corner_radius=40, fg_color=bg_tertiary, border_width=2, border_color=accent).pack(pady=(0, 20))
        ctk.CTkLabel(unlock_content, text="PRO专属功能", font=ctk.CTkFont(size=20, weight="bold"), text_color=text_primary).pack(pady=(0, 8))
        ctk.CTkLabel(unlock_content, text="请联系管理员获取兑换码", font=ctk.CTkFont(size=12), text_color=text_muted).pack(pady=(0, 20))
        ctk.CTkButton(unlock_content, text="前往配置", width=140, height=42, corner_radius=10, fg_color=accent, hover_color=accent_hover, command=lambda: self._goto_config_in_toolbox()).pack()

        # ============ 主功能内容 ============
        self.video_content_frame = ctk.CTkFrame(frame, fg_color="transparent")
        self.video_content_frame.grid_columnconfigure(0, weight=1)
        self.video_content_frame.grid_rowconfigure(1, weight=1)

        # ====== 输入区 ======
        input_card = ctk.CTkFrame(self.video_content_frame, fg_color=bg_secondary, corner_radius=12)
        input_card.grid(row=0, column=0, sticky="ew", padx=24, pady=(24, 16))
        input_card.grid_columnconfigure(0, weight=1)

        input_inner = ctk.CTkFrame(input_card, fg_color="transparent")
        input_inner.pack(fill="x", padx=20, pady=16)
        input_inner.grid_columnconfigure(0, weight=1)

        self.video_url_entry = ctk.CTkEntry(
            input_inner, placeholder_text="粘贴视频链接 (腾讯/爱奇艺/优酷/B站/芒果TV/M3U8)",
            height=48, corner_radius=10, font=ctk.CTkFont(size=13),
            fg_color=bg_tertiary, border_color=border_color, text_color=text_primary,
            placeholder_text_color=text_muted, border_width=1
        )
        self.video_url_entry.pack(side="left", fill="x", expand=True, padx=(0, 12))
        self.video_url_entry.bind("<Return>", lambda e: self._parse_and_play())
        self.video_url_entry.bind("<KeyRelease>", self._on_url_input)

        self.parse_btn = ctk.CTkButton(
            input_inner, text="解析播放", width=120, height=48, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold"), fg_color=accent, hover_color=accent_hover,
            command=self._parse_and_play
        )
        self.parse_btn.pack(side="right")

        # ====== 视频信息面板 ======
        info_card = ctk.CTkFrame(self.video_content_frame, fg_color=bg_secondary, corner_radius=12)
        info_card.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 16))
        info_card.grid_columnconfigure(1, weight=1)
        info_card.grid_rowconfigure(0, weight=1)

        # 封面区域 (左侧)
        self.cover_container = ctk.CTkFrame(info_card, width=320, height=180, fg_color=bg_tertiary, corner_radius=10)
        self.cover_container.grid(row=0, column=0, padx=20, pady=20, sticky="nw")
        self.cover_container.grid_propagate(False)

        self.cover_image_label = ctk.CTkLabel(self.cover_container, text="", fg_color="transparent")
        self.cover_image_label.place(relx=0.5, rely=0.5, anchor="center")

        self.cover_placeholder = ctk.CTkLabel(
            self.cover_container, text="等待解析...",
            font=ctk.CTkFont(size=13), text_color=text_muted
        )
        self.cover_placeholder.place(relx=0.5, rely=0.5, anchor="center")

        # 信息区域 (右侧)
        info_right = ctk.CTkFrame(info_card, fg_color="transparent")
        info_right.grid(row=0, column=1, sticky="nsew", padx=(0, 20), pady=20)
        info_right.grid_columnconfigure(0, weight=1)

        # 标题行
        title_row = ctk.CTkFrame(info_right, fg_color="transparent")
        title_row.pack(fill="x", pady=(0, 12))

        self.video_title = ctk.CTkLabel(
            title_row, text="粘贴链接开始解析",
            font=ctk.CTkFont(size=18, weight="bold"), text_color=text_primary,
            anchor="w", wraplength=450
        )
        self.video_title.pack(side="left", fill="x", expand=True)

        self.vip_tag = ctk.CTkLabel(
            title_row, text="VIP", font=ctk.CTkFont(size=10, weight="bold"),
            fg_color=self.colors["warning"], text_color="#000", corner_radius=4, width=40, height=20
        )
        self.vip_tag.pack(side="right", padx=(8, 0))
        self.vip_tag.pack_forget()

        # 平台 + 时长
        meta_row = ctk.CTkFrame(info_right, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 16))

        self.platform_tag = ctk.CTkLabel(
            meta_row, text="", font=ctk.CTkFont(size=11),
            fg_color=accent, text_color="#fff", corner_radius=4, height=22
        )
        self.platform_tag.pack(side="left")
        self.platform_tag.pack_forget()

        self.duration_label = ctk.CTkLabel(
            meta_row, text="", font=ctk.CTkFont(size=11), text_color=text_muted
        )
        self.duration_label.pack(side="left", padx=(12, 0))

        # 描述
        self.desc_label = ctk.CTkLabel(
            info_right, text="支持平台: 腾讯视频 / 爱奇艺 / 优酷 / 哔哩哔哩 / 芒果TV / M3U8直链",
            font=ctk.CTkFont(size=12), text_color=text_muted, anchor="w", wraplength=450, justify="left"
        )
        self.desc_label.pack(fill="x", pady=(0, 16))

        # 剧集选择区
        ep_frame = ctk.CTkFrame(info_right, fg_color="transparent")
        ep_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(ep_frame, text="选集", font=ctk.CTkFont(size=12, weight="bold"), text_color=text_secondary).pack(side="left")
        self.ep_count_label = ctk.CTkLabel(ep_frame, text="", font=ctk.CTkFont(size=11), text_color=text_muted)
        self.ep_count_label.pack(side="left", padx=(8, 0))

        # 剧集按钮滚动区
        self.ep_scroll = ctk.CTkScrollableFrame(
            info_right, height=50, fg_color=bg_tertiary, corner_radius=8,
            orientation="horizontal"
        )
        self.ep_scroll.pack(fill="x")
        self.ep_buttons = []
        self.episodes_data = []
        self._current_ep_index = 0

        # 底部操作栏
        action_bar = ctk.CTkFrame(info_right, fg_color="transparent")
        action_bar.pack(fill="x", pady=(16, 0))

        self.prev_ep_btn = ctk.CTkButton(
            action_bar, text="◀ 上一集", width=90, height=36, corner_radius=8,
            fg_color=bg_tertiary, hover_color=border_color, text_color=text_primary,
            font=ctk.CTkFont(size=11), command=self._prev_ep, state="disabled"
        )
        self.prev_ep_btn.pack(side="left", padx=(0, 8))

        self.next_ep_btn = ctk.CTkButton(
            action_bar, text="下一集 ▶", width=90, height=36, corner_radius=8,
            fg_color=accent, hover_color=accent_hover,
            font=ctk.CTkFont(size=11, weight="bold"), command=self._next_ep, state="disabled"
        )
        self.next_ep_btn.pack(side="left")

        # 状态
        self.status_label = ctk.CTkLabel(
            action_bar, text="就绪", font=ctk.CTkFont(size=11), text_color=text_muted
        )
        self.status_label.pack(side="right")

        # 初始化状态
        self._video_info = None
        self._parse_api = "https://jx.m3u8.tv/jiexi/?url="
        self._cover_image = None  # 保持引用

    # ====== 视频解析核心方法 ======

    def _on_url_input(self, event=None):
        """URL输入时实时识别平台"""
        url = self.video_url_entry.get().strip()
        if not url:
            self.platform_tag.pack_forget()
            return

        platform = self._identify_platform(url)
        if platform:
            self.platform_tag.configure(text=f" {platform['name']} ", fg_color=platform['color'])
            self.platform_tag.pack(side="left")
        else:
            self.platform_tag.pack_forget()

    def _identify_platform(self, url: str) -> dict:
        """识别视频平台"""
        platforms = {
            "v.qq.com": {"name": "腾讯视频", "color": "#FF6A00", "key": "tencent"},
            "iqiyi.com": {"name": "爱奇艺", "color": "#00BE06", "key": "iqiyi"},
            "youku.com": {"name": "优酷", "color": "#1A9FFF", "key": "youku"},
            "bilibili.com": {"name": "哔哩哔哩", "color": "#FB7299", "key": "bilibili"},
            "b23.tv": {"name": "哔哩哔哩", "color": "#FB7299", "key": "bilibili"},
            "mgtv.com": {"name": "芒果TV", "color": "#FF7F00", "key": "mgtv"},
            "sohu.com": {"name": "搜狐视频", "color": "#FF6600", "key": "sohu"},
            ".m3u8": {"name": "M3U8", "color": self.colors["primary"], "key": "m3u8"},
        }
        url_lower = url.lower()
        for domain, info in platforms.items():
            if domain in url_lower:
                return info
        return None

    def _parse_and_play(self):
        """解析并自动播放"""
        if not self.is_admin and not self.code_manager.is_feature_unlocked("video_parser"):
            self._show_message("权限不足", "此功能需要PRO版本")
            return

        url = self.video_url_entry.get().strip()
        if not url:
            self._set_status("请输入视频链接", "warning")
            return

        if not url.startswith(("http://", "https://")):
            url = "https://" + url
            self.video_url_entry.delete(0, "end")
            self.video_url_entry.insert(0, url)

        self._set_status("正在解析...", "info")
        self.parse_btn.configure(state="disabled", text="解析中...")

        # 重置封面
        self.cover_placeholder.configure(text="加载中...")
        self.cover_placeholder.place(relx=0.5, rely=0.5, anchor="center")
        self.cover_image_label.configure(image=None)

        # 异步获取视频信息
        threading.Thread(target=self._fetch_video_info, args=(url,), daemon=True).start()

    def _fetch_video_info(self, url: str):
        """获取视频信息（异步）"""
        try:
            import requests
            from bs4 import BeautifulSoup
            import re
            import json

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.encoding = 'utf-8'
            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # 提取标题
            title = ""
            meta_title = soup.find("meta", property="og:title")
            if meta_title:
                title = meta_title.get("content", "")
            if not title:
                title_tag = soup.find("title")
                if title_tag:
                    title = title_tag.get_text().strip()
                    for suffix in ["_腾讯视频", "-腾讯视频", "| 腾讯视频", "_高清在线观看", "-爱奇艺", "_哔哩哔哩", " - 哔哩哔哩"]:
                        title = title.replace(suffix, "").strip()

            # 提取封面 - 多种方式尝试
            cover_url = ""
            # 1. og:image
            meta_image = soup.find("meta", property="og:image")
            if meta_image and meta_image.get("content"):
                cover_url = meta_image["content"]
            # 2. itemprop image
            if not cover_url:
                item_image = soup.find("meta", itemprop="image")
                if item_image and item_image.get("content"):
                    cover_url = item_image["content"]
            # 3. video poster
            if not cover_url:
                video_tag = soup.find("video")
                if video_tag and video_tag.get("poster"):
                    cover_url = video_tag["poster"]
            # 4. JSON中的cover
            if not cover_url:
                cover_match = re.search(r'"cover"\s*:\s*"(https?://[^"]+)"', html)
                if cover_match:
                    cover_url = cover_match.group(1)
            # 5. pic_url
            if not cover_url:
                pic_match = re.search(r'"pic(?:_url)?"\s*:\s*"(https?://[^"]+)"', html)
                if pic_match:
                    cover_url = pic_match.group(1)

            # 检查VIP
            is_vip = any(kw in html for kw in ["VIP", "会员", "付费", "用券", "vip-icon", "pay-mark"])

            # 提取时长
            duration = ""
            meta_duration = soup.find("meta", property="video:duration")
            if meta_duration:
                try:
                    seconds = int(meta_duration.get("content", 0))
                    if seconds > 0:
                        mins, secs = divmod(seconds, 60)
                        hours, mins = divmod(mins, 60)
                        if hours > 0:
                            duration = f"{hours}:{mins:02d}:{secs:02d}"
                        else:
                            duration = f"{mins}:{secs:02d}"
                except:
                    pass

            # 提取剧集 - 真正获取每集URL
            platform = self._identify_platform(url)
            episodes = self._extract_episodes_real(html, url, platform)

            # 更新UI
            self.after(0, lambda: self._update_video_ui({
                "url": url,
                "title": title or "未知标题",
                "cover_url": cover_url,
                "is_vip": is_vip,
                "duration": duration,
                "episodes": episodes
            }))

        except Exception as e:
            self.after(0, lambda: self._on_parse_error(str(e), url))

    def _extract_episodes_real(self, html: str, base_url: str, platform: dict) -> list:
        """真正提取每集的独立URL"""
        import re
        import json

        episodes = []
        platform_key = platform.get("key", "") if platform else ""

        # 提取cover_id (腾讯视频)
        cover_match = re.search(r'/x/cover/([a-zA-Z0-9]+)', base_url)
        cover_id = cover_match.group(1) if cover_match else None

        # 腾讯视频
        if platform_key == "tencent":
            patterns = [
                r'"nomark_episode_list"\s*:\s*(\[[\s\S]*?\])\s*,\s*"',
                r'"episode_list"\s*:\s*(\[[\s\S]*?\])\s*,',
            ]
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    try:
                        ep_json = self._fix_json_array(match.group(1))
                        data = json.loads(ep_json)
                        for i, ep in enumerate(data[:60]):
                            if isinstance(ep, dict):
                                vid = ep.get('vid') or ep.get('V') or ep.get('video_id', '')
                                ep_title = ep.get('title') or ep.get('play_title') or f"第{i+1}集"
                                if vid:
                                    if cover_id:
                                        ep_url = f"https://v.qq.com/x/cover/{cover_id}/{vid}.html"
                                    else:
                                        ep_url = f"https://v.qq.com/x/page/{vid}.html"
                                    episodes.append({"url": ep_url, "title": str(ep_title)})
                        if episodes:
                            return episodes
                    except:
                        continue

        # 哔哩哔哩
        elif platform_key == "bilibili":
            # 番剧
            patterns = [
                r'"episodes"\s*:\s*(\[[\s\S]*?\])\s*,\s*"(?:section|activity|positive)',
                r'"epList"\s*:\s*(\[[\s\S]*?\])',
            ]
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    try:
                        ep_json = self._fix_json_array(match.group(1))
                        data = json.loads(ep_json)
                        for ep in data[:60]:
                            ep_id = ep.get('id') or ep.get('ep_id') or ep.get('epid', '')
                            share_url = ep.get('share_url') or ep.get('link', '')
                            ep_title = ep.get('long_title') or ep.get('title') or ''
                            index = ep.get('title') or ep.get('index', '')
                            if ep_id:
                                ep_url = share_url if share_url else f"https://www.bilibili.com/bangumi/play/ep{ep_id}"
                                display = f"第{index}集 {ep_title}".strip() if index else (ep_title or f"第{len(episodes)+1}集")
                                episodes.append({"url": ep_url, "title": display})
                        if episodes:
                            return episodes
                    except:
                        continue

            # 分P视频
            page_match = re.search(r'"pages"\s*:\s*(\[[\s\S]*?\])', html)
            if page_match:
                try:
                    bv_match = re.search(r'/(BV[a-zA-Z0-9]+)', base_url)
                    bvid = bv_match.group(1) if bv_match else None
                    if bvid:
                        pages = json.loads(self._fix_json_array(page_match.group(1)))
                        for page in pages[:60]:
                            page_num = page.get('page', len(episodes) + 1)
                            part_title = page.get('part', f"P{page_num}")
                            ep_url = f"https://www.bilibili.com/video/{bvid}?p={page_num}"
                            episodes.append({"url": ep_url, "title": f"P{page_num} {part_title}"})
                        if episodes:
                            return episodes
                except:
                    pass

        # 爱奇艺
        elif platform_key == "iqiyi":
            patterns = [
                r'"episodeList"\s*:\s*(\[[\s\S]*?\])\s*,',
                r'"videoList"\s*:\s*(\[[\s\S]*?\])\s*,',
            ]
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    try:
                        data = json.loads(self._fix_json_array(match.group(1)))
                        for ep in data[:60]:
                            play_url = ep.get('playUrl') or ep.get('url', '')
                            ep_title = ep.get('name') or ep.get('title') or f"第{len(episodes)+1}集"
                            if play_url and play_url.startswith('http'):
                                episodes.append({"url": play_url, "title": str(ep_title)})
                        if episodes:
                            return episodes
                    except:
                        continue

        # 优酷
        elif platform_key == "youku":
            patterns = [r'"videos"\s*:\s*(\[[\s\S]*?\])\s*,']
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    try:
                        data = json.loads(self._fix_json_array(match.group(1)))
                        for ep in data[:60]:
                            link = ep.get('link') or ep.get('url', '')
                            ep_title = ep.get('title') or ep.get('name', '') or f"第{len(episodes)+1}集"
                            if link:
                                ep_url = link if link.startswith('http') else f"https:{link}"
                                episodes.append({"url": ep_url, "title": str(ep_title)})
                        if episodes:
                            return episodes
                    except:
                        continue

        # 芒果TV
        elif platform_key == "mgtv":
            patterns = [r'"list"\s*:\s*(\[[\s\S]*?\])\s*,\s*"(?:next|total)']
            for pattern in patterns:
                match = re.search(pattern, html)
                if match:
                    try:
                        data = json.loads(self._fix_json_array(match.group(1)))
                        for ep in data[:60]:
                            url_path = ep.get('url', '')
                            ep_title = ep.get('t1') or ep.get('title', '') or f"第{len(episodes)+1}集"
                            if url_path:
                                if url_path.startswith('/'):
                                    ep_url = f"https://www.mgtv.com{url_path}"
                                elif url_path.startswith('http'):
                                    ep_url = url_path
                                else:
                                    continue
                                episodes.append({"url": ep_url, "title": str(ep_title)})
                        if episodes:
                            return episodes
                    except:
                        continue

        return episodes

    def _fix_json_array(self, json_str: str) -> str:
        """修复可能被截断的JSON数组"""
        bracket_count = 0
        in_string = False
        escape_next = False

        for i, char in enumerate(json_str):
            if escape_next:
                escape_next = False
                continue
            if char == '\\':
                escape_next = True
                continue
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == '[':
                bracket_count += 1
            elif char == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    return json_str[:i+1]

        return json_str

    def _update_video_ui(self, info: dict):
        """更新视频信息UI"""
        self._video_info = info
        url = info["url"]

        # 更新标题
        self.video_title.configure(text=info["title"])

        # VIP标签
        if info["is_vip"]:
            self.vip_tag.pack(side="right", padx=(8, 0))
        else:
            self.vip_tag.pack_forget()

        # 时长
        if info["duration"]:
            self.duration_label.configure(text=f"时长: {info['duration']}")
        else:
            self.duration_label.configure(text="")

        # 描述
        self.desc_label.configure(text="")

        # 加载封面
        if info["cover_url"]:
            threading.Thread(target=self._load_cover_image, args=(info["cover_url"],), daemon=True).start()
        else:
            self.cover_placeholder.configure(text="无封面")

        # 更新剧集
        self._update_episodes(info["episodes"])

        # 恢复按钮
        self.parse_btn.configure(state="normal", text="解析播放")
        self._set_status("解析成功", "success")

        # 自动打开播放
        parse_url = f"{self._parse_api}{url}"
        try:
            webbrowser.open(parse_url)
        except Exception as e:
            self._set_status(f"打开失败: {e}", "error")

    def _on_parse_error(self, error: str, url: str):
        """解析出错时仍然尝试播放"""
        self.parse_btn.configure(state="normal", text="解析播放")
        self._set_status("直接播放中...", "info")
        self.cover_placeholder.configure(text="无封面")

        # 即使获取信息失败，也尝试播放
        parse_url = f"{self._parse_api}{url}"
        try:
            webbrowser.open(parse_url)
            self.video_title.configure(text="正在播放...")
        except Exception as e:
            self._set_status(f"播放失败: {e}", "error")

    def _load_cover_image(self, cover_url: str):
        """加载封面图片"""
        try:
            import requests
            from PIL import Image
            import io

            # 处理URL
            if cover_url.startswith("//"):
                cover_url = "https:" + cover_url

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Referer": "https://v.qq.com/"
            }

            response = requests.get(cover_url, headers=headers, timeout=10)
            if response.status_code == 200:
                image_data = io.BytesIO(response.content)
                pil_image = Image.open(image_data)

                # 保持比例缩放
                orig_w, orig_h = pil_image.size
                target_w, target_h = 320, 180
                ratio = min(target_w / orig_w, target_h / orig_h)
                new_w, new_h = int(orig_w * ratio), int(orig_h * ratio)
                pil_image = pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)

                ctk_image = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_w, new_h))
                self.after(0, lambda: self._set_cover(ctk_image))
        except Exception as e:
            self.after(0, lambda: self.cover_placeholder.configure(text="封面加载失败"))

    def _set_cover(self, image):
        """设置封面图片"""
        self._cover_image = image  # 保持引用防止被回收
        self.cover_placeholder.place_forget()
        self.cover_image_label.configure(image=image)

    def _update_episodes(self, episodes: list):
        """更新剧集按钮"""
        # 清空旧按钮
        for btn in self.ep_buttons:
            btn.destroy()
        self.ep_buttons.clear()
        self.episodes_data = episodes
        self._current_ep_index = 0

        if not episodes:
            self.ep_count_label.configure(text="单集")
            self.prev_ep_btn.configure(state="disabled")
            self.next_ep_btn.configure(state="disabled")
            return

        self.ep_count_label.configure(text=f"共{len(episodes)}集")

        bg_tertiary = (self.colors["bg_hover"], self.colors["bg_hover_dark"])
        accent = self.colors["primary"]

        for i, ep in enumerate(episodes):
            is_current = (i == 0)
            btn = ctk.CTkButton(
                self.ep_scroll,
                text=str(i + 1),
                width=40, height=36,
                corner_radius=6,
                fg_color=accent if is_current else bg_tertiary,
                hover_color=self.colors["primary_hover"] if is_current else self.colors["border"],
                font=ctk.CTkFont(size=12, weight="bold" if is_current else "normal"),
                command=lambda idx=i: self._select_episode(idx)
            )
            btn.pack(side="left", padx=3, pady=6)
            self.ep_buttons.append(btn)

        # 启用上下集按钮
        self.prev_ep_btn.configure(state="disabled")
        self.next_ep_btn.configure(state="normal" if len(episodes) > 1 else "disabled")

    def _select_episode(self, index: int):
        """选择剧集并播放对应URL"""
        if not self.episodes_data or index < 0 or index >= len(self.episodes_data):
            return

        # 更新按钮样式
        bg_tertiary = (self.colors["bg_hover"], self.colors["bg_hover_dark"])
        accent = self.colors["primary"]

        for i, btn in enumerate(self.ep_buttons):
            is_current = (i == index)
            btn.configure(
                fg_color=accent if is_current else bg_tertiary,
                font=ctk.CTkFont(size=12, weight="bold" if is_current else "normal")
            )

        self._current_ep_index = index

        # 更新上下集按钮
        self.prev_ep_btn.configure(state="normal" if index > 0 else "disabled")
        self.next_ep_btn.configure(state="normal" if index < len(self.episodes_data) - 1 else "disabled")

        # 播放该集 - 使用该集的独立URL
        ep = self.episodes_data[index]
        ep_url = ep.get("url", "")
        ep_title = ep.get("title", f"第{index+1}集")

        self._set_status(f"播放: {ep_title}", "info")
        self.video_title.configure(text=ep_title)

        if ep_url:
            parse_url = f"{self._parse_api}{ep_url}"
            try:
                webbrowser.open(parse_url)
            except Exception as e:
                self._set_status(f"打开失败: {e}", "error")

    def _prev_ep(self):
        """上一集"""
        if self._current_ep_index > 0:
            self._select_episode(self._current_ep_index - 1)

    def _next_ep(self):
        """下一集"""
        if self._current_ep_index < len(self.episodes_data) - 1:
            self._select_episode(self._current_ep_index + 1)

    def _set_status(self, text: str, status_type: str = "info"):
        """设置状态"""
        colors = {
            "info": (self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            "success": (self.colors["success"], self.colors["success"]),
            "warning": (self.colors["warning"], self.colors["warning"]),
            "error": (self.colors["error"], self.colors["error"]),
        }
        self.status_label.configure(text=text, text_color=colors.get(status_type, colors["info"]))


    def _check_video_parser_access(self):
        """检查视频解析功能访问权限"""
        if self.is_admin or self.code_manager.is_feature_unlocked("video_parser"):
            self.video_unlock_frame.grid_forget()
            self.video_content_frame.grid(row=0, column=0, sticky="nsew", columnspan=2)
            return True
        else:
            self.video_content_frame.grid_forget()
            self.video_unlock_frame.grid(row=0, column=0, sticky="nsew")
            return False

    def _goto_config_in_toolbox(self):
        """跳转到工具箱中的配置页面"""
        self.toolbox_segmented.set("系统配置")
        self._switch_toolbox_tab("系统配置")

    def _build_config_tool(self):
        """构建配置管理工具"""
        # 配置页面框架 - 放入工具箱容器
        frame = ctk.CTkFrame(
            self.toolbox_container,
            fg_color="transparent",
            corner_radius=0
        )
        self.toolbox_pages["config"] = frame

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # 页面标题
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=24, pady=(16, 12))

        ctk.CTkLabel(
            header,
            text="系统配置",
            font=ctk.CTkFont(size=18, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        self.config_status_label = ctk.CTkLabel(
            header,
            text="未解锁",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=self.colors["error"],
        )
        self.config_status_label.pack(side="left", padx=16)

        # 配置解锁状态
        self._config_unlocked = False

        # 主容器
        self.config_container = ctk.CTkFrame(frame, fg_color="transparent")
        self.config_container.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        self.config_container.grid_columnconfigure(0, weight=1)
        self.config_container.grid_rowconfigure(0, weight=1)

        # 解锁界面
        self.unlock_frame = ctk.CTkFrame(
            self.config_container,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10
        )
        self.unlock_frame.grid(row=0, column=0, sticky="nsew")
        self.unlock_frame.grid_columnconfigure(0, weight=1)

        unlock_content = ctk.CTkFrame(self.unlock_frame, fg_color="transparent")
        unlock_content.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            unlock_content,
            text="需要管理员密码",
            font=ctk.CTkFont(size=16, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(pady=(0, 16))

        pwd_frame = ctk.CTkFrame(unlock_content, fg_color="transparent")
        pwd_frame.pack(pady=8)

        self.config_pwd_entry = ctk.CTkEntry(
            pwd_frame,
            show="●",
            width=200,
            height=36,
            corner_radius=8,
            placeholder_text="输入密码",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.config_pwd_entry.pack(side="left", padx=(0, 8))
        self.config_pwd_entry.bind("<Return>", lambda e: self._unlock_config())

        ctk.CTkButton(
            pwd_frame,
            text="解锁",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._unlock_config,
        ).pack(side="left")

        # 配置内容区域（初始隐藏）
        self.config_scroll = ctk.CTkScrollableFrame(
            self.config_container,
            fg_color="transparent"
        )
        self.config_scroll.grid_columnconfigure(0, weight=1)

        # 构建配置选项卡片
        self._build_config_cards()

    def _build_config_cards(self):
        """构建配置选项卡片"""
        # 1. 添加编程语言
        lang_card = ctk.CTkFrame(
            self.config_scroll,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10
        )
        lang_card.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        lang_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            lang_card,
            text="添加编程语言",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            lang_card,
            text="语言名称",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=1, column=0, sticky="w", padx=16, pady=8)

        self.new_lang_entry = ctk.CTkEntry(
            lang_card,
            placeholder_text="如: Kotlin",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.new_lang_entry.grid(row=1, column=1, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            lang_card,
            text="添加",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._add_language,
        ).grid(row=1, column=2, padx=16, pady=(8, 16))

        # 2. 添加框架类别
        cat_card = ctk.CTkFrame(
            self.config_scroll,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10
        )
        cat_card.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        cat_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cat_card,
            text="添加框架类别",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            cat_card,
            text="选择语言",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=1, column=0, sticky="w", padx=16, pady=8)

        self.cat_lang_var = ctk.StringVar()
        self.cat_lang_menu = ctk.CTkOptionMenu(
            cat_card,
            values=list(DataManager.get_all_languages().keys()),
            variable=self.cat_lang_var,
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"])
        )
        self.cat_lang_menu.grid(row=1, column=1, sticky="w", padx=8, pady=8)

        ctk.CTkLabel(
            cat_card,
            text="类别名称",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=2, column=0, sticky="w", padx=16, pady=8)

        self.new_cat_entry = ctk.CTkEntry(
            cat_card,
            placeholder_text="如: 游戏开发",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.new_cat_entry.grid(row=2, column=1, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            cat_card,
            text="添加",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._add_category,
        ).grid(row=2, column=2, padx=16, pady=(8, 16))

        # 3. 添加具体框架
        fw_card = ctk.CTkFrame(
            self.config_scroll,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10
        )
        fw_card.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        fw_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            fw_card,
            text="添加具体框架",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(16, 12))

        ctk.CTkLabel(
            fw_card,
            text="选择语言",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=1, column=0, sticky="w", padx=16, pady=8)

        self.fw_lang_var = ctk.StringVar()
        self.fw_lang_menu = ctk.CTkOptionMenu(
            fw_card,
            values=list(DataManager.get_all_languages().keys()),
            variable=self.fw_lang_var,
            command=self._on_fw_lang_changed,
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"])
        )
        self.fw_lang_menu.grid(row=1, column=1, sticky="w", padx=8, pady=8)

        ctk.CTkLabel(
            fw_card,
            text="选择类别",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=2, column=0, sticky="w", padx=16, pady=8)

        self.fw_cat_var = ctk.StringVar()
        self.fw_cat_menu = ctk.CTkOptionMenu(
            fw_card,
            values=[""],
            variable=self.fw_cat_var,
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"])
        )
        self.fw_cat_menu.grid(row=2, column=1, sticky="w", padx=8, pady=8)

        ctk.CTkLabel(
            fw_card,
            text="框架名称",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=3, column=0, sticky="w", padx=16, pady=8)

        self.new_fw_entry = ctk.CTkEntry(
            fw_card,
            placeholder_text="如: Pygame",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.new_fw_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            fw_card,
            text="添加",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._add_framework,
        ).grid(row=3, column=2, padx=16, pady=(8, 16))

        # 4. 添加AI网站
        web_card = ctk.CTkFrame(
            self.config_scroll,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10
        )
        web_card.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        web_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            web_card,
            text="添加AI网站",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(16, 12))

        websites = DataManager.get_all_ai_websites()
        website_names = ", ".join(list(websites.keys())[:5])
        if len(websites) > 5:
            website_names += "..."
        self.current_websites_label = ctk.CTkLabel(
            web_card,
            text=f"已有: {website_names}",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.current_websites_label.grid(row=1, column=0, columnspan=3, sticky="w", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            web_card,
            text="网站名称",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=2, column=0, sticky="w", padx=16, pady=8)

        self.new_website_name_entry = ctk.CTkEntry(
            web_card,
            placeholder_text="如: DeepSeek",
            width=120,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.new_website_name_entry.grid(row=2, column=1, sticky="w", padx=8, pady=8)

        ctk.CTkLabel(
            web_card,
            text="网站URL",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).grid(row=3, column=0, sticky="w", padx=16, pady=8)

        self.new_website_url_entry = ctk.CTkEntry(
            web_card,
            placeholder_text="https://...",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.new_website_url_entry.grid(row=3, column=1, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            web_card,
            text="添加",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._add_ai_website,
        ).grid(row=3, column=2, padx=16, pady=(8, 16))

        # 5. 兑换码管理
        code_card = ctk.CTkFrame(
            self.config_scroll,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10
        )
        code_card.grid(row=4, column=0, sticky="ew", pady=(0, 12))
        code_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            code_card,
            text="兑换码管理",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=16, pady=(16, 12))

        # 套餐类型
        type_frame = ctk.CTkFrame(code_card, fg_color="transparent")
        type_frame.grid(row=1, column=0, columnspan=3, sticky="w", padx=16, pady=8)

        ctk.CTkLabel(
            type_frame,
            text="套餐类型:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).pack(side="left")

        self.code_package_var = ctk.StringVar(value="basic")
        ctk.CTkRadioButton(
            type_frame, text="基础版",
            variable=self.code_package_var, value="basic",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=self.colors["primary"]
        ).pack(side="left", padx=(12, 8))
        ctk.CTkRadioButton(
            type_frame, text="专业版",
            variable=self.code_package_var, value="pro",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=self.colors["primary"]
        ).pack(side="left", padx=8)

        # 有效期输入（精确到秒）
        expire_frame = ctk.CTkFrame(code_card, fg_color="transparent")
        expire_frame.grid(row=2, column=0, columnspan=3, sticky="w", padx=16, pady=8)

        ctk.CTkLabel(
            expire_frame,
            text="有效期:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).pack(side="left")

        # 天数输入
        self.expire_days_var = ctk.StringVar(value="0")
        ctk.CTkEntry(
            expire_frame,
            textvariable=self.expire_days_var,
            width=45,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            justify="center"
        ).pack(side="left", padx=(8, 2))
        ctk.CTkLabel(
            expire_frame,
            text="天",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(0, 6))

        # 小时输入
        self.expire_hours_var = ctk.StringVar(value="0")
        ctk.CTkEntry(
            expire_frame,
            textvariable=self.expire_hours_var,
            width=40,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            justify="center"
        ).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(
            expire_frame,
            text="时",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(0, 6))

        # 分钟输入
        self.expire_mins_var = ctk.StringVar(value="0")
        ctk.CTkEntry(
            expire_frame,
            textvariable=self.expire_mins_var,
            width=40,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            justify="center"
        ).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(
            expire_frame,
            text="分",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(0, 6))

        # 秒数输入
        self.expire_secs_var = ctk.StringVar(value="0")
        ctk.CTkEntry(
            expire_frame,
            textvariable=self.expire_secs_var,
            width=40,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            justify="center"
        ).pack(side="left", padx=(0, 2))
        ctk.CTkLabel(
            expire_frame,
            text="秒",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(0, 12))

        # 永久有效复选框
        self.expire_permanent_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            expire_frame,
            text="永久有效",
            variable=self.expire_permanent_var,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            corner_radius=4,
            border_width=2,
            command=self._toggle_expire_inputs
        ).pack(side="left")

        # 数量和生成按钮
        gen_frame = ctk.CTkFrame(code_card, fg_color="transparent")
        gen_frame.grid(row=3, column=0, columnspan=3, sticky="w", padx=16, pady=8)

        ctk.CTkLabel(
            gen_frame,
            text="数量:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).pack(side="left")

        self.code_count_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(
            gen_frame,
            values=["1", "5", "10", "20"],
            variable=self.code_count_var,
            width=70,
            height=32,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"])
        ).pack(side="left", padx=(8, 16))

        ctk.CTkButton(
            gen_frame,
            text="生成兑换码",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=100,
            height=32,
            corner_radius=8,
            fg_color=self.colors["accent"],
            hover_color=self.colors["accent_hover"],
            command=self._generate_codes,
        ).pack(side="left")

        # 生成结果
        self.code_result_label = ctk.CTkLabel(
            code_card,
            text="",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=self.colors["success"],
            justify="left",
            anchor="w"
        )
        self.code_result_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=16, pady=8)

        # 兑换码列表标题和删除按钮
        list_header = ctk.CTkFrame(code_card, fg_color="transparent")
        list_header.grid(row=5, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 4))

        ctk.CTkLabel(
            list_header,
            text="已生成的兑换码:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"])
        ).pack(side="left")

        ctk.CTkButton(
            list_header,
            text="删除选中",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            width=70,
            height=26,
            corner_radius=6,
            fg_color=self.colors["error"],
            hover_color="#DC2626",
            command=self._delete_selected_code
        ).pack(side="right")

        ctk.CTkButton(
            list_header,
            text="刷新列表",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            width=70,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._refresh_codes_list
        ).pack(side="right", padx=(0, 8))

        # 兑换码列表
        self.codes_listbox = ctk.CTkTextbox(
            code_card,
            height=100,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=8
        )
        self.codes_listbox.grid(row=6, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 8))

        # 实时监控看板
        monitor_frame = ctk.CTkFrame(
            code_card,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=8
        )
        monitor_frame.grid(row=7, column=0, columnspan=3, sticky="ew", padx=16, pady=(0, 16))

        ctk.CTkLabel(
            monitor_frame,
            text="⏱ 实时监控",
            font=ctk.CTkFont(size=11, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(anchor="w", padx=12, pady=(8, 4))

        self.monitor_label = ctk.CTkLabel(
            monitor_frame,
            text="加载中...",
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            justify="left",
            anchor="w"
        )
        self.monitor_label.pack(fill="x", padx=12, pady=(0, 8))

        # 6. 操作按钮
        btn_frame = ctk.CTkFrame(self.config_scroll, fg_color="transparent")
        btn_frame.grid(row=5, column=0, pady=16)

        ctk.CTkButton(
            btn_frame,
            text="刷新配置",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._refresh_config_options,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text="锁定配置",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=100,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self._lock_config,
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_frame,
            text="重置授权",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=100,
            height=36,
            corner_radius=8,
            fg_color=self.colors["error"],
            hover_color="#DC2626",
            command=self._reset_license,
        ).pack(side="left", padx=8)

        # 初始化列表和监控
        self._refresh_codes_list()
        self._start_monitor_timer()

    # ==== 旧方法已删除 - 使用新的单页导航布局 ====

    # 模板辅助方法 (新布局继续使用)

    def _refresh_templates(self):
        """刷新模板列表"""
        # 清空
        for widget in self.templates_scroll_frame.winfo_children():
            widget.destroy()

        templates = DataManager.get_all_templates()

        # 更新徽章数量
        if hasattr(self, 'template_count_badge'):
            self.template_count_badge.configure(text=f"{len(templates)} 个模板")

        if not templates:
            # 空状态提示
            empty_frame = ctk.CTkFrame(self.templates_scroll_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, sticky="nsew", pady=60)

            ctk.CTkLabel(
                empty_frame,
                text="📭",
                font=ctk.CTkFont(size=48)
            ).pack()

            ctk.CTkLabel(
                empty_frame,
                text="暂无模板",
                font=ctk.CTkFont(size=16, weight="bold", family="Microsoft YaHei UI"),
                text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
            ).pack(pady=(12, 4))

            ctk.CTkLabel(
                empty_frame,
                text="点击右上角添加你的第一个模板",
                font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
                text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
            ).pack()
            return

        for i, (name, template) in enumerate(templates.items()):
            self._create_template_card(self.templates_scroll_frame, name, template, i)

    def _create_template_card(self, parent, name: str, template: dict, row: int):
        """创建模板卡片 - UI-UX-PRO-MAX 高级风格"""
        is_custom = name not in DEFAULT_TEMPLATES

        card = ctk.CTkFrame(
            parent,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        card.grid(row=row, column=0, sticky="ew", padx=0, pady=6)
        card.grid_columnconfigure(1, weight=1)

        # 左侧图标区
        icon_frame = ctk.CTkFrame(
            card,
            width=50,
            height=50,
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            corner_radius=8
        )
        icon_frame.grid(row=0, column=0, sticky="w", padx=16, pady=16)
        icon_frame.grid_propagate(False)

        icon = "📝" if is_custom else "📁"
        ctk.CTkLabel(
            icon_frame,
            text=icon,
            font=ctk.CTkFont(size=22)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 中间信息区
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=16)

        # 标题行
        title_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text=name,
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        # 类型标签
        type_badge = ctk.CTkLabel(
            title_row,
            text="自定义" if is_custom else "内置",
            font=ctk.CTkFont(size=9, family="Microsoft YaHei UI"),
            text_color="white",
            fg_color=self.colors["accent"] if is_custom else self.colors["primary"],
            corner_radius=4,
            padx=6,
            pady=1
        )
        type_badge.pack(side="left", padx=(8, 0))

        # 描述
        ctk.CTkLabel(
            info_frame,
            text=template.get("description", "自定义模板"),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

        # 语言和框架标签
        lang = template.get("language", "")
        fw = template.get("framework", "")
        if lang or fw:
            tag_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            tag_frame.pack(fill="x", pady=(6, 0))

            if lang:
                ctk.CTkLabel(
                    tag_frame,
                    text=lang,
                    font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
                    text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
                    fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
                    corner_radius=4,
                    padx=8,
                    pady=2
                ).pack(side="left", padx=(0, 6))

            if fw:
                ctk.CTkLabel(
                    tag_frame,
                    text=fw,
                    font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
                    text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
                    fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
                    corner_radius=4,
                    padx=8,
                    pady=2
                ).pack(side="left")

        # 右侧按钮区
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e", padx=16, pady=16)

        ctk.CTkButton(
            btn_frame,
            text="使用模板",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=85,
            height=34,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=lambda n=name, t=template: self._use_template(n, t),
        ).pack(side="left", padx=(0, 8))

        if is_custom:
            ctk.CTkButton(
                btn_frame,
                text="删除",
                font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
                width=60,
                height=34,
                corner_radius=8,
                fg_color=self.colors["error"],
                hover_color="#DC2626",
                command=lambda n=name: self._delete_template(n),
            ).pack(side="left")

    def _add_template_dialog(self):
        """添加模板对话框"""
        TemplateDialog(self, callback=self._refresh_templates)

    def _delete_template(self, name: str):
        """删除自定义模板"""
        if name in DEFAULT_TEMPLATES:
            self._show_message("错误", "不能删除内置模板")
            return

        # 确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认删除")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"确定要删除模板 \"{name}\" 吗？",
            font=ctk.CTkFont(size=14),
        ).pack(pady=30)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        def confirm():
            templates = DataManager.load_templates()
            if name in templates:
                del templates[name]
                DataManager.save_templates(templates)
                self._refresh_templates()
                self._show_message("成功", f"模板 \"{name}\" 已删除")
            dialog.destroy()

        ctk.CTkButton(
            btn_frame,
            text="确定",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=80,
            height=34,
            corner_radius=8,
            fg_color=self.colors["error"],
            hover_color="#DC2626",
            command=confirm
        ).pack(side="left", padx=10)
        ctk.CTkButton(
            btn_frame,
            text="取消",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=80,
            height=34,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=dialog.destroy
        ).pack(side="left", padx=10)

    # _build_config_tab removed - using new _build_config_content()

    def _unlock_config(self):
        """解锁配置界面"""
        password = self.config_pwd_entry.get()
        if password == ADMIN_PASSWORD:
            self._config_unlocked = True
            self.config_status_label.configure(text="🔓 已解锁", text_color="green")
            self.unlock_frame.grid_forget()
            self.config_scroll.grid(row=0, column=0, sticky="nsew")
            self.config_pwd_entry.delete(0, "end")
            self.status_label.configure(text="✅ 配置已解锁")
        else:
            self._show_message("错误", "密码错误！")
            self.config_pwd_entry.delete(0, "end")

    def _lock_config(self):
        """锁定配置界面"""
        self._config_unlocked = False
        self.config_status_label.configure(text="🔒 未解锁", text_color="red")
        self.config_scroll.grid_forget()
        self.unlock_frame.grid(row=0, column=0, sticky="nsew")
        self.status_label.configure(text="🔒 配置已锁定")

    def _generate_codes(self):
        """生成兑换码"""
        package_type = self.code_package_var.get()
        count = int(self.code_count_var.get())

        # 计算有效期（精确到秒）
        expires_seconds = None
        if not self.expire_permanent_var.get():
            try:
                days = int(self.expire_days_var.get() or 0)
                hours = int(self.expire_hours_var.get() or 0)
                mins = int(self.expire_mins_var.get() or 0)
                secs = int(self.expire_secs_var.get() or 0)
                expires_seconds = days * 86400 + hours * 3600 + mins * 60 + secs
                if expires_seconds <= 0:
                    self.code_result_label.configure(
                        text="请设置有效期时间（至少1秒）",
                        text_color=self.colors["error"]
                    )
                    return
            except ValueError:
                self.code_result_label.configure(
                    text="请输入有效的数字",
                    text_color=self.colors["error"]
                )
                return

        # 生成兑换码
        codes = self.code_manager.generate_batch(package_type, count, expires_seconds=expires_seconds)

        package_name = "基础版" if package_type == "basic" else "专业版"
        if expires_seconds:
            expire_text = self.code_manager.format_remaining_time(expires_seconds)
        else:
            expire_text = "永久有效"

        self.code_result_label.configure(
            text=f"已生成 {len(codes)} 个 {package_name} 兑换码（{expire_text}）:\n" + "\n".join(codes),
            text_color=self.colors["success"],
        )

        self._refresh_codes_list()
        self._start_monitor_timer()

    def _refresh_codes_list(self):
        """刷新兑换码列表"""
        if not hasattr(self, "codes_listbox"):
            return

        codes = self.code_manager.get_all_codes()
        # 存储当前码列表用于删除功能
        self._current_codes = codes

        self.codes_listbox.configure(state="normal")
        self.codes_listbox.delete("0.0", "end")

        if not codes:
            self.codes_listbox.insert("0.0", "暂无兑换码，请先生成")
        else:
            lines = []
            for code_info in codes:
                package_type = code_info.get("package_type", "basic")
                package_name = "基础版" if package_type == "basic" else "专业版"
                status = "已使用" if code_info.get("is_used") else "可用"

                # 使用精确到秒的时间显示
                remaining_secs = code_info.get("remaining_seconds")
                if remaining_secs is not None:
                    if remaining_secs <= 0:
                        expire_text = "已过期"
                        status = "已过期"
                    else:
                        expire_text = self.code_manager.format_remaining_time(remaining_secs)
                else:
                    expire_text = "永久"

                lines.append(f"{code_info['code']}  [{package_name}]  [{status}]  [{expire_text}]")

            self.codes_listbox.insert("0.0", "\n".join(lines))

        self.codes_listbox.configure(state="disabled")

    def _reset_license(self):
        """重置授权（测试用）"""
        self.code_manager.reset_license()
        self.status_label.configure(text="✅ 授权已重置，重启应用后生效")

    def _toggle_expire_inputs(self):
        """切换有效期输入框状态"""
        if self.expire_permanent_var.get():
            # 永久有效，清空并禁用输入
            self.expire_days_var.set("0")
            self.expire_hours_var.set("0")
            self.expire_mins_var.set("0")
            self.expire_secs_var.set("0")

    def _delete_selected_code(self):
        """删除选中的兑换码"""
        if not hasattr(self, "codes_listbox"):
            return

        # 获取选中的文本
        try:
            # 获取当前选中行
            self.codes_listbox.configure(state="normal")
            selected_text = self.codes_listbox.get("1.0", "end").strip()
            self.codes_listbox.configure(state="disabled")

            if not selected_text or selected_text == "暂无兑换码，请先生成":
                self._show_message("提示", "没有可删除的兑换码")
                return

            # 获取第一行（最新的兑换码）
            first_line = selected_text.split("\n")[0] if selected_text else ""
            if not first_line:
                return

            # 提取兑换码（格式：CODE  [套餐]  [状态]  [时间]）
            code = first_line.split("  ")[0].strip()

            if not code:
                self._show_message("提示", "无法识别兑换码")
                return

            # 确认删除
            if self.code_manager.delete_code(code):
                self._show_message("成功", f"已删除兑换码: {code}")
                self._refresh_codes_list()
                self._update_monitor()
            else:
                self._show_message("错误", "删除失败，兑换码可能不存在")

        except Exception as e:
            self._show_message("错误", f"删除失败: {str(e)}")

    def _start_monitor_timer(self):
        """启动实时监控定时器"""
        if hasattr(self, "_monitor_timer_id"):
            self.after_cancel(self._monitor_timer_id)
        self._update_monitor()

    def _update_monitor(self):
        """更新实时监控面板"""
        if not hasattr(self, "monitor_label"):
            return

        codes = self.code_manager.get_all_codes()

        if not codes:
            self.monitor_label.configure(text="暂无兑换码")
            return

        # 统计信息
        total = len(codes)
        available = sum(1 for c in codes if not c.get("is_used") and (c.get("remaining_seconds") is None or c.get("remaining_seconds", 0) > 0))
        used = sum(1 for c in codes if c.get("is_used"))
        expired = sum(1 for c in codes if c.get("remaining_seconds") is not None and c.get("remaining_seconds", 0) <= 0)

        # 找出即将到期的码（24小时内）
        expiring_soon = []
        for c in codes:
            remaining = c.get("remaining_seconds")
            if remaining is not None and 0 < remaining <= 86400 and not c.get("is_used"):
                expiring_soon.append((c["code"], remaining))

        # 构建显示文本
        lines = [f"总计: {total}  |  可用: {available}  |  已用: {used}  |  过期: {expired}"]

        if expiring_soon:
            lines.append("━" * 40)
            lines.append("⚠ 即将到期 (24小时内):")
            for code, remaining in sorted(expiring_soon, key=lambda x: x[1])[:5]:
                time_str = self.code_manager.format_remaining_time(remaining)
                lines.append(f"  {code[:8]}...  →  {time_str}")

        self.monitor_label.configure(text="\n".join(lines))

        # 每秒更新一次
        self._monitor_timer_id = self.after(1000, self._update_monitor)

    def _on_fw_lang_changed(self, lang: str):
        """框架语言变更事件"""
        all_langs = DataManager.get_all_languages()
        if lang in all_langs:
            categories = list(all_langs[lang].get("categories", {}).keys())
            self.fw_cat_menu.configure(values=categories)
            if categories:
                self.fw_cat_var.set(categories[0])

    def _add_language(self):
        """添加编程语言"""
        if not self._config_unlocked:
            self._show_message("警告", "请先解锁配置")
            return

        name = self.new_lang_entry.get().strip()
        if not name:
            self._show_message("警告", "请输入语言名称")
            return

        if DataManager.add_language(name):
            self._show_message("成功", f"已添加语言: {name}")
            self.new_lang_entry.delete(0, "end")
            self._refresh_config_options()
            self._refresh_language_options()
        else:
            self._show_message("错误", "添加失败，可能名称已存在")

    def _add_category(self):
        """添加框架类别"""
        if not self._config_unlocked:
            self._show_message("警告", "请先解锁配置")
            return

        lang = self.cat_lang_var.get()
        cat = self.new_cat_entry.get().strip()

        if not lang or not cat:
            self._show_message("警告", "请选择语言并输入类别名称")
            return

        if DataManager.add_category_to_language(lang, cat):
            self._show_message("成功", f"已为 {lang} 添加类别: {cat}")
            self.new_cat_entry.delete(0, "end")
            self._refresh_config_options()
            self._refresh_language_options()
        else:
            self._show_message("错误", "添加失败")

    def _add_framework(self):
        """添加具体框架"""
        if not self._config_unlocked:
            self._show_message("警告", "请先解锁配置")
            return

        lang = self.fw_lang_var.get()
        cat = self.fw_cat_var.get()
        fw = self.new_fw_entry.get().strip()

        if not lang or not cat or not fw:
            self._show_message("警告", "请选择语言、类别并输入框架名称")
            return

        if DataManager.add_framework_to_category(lang, cat, fw):
            self._show_message("成功", f"已添加框架: {fw}")
            self.new_fw_entry.delete(0, "end")
            self._refresh_language_options()
        else:
            self._show_message("错误", "添加失败")

    def _add_priority(self):
        """添加开发优先级"""
        if not self._config_unlocked:
            self._show_message("警告", "请先解锁配置")
            return

        priority = self.new_priority_entry.get().strip()
        if not priority:
            self._show_message("警告", "请输入优先级名称")
            return

        if DataManager.add_priority(priority):
            self._show_message("成功", f"已添加优先级: {priority}")
            self.new_priority_entry.delete(0, "end")
            self._refresh_priority_options()
        else:
            self._show_message("错误", "添加失败，可能名称已存在")

    def _add_ai_website(self):
        """添加AI网站"""
        if not self._config_unlocked:
            self._show_message("警告", "请先解锁配置")
            return

        name = self.new_website_name_entry.get().strip()
        url = self.new_website_url_entry.get().strip()

        if not name:
            self._show_message("警告", "请输入网站名称")
            return

        if not url:
            self._show_message("警告", "请输入网站URL")
            return

        # 确保URL以http开头
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url

        if DataManager.add_ai_website(name, url):
            self._show_message("成功", f"已添加网站: {name}")
            self.new_website_name_entry.delete(0, "end")
            self.new_website_url_entry.delete(0, "end")
            self._refresh_website_options()
            self._refresh_website_menu()
        else:
            self._show_message("错误", "添加失败，可能名称已存在或为预置网站")

    def _delete_ai_website(self):
        """删除AI网站"""
        if not self._config_unlocked:
            self._show_message("警告", "请先解锁配置")
            return

        name = self.del_website_var.get()
        if not name or name == "(无自定义网站)":
            self._show_message("警告", "请选择要删除的网站")
            return

        if DataManager.delete_ai_website(name):
            self._show_message("成功", f"已删除网站: {name}")
            self._refresh_website_options()
            self._refresh_website_menu()
        else:
            self._show_message("错误", "删除失败，可能是预置网站")

    def _refresh_website_options(self):
        """刷新网站配置选项"""
        websites = DataManager.get_all_ai_websites()
        # 更新已有网站显示
        website_names = ", ".join(list(websites.keys())[:6])
        if len(websites) > 6:
            website_names += "..."
        self.current_websites_label.configure(text=website_names)
        # 更新删除下拉菜单
        custom_websites = [name for name, info in websites.items() if not info.get("is_preset", True)]
        self.del_website_menu.configure(values=custom_websites if custom_websites else ["(无自定义网站)"])
        if custom_websites:
            self.del_website_var.set(custom_websites[0])
        else:
            self.del_website_var.set("(无自定义网站)")

    def _refresh_config_options(self):
        """刷新配置选项"""
        all_langs = list(DataManager.get_all_languages().keys())
        self.cat_lang_menu.configure(values=all_langs)
        self.fw_lang_menu.configure(values=all_langs)
        self.status_label.configure(text="✅ 配置已刷新")

    def _refresh_language_options(self):
        """刷新语言选项（主界面）"""
        all_langs = DataManager.get_all_languages()
        self.language_menu.configure(values=list(all_langs.keys()))

    def _refresh_priority_options(self):
        """刷新优先级选项（主界面）"""
        # 需要重新构建优先级选项，这里简化处理
        pass

    # _build_right_panel removed - using new single-page layout

    # _build_output_tab removed - using new _build_output_content()

    # _build_packager_tab removed - using new _build_packager_content()

    def _build_beginner_mode(self):
        """构建零基础用户模式界面 - 优化版"""
        self.beginner_frame = ctk.CTkFrame(self.packager_container, fg_color="transparent")
        self.beginner_frame.grid_columnconfigure(0, weight=1)
        self.beginner_frame.grid_rowconfigure(3, weight=1)

        # ===== 第一部分：环境检测卡片 =====
        env_card = ctk.CTkFrame(
            self.beginner_frame,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"])
        )
        env_card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 12))
        env_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            env_card,
            text="环境检测",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(12, 10))

        # Python 状态
        ctk.CTkLabel(
            env_card,
            text="Python 环境:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=1, column=0, sticky="w", padx=12, pady=8)

        self.python_status_label = ctk.CTkLabel(
            env_card,
            text="检测中...",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        )
        self.python_status_label.grid(row=1, column=1, sticky="w", padx=8, pady=8)

        # 重新检测按钮
        ctk.CTkButton(
            env_card,
            text="🔄 重新检测",
            width=110,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            command=self._check_environment,
        ).grid(row=1, column=2, padx=12, pady=8)

        # PyInstaller 状态
        ctk.CTkLabel(
            env_card,
            text="PyInstaller:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=2, column=0, sticky="w", padx=12, pady=8)

        self.pyinstaller_status_label = ctk.CTkLabel(
            env_card,
            text="检测中...",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"])
        )
        self.pyinstaller_status_label.grid(row=2, column=1, sticky="w", padx=8, pady=8)

        # 一键安装按钮
        self.install_btn = ctk.CTkButton(
            env_card,
            text="📦 一键安装",
            width=110,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["success"], self.colors["success"]),
            hover_color=("#059669", "#059669"),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            command=self._install_pyinstaller,
        )
        self.install_btn.grid(row=2, column=2, padx=12, pady=(8, 12))

        # ===== 第二部分：打包设置卡片 =====
        pack_card = ctk.CTkFrame(
            self.beginner_frame,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"])
        )
        pack_card.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 12))
        pack_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            pack_card,
            text="打包设置",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(12, 10))

        # 选择 Python 文件
        ctk.CTkLabel(
            pack_card,
            text="Python 文件:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=1, column=0, sticky="w", padx=12, pady=8)

        self.beginner_script_var = ctk.StringVar()
        ctk.CTkEntry(
            pack_card,
            textvariable=self.beginner_script_var,
            placeholder_text="选择你的 .py 文件",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI")
        ).grid(row=1, column=1, sticky="ew", padx=8, pady=8)

        ctk.CTkButton(
            pack_card,
            text="📂 选择",
            width=90,
            height=40,
            corner_radius=8,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            command=self._select_beginner_script,
        ).grid(row=1, column=2, padx=12, pady=8)

        # 程序名称
        ctk.CTkLabel(
            pack_card,
            text="程序名称:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=2, column=0, sticky="w", padx=12, pady=8)

        self.beginner_name_var = ctk.StringVar(value="我的程序")
        ctk.CTkEntry(
            pack_card,
            textvariable=self.beginner_name_var,
            placeholder_text="生成的 exe 名称",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI")
        ).grid(row=2, column=1, columnspan=2, sticky="ew", padx=8, pady=8)

        # 程序类型
        ctk.CTkLabel(
            pack_card,
            text="程序类型:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=3, column=0, sticky="w", padx=12, pady=8)

        self.beginner_type_var = ctk.StringVar(value="GUI程序")
        type_frame = ctk.CTkFrame(pack_card, fg_color="transparent")
        type_frame.grid(row=3, column=1, sticky="w", padx=8, pady=8)

        ctk.CTkRadioButton(
            type_frame,
            text="GUI 窗口程序",
            variable=self.beginner_type_var,
            value="GUI程序",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left", padx=(0, 15))

        ctk.CTkRadioButton(
            type_frame,
            text="命令行程序",
            variable=self.beginner_type_var,
            value="命令行程序",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        # 输出位置
        ctk.CTkLabel(
            pack_card,
            text="输出位置:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=4, column=0, sticky="w", padx=12, pady=8)

        self.beginner_output_var = ctk.StringVar()
        ctk.CTkEntry(
            pack_card,
            textvariable=self.beginner_output_var,
            placeholder_text="exe 文件保存位置",
            height=40,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).grid(row=4, column=1, sticky="ew", padx=8, pady=(8, 12))

        ctk.CTkButton(
            pack_card,
            text="📂 选择",
            width=90,
            height=40,
            corner_radius=8,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            command=self._select_beginner_output,
        ).grid(row=4, column=2, padx=12, pady=(8, 12))

        # ===== 第三部分：打包按钮区 =====
        action_frame = ctk.CTkFrame(self.beginner_frame, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=(0, 15))

        self.beginner_pack_btn = ctk.CTkButton(
            action_frame,
            text="🚀 一键打包",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            width=180,
            height=48,
            corner_radius=10,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
            command=self._beginner_package,
        )
        self.beginner_pack_btn.pack(side="left", padx=(0, 8))

        self.beginner_ai_pack_btn = ctk.CTkButton(
            action_frame,
            text="🧠 AI分析打包",
            font=ctk.CTkFont(size=14, weight="bold", family="Microsoft YaHei UI"),
            width=180,
            height=48,
            corner_radius=10,
            fg_color=(self.colors["accent"], self.colors["accent"]),
            hover_color=("#DB2777", "#DB2777"),
            command=self._beginner_ai_package,
        )
        self.beginner_ai_pack_btn.pack(side="left", padx=8)

        ctk.CTkButton(
            action_frame,
            text="📂 打开目录",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=120,
            height=48,
            corner_radius=10,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            command=self._open_beginner_output,
        ).pack(side="left", padx=8)

        # ===== 第四部分：日志卡片 =====
        log_card = ctk.CTkFrame(
            self.beginner_frame,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"])
        )
        log_card.grid(row=3, column=0, sticky="nsew", padx=0, pady=0)
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=12, pady=10)

        ctk.CTkLabel(
            log_header,
            text="运行日志",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(side="left")

        ctk.CTkButton(
            log_header,
            text="清空",
            width=70,
            height=30,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            command=lambda: self.beginner_log_textbox.delete("1.0", "end"),
        ).pack(side="right")

        self.beginner_log_textbox = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"])
        )
        self.beginner_log_textbox.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        self.beginner_log_textbox.insert(
            "1.0",
            "欢迎使用零基础打包模式！\n\n"
            "步骤：\n"
            "1. 确保环境检测通过（如未安装 PyInstaller 请点击一键安装）\n"
            "2. 选择你的 Python 文件\n"
            "3. 设置程序名称和类型\n"
            "4. 点击「一键打包」或「AI分析打包」\n"
        )

        # 初始化环境检测
        self.after(500, self._check_environment)

    def _build_developer_mode(self):
        """构建独立开发模式界面 - 统一紫色主题风格"""
        self.developer_frame = ctk.CTkFrame(
            self.packager_container,
            fg_color="transparent"
        )
        self.developer_frame.grid_columnconfigure(0, weight=1)
        self.developer_frame.grid_rowconfigure(2, weight=1)

        # ===== 第一部分：提示卡片 =====
        tip_card = ctk.CTkFrame(
            self.developer_frame,
            fg_color=(self.colors["primary_subtle"], "#1e1b4b"),
            corner_radius=10,
            border_width=1,
            border_color=(self.colors["primary_light"], self.colors["primary"])
        )
        tip_card.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 12))

        ctk.CTkLabel(
            tip_card,
            text="💡 选择入口文件后点击「AI 智能分析」自动检测依赖和配置",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["primary"], self.colors["primary_light"]),
        ).pack(padx=15, pady=12)

        # ===== 第二部分：配置卡片（包含 AI 分析结果）=====
        config_card = ctk.CTkFrame(
            self.developer_frame,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"])
        )
        config_card.grid(row=1, column=0, sticky="ew", padx=0, pady=(0, 12))
        config_card.grid_columnconfigure(0, weight=1)
        config_card.grid_columnconfigure(1, weight=1)

        # 左侧：基本配置
        left_frame = ctk.CTkFrame(config_card, fg_color="transparent")
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(15, 8), pady=15)
        left_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            left_frame,
            text="📦 打包配置",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        # 入口文件
        ctk.CTkLabel(
            left_frame,
            text="入口文件:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=1, column=0, sticky="w", pady=6)

        self.script_path_var = ctk.StringVar()
        ctk.CTkEntry(
            left_frame,
            textvariable=self.script_path_var,
            placeholder_text="选择入口文件 (main.py)",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).grid(row=1, column=1, sticky="ew", padx=8, pady=6)

        btn_frame_1 = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame_1.grid(row=1, column=2, sticky="e", pady=6)

        ctk.CTkButton(
            btn_frame_1,
            text="📂",
            width=36,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            command=self._select_script,
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            btn_frame_1,
            text="🤖 AI分析",
            width=80,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["accent"], self.colors["accent"]),
            hover_color=("#DB2777", "#DB2777"),
            font=ctk.CTkFont(size=11, weight="bold", family="Microsoft YaHei UI"),
            command=self._ai_analyze_project,
        ).pack(side="left")

        # 输出目录
        ctk.CTkLabel(
            left_frame,
            text="输出目录:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=2, column=0, sticky="w", pady=6)

        self.output_dir_var = ctk.StringVar(value=self.settings.get("pyinstaller_output_dir", ""))
        ctk.CTkEntry(
            left_frame,
            textvariable=self.output_dir_var,
            placeholder_text="exe 保存位置",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).grid(row=2, column=1, sticky="ew", padx=8, pady=6)

        ctk.CTkButton(
            left_frame,
            text="📂",
            width=36,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            command=self._select_output_dir,
        ).grid(row=2, column=2, sticky="w", pady=6)

        # 程序名称 + 图标
        ctk.CTkLabel(
            left_frame,
            text="程序名称:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=3, column=0, sticky="w", pady=6)

        name_icon_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        name_icon_frame.grid(row=3, column=1, columnspan=2, sticky="ew", pady=6)

        self.program_name_var = ctk.StringVar(value="MyApp")
        ctk.CTkEntry(
            name_icon_frame,
            textvariable=self.program_name_var,
            placeholder_text="程序名",
            width=120,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=(8, 15))

        ctk.CTkLabel(
            name_icon_frame,
            text="图标:",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(side="left")

        self.icon_path_var = ctk.StringVar()
        ctk.CTkEntry(
            name_icon_frame,
            textvariable=self.icon_path_var,
            width=120,
            height=36,
            corner_radius=8,
            placeholder_text="可选 .ico",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            placeholder_text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            name_icon_frame,
            text="选择",
            width=50,
            height=36,
            corner_radius=8,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            command=self._select_icon,
        ).pack(side="left")

        # 打包选项
        options_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        options_frame.grid(row=4, column=0, columnspan=3, sticky="w", pady=(10, 0))

        self.onefile_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            options_frame,
            text="单文件 (-F)",
            variable=self.onefile_var,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
        ).pack(side="left", padx=(0, 20))

        self.noconsole_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            options_frame,
            text="无控制台 (-w)",
            variable=self.noconsole_var,
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
        ).pack(side="left")

        # 右侧：AI 分析结果
        right_frame = ctk.CTkFrame(
            config_card,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            corner_radius=10
        )
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 15), pady=15)
        right_frame.grid_columnconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right_frame,
            text="🤖 AI 分析结果",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(10, 5))

        self.ai_result_textbox = ctk.CTkTextbox(
            right_frame,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=10),
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
        )
        self.ai_result_textbox.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.ai_result_textbox.insert("1.0", "点击「AI分析」按钮分析项目...\n\n• 自动检测依赖模块\n• 自动检测数据文件\n• 自动配置特殊库")
        self.ai_result_textbox.configure(state="disabled")

        # ===== 打包按钮区 =====
        btn_frame = ctk.CTkFrame(self.developer_frame, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="se", padx=0, pady=(0, 12))

        ctk.CTkButton(
            btn_frame,
            text="🚀 开始打包",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            width=140,
            height=42,
            corner_radius=10,
            fg_color=(self.colors["primary"], self.colors["primary"]),
            hover_color=(self.colors["primary_dark"], self.colors["primary_dark"]),
            command=self._start_packaging,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="🧠 AI分析后打包",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            width=150,
            height=42,
            corner_radius=10,
            fg_color=(self.colors["accent"], self.colors["accent"]),
            hover_color=("#DB2777", "#DB2777"),
            command=self._ai_analyze_and_package,
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="📂 打开目录",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            width=100,
            height=42,
            corner_radius=10,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            hover_color=(self.colors["border_light"], self.colors["border_dark"]),
            text_color=(self.colors["text_light"], self.colors["text_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            command=self._open_output_dir,
        ).pack(side="left")

        # ===== 第三部分：打包日志 =====
        log_card = ctk.CTkFrame(
            self.developer_frame,
            fg_color=(self.colors["surface_light"], self.colors["surface_dark"]),
            corner_radius=12,
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"])
        )
        log_card.grid(row=2, column=0, sticky="nsew", padx=0, pady=0)
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=12, pady=10)

        ctk.CTkLabel(
            log_header,
            text="📋 打包日志",
            font=ctk.CTkFont(size=12, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_light"], self.colors["text_dark"])
        ).pack(side="left")

        ctk.CTkButton(
            log_header,
            text="清空",
            width=60,
            height=28,
            corner_radius=6,
            fg_color="transparent",
            hover_color=(self.colors["bg_light"], self.colors["bg_dark"]),
            text_color=(self.colors["text_muted_light"], self.colors["text_muted_dark"]),
            border_width=1,
            border_color=(self.colors["border_light"], self.colors["border_dark"]),
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            command=lambda: self.pack_log_textbox.delete("1.0", "end"),
        ).pack(side="right")

        self.pack_log_textbox = ctk.CTkTextbox(
            log_card,
            font=ctk.CTkFont(family="Consolas", size=10),
            corner_radius=8,
            fg_color=(self.colors["bg_light"], self.colors["bg_dark"]),
        )
        self.pack_log_textbox.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))

    def _on_packager_mode_changed(self, mode: str):
        """打包模式切换"""
        if mode == "零基础用户":
            self._show_beginner_mode()
        else:
            self._show_developer_mode()

    def _show_beginner_mode(self):
        """显示零基础用户模式"""
        self.developer_frame.grid_forget()
        self.beginner_frame.grid(row=0, column=0, sticky="nsew")

    def _show_developer_mode(self):
        """显示独立开发模式"""
        self.beginner_frame.grid_forget()
        self.developer_frame.grid(row=0, column=0, sticky="nsew")

    def _check_environment(self):
        """检测环境"""
        import sys
        import subprocess

        # 检测 Python
        try:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            self.python_status_label.configure(
                text=f"✅ Python {python_version}",
                text_color="green"
            )
        except Exception:
            self.python_status_label.configure(
                text="❌ 未检测到 Python",
                text_color="red"
            )

        # 检测 PyInstaller
        if PyInstallerService.is_installed():
            self.pyinstaller_status_label.configure(
                text="✅ 已安装",
                text_color="green"
            )
            self.install_btn.configure(state="disabled", text="✅ 已安装")
            self.pyinstaller_status.configure(text="✅ PyInstaller 已安装", text_color="green")
        else:
            self.pyinstaller_status_label.configure(
                text="❌ 未安装",
                text_color="red"
            )
            self.install_btn.configure(state="normal", text="📦 一键安装 PyInstaller")
            self.pyinstaller_status.configure(text="❌ PyInstaller 未安装", text_color="red")

    def _install_pyinstaller(self):
        """一键安装 PyInstaller"""
        import sys

        self.install_btn.configure(state="disabled", text="⏳ 安装中...")
        self._append_beginner_log("=" * 40)
        self._append_beginner_log("📦 开始安装 PyInstaller...")

        def worker():
            try:
                import subprocess
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "pyinstaller", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                def on_complete():
                    if result.returncode == 0:
                        self._append_beginner_log("✅ PyInstaller 安装成功！")
                        self._check_environment()
                    else:
                        self._append_beginner_log(f"❌ 安装失败: {result.stderr}")
                        self.install_btn.configure(state="normal", text="📦 重试安装")

                self.after(0, on_complete)

            except Exception as e:
                error_msg = str(e)
                def on_error(msg=error_msg):
                    self._append_beginner_log(f"❌ 安装出错: {msg}")
                    self.install_btn.configure(state="normal", text="📦 重试安装")

                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _select_beginner_script(self):
        """零基础模式选择脚本"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Python文件", "*.py")],
        )
        if filepath:
            self.beginner_script_var.set(filepath)
            # 自动设置程序名
            name = Path(filepath).stem
            self.beginner_name_var.set(name)
            # 自动设置输出目录为脚本所在目录的 dist 文件夹
            output_dir = os.path.join(os.path.dirname(filepath), "dist")
            self.beginner_output_var.set(output_dir)

    def _select_beginner_output(self):
        """零基础模式选择输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.beginner_output_var.set(directory)

    def _open_beginner_output(self):
        """打开零基础模式输出目录"""
        output_dir = self.beginner_output_var.get()
        if output_dir and os.path.exists(output_dir):
            FileService.open_directory(output_dir)
        else:
            self._show_message("提示", "输出目录不存在")

    def _append_beginner_log(self, msg: str):
        """追加零基础模式日志"""
        self.beginner_log_textbox.insert("end", msg + "\n")
        self.beginner_log_textbox.see("end")

    def _beginner_package(self):
        """零基础模式一键打包"""
        script_path = self.beginner_script_var.get().strip()
        name = self.beginner_name_var.get().strip()
        output_dir = self.beginner_output_var.get().strip()
        app_type = self.beginner_type_var.get()

        # 验证
        if not script_path:
            self._show_message("警告", "请选择 Python 文件")
            return

        if not os.path.exists(script_path):
            self._show_message("错误", "文件不存在")
            return

        if not name:
            name = Path(script_path).stem

        if not output_dir:
            output_dir = os.path.join(os.path.dirname(script_path), "dist")

        if not PyInstallerService.is_installed():
            self._show_message("错误", "请先安装 PyInstaller")
            return

        # 确定是否隐藏控制台
        noconsole = (app_type == "GUI程序")

        self.beginner_pack_btn.configure(state="disabled", text="⏳ 打包中...")
        self._append_beginner_log("")
        self._append_beginner_log("=" * 40)
        self._append_beginner_log(f"🚀 开始打包: {name}")
        self._append_beginner_log(f"   文件: {script_path}")
        self._append_beginner_log(f"   类型: {app_type}")
        self._append_beginner_log(f"   输出: {output_dir}")

        def log_callback(msg):
            self.after(0, lambda: self._append_beginner_log(msg))

        def worker():
            try:
                success = PyInstallerService.build(
                    script_path=script_path,
                    output_dir=output_dir,
                    name=name,
                    onefile=True,
                    noconsole=noconsole,
                    icon="",
                    additional_files=[],
                    callback=log_callback,
                )

                def on_complete():
                    self.beginner_pack_btn.configure(state="normal", text="🚀 一键打包")
                    if success:
                        exe_name = f"{name}.exe"
                        exe_path = os.path.join(output_dir, exe_name)
                        self._append_beginner_log("")
                        self._append_beginner_log("=" * 40)
                        self._append_beginner_log("✅ 打包成功！")
                        self._append_beginner_log(f"📁 文件位置: {exe_path}")
                        self._show_message("成功", f"打包完成！\n\n生成文件：{exe_path}")
                    else:
                        self._append_beginner_log("❌ 打包失败，请查看日志")
                        self._show_message("失败", "打包失败，请查看日志了解详情")

                self.after(0, on_complete)

            except Exception as e:
                error_msg = str(e)
                def on_error(msg=error_msg):
                    self.beginner_pack_btn.configure(state="normal", text="🚀 一键打包")
                    self._append_beginner_log(f"❌ 打包出错: {msg}")
                    self._show_message("错误", f"打包出错: {msg}")

                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _beginner_ai_package(self):
        """零基础模式 AI 分析后打包"""
        script_path = self.beginner_script_var.get().strip()
        name = self.beginner_name_var.get().strip()
        output_dir = self.beginner_output_var.get().strip()
        app_type = self.beginner_type_var.get()

        # 验证
        if not script_path:
            self._show_message("警告", "请选择 Python 文件")
            return

        if not os.path.exists(script_path):
            self._show_message("错误", "文件不存在")
            return

        if not name:
            name = Path(script_path).stem

        if not output_dir:
            output_dir = os.path.join(os.path.dirname(script_path), "dist")

        if not PyInstallerService.is_installed():
            self._show_message("错误", "请先安装 PyInstaller")
            return

        if not self.api_config.is_configured():
            self._show_message("错误", "请先在设置中配置 API 密钥才能使用 AI 分析功能")
            return

        noconsole = (app_type == "GUI程序")
        project_dir = os.path.dirname(script_path)

        self.beginner_ai_pack_btn.configure(state="disabled", text="⏳ AI分析中...")
        self._append_beginner_log("")
        self._append_beginner_log("=" * 40)
        self._append_beginner_log("🧠 开始 AI 智能分析项目...")

        def log_callback(msg):
            self.after(0, lambda: self._append_beginner_log(msg))

        def worker():
            try:
                # 第一步：AI 分析
                config = self.ai_analyzer.analyze_project(
                    project_dir=project_dir,
                    main_script=script_path,
                    callback=log_callback
                )

                def show_analysis_result():
                    self._append_beginner_log("")
                    self._append_beginner_log("✅ AI 分析完成！")
                    hidden_imports = config.get('hidden_imports', [])
                    if hidden_imports:
                        self._append_beginner_log(f"   检测到隐藏导入: {', '.join(hidden_imports[:5])}{'...' if len(hidden_imports) > 5 else ''}")
                    collect_data = config.get('collect_data', [])
                    if collect_data:
                        self._append_beginner_log(f"   检测到数据文件: {len(collect_data)} 个")
                    self._append_beginner_log("")
                    self._append_beginner_log("🚀 开始打包...")
                    self.beginner_ai_pack_btn.configure(text="⏳ 打包中...")

                self.after(0, show_analysis_result)

                # 第二步：使用 AI 配置进行打包
                success = PyInstallerService.build(
                    script_path=script_path,
                    output_dir=output_dir,
                    name=name,
                    onefile=True,
                    noconsole=noconsole,
                    icon="",
                    additional_files=[],
                    ai_config=config,
                    callback=log_callback,
                )

                def on_complete():
                    self.beginner_ai_pack_btn.configure(state="normal", text="🧠 AI分析后打包")
                    if success:
                        exe_name = f"{name}.exe"
                        exe_path = os.path.join(output_dir, exe_name)
                        self._append_beginner_log("")
                        self._append_beginner_log("=" * 40)
                        self._append_beginner_log("✅ AI 智能打包成功！")
                        self._append_beginner_log(f"📁 文件位置: {exe_path}")
                        self._show_message("成功", f"AI 智能打包完成！\n\n生成文件：{exe_path}")
                    else:
                        self._append_beginner_log("❌ 打包失败，请查看日志")
                        self._show_message("失败", "打包失败，请查看日志了解详情")

                self.after(0, on_complete)

            except Exception as e:
                error_msg = str(e)
                def on_error(msg=error_msg):
                    self.beginner_ai_pack_btn.configure(state="normal", text="🧠 AI分析后打包")
                    self._append_beginner_log(f"❌ AI 打包出错: {msg}")
                    self._show_message("错误", f"AI 打包出错: {msg}")

                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _ai_analyze_project(self):
        """AI 分析项目"""
        script_path = self.script_path_var.get().strip()
        if not script_path:
            self._show_message("警告", "请先选择入口文件")
            return

        # 处理多文件情况，取第一个作为主入口
        if ";" in script_path:
            script_path = script_path.split(";")[0].strip()

        if not os.path.exists(script_path):
            self._show_message("错误", f"文件不存在: {script_path}")
            return

        if not self.api_config.is_configured():
            self._show_message("错误", "请先在设置中配置 API 密钥")
            return

        project_dir = os.path.dirname(script_path)

        def log_callback(msg):
            self.after(0, lambda: self._append_pack_log(msg))

        def worker():
            try:
                config = self.ai_analyzer.analyze_project(
                    project_dir=project_dir,
                    main_script=script_path,
                    callback=log_callback
                )

                def on_success():
                    self.ai_package_config = config
                    self._display_ai_result(config)
                    self._show_message("成功", "AI 分析完成！请查看分析结果")

                self.after(0, on_success)

            except Exception as e:
                error_msg = str(e)
                def on_error(msg=error_msg):
                    self._append_pack_log(f"❌ AI 分析失败: {msg}")
                    self._show_message("错误", f"AI 分析失败: {msg}")

                self.after(0, on_error)

        self._append_pack_log("=" * 50)
        self._append_pack_log("🤖 开始 AI 智能分析...")
        threading.Thread(target=worker, daemon=True).start()

    def _display_ai_result(self, config: dict):
        """显示 AI 分析结果"""
        self.ai_result_textbox.configure(state="normal")
        self.ai_result_textbox.delete("1.0", "end")

        result_text = f"""✅ AI 分析完成

📦 隐藏导入模块:
{chr(10).join('  • ' + m for m in config.get('hidden_imports', [])) or '  (无)'}

📁 收集数据包:
{chr(10).join('  • ' + m for m in config.get('collect_data', [])) or '  (无)'}

📂 完整收集包:
{chr(10).join('  • ' + m for m in config.get('collect_all', [])) or '  (无)'}

💡 建议说明:
{config.get('explanation', '无')}
"""
        self.ai_result_textbox.insert("1.0", result_text)
        self.ai_result_textbox.configure(state="disabled")

    def _ai_analyze_and_package(self):
        """AI 分析后立即打包"""
        script_path = self.script_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        name = self.program_name_var.get().strip()

        if not script_path:
            self._show_message("警告", "请先选择入口文件")
            return

        if not output_dir:
            self._show_message("警告", "请选择输出目录")
            return

        if not self.api_config.is_configured():
            self._show_message("错误", "请先在设置中配置 API 密钥")
            return

        # 处理多文件
        if ";" in script_path:
            script_path = script_path.split(";")[0].strip()

        project_dir = os.path.dirname(script_path)

        def log_callback(msg):
            self.after(0, lambda: self._append_pack_log(msg))

        def worker():
            try:
                # 第一步：AI 分析
                log_callback("=" * 50)
                log_callback("🤖 第一步：AI 智能分析项目...")

                config = self.ai_analyzer.analyze_project(
                    project_dir=project_dir,
                    main_script=script_path,
                    callback=log_callback
                )

                self.after(0, lambda: self._display_ai_result(config))

                # 第二步：使用 AI 配置打包
                log_callback("")
                log_callback("=" * 50)
                log_callback("📦 第二步：开始打包...")

                success = self._build_with_ai_config(
                    script_path=script_path,
                    output_dir=output_dir,
                    name=name,
                    ai_config=config,
                    callback=log_callback
                )

                def on_complete():
                    if success:
                        self._show_message("成功", f"打包完成！\n输出目录: {output_dir}")
                    else:
                        self._show_message("失败", "打包失败，请查看日志")

                self.after(0, on_complete)

            except Exception as e:
                error_msg = str(e)
                def on_error(msg=error_msg):
                    self._append_pack_log(f"❌ 打包失败: {msg}")
                    self._show_message("错误", f"打包失败: {msg}")

                self.after(0, on_error)

        self.pack_log_textbox.delete("1.0", "end")
        threading.Thread(target=worker, daemon=True).start()
        self._show_message("提示", "AI 分析和打包已开始，请查看日志...")

    def _build_with_ai_config(
        self,
        script_path: str,
        output_dir: str,
        name: str,
        ai_config: dict,
        callback
    ) -> bool:
        """使用 AI 配置进行打包"""
        import subprocess
        import sys

        try:
            script_path = os.path.abspath(script_path)
            work_dir = os.path.dirname(script_path)

            if not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)

            # 清理旧的 spec 文件和 build 目录，避免残留配置导致问题
            if name:
                old_spec = os.path.join(output_dir, f"{name}.spec")
                if os.path.exists(old_spec):
                    os.remove(old_spec)
                    if callback:
                        callback(f"[清理] 删除旧的 spec 文件: {old_spec}")

            build_dir = os.path.join(output_dir, "build")
            if os.path.exists(build_dir):
                import shutil
                shutil.rmtree(build_dir, ignore_errors=True)
                if callback:
                    callback(f"[清理] 删除旧的 build 目录")

            # 构建命令
            cmd = [sys.executable, "-m", "PyInstaller"]

            if self.onefile_var.get():
                cmd.append("--onefile")

            if self.noconsole_var.get():
                cmd.append("--noconsole")

            cmd.append("--clean")

            # 输出目录
            cmd.extend(["--distpath", output_dir])
            cmd.extend(["--workpath", build_dir])
            cmd.extend(["--specpath", output_dir])

            if name:
                cmd.extend(["--name", name])

            # 检查图标文件是否真实存在，支持自动转换图片格式
            icon = self.icon_path_var.get().strip()
            if icon:
                icon = os.path.abspath(icon)
                if os.path.exists(icon):
                    # 检查是否需要转换格式
                    ext = os.path.splitext(icon)[1].lower()
                    if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.gif']:
                        if callback:
                            callback(f"[图标] 检测到 {ext} 格式，正在转换为 ICO...")
                        try:
                            ico_path = self._convert_image_to_ico(icon, output_dir)
                            cmd.extend(["--icon", ico_path])
                            if callback:
                                callback(f"[图标] 转换成功: {ico_path}")
                        except Exception as e:
                            if callback:
                                callback(f"[警告] 图标转换失败: {e}")
                    elif ext == '.ico':
                        cmd.extend(["--icon", icon])
                        if callback:
                            callback(f"[图标] 使用图标: {icon}")
                    else:
                        if callback:
                            callback(f"[警告] 不支持的图标格式: {ext}")
                else:
                    if callback:
                        callback(f"[警告] 图标文件不存在，跳过: {icon}")
                    self.icon_path_var.set("")

            # 应用 AI 配置
            for module in ai_config.get("hidden_imports", []):
                cmd.extend(["--hidden-import", module])
                if callback:
                    callback(f"[AI] 添加隐藏导入: {module}")

            for package in ai_config.get("collect_data", []):
                cmd.extend(["--collect-data", package])
                if callback:
                    callback(f"[AI] 收集数据: {package}")

            for package in ai_config.get("collect_all", []):
                cmd.extend(["--collect-all", package])
                if callback:
                    callback(f"[AI] 完整收集: {package}")

            # 处理 add_data，修正路径
            for data in ai_config.get("add_data", []):
                if ":" in data or ";" in data:
                    # 分离源路径和目标路径
                    sep = ";" if ";" in data else ":"
                    parts = data.split(sep)
                    if len(parts) == 2:
                        src, dst = parts
                        # 如果源路径不是绝对路径，则相对于工作目录
                        if not os.path.isabs(src):
                            src = os.path.join(work_dir, src)
                        if os.path.exists(src):
                            # Windows 使用分号
                            cmd.extend(["--add-data", f"{src};{dst}"])
                            if callback:
                                callback(f"[AI] 添加数据: {src} -> {dst}")
                        else:
                            if callback:
                                callback(f"[跳过] 文件不存在: {src}")

            # 过滤掉不合理的 extra_args（避免与已有参数冲突）
            skip_prefixes = ("--onefile", "--onedir", "-F", "-D", "--name", "-n",
                           "--icon", "-i", "--windowed", "-w", "--console", "-c",
                           "--distpath", "--workpath", "--specpath", "--clean", "-y")
            for arg in ai_config.get("extra_args", []):
                # 跳过会与已有参数冲突的选项
                should_skip = False
                for prefix in skip_prefixes:
                    if arg.startswith(prefix):
                        should_skip = True
                        if callback:
                            callback(f"[跳过] 忽略冲突参数: {arg}")
                        break
                if not should_skip and arg not in cmd:
                    cmd.append(arg)
                    if callback:
                        callback(f"[AI] 额外参数: {arg}")

            cmd.append("-y")
            cmd.append(script_path)

            if callback:
                callback("")
                callback(f"[命令] {' '.join(cmd)}")
                callback("")

            # 执行
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                cwd=work_dir,
                env=env,
            )

            for line in process.stdout:
                line = line.strip()
                if line and callback:
                    callback(line)

            process.wait()

            success = process.returncode == 0
            if callback:
                if success:
                    exe_name = f"{name}.exe" if sys.platform == "win32" else name
                    exe_path = os.path.join(output_dir, exe_name)
                    callback("")
                    callback("=" * 50)
                    callback("✅ 打包成功！")
                    if os.path.exists(exe_path):
                        callback(f"📁 输出文件: {exe_path}")
                else:
                    callback(f"❌ 打包失败，返回码: {process.returncode}")

            return success

        except Exception as e:
            if callback:
                callback(f"❌ 打包错误: {e}")
            return False

    # ----------------------------------------------------------
    #                       状态栏
    # ----------------------------------------------------------

    def _build_statusbar(self):
        """构建状态栏 - 极简设计"""
        statusbar = ctk.CTkFrame(
            self,
            height=38,
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            corner_radius=10,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        statusbar.grid(row=3, column=0, sticky="ew", padx=32, pady=(8, 20))

        # 左侧状态
        left_container = ctk.CTkFrame(statusbar, fg_color="transparent")
        left_container.pack(side="left", padx=14, pady=8)

        # 状态指示灯
        self.status_dot = ctk.CTkFrame(
            left_container,
            width=7,
            height=7,
            corner_radius=4,
            fg_color=(self.colors["success"], self.colors["success"])
        )
        self.status_dot.pack(side="left", padx=(0, 8))

        self.status_label = ctk.CTkLabel(
            left_container,
            text="就绪",
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
        )
        self.status_label.pack(side="left")

        # 右侧版本
        ctk.CTkLabel(
            statusbar,
            text="7OZP1K v3.0 • AI编程助手",
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            font=ctk.CTkFont(size=10, family="Microsoft YaHei UI"),
        ).pack(side="right", padx=14)

    # ----------------------------------------------------------
    #                       事件处理
    # ----------------------------------------------------------

    def _on_language_changed(self, language: str):
        """语言变更事件"""
        lang_info = LANGUAGE_FRAMEWORKS.get(language, {})

        # 更新图标
        icon = lang_info.get("icon", "🌐")
        self.lang_icon_label.configure(text=icon)

        # 更新类别
        categories = list(lang_info.get("categories", {}).keys())
        self.category_menu.configure(values=categories)
        if categories:
            self.category_var.set(categories[0])
            self._on_category_changed(categories[0])

        # 保存设置
        self.settings["last_language"] = language

    def _on_category_changed(self, category: str):
        """框架类别变更事件"""
        language = self.language_var.get()
        lang_info = LANGUAGE_FRAMEWORKS.get(language, {})
        frameworks = lang_info.get("categories", {}).get(category, [])

        self.framework_menu.configure(values=frameworks)
        if frameworks:
            self.framework_var.set(frameworks[0])

    def _on_theme_changed(self, theme_key: str):
        """主题变更事件"""
        theme = THEMES.get(theme_key, THEMES["dark"])
        ctk.set_appearance_mode(theme["mode"])
        self.settings["theme"] = theme_key

        # 应用自定义背景色
        bg_color = theme.get("bg_color")
        if bg_color:
            self.configure(fg_color=bg_color)

    def _update_char_count(self, event=None):
        """更新字数统计"""
        text = self.idea_textbox.get("1.0", "end-1c")
        count = len(text.strip())
        self.char_count_label.configure(text=f"{count} 字")

    def _optimize_input(self):
        """AI优化用户输入 - 使用haiku 4.5专业优化文本"""
        text = self.idea_textbox.get("1.0", "end-1c").strip()

        if not text:
            self._show_message("提示", "请先输入需要优化的内容")
            return

        if not self.api_config.is_configured():
            self._show_message("错误", "请先在设置中配置API密钥")
            return

        # 禁用按钮防止重复点击
        self.optimize_btn.configure(state="disabled", text="优化中...")
        self.status_label.configure(text="AI优化中...")

        def worker():
            try:
                import anthropic

                # 使用haiku 4.5模型进行优化
                client = anthropic.Anthropic(
                    api_key=self.api_config.api_key,
                    base_url=self.api_config.base_url
                )

                optimize_prompt = f"""你是一个专业的技术文档优化专家。请将以下用户输入优化为更专业、清晰的技术需求描述。

要求：
1. 保持原意不变，不要添加用户没有提到的技术或功能
2. 使用专业术语，但保持简洁
3. 结构化表达，条理清晰
4. 字数控制在原文的1.2倍以内
5. 如果是中文就用中文回复，英文就用英文

用户原文：
{text}

请直接输出优化后的文本，不要包含任何解释或前言："""

                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",  # 使用haiku 4.5
                    max_tokens=1024,
                    messages=[
                        {"role": "user", "content": optimize_prompt}
                    ]
                )

                optimized_text = response.content[0].text.strip()

                def on_success():
                    # 更新文本框内容
                    self.idea_textbox.delete("1.0", "end")
                    self.idea_textbox.insert("1.0", optimized_text)
                    self._update_char_count()

                    self.optimize_btn.configure(state="normal", text="AI优化")
                    self.status_label.configure(text="✅ 输入已优化")

                self.after(0, on_success)

            except Exception as e:
                def on_error():
                    self.optimize_btn.configure(state="normal", text="AI优化")
                    self.status_label.configure(text="❌ 优化失败")
                    self._show_message("错误", f"优化失败: {str(e)}")

                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _update_api_status(self):
        """更新API状态"""
        if self.api_config.is_configured():
            self.api_status_label.configure(
                text="✅ 已配置",
                text_color=(self.colors["success"], self.colors["success"]),
            )
        else:
            self.api_status_label.configure(
                text="❌ 未配置",
                text_color=(self.colors["error"], self.colors["error"]),
            )

    # ----------------------------------------------------------
    #                       核心功能
    # ----------------------------------------------------------

    def _generate_prompt(self):
        """生成提示词"""
        # 检查功能权限（管理员跳过）
        if not self.is_admin and not self.code_manager.is_feature_unlocked("prompt"):
            self._show_message("权限不足", "此功能未解锁，请先输入兑换码激活")
            return

        if self._generating:
            return

        idea = self.idea_textbox.get("1.0", "end-1c").strip()
        if not idea:
            self._show_message("警告", "请输入项目描述")
            return

        if not self.api_config.is_configured():
            self._show_message("错误", "请先在设置中配置API密钥")
            return

        self._generating = True
        self.generate_btn.configure(state="disabled")
        self.progress_label.configure(text="正在生成...")
        self.status_label.configure(text="生成中...")

        # 收集项目信息(包括上传的文件)
        self.current_project_info = ProjectInfo(
            idea=idea,
            language=self.language_var.get(),
            category=self.category_var.get(),
            framework=self.framework_var.get(),
            priority=self.priority_var.get(),
            uploaded_files=self.uploaded_files.copy(),
        )

        def worker():
            try:
                prompt = self.prompt_service.generate(
                    self.current_project_info,
                    callback=lambda msg: self.after(
                        0, lambda: self.progress_label.configure(text=msg)
                    ),
                )

                def on_success():
                    self.current_prompt = prompt
                    self._display_prompt(prompt)
                    self._add_to_history()

                    self.status_label.configure(text="✅ 生成完成")
                    self.progress_label.configure(text="")
                    self._generating = False
                    self.generate_btn.configure(state="normal")

                    self._show_message("成功", "提示词已生成！可以复制使用了。")

                self.after(0, on_success)

            except Exception as e:
                def on_error():
                    self.status_label.configure(text="❌ 生成失败")
                    self.progress_label.configure(text="")
                    self._generating = False
                    self.generate_btn.configure(state="normal")
                    self._show_message("错误", str(e))

                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    def _display_prompt(self, prompt: str):
        """显示生成的提示词"""
        # 清空之前的分页，添加新的初始页
        self.conversation_pages = [{
            "title": "初始生成",
            "content": prompt
        }]
        self.current_page_index = 0
        self._update_page_display()

        # 自动切换到生成结果页面
        self._switch_content("output")

    def _add_followup_page(self, question: str, response: str):
        """添加追问页面"""
        page_num = len(self.conversation_pages)
        self.conversation_pages.append({
            "title": f"💬 追问 #{page_num}: {question[:20]}...",
            "content": response
        })
        self.current_page_index = len(self.conversation_pages) - 1
        self._update_page_display()

    def _update_page_display(self):
        """更新页面显示"""
        if not self.conversation_pages:
            self.output_textbox.configure(state="normal")
            self.output_textbox.delete("1.0", "end")
            self.output_textbox.configure(state="disabled")
            self.page_label.configure(text="0 / 0")
            self.page_title_label.configure(text="")
            self.prev_page_btn.configure(state="disabled")
            self.next_page_btn.configure(state="disabled")
            self.word_count_label.configure(text="字数: 0")
            self.line_count_label.configure(text="行数: 0")
            return

        # 获取当前页
        page = self.conversation_pages[self.current_page_index]
        content = page["content"]

        # 更新文本框
        self.output_textbox.configure(state="normal")
        self.output_textbox.delete("1.0", "end")
        self.output_textbox.insert("1.0", content)
        self.output_textbox.configure(state="disabled")

        # 更新页码
        total = len(self.conversation_pages)
        self.page_label.configure(text=f"{self.current_page_index + 1} / {total}")
        self.page_title_label.configure(text=page["title"])

        # 更新当前提示词（用于复制）
        self.current_prompt = content

        # 更新翻页按钮状态
        self.prev_page_btn.configure(
            state="normal" if self.current_page_index > 0 else "disabled"
        )
        self.next_page_btn.configure(
            state="normal" if self.current_page_index < total - 1 else "disabled"
        )

        # 更新统计
        self.word_count_label.configure(text=f"字数: {len(content)}")
        self.line_count_label.configure(text=f"行数: {len(content.splitlines())}")

    def _prev_page(self):
        """上一页"""
        if self.current_page_index > 0:
            self.current_page_index -= 1
            self._update_page_display()

    def _next_page(self):
        """下一页"""
        if self.current_page_index < len(self.conversation_pages) - 1:
            self.current_page_index += 1
            self._update_page_display()

    def _clear_pages(self):
        """清空所有页面"""
        self.conversation_pages = []
        self.current_page_index = 0
        self.current_prompt = ""
        self.prompt_service.reset_conversation()
        self._update_page_display()
        self.status_label.configure(text="✅ 已清空所有内容")

    def _copy_prompt(self):
        """复制提示词"""
        if not self.current_prompt:
            self._show_message("警告", "没有可复制的提示词")
            return

        self.clipboard_clear()
        self.clipboard_append(self.current_prompt)
        self.status_label.configure(text="✅ 已复制到剪贴板")

    def _get_website_names(self) -> list:
        """获取所有AI网站名称列表"""
        websites = DataManager.get_all_ai_websites()
        return list(websites.keys())

    def _copy_and_jump(self, website_name: str):
        """复制提示词并跳转到AI网站"""
        # 检查功能权限（管理员跳过）
        if not self.is_admin and not self.code_manager.is_feature_unlocked("jump"):
            self._show_message("权限不足", "复制跳转功能未解锁，请先输入兑换码激活")
            self.jump_website_menu.set("🚀 跳转")
            return

        import webbrowser

        if not self.current_prompt:
            self._show_message("警告", "没有可复制的提示词")
            self.jump_website_menu.set("🚀 跳转")
            return

        # 复制提示词
        self.clipboard_clear()
        self.clipboard_append(self.current_prompt)

        # 获取网站URL
        websites = DataManager.get_all_ai_websites()
        if website_name in websites:
            url = websites[website_name].get("url", "")
            if url:
                webbrowser.open(url)
                self.status_label.configure(text=f"✅ 已复制并跳转到 {website_name}")
            else:
                self._show_message("错误", f"网站 {website_name} 的URL为空")
        else:
            self._show_message("错误", f"未找到网站: {website_name}")

        # 重置下拉菜单显示
        self.jump_website_menu.set("🚀 跳转")

    def _refresh_website_menu(self):
        """刷新网站下拉菜单"""
        websites = self._get_website_names()
        self.jump_website_menu.configure(values=websites)
        self.jump_website_menu.set("🚀 跳转")

    def _add_favorite(self):
        """添加到收藏"""
        if not self.current_prompt:
            self._show_message("警告", "没有可收藏的提示词")
            return

        dialog = ctk.CTkInputDialog(
            text="请输入收藏名称:",
            title="添加收藏",
        )
        name = dialog.get_input()

        if name:
            record = FavoriteRecord(
                name=name,
                timestamp=datetime.now().isoformat(),
                language=self.current_project_info.language if self.current_project_info else "",
                framework=self.current_project_info.framework if self.current_project_info else "",
                prompt=self.current_prompt,
            )
            DataManager.add_favorite(record)
            self._show_message("成功", f"已添加到收藏: {name}")

    def _export_prompt(self):
        """导出提示词"""
        if not self.current_prompt:
            self._show_message("警告", "没有可导出的提示词")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[
                ("Markdown", "*.md"),
                ("文本文件", "*.txt"),
            ],
            initialfile=f"prompt_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        )

        if filepath:
            if FileService.export_text(self.current_prompt, filepath):
                self._show_message("成功", f"已导出到: {filepath}")
            else:
                self._show_message("错误", "导出失败")

    # ----------------------------------------------------------
    #                       模板功能
    # ----------------------------------------------------------

    def _use_template(self, name: str, template: dict):
        """使用模板"""
        content = template.get("content", "")
        self.idea_textbox.delete("1.0", "end")
        self.idea_textbox.insert("1.0", content)

        # 设置语言和框架
        if "language" in template:
            self.language_var.set(template["language"])
            self._on_language_changed(template["language"])

        if "framework" in template:
            self.framework_var.set(template["framework"])

        # 切换到新建项目标签页
        self.left_tabview.set("📝 新建项目")
        self._update_char_count()

    # ----------------------------------------------------------
    #                       历史记录
    # ----------------------------------------------------------

    def _add_to_history(self):
        """添加到历史记录"""
        if self.current_prompt and self.current_project_info:
            record = HistoryRecord(
                timestamp=datetime.now().isoformat(),
                language=self.current_project_info.language,
                framework=self.current_project_info.framework,
                idea_preview=self.current_project_info.idea[:50] + "...",
                prompt=self.current_prompt,
            )
            DataManager.add_history(record)
            self._refresh_history()

    def _refresh_history(self):
        """刷新历史记录"""
        # 清空现有内容
        for widget in self.history_frame.winfo_children():
            widget.destroy()

        history = DataManager.load_history()

        # 更新徽章数量
        if hasattr(self, 'history_count_badge'):
            self.history_count_badge.configure(text=f"{len(history)} 条记录")

        if not history:
            # 空状态提示
            empty_frame = ctk.CTkFrame(self.history_frame, fg_color="transparent")
            empty_frame.grid(row=0, column=0, sticky="nsew", pady=60)

            ctk.CTkLabel(
                empty_frame,
                text="📭",
                font=ctk.CTkFont(size=48)
            ).pack()

            ctk.CTkLabel(
                empty_frame,
                text="暂无历史记录",
                font=ctk.CTkFont(size=16, weight="bold", family="Microsoft YaHei UI"),
                text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
            ).pack(pady=(12, 4))

            ctk.CTkLabel(
                empty_frame,
                text="生成提示词后会自动保存到这里",
                font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
                text_color=(self.colors["text_muted"], self.colors["text_muted_dark"])
            ).pack()
            return

        # 倒序显示，最新的在前面
        for i, record in enumerate(reversed(history)):
            # 计算实际索引（因为是倒序，需要转换）
            actual_index = len(history) - 1 - i
            self._create_history_item(i, record, actual_index)

    def _create_history_item(self, row: int, record: dict, actual_index: int):
        """创建历史记录项 - UI-UX-PRO-MAX 高级风格"""
        item = ctk.CTkFrame(
            self.history_frame,
            fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            corner_radius=10,
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"])
        )
        item.grid(row=row, column=0, sticky="ew", padx=0, pady=6)
        item.grid_columnconfigure(1, weight=1)

        timestamp = record.get("timestamp", "")[:19].replace("T", " ")
        lang = record.get("language", "")
        preview = record.get("idea_preview", "")

        # 左侧时间图标
        time_frame = ctk.CTkFrame(
            item,
            width=50,
            height=50,
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            corner_radius=8
        )
        time_frame.grid(row=0, column=0, sticky="w", padx=16, pady=16)
        time_frame.grid_propagate(False)

        ctk.CTkLabel(
            time_frame,
            text="📜",
            font=ctk.CTkFont(size=22)
        ).place(relx=0.5, rely=0.5, anchor="center")

        # 中间信息区
        info_frame = ctk.CTkFrame(item, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="ew", padx=(0, 16), pady=16)

        # 标题行
        title_row = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_row.pack(fill="x")

        ctk.CTkLabel(
            title_row,
            text=timestamp,
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        # 语言标签
        if lang:
            ctk.CTkLabel(
                title_row,
                text=lang,
                font=ctk.CTkFont(size=9, family="Microsoft YaHei UI"),
                text_color="white",
                fg_color=self.colors["primary"],
                corner_radius=4,
                padx=6,
                pady=1
            ).pack(side="left", padx=(8, 0))

        # 预览内容
        ctk.CTkLabel(
            info_frame,
            text=preview if preview else "无描述",
            font=ctk.CTkFont(size=11, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            anchor="w"
        ).pack(fill="x", pady=(4, 0))

        # 右侧按钮区
        btn_frame = ctk.CTkFrame(item, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e", padx=16, pady=16)

        ctk.CTkButton(
            btn_frame,
            text="加载",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            width=70,
            height=34,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=lambda r=record: self._load_history_item(r),
        ).pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="🗑",
            font=ctk.CTkFont(size=14),
            width=40,
            height=34,
            corner_radius=8,
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            hover_color=self.colors["error"],
            text_color=(self.colors["text_muted"], self.colors["text_muted_dark"]),
            command=lambda idx=actual_index: self._delete_history_item(idx),
        ).pack(side="left")

    def _delete_history_item(self, index: int):
        """删除单条历史记录"""
        history = DataManager.load_history()
        if 0 <= index < len(history):
            deleted = history.pop(index)
            DataManager.save_history(history)
            self._refresh_history()
            preview = deleted.get("idea_preview", "")[:20]
            self._show_message("成功", f"已删除: {preview}...")

    def _load_history_item(self, record: dict):
        """加载历史记录项"""
        self.current_prompt = record.get("prompt", "")
        self._display_prompt(self.current_prompt)

    def _clear_history(self):
        """清空历史记录"""
        DataManager.clear_history()
        self._refresh_history()
        self._show_message("成功", "历史记录已清空")

    # ----------------------------------------------------------
    #                     PyInstaller 功能
    # ----------------------------------------------------------

    def _check_pyinstaller(self):
        """检查 PyInstaller 状态"""
        if PyInstallerService.is_installed():
            self.pyinstaller_status.configure(
                text="✅ PyInstaller 已安装",
                text_color="green",
            )
        else:
            self.pyinstaller_status.configure(
                text="❌ PyInstaller 未安装",
                text_color="red",
            )

    def _select_script(self):
        """选择脚本文件（支持多选）"""
        filepaths = filedialog.askopenfilenames(
            filetypes=[("Python文件", "*.py")],
        )
        if filepaths:
            # 多个文件用分号分隔
            self.script_path_var.set(";".join(filepaths))
            # 自动设置程序名（使用第一个文件名）
            name = Path(filepaths[0]).stem
            self.program_name_var.set(name)

    def _select_output_dir(self):
        """选择输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.output_dir_var.set(directory)

    def _select_icon(self):
        """选择图标文件（支持多种图片格式）"""
        filepath = filedialog.askopenfilename(
            filetypes=[
                ("图标和图片文件", "*.ico *.png *.jpg *.jpeg *.bmp *.gif"),
                ("ICO图标", "*.ico"),
                ("PNG图片", "*.png"),
                ("JPG图片", "*.jpg *.jpeg"),
                ("所有文件", "*.*"),
            ],
        )
        if filepath:
            self.icon_path_var.set(filepath)

    def _convert_image_to_ico(self, image_path: str, output_dir: str) -> str:
        """将图片转换为 ICO 格式"""
        try:
            from PIL import Image

            img = Image.open(image_path)

            # 转换为 RGBA 模式
            if img.mode != 'RGBA':
                img = img.convert('RGBA')

            # 生成多尺寸图标
            ico_path = os.path.join(output_dir, "app_icon.ico")

            # 创建多尺寸图标 (Windows 需要多种尺寸)
            sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
            icons = []
            for size in sizes:
                resized = img.resize(size, Image.Resampling.LANCZOS)
                icons.append(resized)

            # 保存为 ICO
            icons[0].save(
                ico_path,
                format='ICO',
                sizes=[(s.width, s.height) for s in icons],
                append_images=icons[1:]
            )

            return ico_path

        except ImportError:
            raise RuntimeError("需要安装 Pillow 库来转换图片: pip install Pillow")
        except Exception as e:
            raise RuntimeError(f"图片转换失败: {e}")

    def _open_output_dir(self):
        """打开输出目录"""
        output_dir = self.output_dir_var.get()
        if output_dir:
            FileService.open_directory(output_dir)

    def _start_packaging(self):
        """开始打包（支持多文件）"""
        # 检查功能权限（管理员跳过）
        if not self.is_admin and not self.code_manager.is_feature_unlocked("package"):
            self._show_message("权限不足", "PyInstaller打包功能未解锁\n需要专业版兑换码才能使用此功能")
            return

        script_paths_str = self.script_path_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        name = self.program_name_var.get().strip()

        # 清空日志并输出调试信息
        self.pack_log_textbox.delete("1.0", "end")
        self._append_pack_log("[DEBUG] ===== 打包参数检查 =====")
        self._append_pack_log(f"[DEBUG] 脚本路径: '{script_paths_str}'")
        self._append_pack_log(f"[DEBUG] 输出目录: '{output_dir}'")
        self._append_pack_log(f"[DEBUG] 程序名称: '{name}'")
        self._append_pack_log(f"[DEBUG] 单文件模式: {self.onefile_var.get()}")
        self._append_pack_log(f"[DEBUG] 无控制台: {self.noconsole_var.get()}")
        self._append_pack_log(f"[DEBUG] 图标路径: '{self.icon_path_var.get()}'")

        if not script_paths_str:
            self._show_message("警告", "请选择 Python 脚本")
            self._append_pack_log("[ERROR] 未选择 Python 脚本")
            return

        if not output_dir:
            self._show_message("警告", "请选择输出目录")
            self._append_pack_log("[ERROR] 未选择输出目录")
            return

        if not PyInstallerService.is_installed():
            self._show_message("错误", "请先安装 PyInstaller")
            self._append_pack_log("[ERROR] PyInstaller 未安装")
            return

        # 解析多个文件路径（用分号分隔）
        script_paths = [p.strip() for p in script_paths_str.split(";") if p.strip()]
        main_script = script_paths[0]
        additional_files = script_paths[1:] if len(script_paths) > 1 else []

        self._append_pack_log(f"[DEBUG] 主脚本: {main_script}")
        self._append_pack_log(f"[DEBUG] 附加文件: {additional_files}")
        self._append_pack_log("[DEBUG] ===== 开始打包 =====")

        def log_callback(msg):
            self.after(0, lambda: self._append_pack_log(msg))

        def worker():
            success = PyInstallerService.build(
                script_path=main_script,
                output_dir=output_dir,
                name=name,
                onefile=self.onefile_var.get(),
                noconsole=self.noconsole_var.get(),
                icon=self.icon_path_var.get(),
                additional_files=additional_files,
                callback=log_callback,
            )

            def on_complete():
                if success:
                    self._show_message("成功", f"打包完成！\n输出目录: {output_dir}")
                else:
                    self._show_message("失败", "打包失败，请查看日志")

            self.after(0, on_complete)

        threading.Thread(target=worker, daemon=True).start()
        self._show_message("提示", "打包已开始，请查看日志...")

    def _append_pack_log(self, msg: str):
        """追加打包日志"""
        self.pack_log_textbox.insert("end", msg + "\n")
        self.pack_log_textbox.see("end")

    # ----------------------------------------------------------
    #                   文件上传功能
    # ----------------------------------------------------------

    def _setup_drag_drop(self):
        """设置拖拽上传功能"""
        try:
            # 尝试使用 tkinterdnd2
            from tkinterdnd2 import DND_FILES, TkinterDnD

            # 注册拖拽目标
            self.drop_frame.drop_target_register(DND_FILES)
            self.drop_frame.dnd_bind('<<Drop>>', self._on_drop)
            self.drop_frame.dnd_bind('<<DragEnter>>', self._on_drag_enter)
            self.drop_frame.dnd_bind('<<DragLeave>>', self._on_drag_leave)

            self.drop_label.configure(text="📂 拖拽文件到此处上传\n支持多文件")
            logger.info("拖拽上传功能已启用 (tkinterdnd2)")

        except (ImportError, Exception) as e:
            # tkinterdnd2 未安装或不兼容，使用备用方案
            logger.info(f"拖拽功能不可用 ({e})，使用点击选择方案")
            self.drop_label.configure(text="📂 点击此处选择文件\n或 Ctrl+V 粘贴文件路径")

            # 绑定粘贴事件
            self.bind("<Control-v>", self._on_paste_files)
            self.drop_frame.bind("<Control-v>", self._on_paste_files)

    def _on_drop(self, event):
        """处理拖拽放下事件"""
        files = event.data
        # 解析文件路径（可能包含大括号）
        if files.startswith('{'):
            # 多个文件
            file_list = []
            current = ""
            in_braces = False
            for char in files:
                if char == '{':
                    in_braces = True
                elif char == '}':
                    in_braces = False
                    if current:
                        file_list.append(current)
                        current = ""
                elif in_braces:
                    current += char
                elif char == ' ' and not in_braces:
                    if current:
                        file_list.append(current)
                        current = ""
                else:
                    current += char
            if current:
                file_list.append(current)
        else:
            file_list = files.split()

        self._process_dropped_files(file_list)
        self._on_drag_leave(None)

    def _on_drag_enter(self, event):
        """拖拽进入事件"""
        self.drop_frame.configure(
            border_color=("green", "lightgreen"),
            fg_color=("gray80", "gray30")
        )
        self.drop_label.configure(text="📥 释放以上传文件")

    def _on_drag_leave(self, event):
        """拖拽离开事件"""
        self.drop_frame.configure(
            border_color=("gray70", "gray40"),
            fg_color=("gray85", "gray25")
        )
        self.drop_label.configure(text="📂 拖拽文件到此处上传\n支持多文件")

    def _on_paste_files(self, event):
        """处理粘贴文件路径"""
        try:
            clipboard = self.clipboard_get()
            # 尝试解析为文件路径
            lines = clipboard.strip().split('\n')
            valid_files = []
            for line in lines:
                path = line.strip().strip('"')
                if Path(path).exists() and Path(path).is_file():
                    valid_files.append(path)

            if valid_files:
                self._process_dropped_files(valid_files)
                self.status_label.configure(text=f"✅ 已粘贴 {len(valid_files)} 个文件")
        except Exception as e:
            logger.debug(f"粘贴处理失败: {e}")

    def _process_dropped_files(self, file_paths: list):
        """处理拖拽/粘贴的文件"""
        for filepath in file_paths:
            try:
                filepath = filepath.strip()
                if not filepath:
                    continue

                path = Path(filepath)
                if not path.exists() or not path.is_file():
                    continue

                # 读取文件内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 限制文件大小 (最大 1MB)
                if len(content) > 1024 * 1024:
                    self._show_message("警告", f"文件 {path.name} 过大，已跳过（最大1MB）")
                    continue

                # 添加到上传列表
                file_info = {
                    'filename': path.name,
                    'content': content,
                    'file_type': path.suffix,
                    'size': len(content),
                }
                self.uploaded_files.append(file_info)

            except Exception as e:
                logger.error(f"处理文件失败 {filepath}: {e}")

        self._update_files_display()

    def _select_files(self):
        """选择文件"""
        filetypes = [
            ("所有文件", "*.*"),
            ("文本文件", "*.txt"),
            ("Python文件", "*.py"),
            ("JavaScript文件", "*.js"),
            ("JSON文件", "*.json"),
            ("Markdown文件", "*.md"),
        ]

        filepaths = filedialog.askopenfilenames(filetypes=filetypes)

        for filepath in filepaths:
            try:
                # 读取文件内容
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 限制文件大小 (最大 1MB)
                if len(content) > 1024 * 1024:
                    self._show_message("警告", f"文件 {Path(filepath).name} 过大，已跳过（最大1MB）")
                    continue

                # 添加到上传列表
                file_info = {
                    'filename': Path(filepath).name,
                    'content': content,
                    'file_type': Path(filepath).suffix,
                    'size': len(content),
                }
                self.uploaded_files.append(file_info)

            except Exception as e:
                self._show_message("错误", f"读取文件 {Path(filepath).name} 失败: {str(e)}")

        self._update_files_display()

    def _clear_files(self):
        """清空文件列表"""
        self.uploaded_files.clear()
        self._update_files_display()

    def _update_files_display(self):
        """更新文件列表显示"""
        self.files_listbox.configure(state="normal")
        self.files_listbox.delete("1.0", "end")

        if not self.uploaded_files:
            self.files_listbox.insert("1.0", "暂无文件上传")
        else:
            lines = []
            for i, file_info in enumerate(self.uploaded_files, 1):
                filename = file_info.get('filename', '未知')
                size = file_info.get('size', 0)
                size_kb = size / 1024
                lines.append(f"{i}. {filename} ({size_kb:.1f} KB)")
            self.files_listbox.insert("1.0", "\n".join(lines))

        self.files_listbox.configure(state="disabled")

    # ----------------------------------------------------------
    #                   追问功能
    # ----------------------------------------------------------

    def _send_followup(self):
        """发送追问"""
        if self._generating:
            return

        question = self.followup_entry.get().strip()
        if not question:
            self._show_message("警告", "请输入追问内容")
            return

        if not self.conversation_pages:
            self._show_message("警告", "请先生成提示词")
            return

        if not self.api_config.is_configured():
            self._show_message("错误", "请先在设置中配置API密钥")
            return

        self._generating = True
        self.followup_btn.configure(state="disabled")
        self.generate_btn.configure(state="disabled")
        self.status_label.configure(text="追问中...")

        # 保存问题用于回调
        saved_question = question

        def worker():
            try:
                # 调用追问接口
                response = self.prompt_service.followup(
                    question=saved_question,
                    callback=lambda msg: self.after(
                        0, lambda: self.status_label.configure(text=msg)
                    ),
                )

                def on_success():
                    # 添加新的追问页面
                    self._add_followup_page(saved_question, response)

                    # 清空输入框
                    self.followup_entry.delete(0, "end")

                    self.status_label.configure(text="✅ 追问完成")
                    self._generating = False
                    self.followup_btn.configure(state="normal")
                    self.generate_btn.configure(state="normal")

                self.after(0, on_success)

            except Exception as e:
                def on_error():
                    self.status_label.configure(text="❌ 追问失败")
                    self._generating = False
                    self.followup_btn.configure(state="normal")
                    self.generate_btn.configure(state="normal")
                    self._show_message("错误", str(e))

                self.after(0, on_error)

        threading.Thread(target=worker, daemon=True).start()

    # ----------------------------------------------------------
    #                   快捷片段功能
    # ----------------------------------------------------------

    def _refresh_snippets(self):
        """刷新快捷片段列表"""
        # 清空现有内容
        for widget in self.snippets_frame.winfo_children():
            widget.destroy()

        # 获取搜索条件
        keyword = self.snippet_search_var.get().strip()
        category = self.snippet_category_var.get()
        if category == "全部":
            category = ""

        # 搜索片段
        snippets = DataManager.search_snippets(keyword, category)

        if not snippets:
            ctk.CTkLabel(
                self.snippets_frame,
                text="没有找到匹配的片段",
                text_color="gray",
            ).grid(row=0, column=0, pady=20)
            return

        # 显示片段卡片
        for i, (name, snippet) in enumerate(snippets.items()):
            self._create_snippet_card(i, name, snippet)

    def _create_snippet_card(self, row: int, name: str, snippet: dict):
        """创建片段卡片"""
        is_preset = snippet.get("is_preset", False)
        category = snippet.get("category", "其他")
        content = snippet.get("content", "")

        card = ctk.CTkFrame(self.snippets_frame)
        card.grid(row=row, column=0, sticky="ew", padx=5, pady=3)
        card.grid_columnconfigure(1, weight=1)

        # 左侧标题和分类
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        # 标题行
        title_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        title_frame.pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text=f"{'🔒 ' if is_preset else '📝 '}{name}",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left")

        # 分类标签
        ctk.CTkLabel(
            title_frame,
            text=f"  [{category}]",
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).pack(side="left")

        # 内容预览
        preview = content[:60] + "..." if len(content) > 60 else content
        ctk.CTkLabel(
            info_frame,
            text=preview,
            font=ctk.CTkFont(size=10),
            text_color="gray",
        ).pack(anchor="w")

        # 右侧按钮
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=10, pady=5)

        # 应用按钮
        ctk.CTkButton(
            btn_frame,
            text="应用",
            width=60,
            command=lambda n=name, c=content: self._apply_snippet(n, c),
        ).pack(side="left", padx=2)

        # 编辑按钮（仅自定义片段）
        if not is_preset:
            ctk.CTkButton(
                btn_frame,
                text="编辑",
                width=60,
                command=lambda n=name, s=snippet: self._edit_snippet_dialog(n, s),
            ).pack(side="left", padx=2)

            ctk.CTkButton(
                btn_frame,
                text="删除",
                width=60,
                fg_color="red",
                hover_color="darkred",
                command=lambda n=name: self._delete_snippet(n),
            ).pack(side="left", padx=2)

    def _add_snippet_dialog(self):
        """添加片段对话框"""
        SnippetDialog(self, mode="add", callback=self._refresh_snippets)

    def _edit_snippet_dialog(self, name: str, snippet: dict):
        """编辑片段对话框"""
        SnippetDialog(
            self,
            mode="edit",
            name=name,
            snippet=snippet,
            callback=self._refresh_snippets
        )

    def _delete_snippet(self, name: str):
        """删除片段"""
        # 确认对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("确认删除")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 150) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text=f"确定要删除片段 \"{name}\" 吗？",
            font=ctk.CTkFont(size=14),
        ).pack(pady=30)

        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=10)

        def confirm():
            if DataManager.delete_snippet(name):
                self._refresh_snippets()
                self._show_message("成功", f"片段 \"{name}\" 已删除")
            else:
                self._show_message("错误", "删除失败")
            dialog.destroy()

        ctk.CTkButton(
            btn_frame,
            text="确定",
            fg_color="red",
            command=confirm,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="取消",
            command=dialog.destroy,
        ).pack(side="left", padx=10)

    def _apply_snippet(self, name: str, content: str):
        """应用片段到项目描述"""
        current_text = self.idea_textbox.get("1.0", "end-1c").strip()

        if current_text:
            # 追加到现有内容
            new_text = f"{current_text}\n\n【{name}】\n{content}"
        else:
            new_text = f"【{name}】\n{content}"

        self.idea_textbox.delete("1.0", "end")
        self.idea_textbox.insert("1.0", new_text)
        self._update_char_count()

        # 切换到新建项目标签页
        self.left_tabview.set("📝 新建项目")
        self.status_label.configure(text=f"✅ 已应用片段: {name}")

    # ----------------------------------------------------------
    #                       对话框
    # ----------------------------------------------------------

    def _show_settings(self):
        """显示设置窗口"""
        SettingsDialog(self, self.settings, self.api_config, self.prompt_service)

    def _show_help(self):
        """显示帮助"""
        HelpDialog(self)

    def _show_message(self, title: str, message: str):
        """显示消息"""
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("400x200")
        dialog.transient(self)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 400) // 2
        y = self.winfo_y() + (self.winfo_height() - 200) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(
            dialog,
            text=title,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(pady=20)

        ctk.CTkLabel(
            dialog,
            text=message,
            wraplength=350,
        ).pack(pady=10)

        ctk.CTkButton(
            dialog,
            text="确定",
            command=dialog.destroy,
        ).pack(pady=20)

    def _on_closing(self):
        """关闭事件"""
        DataManager.save_settings(self.settings)
        self.destroy()


# ============================================================
#                      设置对话框
# ============================================================

class SettingsDialog(ctk.CTkToplevel):
    """设置对话框"""

    def __init__(
        self,
        parent,
        settings: dict,
        api_config: APIConfig,
        prompt_service: PromptGeneratorService,
    ):
        super().__init__(parent)

        self.settings = settings
        self.api_config = api_config
        self.prompt_service = prompt_service
        self.parent = parent

        self.title("⚙️ 设置")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """构建界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 标签页
        tabview = ctk.CTkTabview(self)
        tabview.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        # API 设置
        tab_api = tabview.add("🔑 API配置")
        self._build_api_tab(tab_api)

        # 其他设置
        tab_other = tabview.add("⚙️ 其他")
        self._build_other_tab(tab_other)

        # 按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="保存",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            command=self._save,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="取消",
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=self.destroy,
        ).pack(side="left", padx=5)

    def _build_api_tab(self, parent):
        """构建API设置标签页"""
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            parent,
            text="Anthropic API 配置",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # API Key
        ctk.CTkLabel(parent, text="API密钥:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )

        self.api_key_entry = ctk.CTkEntry(
            parent,
            show="•",
            width=400,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        )
        self.api_key_entry.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        if self.api_config.api_key:
            self.api_key_entry.insert(0, self.api_config.api_key)

        # Base URL
        ctk.CTkLabel(parent, text="API地址:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )

        self.base_url_entry = ctk.CTkEntry(
            parent,
            width=400,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        )
        self.base_url_entry.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.base_url_entry.insert(0, self.api_config.base_url)

        # Model
        ctk.CTkLabel(parent, text="模型:").grid(
            row=5, column=0, sticky="w", padx=10, pady=5
        )

        self.model_var = ctk.StringVar(value=self.api_config.model)
        ctk.CTkOptionMenu(
            parent,
            values=AVAILABLE_MODELS,
            variable=self.model_var,
            width=300,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            button_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            button_hover_color=self.colors["primary"],
            dropdown_fg_color=(self.colors["bg_base"], self.colors["bg_base_dark"]),
            dropdown_hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"])
        ).grid(row=6, column=0, sticky="w", padx=10, pady=5)

        # 提示
        ctk.CTkLabel(
            parent,
            text="💡 获取API密钥: https://console.anthropic.com/",
            text_color="gray",
        ).grid(row=7, column=0, sticky="w", padx=10, pady=10)

        ctk.CTkButton(
            parent,
            text="🔗 打开 Anthropic 控制台",
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            text_color=(self.colors["primary"], self.colors["primary_light"]),
            border_width=1,
            border_color=(self.colors["border"], self.colors["border_dark"]),
            command=lambda: webbrowser.open("https://console.anthropic.com/"),
        ).grid(row=8, column=0, sticky="w", padx=10, pady=5)

    def _build_other_tab(self, parent):
        """构建其他设置标签页"""
        parent.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            parent,
            text="其他设置",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # PyInstaller 输出目录
        ctk.CTkLabel(parent, text="PyInstaller 默认输出目录:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )

        dir_frame = ctk.CTkFrame(parent, fg_color="transparent")
        dir_frame.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.default_output_var = ctk.StringVar(
            value=self.settings.get("pyinstaller_output_dir", "")
        )
        ctk.CTkEntry(
            dir_frame,
            textvariable=self.default_output_var,
            width=300,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_elevated"], self.colors["bg_elevated_dark"]),
            border_color=(self.colors["border"], self.colors["border_dark"]),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"])
        ).pack(side="left")

        ctk.CTkButton(
            dir_frame,
            text="选择",
            width=60,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            fg_color=(self.colors["bg_hover"], self.colors["bg_hover_dark"]),
            hover_color=self.colors["primary"],
            text_color=(self.colors["text_secondary"], self.colors["text_secondary_dark"]),
            command=self._select_default_output,
        ).pack(side="left", padx=5)

        # 自动保存
        self.auto_save_var = ctk.BooleanVar(
            value=self.settings.get("auto_save", True)
        )
        ctk.CTkCheckBox(
            parent,
            text="自动保存历史记录",
            variable=self.auto_save_var,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI"),
            text_color=(self.colors["text_primary"], self.colors["text_primary_dark"]),
            fg_color=self.colors["primary"],
            hover_color=self.colors["primary_hover"],
            checkmark_color="white",
            border_color=(self.colors["border"], self.colors["border_dark"])
        ).grid(row=3, column=0, sticky="w", padx=10, pady=10)

    def _select_default_output(self):
        """选择默认输出目录"""
        directory = filedialog.askdirectory()
        if directory:
            self.default_output_var.set(directory)

    def _save(self):
        """保存设置"""
        # 更新 API 配置
        self.api_config.api_key = self.api_key_entry.get().strip()
        self.api_config.base_url = self.base_url_entry.get().strip()
        self.api_config.model = self.model_var.get()
        self.prompt_service.reset_client()

        # 更新设置
        self.settings["api_key"] = self.api_config.api_key
        self.settings["base_url"] = self.api_config.base_url
        self.settings["model"] = self.api_config.model
        self.settings["pyinstaller_output_dir"] = self.default_output_var.get()
        self.settings["auto_save"] = self.auto_save_var.get()

        DataManager.save_settings(self.settings)
        self.parent._update_api_status()

        self.destroy()


# ============================================================
#                      帮助对话框
# ============================================================

class HelpDialog(ctk.CTkToplevel):
    """帮助对话框"""

    def __init__(self, parent):
        super().__init__(parent)

        self.title("❓ 帮助")
        self.geometry("700x600")
        self.transient(parent)

        self._build_ui()

    def _build_ui(self):
        """构建界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12),
            wrap="word",
        )
        textbox.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

        help_text = """
🚀 AI编程助手 v3.0 - 快速开始指南

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 第一步：配置 API 密钥

1. 点击右上角 "⚙️ 设置" 按钮
2. 在 API 配置中输入你的 Anthropic API Key
3. 如使用第三方 API，可修改 API 地址
4. 选择模型（推荐 claude-haiku-4-5-20251001）
5. 点击 "保存"

💡 获取 API 密钥：https://console.anthropic.com/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 第二步：生成提示词

1. 选择编程语言（如 Python）
2. 选择框架类别和具体框架
3. 选择开发优先级
4. 在项目描述框中详细描述需求
5. 点击 "🚀 生成提示词"
6. 复制生成的提示词到 Claude Code

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 第三步：使用模板（可选）

1. 切换到 "📚 模板库" 标签页
2. 选择合适的项目模板
3. 点击 "使用模板" 自动填充
4. 根据需要修改内容
5. 生成提示词

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 第四步：PyInstaller 打包

1. 切换到 "📦 PyInstaller打包" 标签页
2. 选择要打包的 Python 脚本
3. 配置输出目录和程序名称
4. 选择打包选项
5. 点击 "🚀 开始打包"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 提示与技巧

✅ 项目描述越详细，生成的提示词质量越高
✅ 可以使用模板作为起点，然后修改
✅ 生成的提示词会自动保存到历史记录
✅ 重要的提示词可以添加到收藏
✅ GUI 程序打包时勾选 "无控制台窗口"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 主题切换

使用右上角的下拉菜单可以切换主题：
• dark - 深色主题
• light - 浅色主题
• green - 绿色主题

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        textbox.insert("1.0", help_text)
        textbox.configure(state="disabled")

        ctk.CTkButton(
            self,
            text="关闭",
            command=self.destroy,
        ).grid(row=1, column=0, pady=10)


# ============================================================
#                     片段编辑对话框
# ============================================================

class SnippetDialog(ctk.CTkToplevel):
    """片段添加/编辑对话框"""

    def __init__(
        self,
        parent,
        mode: str = "add",
        name: str = "",
        snippet: dict = None,
        callback=None
    ):
        super().__init__(parent)

        self.parent = parent
        self.mode = mode
        self.original_name = name
        self.snippet = snippet or {}
        self.callback = callback

        self.title("添加片段" if mode == "add" else "编辑片段")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        """构建界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 名称
        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))
        name_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(name_frame, text="片段名称:").grid(row=0, column=0, sticky="w", padx=5)
        self.name_entry = ctk.CTkEntry(name_frame, width=300)
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        if self.mode == "edit":
            self.name_entry.insert(0, self.original_name)
            self.name_entry.configure(state="disabled")  # 编辑时不能改名

        # 分类
        category_frame = ctk.CTkFrame(self, fg_color="transparent")
        category_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        category_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(category_frame, text="分类:").grid(row=0, column=0, sticky="w", padx=5)
        self.category_var = ctk.StringVar(
            value=self.snippet.get("category", SNIPPET_CATEGORIES[0])
        )
        ctk.CTkOptionMenu(
            category_frame,
            values=SNIPPET_CATEGORIES,
            variable=self.category_var,
            width=200,
        ).grid(row=0, column=1, sticky="w", padx=5)

        # 内容
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(content_frame, text="片段内容:").grid(row=0, column=0, sticky="w", padx=5)
        self.content_textbox = ctk.CTkTextbox(content_frame, font=ctk.CTkFont(size=12))
        self.content_textbox.grid(row=1, column=0, sticky="nsew", pady=5)
        if self.snippet.get("content"):
            self.content_textbox.insert("1.0", self.snippet["content"])

        # 按钮
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="保存",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            command=self._save,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="取消",
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            width=80,
            height=36,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#E4E4E7", "#27272A"),
            text_color=("#52525B", "#A1A1AA"),
            border_width=1,
            border_color=("#E4E4E7", "#27272A"),
            command=self.destroy,
        ).pack(side="left", padx=10)

    def _save(self):
        """保存片段"""
        name = self.name_entry.get().strip()
        category = self.category_var.get()
        content = self.content_textbox.get("1.0", "end-1c").strip()

        if not name:
            self._show_error("请输入片段名称")
            return

        if not content:
            self._show_error("请输入片段内容")
            return

        if self.mode == "add":
            if DataManager.add_snippet(name, category, content):
                self._show_success("片段添加成功")
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                self._show_error("添加失败，可能名称已存在或与预置片段冲突")
        else:
            if DataManager.update_snippet(name, category, content):
                self._show_success("片段更新成功")
                if self.callback:
                    self.callback()
                self.destroy()
            else:
                self._show_error("更新失败")

    def _show_error(self, message: str):
        """显示错误提示"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("错误")
        dialog.geometry("300x120")
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text=message, text_color="red").pack(pady=30)
        ctk.CTkButton(dialog, text="确定", command=dialog.destroy).pack()

    def _show_success(self, message: str):
        """显示成功提示"""
        self.parent.status_label.configure(text=f"✅ {message}")


# ============================================================
#                     模板编辑对话框
# ============================================================

class TemplateDialog(ctk.CTkToplevel):
    """模板添加对话框"""

    def __init__(self, parent, callback=None):
        super().__init__(parent)

        self.parent = parent
        self.callback = callback

        self.title("➕ 添加模板")
        self.geometry("600x550")
        self.transient(parent)
        self.grab_set()

        # 居中显示
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 550) // 2
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _build_ui(self):
        """构建界面"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        # 模板名称
        name_frame = ctk.CTkFrame(self, fg_color="transparent")
        name_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 5))
        name_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(name_frame, text="模板名称:", font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")).grid(row=0, column=0, sticky="w", padx=5)
        self.name_entry = ctk.CTkEntry(
            name_frame,
            placeholder_text="如: 电商网站",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")
        )
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # 模板描述
        desc_frame = ctk.CTkFrame(self, fg_color="transparent")
        desc_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        desc_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(desc_frame, text="模板描述:", font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")).grid(row=0, column=0, sticky="w", padx=5)
        self.desc_entry = ctk.CTkEntry(
            desc_frame,
            placeholder_text="简短描述模板用途",
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")
        )
        self.desc_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # 语言和框架
        tech_frame = ctk.CTkFrame(self, fg_color="transparent")
        tech_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        tech_frame.grid_columnconfigure(1, weight=1)
        tech_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(tech_frame, text="编程语言:", font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")).grid(row=0, column=0, sticky="w", padx=5)
        self.lang_var = ctk.StringVar(value="Python")
        ctk.CTkOptionMenu(
            tech_frame,
            values=list(LANGUAGE_FRAMEWORKS.keys()),
            variable=self.lang_var,
            command=self._on_lang_changed,
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")
        ).grid(row=0, column=1, sticky="w", padx=5)

        ctk.CTkLabel(tech_frame, text="框架:", font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")).grid(row=0, column=2, sticky="w", padx=5)
        self.framework_var = ctk.StringVar()
        self.framework_menu = ctk.CTkOptionMenu(
            tech_frame,
            values=[""],
            variable=self.framework_var,
            width=150,
            height=36,
            corner_radius=8,
            font=ctk.CTkFont(size=12, family="Microsoft YaHei UI")
        )
        self.framework_menu.grid(row=0, column=3, sticky="w", padx=5)

        # 初始化框架列表
        self._on_lang_changed("Python")

        # 模板内容标签
        content_label = ctk.CTkFrame(self, fg_color="transparent")
        content_label.grid(row=3, column=0, sticky="ew", padx=20, pady=(10, 0))

        ctk.CTkLabel(
            content_label,
            text="模板内容:",
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            content_label,
            text="(描述项目需求，支持Markdown格式)",
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=5)

        # 模板内容文本框
        self.content_textbox = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=12),
            wrap="word",
        )
        self.content_textbox.grid(row=4, column=0, sticky="nsew", padx=20, pady=5)

        # 插入默认模板格式
        default_content = """【项目描述】
- [描述项目的主要用途和目标]

【核心功能】
1. [功能1]
2. [功能2]
3. [功能3]

【技术要求】
- [技术要求1]
- [技术要求2]

【其他说明】
- [补充说明]"""
        self.content_textbox.insert("1.0", default_content)

        # 按钮区域
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="保存模板",
            font=ctk.CTkFont(size=13, weight="bold", family="Microsoft YaHei UI"),
            width=100,
            height=38,
            corner_radius=8,
            command=self._save,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="取消",
            font=ctk.CTkFont(size=13, family="Microsoft YaHei UI"),
            width=80,
            height=38,
            corner_radius=8,
            fg_color="transparent",
            hover_color=("#E4E4E7", "#27272A"),
            text_color=("#52525B", "#A1A1AA"),
            border_width=1,
            border_color=("#E4E4E7", "#27272A"),
            command=self.destroy,
        ).pack(side="left", padx=10)

    def _on_lang_changed(self, lang: str):
        """语言变更事件"""
        lang_info = LANGUAGE_FRAMEWORKS.get(lang, {})
        categories = lang_info.get("categories", {})

        # 收集所有框架
        all_frameworks = []
        for cat_frameworks in categories.values():
            all_frameworks.extend(cat_frameworks)

        # 去重
        all_frameworks = list(dict.fromkeys(all_frameworks))

        self.framework_menu.configure(values=all_frameworks)
        if all_frameworks:
            self.framework_var.set(all_frameworks[0])

    def _save(self):
        """保存模板"""
        name = self.name_entry.get().strip()
        description = self.desc_entry.get().strip()
        language = self.lang_var.get()
        framework = self.framework_var.get()
        content = self.content_textbox.get("1.0", "end-1c").strip()

        if not name:
            self._show_error("请输入模板名称")
            return

        if not content:
            self._show_error("请输入模板内容")
            return

        # 检查是否与默认模板重名
        if name in DEFAULT_TEMPLATES:
            self._show_error("不能使用与内置模板相同的名称")
            return

        # 保存模板
        templates = DataManager.load_templates()
        templates[name] = {
            "description": description or "自定义模板",
            "language": language,
            "framework": framework,
            "content": content,
        }

        if DataManager.save_templates(templates):
            self.parent.status_label.configure(text=f"✅ 模板 \"{name}\" 已保存")
            if self.callback:
                self.callback()
            self.destroy()
        else:
            self._show_error("保存失败")

    def _show_error(self, message: str):
        """显示错误提示"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("错误")
        dialog.geometry("300x120")
        dialog.transient(self)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 300) // 2
        y = self.winfo_y() + (self.winfo_height() - 120) // 2
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text=message, text_color="red").pack(pady=30)
        ctk.CTkButton(dialog, text="确定", command=dialog.destroy).pack()