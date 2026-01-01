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
    """主应用程序"""

    def __init__(self):
        super().__init__()

        # 兑换码管理器
        self.code_manager = get_code_manager()

        # 加载设置
        self.settings = DataManager.load_settings()

        # 设置主题
        theme_key = self.settings.get("theme", "dark")
        self._current_theme = THEMES.get(theme_key, THEMES["dark"])
        ctk.set_appearance_mode(self._current_theme["mode"])
        ctk.set_default_color_theme(self._current_theme["color_theme"])

        # 窗口配置
        self.title("💢7OZP1K编程助手💬vx:AE86-1w")
        self.geometry("1400x900")
        self.minsize(1200, 800)

        # 初始化服务
        self.api_config = APIConfig(
            api_key=self.settings.get("api_key", ""),
            base_url=self.settings.get("base_url", "https://api.anthropic.com"),
            model=self.settings.get("model", "claude-haiku-4-5-20251001"),
        )
        self.prompt_service = PromptGeneratorService(self.api_config)

        # 状态变量
        self.current_prompt = ""
        self.current_project_info: Optional[ProjectInfo] = None
        self._generating = False
        self.uploaded_files: list = []  # 上传的文件列表
        self.conversation_pages: list = []  # 对话分页列表 [{"title": "...", "content": "..."}]
        self.current_page_index = 0  # 当前页码

        # 检查是否已激活
        if not self.code_manager.get_unlocked_features():
            # 未激活，显示兑换码输入界面
            self._show_activation_screen()
        else:
            # 已激活，构建主界面
            self._build_ui()

        # 应用自定义背景色
        bg_color = self._current_theme.get("bg_color")
        if bg_color:
            self.configure(fg_color=bg_color)

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _show_activation_screen(self):
        """显示激活界面"""
        # 清空窗口
        for widget in self.winfo_children():
            widget.destroy()

        self.geometry("600x550")
        self.minsize(600, 550)

        # 居中容器
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True)

        center = ctk.CTkFrame(container, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # 图标
        ctk.CTkLabel(center, text="🔐", font=ctk.CTkFont(size=72)).pack(pady=(0, 15))

        # 标题
        ctk.CTkLabel(
            center,
            text="7OZP1K编程助手",
            font=ctk.CTkFont(size=28, weight="bold"),
        ).pack(pady=(0, 8))

        # 说明
        ctk.CTkLabel(
            center,
            text="请输入兑换码激活软件",
            font=ctk.CTkFont(size=15),
            text_color="gray",
        ).pack(pady=(0, 25))

        # 兑换码输入框
        self.activation_code_var = ctk.StringVar()
        code_entry = ctk.CTkEntry(
            center,
            textvariable=self.activation_code_var,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(family="Consolas", size=18),
            width=350,
            height=50,
            justify="center",
        )
        code_entry.pack(pady=(0, 12))
        code_entry.bind("<Return>", lambda e: self._activate())

        # 消息标签
        self.activation_msg = ctk.CTkLabel(
            center,
            text="",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        )
        self.activation_msg.pack(pady=(0, 18))

        # 激活按钮
        ctk.CTkButton(
            center,
            text="激活软件",
            font=ctk.CTkFont(size=15, weight="bold"),
            width=220,
            height=45,
            command=self._activate,
        ).pack(pady=(0, 25))

        # 套餐说明
        info_frame = ctk.CTkFrame(center, fg_color=("gray90", "gray20"))
        info_frame.pack(pady=(10, 0))

        ctk.CTkLabel(
            info_frame,
            text="📦 套餐说明",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(pady=(12, 8))

        ctk.CTkLabel(
            info_frame,
            text="基础版：生成提示词 + 复制跳转",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack()

        ctk.CTkLabel(
            info_frame,
            text="专业版：生成提示词 + 复制跳转 + PyInstaller打包",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(pady=(0, 12))

        # 管理员入口
        ctk.CTkButton(
            center,
            text="🔧 管理员模式",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=("gray80", "gray30"),
            text_color="gray",
            width=120,
            height=30,
            command=self._admin_login_from_activation,
        ).pack(pady=(20, 0))

        code_entry.focus()

    def _admin_login_from_activation(self):
        """从激活界面进入管理员模式"""
        # 创建密码输入对话框
        dialog = ctk.CTkToplevel(self)
        dialog.title("管理员登录")
        dialog.geometry("400x250")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # 居中
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() - 400) // 2
        y = (dialog.winfo_screenheight() - 250) // 2
        dialog.geometry(f"+{x}+{y}")

        frame = ctk.CTkFrame(dialog, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(
            frame,
            text="🔧 管理员登录",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(pady=(0, 20))

        pwd_var = ctk.StringVar()
        pwd_entry = ctk.CTkEntry(
            frame,
            textvariable=pwd_var,
            placeholder_text="请输入管理员密码",
            show="*",
            width=280,
            height=45,
            font=ctk.CTkFont(size=14),
        )
        pwd_entry.pack(pady=(0, 10))

        msg_label = ctk.CTkLabel(frame, text="", text_color="red", font=ctk.CTkFont(size=12))
        msg_label.pack(pady=(0, 15))

        def do_login():
            if pwd_var.get() == ADMIN_PASSWORD:
                dialog.destroy()
                self._enter_main_app()
            else:
                msg_label.configure(text="密码错误")
                pwd_var.set("")

        pwd_entry.bind("<Return>", lambda e: do_login())

        ctk.CTkButton(
            frame,
            text="登录",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=200,
            height=40,
            command=do_login,
        ).pack()

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
        """构建用户界面"""
        # 配置网格
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 顶部工具栏
        self._build_toolbar()

        # 主内容区（左右分栏）
        self._build_main_content()

        # 状态栏
        self._build_statusbar()

    # ----------------------------------------------------------
    #                       工具栏
    # ----------------------------------------------------------

    def _build_toolbar(self):
        """构建顶部工具栏"""
        toolbar = ctk.CTkFrame(self, height=60)
        toolbar.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        toolbar.grid_columnconfigure(1, weight=1)

        # 左侧标题
        title_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        title_frame.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        ctk.CTkLabel(
            title_frame,
            text="7OZP1K编程助手",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(side="left")

        ctk.CTkLabel(
            title_frame,
            text="  提示词生成 + PyInstaller打包",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).pack(side="left", padx=10)

        # 右侧控件
        right_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        right_frame.grid(row=0, column=2, sticky="e", padx=10, pady=10)

        # API状态
        self.api_status_label = ctk.CTkLabel(
            right_frame,
            text="❌ API未配置",
            font=ctk.CTkFont(size=12),
            text_color="red",
        )
        self.api_status_label.pack(side="left", padx=10)

        # 设置按钮
        ctk.CTkButton(
            right_frame,
            text="⚙️ 设置",
            width=80,
            command=self._show_settings,
        ).pack(side="left", padx=5)

        # 主题切换
        self.theme_var = ctk.StringVar(value=self.settings.get("theme", "dark"))
        theme_menu = ctk.CTkOptionMenu(
            right_frame,
            values=list(THEMES.keys()),
            variable=self.theme_var,
            command=self._on_theme_changed,
            width=100,
        )
        theme_menu.pack(side="left", padx=5)

        # 帮助按钮
        ctk.CTkButton(
            right_frame,
            text="❓",
            width=40,
            command=self._show_help,
        ).pack(side="left", padx=5)

        # 更新API状态
        self._update_api_status()

    # ----------------------------------------------------------
    #                       主内容区
    # ----------------------------------------------------------

    def _build_main_content(self):
        """构建主内容区"""
        main_frame = ctk.CTkFrame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        # 左侧面板
        self._build_left_panel(main_frame)

        # 右侧面板
        self._build_right_panel(main_frame)

    def _build_left_panel(self, parent):
        """构建左侧输入面板"""
        left_frame = ctk.CTkFrame(parent)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=0)
        left_frame.grid_rowconfigure(0, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)

        # 标签页
        self.left_tabview = ctk.CTkTabview(left_frame)
        self.left_tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 新建项目标签页
        tab_new = self.left_tabview.add("📝 新建项目")
        self._build_new_project_tab(tab_new)

        # 模板库标签页
        tab_templates = self.left_tabview.add("📚 模板库")
        self._build_templates_tab(tab_templates)

        # 历史记录标签页
        tab_history = self.left_tabview.add("📜 历史")
        self._build_history_tab(tab_history)

        # 添加配置标签页
        tab_config = self.left_tabview.add("⚙️ 添加配置")
        self._build_config_tab(tab_config)

    def _build_new_project_tab(self, parent):
        """构建新建项目标签页"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(2, weight=1)

        # 项目配置
        config_frame = ctk.CTkFrame(parent)
        config_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        config_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            config_frame,
            text="🎯 项目配置",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(10, 5))

        # 语言选择
        ctk.CTkLabel(config_frame, text="编程语言:").grid(
            row=1, column=0, sticky="w", padx=10, pady=5
        )

        self.language_var = ctk.StringVar(
            value=self.settings.get("last_language", "Python")
        )
        self.language_menu = ctk.CTkOptionMenu(
            config_frame,
            values=list(LANGUAGE_FRAMEWORKS.keys()),
            variable=self.language_var,
            command=self._on_language_changed,
            width=150,
        )
        self.language_menu.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # 语言图标
        self.lang_icon_label = ctk.CTkLabel(
            config_frame,
            text="Py🐍",
            font=ctk.CTkFont(size=20),
        )
        self.lang_icon_label.grid(row=1, column=2, sticky="w", padx=5)

        # 框架类别
        ctk.CTkLabel(config_frame, text="框架类别:").grid(
            row=2, column=0, sticky="w", padx=10, pady=5
        )

        self.category_var = ctk.StringVar()
        self.category_menu = ctk.CTkOptionMenu(
            config_frame,
            values=[""],
            variable=self.category_var,
            command=self._on_category_changed,
            width=150,
        )
        self.category_menu.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # 具体框架
        ctk.CTkLabel(config_frame, text="具体框架:").grid(
            row=2, column=2, sticky="w", padx=10, pady=5
        )

        self.framework_var = ctk.StringVar()
        self.framework_menu = ctk.CTkOptionMenu(
            config_frame,
            values=[""],
            variable=self.framework_var,
            width=150,
        )
        self.framework_menu.grid(row=2, column=3, sticky="w", padx=5, pady=5)

        # 开发优先级
        ctk.CTkLabel(config_frame, text="开发优先级:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )

        priority_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        priority_frame.grid(row=3, column=1, columnspan=3, sticky="w", padx=5, pady=5)

        self.priority_var = ctk.StringVar(value="功能完整")
        priorities = ["快速原型", "功能完整", "生产就绪", "最佳实践"]
        for i, p in enumerate(priorities):
            ctk.CTkRadioButton(
                priority_frame,
                text=p,
                variable=self.priority_var,
                value=p,
            ).pack(side="left", padx=10)

        # 初始化框架选项
        self._on_language_changed(self.language_var.get())

        # 文件上传区域
        upload_frame = ctk.CTkFrame(parent)
        upload_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        upload_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            upload_frame,
            text="📎 上传文件 (可选)",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # 文件列表和按钮
        files_control_frame = ctk.CTkFrame(upload_frame, fg_color="transparent")
        files_control_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        files_control_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            files_control_frame,
            text="📁 选择文件",
            width=100,
            command=self._select_files,
        ).grid(row=0, column=0, sticky="w", padx=5)

        ctk.CTkButton(
            files_control_frame,
            text="🗑️ 清空文件",
            width=100,
            command=self._clear_files,
        ).grid(row=0, column=1, sticky="w", padx=5)

        # 拖拽区域
        self.drop_frame = ctk.CTkFrame(
            upload_frame,
            height=80,
            fg_color=("gray85", "gray25"),
            border_width=2,
            border_color=("gray70", "gray40"),
        )
        self.drop_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
        self.drop_frame.grid_propagate(False)
        self.drop_frame.grid_columnconfigure(0, weight=1)
        self.drop_frame.grid_rowconfigure(0, weight=1)

        self.drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="📂 拖拽文件到此处上传\n或点击选择文件按钮",
            font=ctk.CTkFont(size=11),
            text_color=("gray50", "gray60"),
        )
        self.drop_label.grid(row=0, column=0, sticky="nsew")

        # 绑定点击事件到拖拽区域
        self.drop_frame.bind("<Button-1>", lambda e: self._select_files())
        self.drop_label.bind("<Button-1>", lambda e: self._select_files())

        # 尝试启用拖拽功能
        self._setup_drag_drop()

        # 文件列表显示
        self.files_listbox = ctk.CTkTextbox(
            upload_frame,
            height=60,
            font=ctk.CTkFont(size=11),
        )
        self.files_listbox.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        self.files_listbox.insert("1.0", "暂无文件上传")
        self.files_listbox.configure(state="disabled")

        # 项目描述
        desc_frame = ctk.CTkFrame(parent)
        desc_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        desc_frame.grid_columnconfigure(0, weight=1)

        header_frame = ctk.CTkFrame(desc_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header_frame,
            text="📋 项目描述",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        self.char_count_label = ctk.CTkLabel(
            header_frame,
            text="0 字",
            text_color="gray",
        )
        self.char_count_label.grid(row=0, column=1, sticky="e")

        # 项目描述文本框
        self.idea_textbox = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(size=12),
            wrap="word",
        )
        self.idea_textbox.grid(row=3, column=0, sticky="nsew", padx=5, pady=5)
        self.idea_textbox.bind("<KeyRelease>", self._update_char_count)

        # 操作按钮
        action_frame = ctk.CTkFrame(parent)
        action_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        self.generate_btn = ctk.CTkButton(
            action_frame,
            text="🚀 生成提示词",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            command=self._generate_prompt,
        )
        self.generate_btn.pack(side="left", padx=10, pady=10)

        self.progress_label = ctk.CTkLabel(
            action_frame,
            text="",
            text_color="gray",
        )
        self.progress_label.pack(side="left", padx=10)

    def _build_templates_tab(self, parent):
        """构建模板库标签页"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        toolbar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            toolbar,
            text="📚 项目模板库",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            toolbar,
            text="➕ 添加模板",
            width=100,
            command=self._add_template_dialog,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            toolbar,
            text="🔄 刷新",
            width=80,
            command=self._refresh_templates,
        ).pack(side="right", padx=5)

        # 模板列表
        self.templates_scroll_frame = ctk.CTkScrollableFrame(parent)
        self.templates_scroll_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.templates_scroll_frame.grid_columnconfigure(0, weight=1)

        self._refresh_templates()

    def _refresh_templates(self):
        """刷新模板列表"""
        # 清空
        for widget in self.templates_scroll_frame.winfo_children():
            widget.destroy()

        templates = DataManager.get_all_templates()
        for i, (name, template) in enumerate(templates.items()):
            self._create_template_card(self.templates_scroll_frame, name, template, i)

    def _create_template_card(self, parent, name: str, template: dict, row: int):
        """创建模板卡片"""
        is_custom = name not in DEFAULT_TEMPLATES

        card = ctk.CTkFrame(parent)
        card.grid(row=row, column=0, sticky="ew", padx=5, pady=5)
        card.grid_columnconfigure(1, weight=1)

        # 左侧信息
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        icon = "📝" if is_custom else "📁"
        ctk.CTkLabel(
            info_frame,
            text=f"{icon} {name}",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).pack(anchor="w")

        ctk.CTkLabel(
            info_frame,
            text=template.get("description", "自定义模板"),
            text_color="gray",
            font=ctk.CTkFont(size=11),
        ).pack(anchor="w")

        # 语言和框架标签
        lang = template.get("language", "")
        fw = template.get("framework", "")
        if lang or fw:
            tag_text = f"[{lang}] {fw}" if lang and fw else lang or fw
            ctk.CTkLabel(
                info_frame,
                text=tag_text,
                text_color=("blue", "lightblue"),
                font=ctk.CTkFont(size=10),
            ).pack(anchor="w")

        # 右侧按钮
        btn_frame = ctk.CTkFrame(card, fg_color="transparent")
        btn_frame.grid(row=0, column=1, sticky="e", padx=10, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="使用",
            width=60,
            command=lambda n=name, t=template: self._use_template(n, t),
        ).pack(side="left", padx=3)

        if is_custom:
            ctk.CTkButton(
                btn_frame,
                text="删除",
                width=60,
                fg_color="red",
                hover_color="darkred",
                command=lambda n=name: self._delete_template(n),
            ).pack(side="left", padx=3)

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

        ctk.CTkButton(btn_frame, text="确定", fg_color="red", command=confirm).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="取消", command=dialog.destroy).pack(side="left", padx=10)

    def _build_history_tab(self, parent):
        """构建历史记录标签页"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            toolbar,
            text="最近生成的提示词",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            toolbar,
            text="🗑️ 清空",
            width=80,
            command=self._clear_history,
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            toolbar,
            text="🔄 刷新",
            width=80,
            command=self._refresh_history,
        ).pack(side="right", padx=5)

        # 历史列表
        self.history_frame = ctk.CTkScrollableFrame(parent)
        self.history_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.history_frame.grid_columnconfigure(0, weight=1)

        self._refresh_history()

    def _build_config_tab(self, parent):
        """构建添加配置标签页"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 配置解锁状态
        self._config_unlocked = False

        # 标题和说明
        header = ctk.CTkFrame(parent)
        header.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            header,
            text="⚙️ 添加配置",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left", padx=10, pady=10)

        self.config_status_label = ctk.CTkLabel(
            header,
            text="🔒 未解锁",
            font=ctk.CTkFont(size=11),
            text_color="red",
        )
        self.config_status_label.pack(side="left")

        # 主容器 - 包含解锁界面和配置界面
        self.config_container = ctk.CTkFrame(parent)
        self.config_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.config_container.grid_columnconfigure(0, weight=1)
        self.config_container.grid_rowconfigure(0, weight=1)

        # 解锁界面
        self.unlock_frame = ctk.CTkFrame(self.config_container)
        self.unlock_frame.grid(row=0, column=0, sticky="nsew")
        self.unlock_frame.grid_columnconfigure(0, weight=1)

        # 解锁提示
        unlock_content = ctk.CTkFrame(self.unlock_frame, fg_color="transparent")
        unlock_content.place(relx=0.5, rely=0.4, anchor="center")

        ctk.CTkLabel(
            unlock_content,
            text="🔐",
            font=ctk.CTkFont(size=48),
        ).pack(pady=10)

        ctk.CTkLabel(
            unlock_content,
            text="需要管理员密码才能添加配置",
            font=ctk.CTkFont(size=14),
        ).pack(pady=10)

        # 密码输入框
        pwd_frame = ctk.CTkFrame(unlock_content, fg_color="transparent")
        pwd_frame.pack(pady=10)

        ctk.CTkLabel(pwd_frame, text="密码:").pack(side="left", padx=5)
        self.config_pwd_entry = ctk.CTkEntry(pwd_frame, show="•", width=150)
        self.config_pwd_entry.pack(side="left", padx=5)
        self.config_pwd_entry.bind("<Return>", lambda e: self._unlock_config())

        ctk.CTkButton(
            unlock_content,
            text="🔓 解锁",
            width=120,
            command=self._unlock_config,
        ).pack(pady=15)

        # 配置内容区域（初始隐藏）
        self.config_scroll = ctk.CTkScrollableFrame(self.config_container)
        self.config_scroll.grid_columnconfigure(0, weight=1)

        # 1. 添加编程语言
        lang_frame = ctk.CTkFrame(self.config_scroll)
        lang_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        lang_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            lang_frame,
            text="📌 添加编程语言",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(lang_frame, text="语言名称:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.new_lang_entry = ctk.CTkEntry(lang_frame, placeholder_text="如: Kotlin")
        self.new_lang_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(
            lang_frame,
            text="添加语言",
            width=100,
            command=self._add_language,
        ).grid(row=1, column=2, padx=10, pady=5)

        # 2. 添加框架类别
        cat_frame = ctk.CTkFrame(self.config_scroll)
        cat_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        cat_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cat_frame,
            text="📌 添加框架类别",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(cat_frame, text="选择语言:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.cat_lang_var = ctk.StringVar()
        self.cat_lang_menu = ctk.CTkOptionMenu(
            cat_frame,
            values=list(DataManager.get_all_languages().keys()),
            variable=self.cat_lang_var,
            width=150,
        )
        self.cat_lang_menu.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(cat_frame, text="类别名称:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.new_cat_entry = ctk.CTkEntry(cat_frame, placeholder_text="如: 游戏开发")
        self.new_cat_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(
            cat_frame,
            text="添加类别",
            width=100,
            command=self._add_category,
        ).grid(row=2, column=2, padx=10, pady=5)

        # 3. 添加具体框架
        fw_frame = ctk.CTkFrame(self.config_scroll)
        fw_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        fw_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            fw_frame,
            text="📌 添加具体框架",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(fw_frame, text="选择语言:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.fw_lang_var = ctk.StringVar()
        self.fw_lang_menu = ctk.CTkOptionMenu(
            fw_frame,
            values=list(DataManager.get_all_languages().keys()),
            variable=self.fw_lang_var,
            command=self._on_fw_lang_changed,
            width=150,
        )
        self.fw_lang_menu.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(fw_frame, text="选择类别:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.fw_cat_var = ctk.StringVar()
        self.fw_cat_menu = ctk.CTkOptionMenu(
            fw_frame,
            values=[""],
            variable=self.fw_cat_var,
            width=150,
        )
        self.fw_cat_menu.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(fw_frame, text="框架名称:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.new_fw_entry = ctk.CTkEntry(fw_frame, placeholder_text="如: Pygame")
        self.new_fw_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(
            fw_frame,
            text="添加框架",
            width=100,
            command=self._add_framework,
        ).grid(row=3, column=2, padx=10, pady=5)

        # 4. 添加开发优先级
        pri_frame = ctk.CTkFrame(self.config_scroll)
        pri_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        pri_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            pri_frame,
            text="📌 添加开发优先级",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        ctk.CTkLabel(pri_frame, text="当前优先级:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        priorities = DataManager.get_all_priorities()
        ctk.CTkLabel(
            pri_frame,
            text=", ".join(priorities),
            text_color="gray",
            wraplength=300,
        ).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(pri_frame, text="新优先级:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.new_priority_entry = ctk.CTkEntry(pri_frame, placeholder_text="如: 高性能")
        self.new_priority_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(
            pri_frame,
            text="添加优先级",
            width=100,
            command=self._add_priority,
        ).grid(row=2, column=2, padx=10, pady=5)

        # 5. 添加AI网站
        web_frame = ctk.CTkFrame(self.config_scroll)
        web_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        web_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            web_frame,
            text="📌 添加AI网站 (用于复制跳转)",
            font=ctk.CTkFont(size=13, weight="bold"),
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=10, pady=(10, 5))

        # 当前网站列表
        ctk.CTkLabel(web_frame, text="已有网站:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        websites = DataManager.get_all_ai_websites()
        website_names = ", ".join(list(websites.keys())[:6])
        if len(websites) > 6:
            website_names += "..."
        self.current_websites_label = ctk.CTkLabel(
            web_frame,
            text=website_names,
            text_color="gray",
            wraplength=400,
        )
        self.current_websites_label.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(web_frame, text="网站名称:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.new_website_name_entry = ctk.CTkEntry(web_frame, placeholder_text="如: DeepSeek", width=120)
        self.new_website_name_entry.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ctk.CTkLabel(web_frame, text="网站URL:").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.new_website_url_entry = ctk.CTkEntry(web_frame, placeholder_text="如: https://chat.deepseek.com/")
        self.new_website_url_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        ctk.CTkButton(
            web_frame,
            text="添加网站",
            width=100,
            command=self._add_ai_website,
        ).grid(row=3, column=2, padx=10, pady=5)

        # 删除网站
        del_web_frame = ctk.CTkFrame(web_frame, fg_color="transparent")
        del_web_frame.grid(row=4, column=0, columnspan=3, sticky="w", padx=10, pady=5)

        ctk.CTkLabel(del_web_frame, text="删除网站:").pack(side="left")
        self.del_website_var = ctk.StringVar()
        custom_websites = [name for name, info in websites.items() if not info.get("is_preset", True)]
        self.del_website_menu = ctk.CTkOptionMenu(
            del_web_frame,
            values=custom_websites if custom_websites else ["(无自定义网站)"],
            variable=self.del_website_var,
            width=150,
        )
        self.del_website_menu.pack(side="left", padx=5)

        ctk.CTkButton(
            del_web_frame,
            text="删除",
            width=60,
            fg_color=("red", "darkred"),
            command=self._delete_ai_website,
        ).pack(side="left", padx=5)

        # 6. 刷新和锁定按钮
        btn_frame = ctk.CTkFrame(self.config_scroll, fg_color="transparent")
        btn_frame.grid(row=5, column=0, pady=20)

        ctk.CTkButton(
            btn_frame,
            text="🔄 刷新配置列表",
            command=self._refresh_config_options,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="🔒 锁定配置",
            fg_color=("gray70", "gray30"),
            command=self._lock_config,
        ).pack(side="left", padx=10)

        # 7. 兑换码管理
        code_frame = ctk.CTkFrame(self.config_scroll)
        code_frame.grid(row=6, column=0, sticky="ew", padx=5, pady=10)

        # 标题
        ctk.CTkLabel(
            code_frame,
            text="🔑 兑换码管理",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", padx=15, pady=(15, 10))

        # 第一行：套餐选择
        row1 = ctk.CTkFrame(code_frame, fg_color="transparent")
        row1.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row1, text="套餐类型:").pack(side="left")
        self.code_package_var = ctk.StringVar(value="basic")
        ctk.CTkRadioButton(
            row1, text="基础版 (提示词+跳转)",
            variable=self.code_package_var, value="basic",
        ).pack(side="left", padx=(15, 10))
        ctk.CTkRadioButton(
            row1, text="专业版 (全功能)",
            variable=self.code_package_var, value="pro",
        ).pack(side="left", padx=10)

        # 第二行：有效期和数量
        row2 = ctk.CTkFrame(code_frame, fg_color="transparent")
        row2.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(row2, text="有效期:").pack(side="left")
        self.code_expire_var = ctk.StringVar(value="永久")
        ctk.CTkOptionMenu(
            row2, values=["1天", "7天", "30天", "永久"],
            variable=self.code_expire_var, width=100,
        ).pack(side="left", padx=(10, 20))

        ctk.CTkLabel(row2, text="数量:").pack(side="left")
        self.code_count_var = ctk.StringVar(value="1")
        ctk.CTkOptionMenu(
            row2, values=["1", "5", "10", "20"],
            variable=self.code_count_var, width=80,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            row2, text="🎫 生成兑换码",
            fg_color=("purple", "darkviolet"),
            hover_color=("darkviolet", "purple"),
            width=130, command=self._generate_codes,
        ).pack(side="left", padx=20)

        # 生成结果
        self.code_result_label = ctk.CTkLabel(
            code_frame, text="", font=ctk.CTkFont(family="Consolas", size=11),
            text_color="green", justify="left", anchor="w",
        )
        self.code_result_label.pack(fill="x", padx=15, pady=5)

        # 兑换码列表
        list_header = ctk.CTkFrame(code_frame, fg_color="transparent")
        list_header.pack(fill="x", padx=15, pady=(10, 5))
        ctk.CTkLabel(
            list_header, text="📋 已生成的兑换码",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(side="left")
        ctk.CTkButton(
            list_header, text="🔄 刷新", width=60,
            command=self._refresh_codes_list,
        ).pack(side="right")

        self.codes_listbox = ctk.CTkTextbox(
            code_frame, height=100,
            font=ctk.CTkFont(family="Consolas", size=10),
        )
        self.codes_listbox.pack(fill="x", padx=15, pady=5)

        # 重置按钮
        reset_row = ctk.CTkFrame(code_frame, fg_color="transparent")
        reset_row.pack(fill="x", padx=15, pady=(5, 15))
        ctk.CTkButton(
            reset_row, text="🔄 重置授权 (测试用)",
            fg_color=("red", "darkred"), hover_color=("darkred", "red"),
            width=150, command=self._reset_license,
        ).pack(side="left")
        ctk.CTkLabel(
            reset_row, text="← 重置后需重启应用",
            text_color="gray", font=ctk.CTkFont(size=11),
        ).pack(side="left", padx=10)

        # 初始化列表
        self._refresh_codes_list()

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
        expire_option = self.code_expire_var.get()
        count = int(self.code_count_var.get())

        # 转换有效期
        expire_days = None
        if expire_option == "1天":
            expire_days = 1
        elif expire_option == "7天":
            expire_days = 7
        elif expire_option == "30天":
            expire_days = 30
        # 永久为 None

        # 生成兑换码
        codes = self.code_manager.generate_batch(package_type, count, expire_days)

        package_name = "基础版" if package_type == "basic" else "专业版"
        expire_text = expire_option

        self.code_result_label.configure(
            text=f"已生成 {len(codes)} 个 {package_name} 兑换码（{expire_text}）:\n" + "\n".join(codes),
            text_color="green",
        )

        self._refresh_codes_list()

    def _refresh_codes_list(self):
        """刷新兑换码列表"""
        if not hasattr(self, "codes_listbox"):
            return

        codes = self.code_manager.get_all_codes()

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

                if code_info.get("expires_at"):
                    from datetime import datetime
                    expires = datetime.fromisoformat(code_info["expires_at"])
                    remaining = (expires - datetime.now()).days
                    if remaining > 0:
                        expire_text = f"{remaining}天后到期"
                    elif remaining == 0:
                        expire_text = "今天到期"
                    else:
                        expire_text = "已过期"
                        status = "已过期"
                else:
                    expire_text = "永久"

                lines.append(f"{code_info['code']}  [{package_name}]  [{status}]  [{expire_text}]")

            self.codes_listbox.insert("0.0", "\n".join(lines))

        self.codes_listbox.configure(state="disabled")

    def _reset_license(self):
        """重置授权（测试用）"""
        self.code_manager.reset_license()
        self.status_label.configure(text="✅ 授权已重置，重启应用后生效")

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

    def _build_right_panel(self, parent):
        """构建右侧输出面板"""
        right_frame = ctk.CTkFrame(parent)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=0)
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)

        # 标签页
        self.right_tabview = ctk.CTkTabview(right_frame)
        self.right_tabview.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 输出结果标签页
        tab_output = self.right_tabview.add("✨ 生成结果")
        self._build_output_tab(tab_output)

        # PyInstaller标签页
        tab_packager = self.right_tabview.add("📦 PyInstaller打包")
        self._build_packager_tab(tab_packager)

    def _build_output_tab(self, parent):
        """构建输出结果标签页"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 工具栏
        toolbar = ctk.CTkFrame(parent, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        toolbar.grid_columnconfigure(1, weight=1)

        # 翻页控件
        page_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        page_frame.grid(row=0, column=0, sticky="w")

        self.prev_page_btn = ctk.CTkButton(
            page_frame,
            text="◀",
            width=40,
            command=self._prev_page,
            state="disabled",
        )
        self.prev_page_btn.pack(side="left", padx=2)

        self.page_label = ctk.CTkLabel(
            page_frame,
            text="0 / 0",
            font=ctk.CTkFont(size=12),
        )
        self.page_label.pack(side="left", padx=10)

        self.next_page_btn = ctk.CTkButton(
            page_frame,
            text="▶",
            width=40,
            command=self._next_page,
            state="disabled",
        )
        self.next_page_btn.pack(side="left", padx=2)

        # 当前页标题
        self.page_title_label = ctk.CTkLabel(
            toolbar,
            text="",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        self.page_title_label.grid(row=0, column=1, sticky="w", padx=20)

        # 右侧按钮
        btn_frame = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_frame.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(
            btn_frame, text="📋 复制", width=70, command=self._copy_prompt
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame, text="⭐ 收藏", width=70, command=self._add_favorite
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            btn_frame, text="💾 导出", width=70, command=self._export_prompt
        ).pack(side="left", padx=3)

        # 复制并跳转按钮（下拉菜单）
        self.jump_website_var = ctk.StringVar(value="复制并跳转")
        self.jump_website_menu = ctk.CTkOptionMenu(
            btn_frame,
            values=self._get_website_names(),
            variable=self.jump_website_var,
            command=self._copy_and_jump,
            width=110,
            fg_color=("green", "darkgreen"),
            button_color=("green", "darkgreen"),
            button_hover_color=("darkgreen", "green"),
        )
        self.jump_website_menu.pack(side="left", padx=3)
        self.jump_website_menu.set("🚀 跳转")

        ctk.CTkButton(
            btn_frame, text="🗑️ 清空", width=70, command=self._clear_pages
        ).pack(side="left", padx=3)

        # 输出文本框
        self.output_textbox = ctk.CTkTextbox(
            parent,
            font=ctk.CTkFont(family="Consolas", size=12),
            wrap="word",
            state="disabled",
        )
        self.output_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        # 统计信息
        stats_frame = ctk.CTkFrame(parent, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)

        self.word_count_label = ctk.CTkLabel(
            stats_frame, text="字数: 0", text_color="gray"
        )
        self.word_count_label.pack(side="left", padx=10)

        self.line_count_label = ctk.CTkLabel(
            stats_frame, text="行数: 0", text_color="gray"
        )
        self.line_count_label.pack(side="left", padx=10)

        # 追问功能区域
        followup_frame = ctk.CTkFrame(parent)
        followup_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        followup_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            followup_frame,
            text="💬 追问 (对当前提示词进行修改和优化)",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(10, 5))

        self.followup_entry = ctk.CTkEntry(
            followup_frame,
            placeholder_text="例如: 请添加错误处理逻辑 / 请优化代码结构 / 请添加单元测试...",
            font=ctk.CTkFont(size=11),
        )
        self.followup_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        self.followup_entry.bind("<Return>", lambda e: self._send_followup())

        self.followup_btn = ctk.CTkButton(
            followup_frame,
            text="发送追问",
            width=100,
            command=self._send_followup,
        )
        self.followup_btn.grid(row=1, column=1, sticky="e", padx=10, pady=5)

    def _build_packager_tab(self, parent):
        """构建 PyInstaller 打包标签页 - 双模式支持"""
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        # 初始化 AI 分析器
        self.ai_analyzer = AIPackageAnalyzer(self.api_config)
        self.ai_package_config = None  # 存储 AI 分析结果

        # 顶部标题和模式切换
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text="🎁 Python 打包工具",
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=0, sticky="w")

        # 模式切换
        mode_frame = ctk.CTkFrame(header, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(mode_frame, text="模式:").pack(side="left", padx=5)

        self.packager_mode_var = ctk.StringVar(value="beginner")
        self.packager_mode_menu = ctk.CTkSegmentedButton(
            mode_frame,
            values=["零基础用户", "独立开发"],
            variable=self.packager_mode_var,
            command=self._on_packager_mode_changed,
        )
        self.packager_mode_menu.pack(side="left", padx=5)
        self.packager_mode_menu.set("零基础用户")

        # PyInstaller 状态
        self.pyinstaller_status = ctk.CTkLabel(
            mode_frame,
            text="检查中...",
            text_color="gray",
        )
        self.pyinstaller_status.pack(side="left", padx=10)

        # 主内容容器
        self.packager_container = ctk.CTkFrame(parent)
        self.packager_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.packager_container.grid_columnconfigure(0, weight=1)
        self.packager_container.grid_rowconfigure(0, weight=1)

        # 构建两种模式的界面
        self._build_beginner_mode()
        self._build_developer_mode()

        # 默认显示零基础模式
        self._show_beginner_mode()

        # 检查 PyInstaller 状态
        self._check_pyinstaller()

    def _build_beginner_mode(self):
        """构建零基础用户模式界面"""
        self.beginner_frame = ctk.CTkFrame(self.packager_container)
        self.beginner_frame.grid_columnconfigure(0, weight=1)
        self.beginner_frame.grid_rowconfigure(3, weight=1)

        # ===== 第一部分：环境检测 =====
        env_frame = ctk.CTkFrame(self.beginner_frame)
        env_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        env_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            env_frame,
            text="🔍 环境检测",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        # Python 状态
        ctk.CTkLabel(env_frame, text="Python 环境:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.python_status_label = ctk.CTkLabel(env_frame, text="检测中...", text_color="gray")
        self.python_status_label.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # PyInstaller 状态
        ctk.CTkLabel(env_frame, text="PyInstaller:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.pyinstaller_status_label = ctk.CTkLabel(env_frame, text="检测中...", text_color="gray")
        self.pyinstaller_status_label.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # 一键安装按钮
        self.install_btn = ctk.CTkButton(
            env_frame,
            text="📦 一键安装 PyInstaller",
            width=180,
            fg_color=("green", "darkgreen"),
            command=self._install_pyinstaller,
        )
        self.install_btn.grid(row=2, column=2, padx=10, pady=5)

        # 刷新检测按钮
        ctk.CTkButton(
            env_frame,
            text="🔄 重新检测",
            width=100,
            command=self._check_environment,
        ).grid(row=1, column=2, padx=10, pady=5)

        # ===== 第二部分：简化打包 =====
        pack_frame = ctk.CTkFrame(self.beginner_frame)
        pack_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)
        pack_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            pack_frame,
            text="📁 打包设置",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=10, pady=(10, 5))

        # 选择 Python 文件
        ctk.CTkLabel(pack_frame, text="Python 文件:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
        self.beginner_script_var = ctk.StringVar()
        ctk.CTkEntry(
            pack_frame,
            textvariable=self.beginner_script_var,
            placeholder_text="选择你的 .py 文件",
        ).grid(row=1, column=1, sticky="ew", padx=5, pady=8)
        ctk.CTkButton(
            pack_frame,
            text="📂 选择",
            width=80,
            command=self._select_beginner_script,
        ).grid(row=1, column=2, padx=10, pady=8)

        # 程序名称
        ctk.CTkLabel(pack_frame, text="程序名称:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
        self.beginner_name_var = ctk.StringVar(value="我的程序")
        ctk.CTkEntry(
            pack_frame,
            textvariable=self.beginner_name_var,
            placeholder_text="生成的 exe 名称",
        ).grid(row=2, column=1, sticky="ew", padx=5, pady=8)

        # 程序类型
        ctk.CTkLabel(pack_frame, text="程序类型:").grid(row=3, column=0, sticky="w", padx=10, pady=8)
        self.beginner_type_var = ctk.StringVar(value="GUI程序")
        type_frame = ctk.CTkFrame(pack_frame, fg_color="transparent")
        type_frame.grid(row=3, column=1, sticky="w", padx=5, pady=8)
        ctk.CTkRadioButton(type_frame, text="GUI 窗口程序", variable=self.beginner_type_var, value="GUI程序").pack(side="left", padx=10)
        ctk.CTkRadioButton(type_frame, text="命令行程序", variable=self.beginner_type_var, value="命令行程序").pack(side="left", padx=10)

        # 输出位置
        ctk.CTkLabel(pack_frame, text="输出位置:").grid(row=4, column=0, sticky="w", padx=10, pady=8)
        self.beginner_output_var = ctk.StringVar()
        ctk.CTkEntry(
            pack_frame,
            textvariable=self.beginner_output_var,
            placeholder_text="exe 文件保存位置",
        ).grid(row=4, column=1, sticky="ew", padx=5, pady=8)
        ctk.CTkButton(
            pack_frame,
            text="📂 选择",
            width=80,
            command=self._select_beginner_output,
        ).grid(row=4, column=2, padx=10, pady=8)

        # ===== 第三部分：打包按钮区 =====
        action_frame = ctk.CTkFrame(self.beginner_frame, fg_color="transparent")
        action_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=15)

        self.beginner_pack_btn = ctk.CTkButton(
            action_frame,
            text="🚀 一键打包",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=45,
            command=self._beginner_package,
        )
        self.beginner_pack_btn.pack(side="left", padx=10)

        self.beginner_ai_pack_btn = ctk.CTkButton(
            action_frame,
            text="🧠 AI分析后打包",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=45,
            fg_color=("purple", "darkviolet"),
            hover_color=("darkviolet", "purple"),
            command=self._beginner_ai_package,
        )
        self.beginner_ai_pack_btn.pack(side="left", padx=10)

        ctk.CTkButton(
            action_frame,
            text="📂 打开输出目录",
            width=120,
            command=self._open_beginner_output,
        ).pack(side="left", padx=10)

        # ===== 第四部分：日志 =====
        log_frame = ctk.CTkFrame(self.beginner_frame)
        log_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(
            log_header,
            text="📋 运行日志",
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            log_header,
            text="清空",
            width=60,
            command=lambda: self.beginner_log_textbox.delete("1.0", "end"),
        ).pack(side="right")

        self.beginner_log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=10),
        )
        self.beginner_log_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.beginner_log_textbox.insert("1.0", "欢迎使用零基础打包模式！\n\n步骤：\n1. 确保环境检测通过（如未安装 PyInstaller 请点击一键安装）\n2. 选择你的 Python 文件\n3. 设置程序名称和类型\n4. 点击「一键打包」\n")

        # 初始化环境检测
        self.after(500, self._check_environment)

    def _build_developer_mode(self):
        """构建独立开发模式界面（保持原有功能）"""
        self.developer_frame = ctk.CTkFrame(self.packager_container)
        self.developer_frame.grid_columnconfigure(0, weight=1)
        self.developer_frame.grid_rowconfigure(5, weight=1)

        # 重要提示
        tip_frame = ctk.CTkFrame(self.developer_frame, fg_color=("gray85", "gray20"))
        tip_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            tip_frame,
            text="💡 提示：选择入口文件后点击「AI 智能分析」自动检测依赖和配置",
            font=ctk.CTkFont(size=12),
            text_color=("blue", "cyan"),
        ).pack(padx=10, pady=8)

        # 脚本选择
        script_frame = ctk.CTkFrame(self.developer_frame)
        script_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        script_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(script_frame, text="入口文件:").grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.script_path_var = ctk.StringVar()
        ctk.CTkEntry(
            script_frame,
            textvariable=self.script_path_var,
            placeholder_text="选择包含 if __name__ == '__main__' 的入口文件 (如 main.py)",
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        ctk.CTkButton(
            script_frame,
            text="📂 选择",
            width=80,
            command=self._select_script,
        ).grid(row=0, column=2, padx=5, pady=10)

        ctk.CTkButton(
            script_frame,
            text="🤖 AI 智能分析",
            width=120,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green"),
            command=self._ai_analyze_project,
        ).grid(row=0, column=3, padx=5, pady=10)

        # 输出配置
        output_frame = ctk.CTkFrame(self.developer_frame)
        output_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        output_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(output_frame, text="输出目录:").grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.output_dir_var = ctk.StringVar(value=self.settings.get("pyinstaller_output_dir", ""))
        ctk.CTkEntry(
            output_frame,
            textvariable=self.output_dir_var,
        ).grid(row=0, column=1, sticky="ew", padx=5, pady=10)

        ctk.CTkButton(
            output_frame,
            text="📂 选择",
            width=80,
            command=self._select_output_dir,
        ).grid(row=0, column=2, padx=5, pady=10)

        ctk.CTkLabel(output_frame, text="程序名称:").grid(row=1, column=0, sticky="w", padx=10, pady=10)

        self.program_name_var = ctk.StringVar(value="MyApp")
        ctk.CTkEntry(
            output_frame,
            textvariable=self.program_name_var,
            width=200,
        ).grid(row=1, column=1, sticky="w", padx=5, pady=10)

        # 打包选项
        options_frame = ctk.CTkFrame(self.developer_frame)
        options_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        options_frame.grid_columnconfigure(1, weight=1)

        # 左侧基本选项
        left_options = ctk.CTkFrame(options_frame, fg_color="transparent")
        left_options.grid(row=0, column=0, sticky="nw", padx=10, pady=5)

        ctk.CTkLabel(
            left_options,
            text="基本选项",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.onefile_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            left_options,
            text="单文件模式 (-F)",
            variable=self.onefile_var,
        ).grid(row=1, column=0, sticky="w", pady=3)

        self.noconsole_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            left_options,
            text="无控制台窗口 (-w)",
            variable=self.noconsole_var,
        ).grid(row=2, column=0, sticky="w", pady=3)

        # 图标选择
        icon_frame = ctk.CTkFrame(left_options, fg_color="transparent")
        icon_frame.grid(row=3, column=0, sticky="w", pady=5)

        ctk.CTkLabel(icon_frame, text="程序图标:").pack(side="left")

        self.icon_path_var = ctk.StringVar()
        ctk.CTkEntry(
            icon_frame,
            textvariable=self.icon_path_var,
            width=150,
            placeholder_text="可选 .ico 文件",
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            icon_frame,
            text="选择",
            width=60,
            command=self._select_icon,
        ).pack(side="left", padx=5)

        # 右侧 AI 分析结果
        right_options = ctk.CTkFrame(options_frame)
        right_options.grid(row=0, column=1, sticky="nsew", padx=10, pady=5)
        right_options.grid_columnconfigure(0, weight=1)
        right_options.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            right_options,
            text="🤖 AI 分析结果",
            font=ctk.CTkFont(weight="bold"),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.ai_result_textbox = ctk.CTkTextbox(
            right_options,
            height=120,
            font=ctk.CTkFont(family="Consolas", size=10),
        )
        self.ai_result_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.ai_result_textbox.insert("1.0", "点击「AI 智能分析」按钮分析项目依赖...\n\n提示：AI 会自动检测：\n• 需要导入的模块\n• 需要收集的数据文件\n• CustomTkinter 等特殊库的配置")
        self.ai_result_textbox.configure(state="disabled")

        # 打包按钮区
        btn_frame = ctk.CTkFrame(self.developer_frame, fg_color="transparent")
        btn_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=10)

        ctk.CTkButton(
            btn_frame,
            text="🚀 开始打包",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=40,
            command=self._start_packaging,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="🧠 AI 分析后打包",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=150,
            height=40,
            fg_color=("purple", "darkviolet"),
            hover_color=("darkviolet", "purple"),
            command=self._ai_analyze_and_package,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="📂 打开输出目录",
            width=120,
            command=self._open_output_dir,
        ).pack(side="left", padx=5)

        # 打包日志
        log_frame = ctk.CTkFrame(self.developer_frame)
        log_frame.grid(row=5, column=0, sticky="nsew", padx=5, pady=5)
        log_frame.grid_columnconfigure(0, weight=1)
        log_frame.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_frame, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        ctk.CTkLabel(
            log_header,
            text="📋 打包日志",
            font=ctk.CTkFont(weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            log_header,
            text="清空日志",
            width=80,
            command=lambda: self.pack_log_textbox.delete("1.0", "end"),
        ).pack(side="right")

        self.pack_log_textbox = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=10),
        )
        self.pack_log_textbox.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

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
                def on_error():
                    self._append_beginner_log(f"❌ 安装出错: {e}")
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
                def on_error():
                    self.beginner_pack_btn.configure(state="normal", text="🚀 一键打包")
                    self._append_beginner_log(f"❌ 打包出错: {e}")
                    self._show_message("错误", f"打包出错: {e}")

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
                def on_error():
                    self.beginner_ai_pack_btn.configure(state="normal", text="🧠 AI分析后打包")
                    self._append_beginner_log(f"❌ AI 打包出错: {e}")
                    self._show_message("错误", f"AI 打包出错: {e}")

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
                def on_error():
                    self._append_pack_log(f"❌ AI 分析失败: {e}")
                    self._show_message("错误", f"AI 分析失败: {e}")

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
                def on_error():
                    self._append_pack_log(f"❌ 打包失败: {e}")
                    self._show_message("错误", f"打包失败: {e}")

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
        """构建状态栏"""
        statusbar = ctk.CTkFrame(self, height=30)
        statusbar.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 10))

        self.status_label = ctk.CTkLabel(
            statusbar,
            text="就绪",
            font=ctk.CTkFont(size=11),
        )
        self.status_label.pack(side="left", padx=10)

        ctk.CTkLabel(
            statusbar,
            text="AI编程助手 v3.0 | Powered by Claude",
            text_color="gray",
            font=ctk.CTkFont(size=10),
        ).pack(side="right", padx=10)

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

    def _update_api_status(self):
        """更新API状态"""
        if self.api_config.is_configured():
            self.api_status_label.configure(
                text="✅ API已配置",
                text_color="green",
            )
        else:
            self.api_status_label.configure(
                text="❌ API未配置",
                text_color="red",
            )

    # ----------------------------------------------------------
    #                       核心功能
    # ----------------------------------------------------------

    def _generate_prompt(self):
        """生成提示词"""
        # 检查功能权限
        if not self.code_manager.is_feature_unlocked("prompt"):
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
            "title": "✨ 初始生成",
            "content": prompt
        }]
        self.current_page_index = 0
        self._update_page_display()

        # 切换到输出标签页
        self.right_tabview.set("✨ 生成结果")

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
        # 检查功能权限
        if not self.code_manager.is_feature_unlocked("jump"):
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
        # 倒序显示，最新的在前面
        for i, record in enumerate(reversed(history)):
            # 计算实际索引（因为是倒序，需要转换）
            actual_index = len(history) - 1 - i
            self._create_history_item(i, record, actual_index)

    def _create_history_item(self, row: int, record: dict, actual_index: int):
        """创建历史记录项"""
        item = ctk.CTkFrame(self.history_frame)
        item.grid(row=row, column=0, sticky="ew", padx=5, pady=3)
        item.grid_columnconfigure(0, weight=1)

        timestamp = record.get("timestamp", "")[:19].replace("T", " ")
        lang = record.get("language", "")
        preview = record.get("idea_preview", "")

        ctk.CTkLabel(
            item,
            text=f"[{timestamp}] {lang}",
            font=ctk.CTkFont(size=11),
        ).grid(row=0, column=0, sticky="w", padx=10, pady=2)

        ctk.CTkLabel(
            item,
            text=preview,
            text_color="gray",
            font=ctk.CTkFont(size=10),
        ).grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))

        # 按钮区域
        btn_frame = ctk.CTkFrame(item, fg_color="transparent")
        btn_frame.grid(row=0, column=1, rowspan=2, sticky="e", padx=5, pady=5)

        ctk.CTkButton(
            btn_frame,
            text="加载",
            width=60,
            command=lambda r=record: self._load_history_item(r),
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text="🗑️",
            width=40,
            fg_color=("gray70", "gray30"),
            hover_color=("red", "darkred"),
            command=lambda idx=actual_index: self._delete_history_item(idx),
        ).pack(side="left", padx=2)

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
        # 检查功能权限
        if not self.code_manager.is_feature_unlocked("package"):
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
            command=self._save,
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="取消",
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

        self.api_key_entry = ctk.CTkEntry(parent, show="•", width=400)
        self.api_key_entry.grid(row=2, column=0, sticky="w", padx=10, pady=5)
        if self.api_config.api_key:
            self.api_key_entry.insert(0, self.api_config.api_key)

        # Base URL
        ctk.CTkLabel(parent, text="API地址:").grid(
            row=3, column=0, sticky="w", padx=10, pady=5
        )

        self.base_url_entry = ctk.CTkEntry(parent, width=400)
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
        ).pack(side="left")

        ctk.CTkButton(
            dir_frame,
            text="选择",
            width=60,
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
            command=self._save,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="取消",
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

        ctk.CTkLabel(name_frame, text="模板名称:").grid(row=0, column=0, sticky="w", padx=5)
        self.name_entry = ctk.CTkEntry(name_frame, placeholder_text="如: 电商网站")
        self.name_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # 模板描述
        desc_frame = ctk.CTkFrame(self, fg_color="transparent")
        desc_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        desc_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(desc_frame, text="模板描述:").grid(row=0, column=0, sticky="w", padx=5)
        self.desc_entry = ctk.CTkEntry(desc_frame, placeholder_text="简短描述模板用途")
        self.desc_entry.grid(row=0, column=1, sticky="ew", padx=5)

        # 语言和框架
        tech_frame = ctk.CTkFrame(self, fg_color="transparent")
        tech_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=5)
        tech_frame.grid_columnconfigure(1, weight=1)
        tech_frame.grid_columnconfigure(3, weight=1)

        ctk.CTkLabel(tech_frame, text="编程语言:").grid(row=0, column=0, sticky="w", padx=5)
        self.lang_var = ctk.StringVar(value="Python")
        ctk.CTkOptionMenu(
            tech_frame,
            values=list(LANGUAGE_FRAMEWORKS.keys()),
            variable=self.lang_var,
            command=self._on_lang_changed,
            width=150,
        ).grid(row=0, column=1, sticky="w", padx=5)

        ctk.CTkLabel(tech_frame, text="框架:").grid(row=0, column=2, sticky="w", padx=5)
        self.framework_var = ctk.StringVar()
        self.framework_menu = ctk.CTkOptionMenu(
            tech_frame,
            values=[""],
            variable=self.framework_var,
            width=150,
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
            font=ctk.CTkFont(weight="bold"),
            command=self._save,
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            btn_frame,
            text="取消",
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
