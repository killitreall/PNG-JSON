import base64
import json
import os
import re
import struct
from pathlib import Path


def pack_png_sequence(input_dir, output_json, fps):
    def png_size(path):
        with open(path, 'rb') as f:
            f.seek(16)
            return struct.unpack('>II', f.read(8))

    files = sorted(Path(input_dir).glob('*.png'))
    if not files:
        raise Exception(f'В папке {input_dir} нет *.png файлов.')

    w, h = png_size(files[0])
    assets = []
    for i, file in enumerate(files):
        with open(file, 'rb') as img:
            b64 = base64.b64encode(img.read()).decode('ascii')
        assets.append({
            'id': f'imgSeq_{i}',
            'w': w,
            'h': h,
            'u': '',
            'p': f'data:image/png;base64,{b64}',
            'e': 1
        })

    n = len(assets)

    def build_layers():
        return [{
            'ddd': 0,
            'ind': i + 1,
            'ty': 2,
            'nm': f'frame_{i}',
            'refId': f'imgSeq_{i}',
            'sr': 1,
            'ks': {
                'o': {'k': 100},
                'r': {'k': 0},
                'p': {'k': [w / 2, h / 2, 0]},
                'a': {'k': [w / 2, h / 2, 0]},
                's': {'k': [100, 100, 100]}
            },
            'ao': 0,
            'ip': i,
            'op': i + 1,
            'st': 0,
            'bm': 0
        } for i in range(n)]

    lottie = {
        'v': '5.7.4',
        'fr': fps,
        'ip': 0,
        'op': n,
        'w': w,
        'h': h,
        'nm': Path(output_json).name,
        'ddd': 0,
        'assets': assets,
        'layers': build_layers()
    }
    Path(output_json).write_text(json.dumps(lottie, separators=(',', ':')))
    return str(output_json), n


def extract_pngs(json_file, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    saved = []
    for asset in data.get('assets', []):
        img_data = asset.get('p', '')
        if img_data.startswith('data:image/png;base64,'):
            idx = int(re.search(r'\d+$', asset.get('id', '0')).group())
            b64 = img_data.split(',', 1)[1]
            png = base64.b64decode(b64)
            out_path = os.path.join(out_dir, f'frame_{idx:03}.png')
            with open(out_path, 'wb') as out:
                out.write(png)
            saved.append(out_path)
    return saved
