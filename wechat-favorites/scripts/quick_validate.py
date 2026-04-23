# -*- coding: utf-8 -*-
"""
快速验证脚本 - 检查 skill 依赖和配置是否就绪
用法: python quick_validate.py
"""
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def check_python_version():
    """检查 Python 版本"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        return False, f"Python 3.8+ required, got {version.major}.{version.minor}"
    return True, f"Python {version.major}.{version.minor}.{version.micro}"

def check_dependencies():
    """检查依赖包"""
    missing = []
    try:
        import zstandard
    except ImportError:
        missing.append("zstandard")
    
    try:
        from Crypto.Cipher import AES
    except ImportError:
        missing.append("pycryptodome")
    
    if missing:
        return False, f"Missing: {', '.join(missing)}. Run: pip install {' '.join(missing)}"
    return True, "All dependencies installed"

def check_config():
    """检查配置文件"""
    cfg_path = os.path.join(SCRIPT_DIR, "config.json")
    example_path = os.path.join(SCRIPT_DIR, "config.json.example")
    
    if not os.path.exists(example_path):
        return False, "config.json.example missing"
    
    if not os.path.exists(cfg_path):
        return False, "config.json not found. Copy config.json.example and fill in values"
    
    try:
        import json
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        
        # 检查关键字段
        if not cfg.get("db_dir"):
            return False, "config.json: db_dir not set"
        
        return True, "config.json valid"
    except Exception as e:
        return False, f"config.json parse error: {e}"

def check_decrypted_db():
    """检查解密数据库是否存在"""
    db_path = os.path.join(SCRIPT_DIR, "decrypted", "favorite", "favorite.db")
    if os.path.exists(db_path):
        size = os.path.getsize(db_path) / 1024
        return True, f"favorite.db found ({size:.1f} KB)"
    return False, "favorite.db not found. Run decrypt_db.py first"

def check_ima_credentials():
    """检查 IMA 凭证（可选）"""
    client_id_path = os.path.expanduser("~/.config/ima/client_id")
    api_key_path = os.path.expanduser("~/.config/ima/api_key")
    
    has_client_id = os.path.exists(client_id_path)
    has_api_key = os.path.exists(api_key_path)
    
    if has_client_id and has_api_key:
        return True, "IMA credentials configured"
    elif has_client_id or has_api_key:
        return False, "IMA credentials incomplete (need both client_id and api_key)"
    return None, "IMA credentials not configured (optional for IMA import)"

def main():
    print("=" * 60)
    print("  WeChat Favorites Skill - Quick Validation")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Config File", check_config),
        ("Decrypted DB", check_decrypted_db),
        ("IMA Credentials", check_ima_credentials),
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            result, msg = check_func()
            if result is None:
                status = "⚠️ "
            elif result:
                status = "✅"
            else:
                status = "❌"
                all_passed = False
            print(f"{status} {name}: {msg}")
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All checks passed! Ready to use.")
    else:
        print("❌ Some checks failed. Fix above issues before using.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
