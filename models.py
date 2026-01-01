"""
数据模型层 - 数据结构定义和持久化操作
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from .config import (
        HISTORY_FILE,
        FAVORITES_FILE,
        SETTINGS_FILE,
        TEMPLATES_FILE,
        SNIPPETS_FILE,
        CUSTOM_CONFIG_FILE,
        AI_WEBSITES_FILE,
        DEFAULT_SETTINGS,
        DEFAULT_TEMPLATES,
        DEFAULT_SNIPPETS,
        DEFAULT_AI_WEBSITES,
        LANGUAGE_FRAMEWORKS,
        DEFAULT_PRIORITIES,
    )
except ImportError:
    from config import (
        HISTORY_FILE,
        FAVORITES_FILE,
        SETTINGS_FILE,
        TEMPLATES_FILE,
        SNIPPETS_FILE,
        CUSTOM_CONFIG_FILE,
        AI_WEBSITES_FILE,
        DEFAULT_SETTINGS,
        DEFAULT_TEMPLATES,
        DEFAULT_SNIPPETS,
        DEFAULT_AI_WEBSITES,
        LANGUAGE_FRAMEWORKS,
        DEFAULT_PRIORITIES,
    )

logger = logging.getLogger(__name__)


# ============================================================
#                       数据类定义
# ============================================================

@dataclass
class APIConfig:
    """API配置"""
    api_key: str = ""
    base_url: str = "https://api.anthropic.com"
    model: str = "claude-haiku-4-5-20251001"

    def is_configured(self) -> bool:
        return bool(self.api_key)


@dataclass
class ProjectInfo:
    """项目信息"""
    idea: str = ""
    language: str = "Python"
    category: str = ""
    framework: str = ""
    priority: str = "功能完整"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    uploaded_files: list = field(default_factory=list)  # 上传的文件列表


@dataclass
class UploadedFile:
    """上传的文件信息"""
    filename: str
    content: str
    file_type: str  # 文件类型，如 text, code, etc.
    size: int  # 文件大小（字节）


@dataclass
class ConversationMessage:
    """对话消息"""
    role: str  # 'user' 或 'assistant'
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class HistoryRecord:
    """历史记录"""
    timestamp: str
    language: str
    framework: str
    idea_preview: str
    prompt: str


@dataclass
class FavoriteRecord:
    """收藏记录"""
    name: str
    timestamp: str
    language: str
    framework: str
    prompt: str


# ============================================================
#                     数据管理器
# ============================================================

class DataManager:
    """数据持久化管理器"""

    @staticmethod
    def _load_json(file_path: Path, default=None):
        """加载JSON文件"""
        if default is None:
            default = {}
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载 {file_path} 失败: {e}")
        return default

    @staticmethod
    def _save_json(file_path: Path, data) -> bool:
        """保存JSON文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存 {file_path} 失败: {e}")
            return False

    # -------------------- 设置 --------------------

    @classmethod
    def load_settings(cls) -> dict:
        """加载设置"""
        settings = cls._load_json(SETTINGS_FILE, DEFAULT_SETTINGS.copy())
        # 合并默认设置（确保新增字段有默认值）
        for key, value in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = value
        return settings

    @classmethod
    def save_settings(cls, settings: dict) -> bool:
        """保存设置"""
        return cls._save_json(SETTINGS_FILE, settings)

    # -------------------- 历史记录 --------------------

    @classmethod
    def load_history(cls) -> list:
        """加载历史记录"""
        return cls._load_json(HISTORY_FILE, [])

    @classmethod
    def save_history(cls, history: list) -> bool:
        """保存历史记录（最多50条）"""
        history = history[-50:]
        return cls._save_json(HISTORY_FILE, history)

    @classmethod
    def add_history(cls, record: HistoryRecord) -> bool:
        """添加历史记录"""
        history = cls.load_history()
        history.append(asdict(record))
        return cls.save_history(history)

    @classmethod
    def clear_history(cls) -> bool:
        """清空历史记录"""
        return cls._save_json(HISTORY_FILE, [])

    # -------------------- 收藏 --------------------

    @classmethod
    def load_favorites(cls) -> list:
        """加载收藏"""
        return cls._load_json(FAVORITES_FILE, [])

    @classmethod
    def save_favorites(cls, favorites: list) -> bool:
        """保存收藏"""
        return cls._save_json(FAVORITES_FILE, favorites)

    @classmethod
    def add_favorite(cls, record: FavoriteRecord) -> bool:
        """添加收藏"""
        favorites = cls.load_favorites()
        favorites.append(asdict(record))
        return cls.save_favorites(favorites)

    @classmethod
    def clear_favorites(cls) -> bool:
        """清空收藏"""
        return cls._save_json(FAVORITES_FILE, [])

    # -------------------- 模板 --------------------

    @classmethod
    def load_templates(cls) -> dict:
        """加载自定义模板"""
        return cls._load_json(TEMPLATES_FILE, {})

    @classmethod
    def save_templates(cls, templates: dict) -> bool:
        """保存自定义模板"""
        return cls._save_json(TEMPLATES_FILE, templates)

    @classmethod
    def get_all_templates(cls) -> dict:
        """获取所有模板（内置 + 自定义）"""
        custom = cls.load_templates()
        return {**DEFAULT_TEMPLATES, **custom}

    # -------------------- 快捷片段 --------------------

    @classmethod
    def load_snippets(cls) -> dict:
        """加载自定义快捷片段"""
        return cls._load_json(SNIPPETS_FILE, {})

    @classmethod
    def save_snippets(cls, snippets: dict) -> bool:
        """保存自定义快捷片段"""
        return cls._save_json(SNIPPETS_FILE, snippets)

    @classmethod
    def get_all_snippets(cls) -> dict:
        """获取所有片段（预置 + 自定义）"""
        custom = cls.load_snippets()
        # 预置片段优先，自定义片段不能覆盖预置
        all_snippets = {**DEFAULT_SNIPPETS}
        for name, snippet in custom.items():
            if name not in DEFAULT_SNIPPETS:
                all_snippets[name] = snippet
        return all_snippets

    @classmethod
    def add_snippet(cls, name: str, category: str, content: str) -> bool:
        """添加自定义片段"""
        if name in DEFAULT_SNIPPETS:
            logger.warning(f"不能覆盖预置片段: {name}")
            return False

        snippets = cls.load_snippets()
        snippets[name] = {
            "category": category,
            "content": content,
            "is_preset": False,
        }
        return cls.save_snippets(snippets)

    @classmethod
    def update_snippet(cls, name: str, category: str, content: str) -> bool:
        """更新自定义片段"""
        if name in DEFAULT_SNIPPETS:
            logger.warning(f"不能修改预置片段: {name}")
            return False

        snippets = cls.load_snippets()
        if name not in snippets:
            logger.warning(f"片段不存在: {name}")
            return False

        snippets[name] = {
            "category": category,
            "content": content,
            "is_preset": False,
        }
        return cls.save_snippets(snippets)

    @classmethod
    def delete_snippet(cls, name: str) -> bool:
        """删除自定义片段"""
        if name in DEFAULT_SNIPPETS:
            logger.warning(f"不能删除预置片段: {name}")
            return False

        snippets = cls.load_snippets()
        if name in snippets:
            del snippets[name]
            return cls.save_snippets(snippets)
        return False

    @classmethod
    def search_snippets(cls, keyword: str = "", category: str = "") -> dict:
        """搜索片段"""
        all_snippets = cls.get_all_snippets()
        results = {}

        for name, snippet in all_snippets.items():
            # 按分类过滤
            if category and snippet.get("category") != category:
                continue

            # 按关键词过滤（名称或内容）
            if keyword:
                keyword_lower = keyword.lower()
                if (keyword_lower not in name.lower() and
                    keyword_lower not in snippet.get("content", "").lower()):
                    continue

            results[name] = snippet

        return results

    # -------------------- 自定义配置 --------------------

    @classmethod
    def load_custom_config(cls) -> dict:
        """加载自定义配置"""
        default = {
            "languages": {},  # 自定义语言 {name: {icon, categories}}
            "priorities": [],  # 自定义优先级
        }
        return cls._load_json(CUSTOM_CONFIG_FILE, default)

    @classmethod
    def save_custom_config(cls, config: dict) -> bool:
        """保存自定义配置"""
        return cls._save_json(CUSTOM_CONFIG_FILE, config)

    @classmethod
    def get_all_languages(cls) -> dict:
        """获取所有语言配置（内置 + 自定义）"""
        custom = cls.load_custom_config()
        custom_languages = custom.get("languages", {})
        # 合并，自定义可以扩展但不能覆盖内置
        all_languages = dict(LANGUAGE_FRAMEWORKS)
        for lang, info in custom_languages.items():
            if lang not in all_languages:
                all_languages[lang] = info
            else:
                # 合并类别
                for cat, frameworks in info.get("categories", {}).items():
                    if cat not in all_languages[lang]["categories"]:
                        all_languages[lang]["categories"][cat] = frameworks
                    else:
                        # 合并框架列表
                        existing = all_languages[lang]["categories"][cat]
                        for fw in frameworks:
                            if fw not in existing:
                                existing.append(fw)
        return all_languages

    @classmethod
    def get_all_priorities(cls) -> list:
        """获取所有优先级（内置 + 自定义）"""
        custom = cls.load_custom_config()
        custom_priorities = custom.get("priorities", [])
        all_priorities = list(DEFAULT_PRIORITIES)
        for p in custom_priorities:
            if p not in all_priorities:
                all_priorities.append(p)
        return all_priorities

    @classmethod
    def add_language(cls, name: str, icon: str = "🌐") -> bool:
        """添加新语言"""
        if name in LANGUAGE_FRAMEWORKS:
            return False  # 不能覆盖内置

        config = cls.load_custom_config()
        if "languages" not in config:
            config["languages"] = {}

        config["languages"][name] = {
            "icon": icon,
            "categories": {"通用": ["自定义"]}
        }
        return cls.save_custom_config(config)

    @classmethod
    def add_category_to_language(cls, language: str, category: str, frameworks: list = None) -> bool:
        """为语言添加类别"""
        config = cls.load_custom_config()
        if "languages" not in config:
            config["languages"] = {}

        if language not in config["languages"]:
            # 如果是内置语言，创建扩展配置
            if language in LANGUAGE_FRAMEWORKS:
                config["languages"][language] = {
                    "icon": LANGUAGE_FRAMEWORKS[language].get("icon", "🌐"),
                    "categories": {}
                }
            else:
                return False

        config["languages"][language]["categories"][category] = frameworks or ["自定义"]
        return cls.save_custom_config(config)

    @classmethod
    def add_framework_to_category(cls, language: str, category: str, framework: str) -> bool:
        """为类别添加框架"""
        config = cls.load_custom_config()
        if "languages" not in config:
            config["languages"] = {}

        if language not in config["languages"]:
            if language in LANGUAGE_FRAMEWORKS:
                config["languages"][language] = {
                    "icon": LANGUAGE_FRAMEWORKS[language].get("icon", "🌐"),
                    "categories": {}
                }
            else:
                return False

        if category not in config["languages"][language]["categories"]:
            config["languages"][language]["categories"][category] = []

        if framework not in config["languages"][language]["categories"][category]:
            config["languages"][language]["categories"][category].append(framework)

        return cls.save_custom_config(config)

    @classmethod
    def add_priority(cls, priority: str) -> bool:
        """添加自定义优先级"""
        if priority in DEFAULT_PRIORITIES:
            return False  # 不能重复

        config = cls.load_custom_config()
        if "priorities" not in config:
            config["priorities"] = []

        if priority not in config["priorities"]:
            config["priorities"].append(priority)
            return cls.save_custom_config(config)
        return False

    @classmethod
    def delete_custom_language(cls, name: str) -> bool:
        """删除自定义语言"""
        if name in LANGUAGE_FRAMEWORKS:
            return False  # 不能删除内置

        config = cls.load_custom_config()
        if name in config.get("languages", {}):
            del config["languages"][name]
            return cls.save_custom_config(config)
        return False

    @classmethod
    def delete_custom_priority(cls, priority: str) -> bool:
        """删除自定义优先级"""
        if priority in DEFAULT_PRIORITIES:
            return False  # 不能删除内置

        config = cls.load_custom_config()
        if priority in config.get("priorities", []):
            config["priorities"].remove(priority)
            return cls.save_custom_config(config)
        return False

    # -------------------- AI网站管理 --------------------

    @classmethod
    def load_ai_websites(cls) -> dict:
        """加载自定义AI网站"""
        return cls._load_json(AI_WEBSITES_FILE, {})

    @classmethod
    def save_ai_websites(cls, websites: dict) -> bool:
        """保存自定义AI网站"""
        return cls._save_json(AI_WEBSITES_FILE, websites)

    @classmethod
    def get_all_ai_websites(cls) -> dict:
        """获取所有AI网站（预置 + 自定义）"""
        custom = cls.load_ai_websites()
        # 预置优先，自定义不能覆盖
        all_websites = dict(DEFAULT_AI_WEBSITES)
        for name, info in custom.items():
            if name not in DEFAULT_AI_WEBSITES:
                all_websites[name] = info
        return all_websites

    @classmethod
    def add_ai_website(cls, name: str, url: str, description: str = "") -> bool:
        """添加自定义AI网站"""
        if name in DEFAULT_AI_WEBSITES:
            return False  # 不能覆盖预置

        websites = cls.load_ai_websites()
        websites[name] = {
            "url": url,
            "description": description,
            "is_preset": False,
        }
        return cls.save_ai_websites(websites)

    @classmethod
    def update_ai_website(cls, name: str, url: str, description: str = "") -> bool:
        """更新自定义AI网站"""
        if name in DEFAULT_AI_WEBSITES:
            return False  # 不能修改预置

        websites = cls.load_ai_websites()
        if name not in websites:
            return False

        websites[name] = {
            "url": url,
            "description": description,
            "is_preset": False,
        }
        return cls.save_ai_websites(websites)

    @classmethod
    def delete_ai_website(cls, name: str) -> bool:
        """删除自定义AI网站"""
        if name in DEFAULT_AI_WEBSITES:
            return False  # 不能删除预置

        websites = cls.load_ai_websites()
        if name in websites:
            del websites[name]
            return cls.save_ai_websites(websites)
        return False
