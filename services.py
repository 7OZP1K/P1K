"""
服务层 - 业务逻辑处理
"""

import logging
import os
import subprocess
import sys
from typing import Callable, Optional

import anthropic
import httpx

try:
    from .models import APIConfig, ProjectInfo, UploadedFile, ConversationMessage
except ImportError:
    from models import APIConfig, ProjectInfo, UploadedFile, ConversationMessage

logger = logging.getLogger(__name__)


# ============================================================
#                    提示词生成服务
# ============================================================

class PromptGeneratorService:
    """提示词生成服务"""

    SYSTEM_PROMPT = """你是一个专业的编程提示词工程师,专门为 Claude Code 生成高质量的项目开发提示词。

你的任务是将用户的项目想法转化为详细、结构化、可执行的提示词。

生成的提示词应该：
1. 清晰明确，没有歧义
2. 技术细节完整
3. 包含项目结构建议
4. 包含具体的实现步骤
5. 考虑错误处理和边界情况
6. 包含测试建议

如果用户提供了文件内容，请仔细阅读文件内容，理解其结构和功能，并在生成提示词时充分考虑这些信息。

请用 Markdown 格式组织提示词。"""

    def __init__(self, api_config: APIConfig):
        self.api_config = api_config
        self._client: Optional[anthropic.Anthropic] = None
        self.conversation_history: list[dict] = []  # 对话历史

    def _ensure_client(self):
        """确保客户端已初始化"""
        if not self.api_config.is_configured():
            raise RuntimeError("API密钥未配置")

        if self._client is None:
            logger.info(f"初始化 Anthropic 客户端: {self.api_config.base_url}")
            http_client = httpx.Client(
                verify=False,
                timeout=httpx.Timeout(120.0, connect=30.0),
                trust_env=False,
                proxy=None,
            )
            self._client = anthropic.Anthropic(
                http_client=http_client,
                api_key=self.api_config.api_key,
                base_url=self.api_config.base_url,
            )

    def reset_client(self):
        """重置客户端"""
        self._client = None

    def reset_conversation(self):
        """重置对话历史"""
        self.conversation_history = []

    def _build_user_message(self, project_info: ProjectInfo) -> str:
        """构建用户消息"""
        message_parts = [f"""请为以下项目生成详细的开发提示词：

**项目描述：**
{project_info.idea}

**技术栈：**
- 编程语言: {project_info.language}
- 框架/技术: {project_info.framework}

**开发优先级：** {project_info.priority}"""]

        # 如果有上传的文件，添加文件内容
        if project_info.uploaded_files:
            message_parts.append("\n\n**上传的文件内容：**\n")
            for file_info in project_info.uploaded_files:
                if isinstance(file_info, dict):
                    filename = file_info.get('filename', '未知文件')
                    content = file_info.get('content', '')
                else:
                    filename = file_info.filename
                    content = file_info.content

                message_parts.append(f"\n--- 文件: {filename} ---\n```\n{content}\n```\n")

        message_parts.append("\n请生成一个完整、详细的提示词，让 Claude Code 能够直接开始开发这个项目。")

        return "".join(message_parts)

    def generate(
        self,
        project_info: ProjectInfo,
        callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        生成提示词

        Args:
            project_info: 项目信息
            callback: 进度回调函数

        Returns:
            生成的提示词
        """
        self._ensure_client()

        # 构建用户消息
        user_message = self._build_user_message(project_info)

        # 重置对话历史，开始新对话
        self.conversation_history = [{"role": "user", "content": user_message}]

        try:
            logger.info("调用API生成提示词...")
            if callback:
                callback("正在连接 API...")

            message = self._client.messages.create(
                model=self.api_config.model,
                max_tokens=8192,
                system=self.SYSTEM_PROMPT,
                messages=self.conversation_history,
            )

            content = message.content[0].text

            # 保存助手回复到对话历史
            self.conversation_history.append({"role": "assistant", "content": content})

            logger.info(f"生成完成，长度: {len(content)}")
            return content

        except anthropic.APIConnectionError as e:
            logger.exception("API连接错误")
            raise RuntimeError(f"API连接失败: {e}") from e
        except anthropic.RateLimitError as e:
            logger.exception("API速率限制")
            raise RuntimeError(f"请求过于频繁: {e}") from e
        except anthropic.APIStatusError as e:
            logger.exception("API状态错误")
            raise RuntimeError(f"API错误({e.status_code}): {e.message}") from e
        except Exception as e:
            logger.exception("生成失败")
            raise RuntimeError(f"生成失败: {e}") from e

    def followup(
        self,
        question: str,
        callback: Optional[Callable[[str], None]] = None
    ) -> str:
        """
        追问功能 - 基于当前对话历史继续对话

        Args:
            question: 追问的问题
            callback: 进度回调函数

        Returns:
            AI的回复
        """
        self._ensure_client()

        if not self.conversation_history:
            raise RuntimeError("没有对话历史，请先生成提示词")

        # 添加用户的追问到对话历史
        self.conversation_history.append({"role": "user", "content": question})

        try:
            logger.info("调用API进行追问...")
            if callback:
                callback("正在思考...")

            message = self._client.messages.create(
                model=self.api_config.model,
                max_tokens=8192,
                system=self.SYSTEM_PROMPT,
                messages=self.conversation_history,
            )

            content = message.content[0].text

            # 保存助手回复到对话历史
            self.conversation_history.append({"role": "assistant", "content": content})

            logger.info(f"追问完成，长度: {len(content)}")
            return content

        except anthropic.APIConnectionError as e:
            logger.exception("API连接错误")
            raise RuntimeError(f"API连接失败: {e}") from e
        except anthropic.RateLimitError as e:
            logger.exception("API速率限制")
            raise RuntimeError(f"请求过于频繁: {e}") from e
        except anthropic.APIStatusError as e:
            logger.exception("API状态错误")
            raise RuntimeError(f"API错误({e.status_code}): {e.message}") from e
        except Exception as e:
            logger.exception("追问失败")
            raise RuntimeError(f"追问失败: {e}") from e


# ============================================================
#                   PyInstaller 打包服务
# ============================================================

class PyInstallerService:
    """PyInstaller 打包服务"""

    @staticmethod
    def is_installed() -> bool:
        """检查 PyInstaller 是否已安装"""
        try:
            import PyInstaller
            return True
        except ImportError:
            return False

    @staticmethod
    def install(callback: Optional[Callable[[str], None]] = None) -> bool:
        """
        安装 PyInstaller

        Args:
            callback: 日志回调函数

        Returns:
            是否安装成功
        """
        try:
            if callback:
                callback("正在安装 PyInstaller...")

            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "pyinstaller"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            if callback:
                callback("PyInstaller 安装成功！")
            return True

        except Exception as e:
            if callback:
                callback(f"安装失败: {e}")
            return False

    @staticmethod
    def build(
        script_path: str,
        output_dir: str,
        name: str = "",
        onefile: bool = True,
        noconsole: bool = False,
        icon: str = "",
        clean: bool = True,
        additional_files: list = None,
        callback: Optional[Callable[[str], None]] = None
    ) -> bool:
        """
        打包 Python 脚本

        Args:
            script_path: 脚本路径
            output_dir: 输出目录
            name: 程序名称
            onefile: 单文件模式
            noconsole: 无控制台
            icon: 图标路径
            clean: 清理临时文件
            additional_files: 额外的 Python 文件
            callback: 日志回调函数

        Returns:
            是否打包成功
        """
        try:
            if callback:
                callback("=" * 50)
                callback("[DEBUG] 开始打包...")
                callback(f"[DEBUG] Python 解释器: {sys.executable}")
                callback(f"[DEBUG] Python 版本: {sys.version}")
                callback(f"[DEBUG] 当前工作目录: {os.getcwd()}")

            # 验证脚本路径
            script_path = os.path.abspath(script_path)
            if callback:
                callback(f"[DEBUG] 脚本路径: {script_path}")
                callback(f"[DEBUG] 脚本是否存在: {os.path.exists(script_path)}")

            if not os.path.exists(script_path):
                if callback:
                    callback(f"❌ 脚本文件不存在: {script_path}")
                return False

            # 获取脚本所在目录作为工作目录
            work_dir = os.path.dirname(script_path)
            if callback:
                callback(f"[DEBUG] 工作目录: {work_dir}")

            # 验证输出目录
            if output_dir:
                output_dir = os.path.abspath(output_dir)
                if callback:
                    callback(f"[DEBUG] 输出目录: {output_dir}")
                    callback(f"[DEBUG] 输出目录是否存在: {os.path.exists(output_dir)}")
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                    if callback:
                        callback(f"[DEBUG] 创建输出目录: {output_dir}")

            # 检查 PyInstaller 是否可用
            if callback:
                callback("[DEBUG] 检查 PyInstaller...")
            try:
                import PyInstaller
                if callback:
                    callback(f"[DEBUG] PyInstaller 版本: {PyInstaller.__version__}")
            except ImportError as e:
                if callback:
                    callback(f"[DEBUG] PyInstaller 未安装: {e}")
                    callback("❌ PyInstaller 未安装，请运行: pip install pyinstaller")
                return False

            # 使用 sys.executable -m PyInstaller 确保使用正确的 Python 环境
            cmd = [sys.executable, "-m", "PyInstaller"]

            if onefile:
                cmd.append("--onefile")

            if noconsole:
                cmd.append("--noconsole")

            if clean:
                cmd.append("--clean")

            # 设置输出目录
            if output_dir:
                cmd.extend(["--distpath", output_dir])
                # 同时设置 build 和 spec 文件目录，避免污染源码目录
                build_dir = os.path.join(output_dir, "build")
                cmd.extend(["--workpath", build_dir])
                cmd.extend(["--specpath", output_dir])

            if name:
                cmd.extend(["--name", name])

            if icon and os.path.exists(icon):
                cmd.extend(["--icon", os.path.abspath(icon)])

            # 检测是否是 CustomTkinter 应用，添加必要的 hook
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    script_content = f.read()

                # 检测 CustomTkinter
                if 'customtkinter' in script_content or 'ctk' in script_content:
                    if callback:
                        callback("[DEBUG] 检测到 CustomTkinter，添加相关配置...")
                    # 收集 customtkinter 数据文件
                    try:
                        import customtkinter
                        ctk_path = os.path.dirname(customtkinter.__file__)
                        cmd.extend(["--collect-data", "customtkinter"])
                        if callback:
                            callback(f"[DEBUG] CustomTkinter 路径: {ctk_path}")
                    except ImportError:
                        if callback:
                            callback("[WARNING] customtkinter 未安装")

                # 检测 tkinterdnd2
                if 'tkinterdnd2' in script_content:
                    if callback:
                        callback("[DEBUG] 检测到 tkinterdnd2，添加相关配置...")
                    cmd.extend(["--collect-data", "tkinterdnd2"])
                    cmd.extend(["--hidden-import", "tkinterdnd2"])

                # 检测 anthropic
                if 'anthropic' in script_content:
                    if callback:
                        callback("[DEBUG] 检测到 anthropic，添加相关配置...")
                    cmd.extend(["--hidden-import", "anthropic"])
                    cmd.extend(["--hidden-import", "httpx"])
                    cmd.extend(["--collect-data", "certifi"])

            except Exception as e:
                if callback:
                    callback(f"[WARNING] 分析脚本内容失败: {e}")

            # 添加额外的 Python 文件作为隐藏导入（不再添加为数据文件）
            if additional_files:
                for f in additional_files:
                    if f and os.path.exists(f):
                        f = os.path.abspath(f)
                        # 获取模块名（不带 .py 扩展名）
                        module_name = os.path.splitext(os.path.basename(f))[0]
                        cmd.extend(["--hidden-import", module_name])
                        if callback:
                            callback(f"[DEBUG] 添加隐藏导入: {module_name}")

            # 添加 -y 参数自动确认覆盖
            cmd.append("-y")

            cmd.append(script_path)

            if callback:
                callback("=" * 50)
                callback(f"[DEBUG] 完整命令: {' '.join(cmd)}")
                callback(f"[DEBUG] 命令列表: {cmd}")
                callback("=" * 50)

            logger.info(f"执行命令: {' '.join(cmd)}")
            logger.info(f"工作目录: {work_dir}")

            # 设置环境变量，解决 Windows 编码问题
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"

            if callback:
                callback("[DEBUG] 启动子进程...")

            # 执行打包
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

            if callback:
                callback(f"[DEBUG] 子进程已启动, PID: {process.pid}")
                callback("[DEBUG] 等待输出...")

            # 实时输出日志
            for line in process.stdout:
                line = line.strip()
                if line:
                    if callback:
                        callback(line)
                    logger.info(line)

            process.wait()

            success = process.returncode == 0
            if callback:
                if success:
                    # 显示输出文件位置
                    if output_dir and name:
                        exe_name = f"{name}.exe" if sys.platform == "win32" else name
                        exe_path = os.path.join(output_dir, exe_name)
                        if os.path.exists(exe_path):
                            callback(f"✅ 打包成功！")
                            callback(f"输出文件: {exe_path}")
                        else:
                            callback("✅ 打包成功！")
                    else:
                        callback("✅ 打包成功！")
                else:
                    callback(f"❌ 打包失败，返回码: {process.returncode}")

            return success

        except FileNotFoundError as e:
            logger.exception("找不到 PyInstaller")
            if callback:
                callback(f"❌ FileNotFoundError: {e}")
                callback("❌ 找不到 PyInstaller，请先安装: pip install pyinstaller")
            return False
        except PermissionError as e:
            logger.exception("权限错误")
            if callback:
                callback(f"❌ PermissionError: {e}")
                callback("❌ 权限不足，请检查文件和目录权限")
            return False
        except Exception as e:
            import traceback
            logger.exception("打包出错")
            if callback:
                callback(f"❌ 打包错误类型: {type(e).__name__}")
                callback(f"❌ 打包错误信息: {e}")
                callback(f"❌ 错误堆栈:\n{traceback.format_exc()}")
            return False

    @staticmethod
    def generate_command(
        script_path: str,
        output_dir: str = "",
        name: str = "",
        onefile: bool = True,
        noconsole: bool = False,
        icon: str = "",
        clean: bool = True,
    ) -> str:
        """
        生成打包命令（不执行）

        Returns:
            PyInstaller 命令字符串
        """
        # 使用 python -m PyInstaller 确保使用正确的 Python 环境
        parts = ["python", "-m", "PyInstaller"]

        if onefile:
            parts.append("-F")
        if noconsole:
            parts.append("-w")
        if clean:
            parts.append("--clean")
        if output_dir:
            parts.append(f'--distpath "{output_dir}"')
            parts.append(f'--workpath "{output_dir}\\build"')
            parts.append(f'--specpath "{output_dir}"')
        if name:
            parts.append(f'-n "{name}"')
        if icon:
            parts.append(f'--icon="{icon}"')

        # 自动确认覆盖
        parts.append("-y")
        parts.append(f'"{script_path}"')

        return " ".join(parts)

    @staticmethod
    def generate_bat(
        script_path: str,
        output_dir: str = "",
        name: str = "",
        onefile: bool = True,
        noconsole: bool = False,
        icon: str = "",
        clean: bool = True,
    ) -> str:
        """
        生成 BAT 脚本内容

        Returns:
            BAT 脚本内容
        """
        cmd = PyInstallerService.generate_command(
            script_path, output_dir, name, onefile, noconsole, icon, clean
        )

        script_name = os.path.basename(script_path)

        return f"""@echo off
chcp 65001 >nul
echo ========================================
echo   PyInstaller 打包脚本
echo ========================================
echo.
echo 正在打包: {script_name}
echo.
{cmd}
echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo 打包成功！
) else (
    echo 打包失败！
)
echo ========================================
pause
"""


# ============================================================
#                      文件服务
# ============================================================

class AIPackageAnalyzer:
    """AI 辅助打包分析服务"""

    ANALYZE_PROMPT = """你是一个 Python 打包专家。请分析以下项目文件，生成正确的 PyInstaller 打包配置。

项目结构：
{project_structure}

主入口文件内容：
```python
{main_content}
```

其他关键文件：
{other_files}

请分析这个项目并返回以下 JSON 格式（只返回 JSON，不要其他内容）：
{{
    "hidden_imports": ["需要隐藏导入的模块列表，包括项目内的模块如 config, models, views 等"],
    "collect_data": ["需要收集数据的第三方包列表，如 customtkinter"],
    "collect_all": ["需要完整收集的包列表"],
    "add_data": [],
    "extra_args": [],
    "explanation": "打包建议说明"
}}

重要规则：
1. hidden_imports 必须包含项目中所有被 import 的本地模块（如 config, models, services, views）
2. 如果使用了 customtkinter，必须在 collect_data 中添加 "customtkinter"
3. 如果使用了 anthropic 或 httpx，添加到 hidden_imports
4. extra_args 留空！不要添加 --onefile, --icon, --name, --windowed 等参数（这些由用户自己配置）
5. add_data 留空！（路径问题容易出错）
"""

    def __init__(self, api_config: APIConfig):
        self.api_config = api_config
        self._client = None

    def _ensure_client(self):
        """确保客户端已初始化"""
        if not self.api_config.is_configured():
            raise RuntimeError("API密钥未配置")

        if self._client is None:
            http_client = httpx.Client(
                verify=False,
                timeout=httpx.Timeout(120.0, connect=30.0),
                trust_env=False,
                proxy=None,
            )
            self._client = anthropic.Anthropic(
                http_client=http_client,
                api_key=self.api_config.api_key,
                base_url=self.api_config.base_url,
            )

    def analyze_project(
        self,
        project_dir: str,
        main_script: str,
        callback: Optional[Callable[[str], None]] = None
    ) -> dict:
        """
        分析项目并生成打包建议

        Args:
            project_dir: 项目目录
            main_script: 主入口文件
            callback: 进度回调

        Returns:
            打包配置字典
        """
        import json
        import glob

        self._ensure_client()

        if callback:
            callback("正在扫描项目文件...")

        # 收集项目结构
        project_files = []
        py_files = []
        for ext in ['*.py', '*.json', '*.yaml', '*.yml', '*.ini', '*.cfg']:
            for f in glob.glob(os.path.join(project_dir, '**', ext), recursive=True):
                rel_path = os.path.relpath(f, project_dir)
                if '__pycache__' not in rel_path and 'venv' not in rel_path:
                    project_files.append(rel_path)
                    if f.endswith('.py'):
                        py_files.append(f)

        project_structure = "\n".join(project_files)

        # 读取主文件内容
        main_content = ""
        try:
            with open(main_script, 'r', encoding='utf-8') as f:
                main_content = f.read()
        except Exception as e:
            logger.error(f"读取主文件失败: {e}")

        # 读取其他 Python 文件内容（限制大小）
        other_files_content = []
        for py_file in py_files[:10]:  # 最多10个文件
            if py_file != main_script:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if len(content) < 5000:  # 限制单文件大小
                            rel_name = os.path.relpath(py_file, project_dir)
                            other_files_content.append(f"--- {rel_name} ---\n```python\n{content}\n```")
                except:
                    pass

        other_files = "\n\n".join(other_files_content) if other_files_content else "无"

        # 构建提示词
        prompt = self.ANALYZE_PROMPT.format(
            project_structure=project_structure,
            main_content=main_content[:8000],  # 限制长度
            other_files=other_files[:15000]
        )

        if callback:
            callback("正在调用 AI 分析项目...")

        try:
            message = self._client.messages.create(
                model=self.api_config.model,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text.strip()

            # 尝试提取 JSON
            if callback:
                callback("正在解析 AI 响应...")

            # 查找 JSON 块
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)

                if callback:
                    callback("✅ AI 分析完成")

                return result
            else:
                raise ValueError("AI 响应中未找到 JSON")

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            if callback:
                callback(f"❌ JSON 解析失败: {e}")
            return self._get_default_config(project_dir, main_script)
        except Exception as e:
            logger.error(f"AI 分析失败: {e}")
            if callback:
                callback(f"❌ AI 分析失败: {e}")
            return self._get_default_config(project_dir, main_script)

    def _get_default_config(self, project_dir: str, main_script: str) -> dict:
        """获取默认打包配置"""
        # 扫描项目中的 Python 文件作为隐藏导入
        hidden_imports = []
        for f in os.listdir(project_dir):
            if f.endswith('.py') and f != os.path.basename(main_script) and f != '__init__.py':
                module_name = f[:-3]
                hidden_imports.append(module_name)

        return {
            "main_script": main_script,
            "hidden_imports": hidden_imports,
            "collect_data": ["customtkinter"],
            "collect_all": [],
            "add_data": [],
            "extra_args": [],
            "explanation": "使用默认配置（AI 分析失败时的备选方案）"
        }


class FileService:
    """文件操作服务"""

    @staticmethod
    def export_text(content: str, filepath: str) -> bool:
        """导出文本文件"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False

    @staticmethod
    def import_text(filepath: str) -> Optional[str]:
        """导入文本文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"导入失败: {e}")
            return None

    @staticmethod
    def open_directory(path: str):
        """打开目录"""
        if os.path.exists(path):
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
