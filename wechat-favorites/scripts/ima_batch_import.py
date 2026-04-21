# -*- coding: utf-8 -*-
"""批量导入微信收藏文章URL到IMA知识库"""
import csv, json, urllib.request, time, sys, os

KB_ID = 'E8t176twy7MGPS2WYZ6XAwA8VxRs4zi8t7og2-ZxLX4='
IMA_CLIENT_ID = open(os.path.expanduser('~/.config/ima/client_id')).read().strip()
IMA_API_KEY = open(os.path.expanduser('~/.config/ima/api_key')).read().strip()
CSV_PATH = r'C:\Users\George Sun\.qclaw\workspace\archive\wechat-decrypt\exported_favorites\articles_final.csv'
STATE_FILE = r'C:\Users\George Sun\.qclaw\workspace\archive\wechat-decrypt\ima_import_state.json'
LOG_FILE = r'C:\Users\George Sun\.qclaw\workspace\archive\wechat-decrypt\ima_import.log'
BATCH_SIZE = 10

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {'imported': 0, 'failed': 0, 'skipped': 0, 'batch': 0, 'errors': [], 'last_url': ''}

def save_state(state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def log(msg):
    ts = time.strftime('%H:%M:%S')
    line = f'[{ts}] {msg}'
    print(line, flush=True)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def import_batch(urls):
    body = json.dumps({'knowledge_base_id': KB_ID, 'urls': urls}, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        'https://ima.qq.com/openapi/wiki/v1/import_urls',
        data=body,
        headers={
            'ima-openapi-clientid': IMA_CLIENT_ID,
            'ima-openapi-apikey': IMA_API_KEY,
            'Content-Type': 'application/json; charset=utf-8'
        },
        method='POST'
    )
    resp = urllib.request.urlopen(req, timeout=120)
    return json.loads(resp.read())

def main():
    state = load_state()
    log(f'=== Starting batch import (resume from batch {state["batch"]}) ===')
    log(f'Previous: imported={state["imported"]}, failed={state["failed"]}, skipped={state["skipped"]}')

    # Collect all URLs
    all_urls = []
    with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            url = row.get('url', '').strip()
            title = row.get('title', '').strip()[:50]
            if url.startswith('http'):
                all_urls.append(url)

    total = len(all_urls)
    log(f'Total URLs to import: {total}')
    log(f'Total batches: {total // BATCH_SIZE + (1 if total % BATCH_SIZE else 0)}')

    # Skip already processed
    start_idx = state['batch'] * BATCH_SIZE
    if start_idx >= total:
        log('All batches already processed!')
        return

    batch_urls = []
    batch_count = 0

    for i in range(start_idx, total):
        batch_urls.append(all_urls[i])

        if len(batch_urls) == BATCH_SIZE or i == total - 1:
            batch_count += 1
            try:
                result = import_batch(batch_urls)
                if result.get('code') == 0:
                    results = result.get('data', {}).get('results', {})
                    success = sum(1 for r in results.values() if r.get('ret_code') == 0)
                    fail = len(results) - success
                    state['imported'] += success
                    state['failed'] += fail
                    # Check for rate limit in API response
                    api_msg = result.get('msg', '')
                    if '频率' in api_msg or 'limit' in api_msg.lower():
                        log(f'Rate limited by API! Sleeping 60s...')
                        time.sleep(60)

                    if fail > 0:
                        for url, info in results.items():
                            if info.get('ret_code') != 0:
                                err_msg = info.get('errmsg', 'unknown')
                                state['errors'].append({'url': url[:100], 'error': err_msg})
                                if len(state['errors']) > 200:
                                    state['errors'] = state['errors'][-100:]
                    log(f'Batch {state["batch"] + batch_count}: +{success} ok, {fail} fail | total_ok={state["imported"]}')
                else:
                    state['failed'] += len(batch_urls)
                    msg = result.get('msg', 'unknown')
                    log(f'Batch {state["batch"] + batch_count}: API error - {msg}')
                    state['errors'].append({'batch': state["batch"] + batch_count, 'error': msg})

            except Exception as e:
                state['failed'] += len(batch_urls)
                err_str = str(e)
                log(f'Batch {state["batch"] + batch_count}: Exception - {err_str}')
                state['errors'].append({'batch': state["batch"] + batch_count, 'error': err_str})
                # Back off: longer delay on rate limit / forbidden
                if '403' in err_str or 'Forbidden' in err_str:
                    log('Rate limited! Sleeping 60s...')
                    time.sleep(60)
                else:
                    time.sleep(5)

            state['batch'] = state.get('batch', 0) + 1
            state['last_url'] = batch_urls[-1][:80]

            # Save state every 10 batches
            if batch_count % 10 == 0:
                save_state(state)

            batch_urls = []

            # Rate limiting - conservative pace to avoid 403 (3s/batch ~ 3 batches/min)
            time.sleep(3.0)

    save_state(state)
    log(f'=== Import complete ===')
    log(f'Imported: {state["imported"]}')
    log(f'Failed: {state["failed"]}')
    log(f'Total processed: {state["imported"] + state["failed"]}')
    if state['errors']:
        log(f'First 5 errors: {json.dumps(state["errors"][:5], ensure_ascii=False)}')

if __name__ == '__main__':
    main()
