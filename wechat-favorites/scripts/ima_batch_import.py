# -*- coding: utf-8 -*-
"""批量导入微信收藏文章URL到IMA知识库

配置方式（任选一种）：
1. 命令行参数
2. 环境变量
3. 配置文件 ~/.config/ima/config.json

用法：
    python ima_batch_import.py [--csv PATH] [--kb-id ID] [--state PATH] [--log PATH]
"""
import csv, json, urllib.request, time, sys, os, argparse

# ── 配置加载 ──────────────────────────────────────────────

def load_config():
    """从 环境变量 / 配置文件 加载 IMA 凭证"""
    config = {}

    # 1. 配置文件
    config_path = os.path.expanduser('~/.config/ima/config.json')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        config['client_id'] = cfg.get('client_id', '')
        config['api_key'] = cfg.get('api_key', '')
        config['kb_id'] = cfg.get('kb_id', '')

    # 2. 环境变量覆盖
    config['client_id'] = os.environ.get('IMA_CLIENT_ID', config.get('client_id', ''))
    config['api_key'] = os.environ.get('IMA_API_KEY', config.get('api_key', ''))
    config['kb_id'] = os.environ.get('IMA_KB_ID', config.get('kb_id', ''))

    # 3. 单独文件兼容（旧格式）
    if not config['client_id']:
        cid_path = os.path.expanduser('~/.config/ima/client_id')
        if os.path.exists(cid_path):
            config['client_id'] = open(cid_path).read().strip()
    if not config['api_key']:
        key_path = os.path.expanduser('~/.config/ima/api_key')
        if os.path.exists(key_path):
            config['api_key'] = open(key_path).read().strip()

    return config


def parse_args():
    parser = argparse.ArgumentParser(description='批量导入微信收藏到IMA知识库')
    parser.add_argument('--csv', default='exported_favorites/articles_final.csv',
                        help='CSV 文件路径（默认: exported_favorites/articles_final.csv）')
    parser.add_argument('--kb-id', default='', help='IMA 知识库 ID')
    parser.add_argument('--state', default='ima_import_state.json',
                        help='断点续传状态文件（默认: ima_import_state.json）')
    parser.add_argument('--log', default='ima_import.log',
                        help='日志文件（默认: ima_import.log）')
    parser.add_argument('--batch-size', type=int, default=10,
                        help='每批导入数量（默认: 10）')
    return parser.parse_args()


# ── 核心逻辑 ──────────────────────────────────────────────

def load_state(state_file):
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'imported': 0, 'failed': 0, 'skipped': 0, 'batch': 0, 'errors': [], 'last_url': ''}

def save_state(state, state_file):
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def log_msg(msg, log_file):
    ts = time.strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def import_batch(urls, client_id, api_key, kb_id):
    body = json.dumps({'knowledge_base_id': kb_id, 'urls': urls}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        'https://ima.qq.com/openapi/wiki/v1/import_urls',
        data=body,
        headers={
            'ima-openapi-clientid': client_id,
            'ima-openapi-apikey': api_key,
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())

def main():
    args = parse_args()
    config = load_config()

    kb_id = args.kb_id or config.get('kb_id', '')
    client_id = config.get('client_id', '')
    api_key = config.get('api_key', '')

    if not kb_id:
        print('错误: 未配置 IMA 知识库 ID。使用 --kb-id 参数或设置 IMA_KB_ID 环境变量')
        sys.exit(1)
    if not client_id or not api_key:
        print('错误: 未配置 IMA 凭证。请设置 ~/.config/ima/config.json 或环境变量 IMA_CLIENT_ID / IMA_API_KEY')
        sys.exit(1)

    csv_path = args.csv
    state_file = args.state
    log_file = args.log
    batch_size = args.batch_size

    if not os.path.exists(csv_path):
        print(f'错误: CSV 文件不存在: {csv_path}')
        sys.exit(1)

    state = load_state(state_file)
    log_msg(f'=== Starting batch import (resume from batch {state["batch"]}) ===', log_file)
    log_msg(f'Previous: imported={state["imported"]}, failed={state["failed"]}, skipped={state["skipped"]}', log_file)

    # Collect all URLs
    all_urls = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url', '').strip()
            if url.startswith('http'):
                all_urls.append(url)

    total = len(all_urls)
    log_msg(f'Total URLs to import: {total}', log_file)
    log_msg(f'Total batches: {total // batch_size + (1 if total % batch_size else 0)}', log_file)

    # Skip already processed
    start_idx = state['batch'] * batch_size
    if start_idx >= total:
        log_msg('All batches already processed!', log_file)
        return

    batch_urls = []
    batch_count = 0

    for i in range(start_idx, total):
        batch_urls.append(all_urls[i])

        if len(batch_urls) == batch_size or i == total - 1:
            batch_count += 1
            try:
                result = import_batch(batch_urls, client_id, api_key, kb_id)
                if result.get('code') == 0:
                    results = result.get('data', {}).get('results', {})
                    success = sum(1 for r in results.values() if r.get('ret_code') == 0)
                    fail = len(results) - success
                    state['imported'] += success
                    state['failed'] += fail
                    # Check for rate limit in API response
                    api_msg = result.get('msg', '')
                    if '频率' in api_msg or 'limit' in api_msg.lower():
                        log_msg('Rate limited by API! Sleeping 60s...', log_file)
                        time.sleep(60)

                    if fail > 0:
                        for url, info in results.items():
                            if info.get('ret_code') != 0:
                                err_msg = info.get('errmsg', 'unknown')
                                state['errors'].append({'url': url[:100], 'error': err_msg})
                                if len(state['errors']) > 200:
                                    state['errors'] = state['errors'][-100:]
                    log_msg(f'Batch {state["batch"] + batch_count}: +{success} ok, {fail} fail | total_ok={state["imported"]}', log_file)
                else:
                    state['failed'] += len(batch_urls)
                    msg = result.get('msg', 'unknown')
                    log_msg(f'Batch {state["batch"] + batch_count}: API error - {msg}', log_file)
                    state['errors'].append({'batch': state["batch"] + batch_count, 'error': msg})

            except Exception as e:
                state['failed'] += len(batch_urls)
                err_str = str(e)
                log_msg(f'Batch {state["batch"] + batch_count}: Exception - {err_str}', log_file)
                state['errors'].append({'batch': state["batch"] + batch_count, 'error': err_str})
                # Back off: longer delay on rate limit / forbidden
                if '403' in err_str or 'Forbidden' in err_str:
                    log_msg('Rate limited! Sleeping 60s...', log_file)
                    time.sleep(60)
                else:
                    time.sleep(5)

            state['batch'] = state.get('batch', 0) + 1
            state['last_url'] = batch_urls[-1][:80]

            # Save state every 10 batches
            if batch_count % 10 == 0:
                save_state(state, state_file)

            batch_urls = []

            # Rate limiting - conservative pace to avoid 403 (3s/batch ~ 3 batches/min)
            time.sleep(3.0)

    save_state(state, state_file)
    log_msg(f'=== Import complete ===', log_file)
    log_msg(f'Imported: {state["imported"]}', log_file)
    log_msg(f'Failed: {state["failed"]}', log_file)
    log_msg(f'Total processed: {state["imported"] + state["failed"]}', log_file)
    if state['errors']:
        log_msg(f'First 5 errors: {json.dumps(state["errors"][:5], ensure_ascii=False)}', log_file)

if __name__ == '__main__':
    main()