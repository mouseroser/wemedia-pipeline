#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/Users/lucifinil_chen/.openclaw/workspace')
BASE_DIR = WORKSPACE / 'intel' / 'collaboration' / 'media' / 'wemedia'


def parse_list(value: str):
    if not value:
        return []
    parts = [x.strip() for x in value.replace('\n', ',').split(',')]
    return [x for x in parts if x]


def ensure_abs_list(paths):
    return [str(Path(p).expanduser().resolve()) for p in paths]


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build_douyin(args):
    content_id = args.content_id or f"{datetime.now().strftime('%Y-%m-%d')}-{args.title[:12]}".replace(' ', '-')
    out = BASE_DIR / 'douyin' / f'{content_id}.md'
    text = f'''平台：douyin
内容ID：{content_id}
标题：{args.title}
描述：
{args.body}
视频路径：{Path(args.video_path).expanduser().resolve()}
竖封面路径：{Path(args.vertical_cover_path).expanduser().resolve()}
横封面路径：{Path(args.horizontal_cover_path).expanduser().resolve()}
音乐：{args.music or '热门'}
可见性：{args.visibility or 'private'}
备注：{args.notes or ''}
'''
    write_text(out, text)
    return out


def build_xhs(args):
    content_id = args.content_id or f"{datetime.now().strftime('%Y-%m-%d')}-{args.title[:12]}".replace(' ', '-')
    out = BASE_DIR / 'xiaohongshu' / f'{content_id}.md'
    images = ensure_abs_list(parse_list(args.image_paths))
    tags = parse_list(args.tags)
    lines = [
        '平台：xiaohongshu',
        f'内容ID：{content_id}',
        f'标题：{args.title}',
        '正文：',
        args.body,
        '图片路径：',
    ]
    lines.extend([f'- {p}' for p in images])
    lines.extend([
        f'标签：{", ".join(tags)}',
        f'可见性：{args.visibility or "public"}',
        f'备注：{args.notes or ""}',
        ''
    ])
    write_text(out, '\n'.join(lines))
    return out


def main():
    ap = argparse.ArgumentParser(description='Build executable publish pack for wemedia')
    ap.add_argument('--platform', required=True, choices=['douyin', 'xiaohongshu'])
    ap.add_argument('--content-id')
    ap.add_argument('--title', required=True)
    ap.add_argument('--body', required=True)
    ap.add_argument('--notes')
    ap.add_argument('--visibility')
    ap.add_argument('--music')
    ap.add_argument('--tags', help='comma separated')
    ap.add_argument('--video-path')
    ap.add_argument('--vertical-cover-path')
    ap.add_argument('--horizontal-cover-path')
    ap.add_argument('--image-paths', help='comma separated absolute/relative paths')
    args = ap.parse_args()

    if args.platform == 'douyin':
        required = ['video_path', 'vertical_cover_path', 'horizontal_cover_path']
        for r in required:
            if not getattr(args, r):
                raise SystemExit(f'missing --{r.replace("_", "-")}')
        out = build_douyin(args)
    else:
        if not args.image_paths:
            raise SystemExit('missing --image-paths')
        out = build_xhs(args)

    print(json.dumps({'ok': True, 'platform': args.platform, 'path': str(out)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
