#!/usr/bin/env python3
"""
API Connector 通用 API 连接器
统一接口调用任何 API

用法：
    python api-connector.py config add github --base-url "https://api.github.com" --auth-type bearer --token $TOKEN
    python api-connector.py call github /users/mizai
    python api-connector.py call github /repos --method POST --body '{"name":"my-repo"}'
"""

import argparse
import json
import os
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
import re

# 尝试导入 httpx，如果不存在则用 requests
try:
    import httpx
    HTTP_CLIENT = "httpx"
except ImportError:
    try:
        import requests
        HTTP_CLIENT = "requests"
    except ImportError:
        print("❌ 需要安装 httpx 或 requests: pip install httpx")
        sys.exit(1)

# 配置
CONFIG_DIR = os.path.expanduser("~/.openclaw/api-connector")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
CACHE_DIR = os.path.join(CONFIG_DIR, "cache")
HISTORY_FILE = os.path.join(CONFIG_DIR, "history.json")

def ensure_dirs():
    """确保目录存在"""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)

def load_config():
    """加载配置文件"""
    ensure_dirs()
    if not os.path.exists(CONFIG_FILE):
        return {"apis": {}, "defaults": {"timeout": 30}}
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置文件"""
    ensure_dirs()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def expand_env_vars(value):
    """展开环境变量 ${VAR} 或 $VAR"""
    if not isinstance(value, str):
        return value
    
    # 匹配 ${VAR} 格式
    pattern = r'\$\{([^}]+)\}'
    def replace(match):
        var_name = match.group(1)
        return os.getenv(var_name, match.group(0))
    
    result = re.sub(pattern, replace, value)
    
    # 匹配 $VAR 格式（简单情况）
    if '$' in result:
        for match in re.finditer(r'\$(\w+)', result):
            var_name = match.group(1)
            env_value = os.getenv(var_name)
            if env_value:
                result = result.replace(f'${var_name}', env_value)
    
    return result

def resolve_config_value(value):
    """递归解析配置中的环境变量"""
    if isinstance(value, str):
        return expand_env_vars(value)
    elif isinstance(value, dict):
        return {k: resolve_config_value(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [resolve_config_value(v) for v in value]
    return value

def add_api_config(args):
    """添加 API 配置"""
    config = load_config()
    
    api_config = {
        "baseUrl": args.base_url,
        "authType": args.auth_type,
        "headers": {}
    }
    
    # 认证配置
    if args.auth_type == "bearer":
        api_config["token"] = args.token
    elif args.auth_type == "api-key":
        api_config["apiKey"] = args.api_key
        if args.api_key_header:
            api_config["apiKeyHeader"] = args.api_key_header
    elif args.auth_type == "basic":
        api_config["username"] = args.username
        api_config["password"] = args.password
    elif args.auth_type == "oauth2":
        api_config["clientId"] = args.client_id
        api_config["clientSecret"] = args.client_secret
        if args.redirect_uri:
            api_config["redirectUri"] = args.redirect_uri
    
    # 添加自定义 headers
    if args.header:
        for h in args.header:
            if ':' in h:
                key, value = h.split(':', 1)
                api_config["headers"][key.strip()] = value.strip()
    
    # 超时配置
    if args.timeout:
        api_config["timeout"] = args.timeout
    
    config["apis"][args.name] = api_config
    save_config(config)
    
    print(f"✅ API 配置已添加：{args.name}")
    print(f"   Base URL: {args.base_url}")
    print(f"   认证类型：{args.auth_type}")

def list_configs(args):
    """列出所有 API 配置"""
    config = load_config()
    apis = config.get("apis", {})
    
    if not apis:
        print("📭 没有配置的 API")
        return
    
    print("\n" + "="*60)
    print("🔌 已配置的 API")
    print("="*60 + "\n")
    
    for name, api_config in apis.items():
        auth_type = api_config.get("authType", "none")
        base_url = api_config.get("baseUrl", "")
        
        auth_icon = {
            "bearer": "🔑",
            "api-key": "🔐",
            "basic": "👤",
            "oauth2": "🌐",
            "none": "⚪"
        }.get(auth_type, "❓")
        
        print(f"{auth_icon} {name}")
        print(f"   URL: {base_url}")
        print(f"   认证：{auth_type}")
        print()

def show_config(args):
    """显示 API 配置详情"""
    config = load_config()
    api_config = config.get("apis", {}).get(args.name)
    
    if not api_config:
        print(f"❌ API '{args.name}' 未配置")
        return
    
    print(f"\n🔌 API 配置：{args.name}\n")
    print(json.dumps(resolve_config_value(api_config), indent=2, ensure_ascii=False))
    print()

def remove_config(args):
    """删除 API 配置"""
    config = load_config()
    
    if args.name not in config.get("apis", {}):
        print(f"❌ API '{args.name}' 未配置")
        return
    
    del config["apis"][args.name]
    save_config(config)
    print(f"✅ API 配置已删除：{args.name}")

def make_request(api_name, path, method="GET", params=None, body=None, headers=None, 
                 use_cache=False, cache_ttl=300, verbose=False):
    """发送 HTTP 请求"""
    config = load_config()
    api_config = config.get("apis", {}).get(api_name)
    
    if not api_config:
        print(f"❌ API '{api_name}' 未配置")
        sys.exit(1)
    
    # 解析配置
    api_config = resolve_config_value(api_config)
    
    base_url = api_config.get("baseUrl", "")
    timeout = api_config.get("timeout", config.get("defaults", {}).get("timeout", 30))
    
    # 构建 URL
    url = base_url.rstrip('/') + '/' + path.lstrip('/')
    
    # 构建请求头
    request_headers = dict(api_config.get("headers", {}))
    if headers:
        request_headers.update(headers)
    
    # 添加认证
    auth_type = api_config.get("authType", "none")
    if auth_type == "bearer":
        token = api_config.get("token", "")
        request_headers["Authorization"] = f"Bearer {token}"
    elif auth_type == "api-key":
        api_key = api_config.get("apiKey", "")
        header_name = api_config.get("apiKeyHeader", "X-API-Key")
        request_headers[header_name] = api_key
    elif auth_type == "basic":
        import base64
        username = api_config.get("username", "")
        password = api_config.get("password", "")
        credentials = f"{username}:{password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        request_headers["Authorization"] = f"Basic {encoded}"
    
    # 检查缓存
    cache_key = None
    if use_cache:
        cache_key = hashlib.md5(f"{method}:{url}:{json.dumps(params or {})}".encode()).hexdigest()
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            cached_at = datetime.fromisoformat(cache_data["cached_at"])
            if datetime.now() - cached_at < timedelta(seconds=cache_ttl):
                if verbose:
                    print(f"💾 使用缓存响应")
                return cache_data["response"], cache_data["status_code"], cache_data["headers"], True
    
    # 发送请求
    if verbose:
        print(f"🌐 {method} {url}")
        if params:
            print(f"   参数：{params}")
        if body:
            print(f"   请求体：{body}")
    
    try:
        if HTTP_CLIENT == "httpx":
            response = httpx.request(
                method,
                url,
                params=params,
                json=body if isinstance(body, dict) else None,
                data=body if isinstance(body, str) else None,
                headers=request_headers,
                timeout=timeout
            )
            status_code = response.status_code
            response_headers = dict(response.headers)
            response_body = response.text
        else:
            response = requests.request(
                method,
                url,
                params=params,
                json=body if isinstance(body, dict) else None,
                data=body if isinstance(body, str) else None,
                headers=request_headers,
                timeout=timeout
            )
            status_code = response.status_code
            response_headers = dict(response.headers)
            response_body = response.text
        
        # 保存缓存
        if use_cache and cache_key and 200 <= status_code < 300:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "url": url,
                "status_code": status_code,
                "headers": response_headers,
                "response": response_body
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        # 记录历史
        record_history(api_name, method, path, status_code)
        
        return response_body, status_code, response_headers, False
        
    except Exception as e:
        print(f"❌ 请求失败：{e}")
        sys.exit(1)

def record_history(api_name, method, path, status_code):
    """记录调用历史"""
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history = json.load(f)
    
    history.append({
        "timestamp": datetime.now().isoformat(),
        "api": api_name,
        "method": method,
        "path": path,
        "status_code": status_code
    })
    
    # 保留最近 1000 条记录
    history = history[-1000:]
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def call_api(args):
    """调用 API"""
    # 解析路径参数 {param} -> value
    path = args.path
    if args.params:
        for param in args.params:
            if '=' in param:
                key, value = param.split('=', 1)
                path = path.replace('{' + key + '}', value)
    
    # 解析查询参数
    query_params = {}
    if args.query:
        for q in args.query:
            if '=' in q:
                key, value = q.split('=', 1)
                query_params[key] = value
    
    # 解析请求体
    body = None
    if args.body:
        if args.body.startswith('@'):
            # 从文件读取
            with open(args.body[1:], 'r', encoding='utf-8') as f:
                body = f.read()
        else:
            # 尝试解析 JSON
            try:
                body = json.loads(args.body)
            except json.JSONDecodeError:
                body = args.body
    
    # 发送请求
    response_body, status_code, headers, from_cache = make_request(
        args.api,
        path,
        method=args.method,
        params=query_params if query_params else None,
        body=body,
        headers=dict(args.header) if args.header else None,
        use_cache=args.cache_ttl is not None,
        cache_ttl=args.cache_ttl or 300,
        verbose=args.verbose
    )
    
    # 输出结果
    if args.verbose:
        print(f"📊 状态码：{status_code}")
        print(f"📦 响应头：")
        for k, v in headers.items():
            print(f"   {k}: {v}")
        print()
    
    if args.field:
        # 输出特定字段
        try:
            data = json.loads(response_body)
            values = []
            for field in args.field:
                parts = field.split('.')
                value = data
                for part in parts:
                    if isinstance(value, dict):
                        value = value.get(part)
                    elif isinstance(value, list):
                        value = [item.get(part) for item in value]
                    else:
                        value = None
                        break
                if value is not None:
                    values.append(str(value))
            print('\n'.join(values))
        except json.JSONDecodeError:
            print(response_body)
    elif args.format == "table":
        # 表格输出
        try:
            data = json.loads(response_body)
            if isinstance(data, list) and len(data) > 0:
                # 简单的表格输出
                if isinstance(data[0], dict):
                    headers_list = list(data[0].keys())[:5]
                    print(" | ".join(headers_list))
                    print("-" * 60)
                    for item in data[:20]:
                        print(" | ".join(str(item.get(h, ''))[:20] for h in headers_list))
        except json.JSONDecodeError:
            print(response_body)
    elif args.raw:
        # 原始输出
        print(response_body)
    else:
        # 美化 JSON 输出
        try:
            data = json.loads(response_body)
            print(json.dumps(data, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(response_body)
    
    # 非 2xx 状态码退出
    if not (200 <= status_code < 300):
        sys.exit(status_code)

def clear_cache(args):
    """清除缓存"""
    import glob
    
    if args.api:
        # 清除特定 API 的缓存（简化：清除所有）
        cache_files = glob.glob(os.path.join(CACHE_DIR, "*.json"))
        for f in cache_files:
            os.remove(f)
        print(f"✅ 缓存已清除")
    else:
        # 清除所有缓存
        cache_files = glob.glob(os.path.join(CACHE_DIR, "*.json"))
        for f in cache_files:
            os.remove(f)
        print(f"✅ 所有缓存已清除 ({len(cache_files)} 个文件)")

def show_stats(args):
    """显示统计信息"""
    if not os.path.exists(HISTORY_FILE):
        print("📭 没有调用历史")
        return
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    total = len(history)
    by_api = {}
    by_status = {}
    
    for record in history:
        api = record["api"]
        status = record["status_code"]
        by_api[api] = by_api.get(api, 0) + 1
        status_class = f"{status // 100}xx"
        by_status[status_class] = by_status.get(status_class, 0) + 1
    
    print("\n" + "="*60)
    print("📊 API 调用统计")
    print("="*60 + "\n")
    
    print(f"总调用次数：{total}")
    print()
    print("按 API:")
    for api, count in sorted(by_api.items(), key=lambda x: -x[1]):
        print(f"  {api}: {count}")
    
    print()
    print("按状态码:")
    for status, count in sorted(by_status.items()):
        print(f"  {status}: {count}")
    
    # 成功率
    success = by_status.get("2xx", 0)
    if total > 0:
        rate = (success / total) * 100
        print(f"\n成功率：{rate:.1f}%")

def show_history(args):
    """显示调用历史"""
    if not os.path.exists(HISTORY_FILE):
        print("📭 没有调用历史")
        return
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        history = json.load(f)
    
    # 按 API 过滤
    if args.api:
        history = [h for h in history if h["api"] == args.api]
    
    # 按天数过滤
    if args.days:
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(days=args.days)
        history = [
            h for h in history 
            if datetime.fromisoformat(h["timestamp"]) > cutoff
        ]
    
    # 限制显示数量
    limit = args.limit or 20
    history = history[-limit:]
    
    if not history:
        print("📭 没有匹配的历史记录")
        return
    
    print(f"\n{'='*60}")
    print(f"📜 调用历史 (最近 {len(history)} 条)")
    print(f"{'='*60}\n")
    
    for record in reversed(history):
        status_icon = {
            2: "✅",
            4: "❌",
            5: "💥"
        }.get(record["status_code"] // 100, "❓")
        
        print(f"{status_icon} [{record['timestamp'][:19]}] {record['api']}")
        print(f"   {record['method']} {record['path']}")
        print(f"   状态：{record['status_code']}")
        print()

def main():
    parser = argparse.ArgumentParser(
        description="API Connector 通用 API 连接器",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_subparsers = config_parser.add_subparsers(dest="config_command")
    
    # config add
    config_add_parser = config_subparsers.add_parser("add", help="添加 API 配置")
    config_add_parser.add_argument("name", help="API 名称")
    config_add_parser.add_argument("--base-url", "-b", required=True, help="API 基础 URL")
    config_add_parser.add_argument("--auth-type", "-a", required=True,
                                   choices=["bearer", "api-key", "basic", "oauth2", "none"],
                                   help="认证类型")
    config_add_parser.add_argument("--token", "-t", help="Bearer Token")
    config_add_parser.add_argument("--api-key", "-k", help="API Key")
    config_add_parser.add_argument("--api-key-header", help="API Key Header 名称")
    config_add_parser.add_argument("--username", "-u", help="Basic Auth 用户名")
    config_add_parser.add_argument("--password", "-p", help="Basic Auth 密码")
    config_add_parser.add_argument("--client-id", help="OAuth2 Client ID")
    config_add_parser.add_argument("--client-secret", help="OAuth2 Client Secret")
    config_add_parser.add_argument("--redirect-uri", help="OAuth2 Redirect URI")
    config_add_parser.add_argument("--header", "-H", action="append", help="自定义 Header")
    config_add_parser.add_argument("--timeout", type=int, help="超时时间（秒）")
    
    # config list
    config_subparsers.add_parser("list", help="列出所有 API 配置")
    
    # config show
    config_show_parser = config_subparsers.add_parser("show", help="显示 API 配置")
    config_show_parser.add_argument("name", help="API 名称")
    
    # config remove
    config_remove_parser = config_subparsers.add_parser("remove", help="删除 API 配置")
    config_remove_parser.add_argument("name", help="API 名称")
    
    # call 命令
    call_parser = subparsers.add_parser("call", help="调用 API")
    call_parser.add_argument("api", help="API 名称")
    call_parser.add_argument("path", help="API 路径")
    call_parser.add_argument("--method", "-X", default="GET",
                             choices=["GET", "POST", "PUT", "PATCH", "DELETE"],
                             help="HTTP 方法")
    call_parser.add_argument("--params", "-P", action="append",
                             help="路径参数 (key=value)")
    call_parser.add_argument("--query", "-q", action="append",
                             help="查询参数 (key=value)")
    call_parser.add_argument("--body", "-d", help="请求体")
    call_parser.add_argument("--header", "-H", action="append",
                             help="自定义 Header")
    call_parser.add_argument("--field", "-f", action="append",
                             help="输出特定字段")
    call_parser.add_argument("--format", choices=["json", "table"], default="json",
                             help="输出格式")
    call_parser.add_argument("--cache-ttl", type=int, help="缓存时间（秒）")
    call_parser.add_argument("--raw", action="store_true", help="原始输出")
    call_parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    # cache 命令
    cache_parser = subparsers.add_parser("cache", help="缓存管理")
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command")
    cache_subparsers.add_parser("clear", help="清除缓存")
    
    # stats 命令
    subparsers.add_parser("stats", help="显示统计信息")
    
    # history 命令
    history_parser = subparsers.add_parser("history", help="显示调用历史")
    history_parser.add_argument("--api", "-a", help="按 API 过滤")
    history_parser.add_argument("--days", "-d", type=int, help="显示最近 N 天")
    history_parser.add_argument("--limit", "-l", type=int, default=20, help="显示数量")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "config":
        if not args.config_command:
            config_parser.print_help()
            return
        
        if args.config_command == "add":
            add_api_config(args)
        elif args.config_command == "list":
            list_configs(args)
        elif args.config_command == "show":
            show_config(args)
        elif args.config_command == "remove":
            remove_config(args)
    
    elif args.command == "call":
        call_api(args)
    
    elif args.command == "cache":
        if args.cache_command == "clear":
            clear_cache(args)
    
    elif args.command == "stats":
        show_stats(args)
    
    elif args.command == "history":
        show_history(args)

if __name__ == "__main__":
    main()
