"""
简化兑换码系统 - 两种套餐

套餐一：生成提示词 + 跳转
套餐二：生成提示词 + 跳转 + 打包
"""

import json
import secrets
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass

# 数据文件路径
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
CODES_FILE = DATA_DIR / "codes.json"
LICENSE_FILE = DATA_DIR / "license.json"

# ============================================================
#                    预设兑换码（打包后可用）
# ============================================================
# 格式: "兑换码": "套餐类型(basic/pro)"
# 这些兑换码会硬编码到程序里，打包给别人后可直接使用
PRESET_CODES = {
    # 基础版兑换码（提示词 + 跳转）
    "BASIC-2024-ABCD-1234": "basic",
    "BASIC-2024-EFGH-5678": "basic",
    "BASIC-2024-IJKL-9012": "basic",

    # 专业版兑换码（全功能）
    "PRO-2024-MNOP-3456": "pro",
    "PRO-2024-QRST-7890": "pro",
    "PRO-2024-UVWX-1357": "pro",
}
# ============================================================

# 套餐定义
PACKAGES = {
    "basic": {
        "name": "基础版",
        "features": ["prompt", "jump"],
        "description": "生成提示词 + 复制跳转"
    },
    "pro": {
        "name": "专业版",
        "features": ["prompt", "jump", "package"],
        "description": "生成提示词 + 复制跳转 + PyInstaller打包"
    }
}

# 功能定义
FEATURES = {
    "prompt": "生成提示词",
    "jump": "复制跳转",
    "package": "PyInstaller打包"
}


@dataclass
class CodeInfo:
    """兑换码信息"""
    code: str
    package_type: str  # basic 或 pro
    expires_at: Optional[str] = None
    is_used: bool = False
    created_at: str = ""


class CodeManager:
    """兑换码管理器"""

    def __init__(self):
        self._ensure_files()

    def _ensure_files(self):
        """确保数据文件存在"""
        if not CODES_FILE.exists():
            self._save_codes({})
        if not LICENSE_FILE.exists():
            self._save_license({"unlocked_features": [], "activated_at": None})

    def _load_codes(self) -> dict:
        """加载兑换码数据"""
        try:
            with open(CODES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}

    def _save_codes(self, codes: dict):
        """保存兑换码数据"""
        with open(CODES_FILE, "w", encoding="utf-8") as f:
            json.dump(codes, f, indent=2, ensure_ascii=False)

    def _load_license(self) -> dict:
        """加载授权状态"""
        try:
            with open(LICENSE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"unlocked_features": [], "activated_at": None}

    def _save_license(self, license_data: dict):
        """保存授权状态"""
        with open(LICENSE_FILE, "w", encoding="utf-8") as f:
            json.dump(license_data, f, indent=2, ensure_ascii=False)

    def _load_used_preset_codes(self) -> list:
        """加载已使用的预设兑换码"""
        license_data = self._load_license()
        return license_data.get("used_preset_codes", [])

    def _save_used_preset_code(self, code: str):
        """保存已使用的预设兑换码"""
        license_data = self._load_license()
        used = license_data.get("used_preset_codes", [])
        if code not in used:
            used.append(code)
            license_data["used_preset_codes"] = used
            self._save_license(license_data)

    def generate_code(self, package_type: str, expires_days: Optional[int] = None) -> str:
        """
        生成兑换码

        参数:
            package_type: "basic" 或 "pro"
            expires_days: 有效天数，None表示永久
        """
        # 生成随机码：XXXX-XXXX-XXXX-XXXX
        chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        segments = []
        for _ in range(4):
            segment = ''.join(secrets.choice(chars) for _ in range(4))
            segments.append(segment)
        code = '-'.join(segments)

        # 计算过期时间
        expires_at = None
        if expires_days:
            expires_at = (datetime.now() + timedelta(days=expires_days)).isoformat()

        # 保存兑换码
        codes = self._load_codes()
        codes[code] = {
            "package_type": package_type,
            "expires_at": expires_at,
            "is_used": False,
            "created_at": datetime.now().isoformat()
        }
        self._save_codes(codes)

        return code

    def generate_batch(self, package_type: str, count: int, expires_days: Optional[int] = None) -> list:
        """批量生成兑换码"""
        return [self.generate_code(package_type, expires_days) for _ in range(count)]

    def verify_code(self, code: str) -> tuple[bool, str, Optional[str]]:
        """
        验证兑换码

        返回: (是否有效, 消息, 套餐类型)
        """
        code = code.strip().upper()

        # 1. 先检查预设兑换码
        if code in PRESET_CODES:
            # 检查是否已在本机使用过
            used_preset = self._load_used_preset_codes()
            if code in used_preset:
                return False, "该兑换码已在本机使用", None
            return True, "兑换码有效", PRESET_CODES[code]

        # 2. 再检查本地生成的兑换码
        codes = self._load_codes()

        if code not in codes:
            return False, "兑换码无效", None

        code_info = codes[code]

        if code_info["is_used"]:
            return False, "该兑换码已被使用", None

        # 检查是否过期
        if code_info["expires_at"]:
            expires = datetime.fromisoformat(code_info["expires_at"])
            if datetime.now() > expires:
                return False, "该兑换码已过期", None

        return True, "兑换码有效", code_info["package_type"]

    def redeem_code(self, code: str) -> tuple[bool, str]:
        """
        兑换激活码

        返回: (是否成功, 消息)
        """
        code = code.strip().upper()
        is_valid, message, package_type = self.verify_code(code)

        if not is_valid:
            return False, message

        # 检查是否是预设兑换码
        if code in PRESET_CODES:
            # 标记预设码在本机已使用
            self._save_used_preset_code(code)
        else:
            # 标记本地生成的码为已使用
            codes = self._load_codes()
            codes[code]["is_used"] = True
            codes[code]["used_at"] = datetime.now().isoformat()
            self._save_codes(codes)

        # 解锁功能
        package_info = PACKAGES.get(package_type, PACKAGES["basic"])
        license_data = self._load_license()
        license_data["unlocked_features"] = package_info["features"]
        license_data["activated_at"] = datetime.now().isoformat()
        license_data["package_type"] = package_type
        self._save_license(license_data)

        return True, f"激活成功！已解锁：{package_info['name']} ({package_info['description']})"

    def is_feature_unlocked(self, feature: str) -> bool:
        """检查功能是否已解锁"""
        license_data = self._load_license()
        return feature in license_data.get("unlocked_features", [])

    def get_unlocked_features(self) -> list:
        """获取已解锁的功能列表"""
        license_data = self._load_license()
        return license_data.get("unlocked_features", [])

    def get_license_info(self) -> dict:
        """获取授权信息"""
        return self._load_license()

    def get_all_codes(self) -> list:
        """获取所有兑换码（管理员用）"""
        codes = self._load_codes()
        result = []
        for code, info in codes.items():
            result.append({
                "code": code,
                **info
            })
        return sorted(result, key=lambda x: x.get("created_at", ""), reverse=True)

    def get_preset_codes(self) -> list:
        """获取预设兑换码列表"""
        used_preset = self._load_used_preset_codes()
        result = []
        for code, pkg_type in PRESET_CODES.items():
            result.append({
                "code": code,
                "package_type": pkg_type,
                "is_preset": True,
                "is_used": code in used_preset,
            })
        return result

    def delete_code(self, code: str) -> bool:
        """删除兑换码"""
        codes = self._load_codes()
        if code in codes:
            del codes[code]
            self._save_codes(codes)
            return True
        return False

    def reset_license(self):
        """重置授权（用于测试）"""
        self._save_license({"unlocked_features": [], "activated_at": None})


# 单例
_manager: Optional[CodeManager] = None

def get_code_manager() -> CodeManager:
    """获取兑换码管理器单例"""
    global _manager
    if _manager is None:
        _manager = CodeManager()
    return _manager
