#!/usr/bin/env python3
import importlib.util, os, sys, tempfile
from pathlib import Path
p = Path(__file__).parents[1] / 'telegram_notify.py'
spec = importlib.util.spec_from_file_location('telegram_notify', p)
tn = importlib.util.module_from_spec(spec); sys.modules['telegram_notify'] = tn; spec.loader.exec_module(tn)

# load_env: reads KEY=VALUE, skips comments/blank, does not override existing env
with tempfile.TemporaryDirectory() as d:
    envfile = Path(d) / '.env'
    envfile.write_text('# comment\nTELEGRAM_BOT_TOKEN=abc123\n\nTELEGRAM_CHAT_ID=999\n', encoding='utf-8')
    for k in ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'):
        os.environ.pop(k, None)
    tn.load_env(str(envfile))
    assert os.environ['TELEGRAM_BOT_TOKEN'] == 'abc123'
    assert os.environ['TELEGRAM_CHAT_ID'] == '999'
    os.environ['TELEGRAM_CHAT_ID'] = 'preset'
    tn.load_env(str(envfile))
    assert os.environ['TELEGRAM_CHAT_ID'] == 'preset'  # existing env wins
    for k in ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'):
        os.environ.pop(k, None)

# plain_text: strips markdown decoration
md = '# Title\n\n**bold alert**\n- bullet one\n## Sub'
out = tn.plain_text(md)
assert 'Title' in out and '#' not in out
assert 'bold alert' in out and '**' not in out
assert '• bullet one' in out

# truncate: respects Telegram's 4096-char limit
long_text = 'x' * 5000
short = tn.truncate(long_text)
assert len(short) <= tn.MAX_LEN
assert short.endswith('(truncated)')
assert tn.truncate('short') == 'short'

# send_telegram_message: raises a clear error when no credentials are configured
for k in ('TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID'):
    os.environ.pop(k, None)
try:
    tn.send_telegram_message('hi')
    assert False, 'expected RuntimeError'
except RuntimeError as e:
    assert 'TELEGRAM_BOT_TOKEN' in str(e)

# notify_safe: never raises, returns False on missing credentials
assert tn.notify_safe('hi') is False

print('OK telegram notify tests passed')
