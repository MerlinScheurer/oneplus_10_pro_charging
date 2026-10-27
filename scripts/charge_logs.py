import re
from pathlib import Path

import pandas as pd


def read_text(path):
    raw = Path(path).read_bytes()
    if raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return raw.decode('utf-16')
    return raw.decode('utf-8', errors='replace')


def load_battery(path):
    rows, cur = [], None
    for line in read_text(path).splitlines():
        m = re.match(r'--- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) ---', line)
        if m:
            cur = {'time': pd.Timestamp(m.group(1))}
            rows.append(cur)
            continue
        if cur is None:
            continue
        for key, pat in [
            ('current_ma', r'Battery current\s*:\s*(-?\d+)'),
            ('level', r'^\s*level:\s*(\d+)'),
            ('voltage_mv', r'^\s*voltage:\s*(\d+)'),
            ('temp_dc', r'^\s*temperature:\s*(\d+)'),
            ('charger_mv', r'Charger voltage\s*:\s*(\d+)'),
            ('status', r'^\s*status:\s*(\d+)'),
        ]:
            mm = re.search(pat, line)
            if mm:
                cur[key] = int(mm.group(1))
    df = pd.DataFrame([r for r in rows if 'current_ma' in r])
    df['pack_mv_est'] = 2 * df['voltage_mv']
    df['power_w'] = -df['current_ma'] * df['pack_mv_est'] / 1e6
    return df


def load_bcc(path):
    recs = []
    for line in read_text(path).splitlines():
        if 'control current' not in line:
            continue
        ts = line[:18]
        cell = int(re.search(r'cell\[(\d)\]', line).group(1))
        vals = dict(re.findall(r'(\w+)\[(-?\d+)\]', line))
        recs.append({
            'time': pd.Timestamp('2026-' + ts.replace(' ', ' ')) if False else ts,
            'cell': cell,
            'voltage_mv': int(vals['voltage']),
            'temp_dc': int(vals['temperature']),
            'soc_raw': int(vals['soc']),
            'current_ma': int(vals['current']),
            'max_current_ma': int(vals['max_current']),
            'charge_current_ma': int(vals['charge_current']),
            'anode_potential': int(vals['anode_potential']),
            'error_code': int(vals['error_code']),
        })
    df = pd.DataFrame(recs)
    df['time'] = pd.to_datetime('2026-10-26 ' + df['time'].str[6:], format='%Y-%m-%d %H:%M:%S.%f')
    return df


def load_sent_current(path):
    out = []
    for line in read_text(path).splitlines():
        m = re.search(r'^(\S+ \S+).*send current\[(-?\d+)\] to voocphy( passed)?', line)
        if m and not m.group(3):
            out.append({'time': m.group(1), 'requested_ma': int(m.group(2)) * 100})
    df = pd.DataFrame(out)
    if len(df):
        df['time'] = pd.to_datetime('2026-10-26 ' + df['time'].str[6:], format='%Y-%m-%d %H:%M:%S.%f')
    return df
