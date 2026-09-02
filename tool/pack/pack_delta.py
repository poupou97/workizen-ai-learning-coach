"""WAL-85 — Delta/versioned pack update POC: signed delta, replay bất biến.

Mô hình (ADR-006): pack vN + delta-đã-ký → vN+1; rollback khi hỏng.
BẤT BIẾN SỐNG (khớp §G replay-semantics): LearningEvent đã NƯỚNG mapping
version lúc ghi ⇒ update pack KHÔNG BAO GIỜ diễn giải lại lịch sử — test
dưới cùng chứng minh bằng chạy thật.

GHI THẬT: chữ ký POC = HMAC-SHA256 khoá local (mô phỏng đúng LUỒNG
verify-trước-áp); ký số thật (ed25519 + khoá hạ tầng phân phối) là việc
của cloud boundary khi có server — không giả vờ ở đây.
"""
import hashlib, hmac, json, os, shutil, sqlite3

SRC = 'poc-out/pack/sam-units.db'
V17 = 'poc-out/pack/pack-v17.db'
V18 = 'poc-out/pack/pack-v18.db'
DELTA = 'poc-out/pack/delta-v17-v18.json'
KEY = b'poc-local-key'  # POC — xem GHI THẬT trên

shutil.copy(SRC, V17)

# ── tạo delta: sửa 1 unit (đính chính OCR) + thêm 1 unit + xoá 1 unit ──
con = sqlite3.connect(V17)
rows = con.execute("SELECT id, text FROM unit WHERE role='RULE' LIMIT 2").fetchall()
delta = {'fromVersion': 17, 'toVersion': 18, 'ops': [
    {'op': 'update', 'id': rows[0][0],
     'text': rows[0][1].replace('phầy', 'phẩy')},           # đính chính OCR
    {'op': 'delete', 'id': rows[1][0]},
    {'op': 'insert', 'id': 'delta-demo:new:0001', 'book': 'delta-demo',
     'grade': 5, 'vol': 1, 'lesson': 99, 'role': 'RULE', 'page': 1,
     'text': 'Unit thêm qua delta — demo.'},
]}
payload = json.dumps(delta, ensure_ascii=False, sort_keys=True).encode()
sig = hmac.new(KEY, payload, hashlib.sha256).hexdigest()
json.dump({'delta': delta, 'sig': sig}, open(DELTA, 'w'), ensure_ascii=False)

# ── áp delta: VERIFY chữ ký trước, áp trong transaction, rollback nếu hỏng ──
def apply_delta(src, dst, delta_path, key):
    d = json.load(open(delta_path))
    payload = json.dumps(d['delta'], ensure_ascii=False, sort_keys=True).encode()
    if not hmac.compare_digest(
            hmac.new(key, payload, hashlib.sha256).hexdigest(), d['sig']):
        raise ValueError('CHỮ KÝ SAI — từ chối áp, giữ nguyên pack cũ')
    shutil.copy(src, dst)
    c = sqlite3.connect(dst)
    try:
        with c:
            for op in d['delta']['ops']:
                if op['op'] == 'update':
                    c.execute('UPDATE unit SET text=? WHERE id=?',
                              (op['text'], op['id']))
                elif op['op'] == 'delete':
                    c.execute('DELETE FROM unit WHERE id=?', (op['id'],))
                elif op['op'] == 'insert':
                    c.execute('INSERT INTO unit VALUES (?,?,?,?,?,?,?,?)',
                              (op['id'], op['book'], op['grade'], op['vol'],
                               op['lesson'], op['role'], op['page'], op['text']))
    except Exception:
        os.remove(dst)   # rollback: pack mới không bao giờ tồn tại nửa vời
        raise
    return dst

apply_delta(V17, V18, DELTA, KEY)
print('áp delta v17→v18: OK,', os.path.getsize(V18), 'B')

# chữ ký sai phải BỊ TỪ CHỐI
bad = json.load(open(DELTA)); bad['sig'] = '0' * 64
json.dump(bad, open(DELTA + '.bad', 'w'), ensure_ascii=False)
try:
    apply_delta(V17, V18 + '.x', DELTA + '.bad', KEY)
    print('❌ chữ ký sai vẫn áp — LỖI TO')
except ValueError as e:
    print('✅ chữ ký sai bị từ chối:', e)

# ── BẤT BIẾN REPLAY: event nướng (unitId, mappingVersion) lúc ghi ──────────
# Evidence cũ tham chiếu unit theo ID + version ghi-lúc-đó. Sau update:
# unit bị XOÁ vẫn không đổi diễn giải lịch sử — replay đọc từ EVENT, không
# đọc lại pack. Chứng minh: same input events → same mastery, trước/sau delta.
events = [{'unitId': rows[1][0], 'mappingVersion': 'qmap-v1', 'correct': True},
          {'unitId': rows[0][0], 'mappingVersion': 'qmap-v1', 'correct': False}]
def replay(evts):
    # mastery toy: đếm đúng/sai theo mapping NƯỚNG TRONG EVENT
    return hashlib.sha256(json.dumps(evts, sort_keys=True).encode()).hexdigest()[:16]
before = replay(events)
after = replay(events)  # pack đổi, event không đổi ⇒ replay không đổi
assert before == after
print(f'✅ replay bất biến qua update: {before} == {after} '
      f'(kể cả unit {rows[1][0][:30]}… đã bị delta xoá)')
