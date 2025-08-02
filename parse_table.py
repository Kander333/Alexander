import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Channel:
    name: str
    mentions: int
    reposts: int


@dataclass
class Record:
    day: str
    date: int
    month: str
    day_total: int
    hour: str
    mentions: Optional[int]
    reposts: Optional[int]
    mentions_change: int
    reposts_change: int
    social_change: int
    channels: List[Channel]

weekday_pattern = re.compile(
    r'(Пн|Вт|Ср|Чт|Пт|Сб|Вс),\s*(\d{1,2})\s*(\w{3})\s*([+\-]?\d+)?'
)
# hour with optional absolute mention/repost counts before the deltas
hour_pattern = re.compile(
    r'(\d{2}:\d{2})(?:\s(\d+))?(?:\s(\d+))?\s([+\-]?\d+)\s\|\s([+\-]?\d+)\s([+\-]?\d+)'
)

channel_pattern = re.compile(
    r'(.+?)\s(\d+(?:\.\d+)?k?)\s(\d+(?:\.\d+)?k?)\s'
)


def _parse_count(value: str) -> int:
    if value.endswith("k"):
        return int(float(value[:-1]) * 1000)
    return int(value)

def parse_table(text: str) -> List[Record]:
    pos = 0
    current_day = None
    records: List[Record] = []
    pending_channels: List[Channel] = []
    while pos < len(text):
        wd_match = weekday_pattern.match(text, pos)
        if wd_match:
            day_name, date, month, day_total = wd_match.groups()
            current_day = (day_name, int(date), month, int(day_total or '0'))
            pos = wd_match.end()
            pending_channels = []
            # skip whitespace
            while pos < len(text) and text[pos].isspace():
                pos += 1
            continue
        hr_match = hour_pattern.match(text, pos)
        if hr_match and current_day:
            hour, m_abs, r_abs, mchg, rchg, schg = hr_match.groups()
            record = Record(
                day=current_day[0],
                date=current_day[1],
                month=current_day[2],
                day_total=current_day[3],
                hour=hour,
                mentions=int(m_abs) if m_abs else None,
                reposts=int(r_abs) if r_abs else None,
                mentions_change=int(mchg),
                reposts_change=int(rchg),
                social_change=int(schg),
                channels=pending_channels,
            )
            records.append(record)
            pending_channels = []
            pos = hr_match.end()
            while pos < len(text) and text[pos].isspace():
                pos += 1
            continue
        ch_match = channel_pattern.match(text, pos)
        if ch_match:
            name, m_cnt, r_cnt = ch_match.groups()
            pending_channels.append(
                Channel(name.strip(), _parse_count(m_cnt), _parse_count(r_cnt))
            )
            pos = ch_match.end()
            while pos < len(text) and text[pos].isspace():
                pos += 1
            continue
        pos += 1
    return records

def main() -> None:
    import argparse
    import csv
    import sys

    parser = argparse.ArgumentParser(
        description="Parse activity log from text into CSV records"
    )
    parser.add_argument("input", nargs="?", help="input text file; defaults to stdin")
    parser.add_argument("output", nargs="?", help="output CSV file; defaults to stdout")
    args = parser.parse_args()

    if args.input:
        text = open(args.input, encoding="utf-8").read()
    else:
        text = sys.stdin.read()

    records = parse_table(text)

    out_f = open(args.output, "w", newline="", encoding="utf-8") if args.output else sys.stdout
    writer = csv.writer(out_f, lineterminator="\n")
    writer.writerow(
        [
            "day",
            "date",
            "month",
            "day_total",
            "hour",
            "mentions",
            "reposts",
            "mentions_change",
            "reposts_change",
            "social_change",
            "channel",
            "channel_mentions",
            "channel_reposts",
        ]
    )
    for r in records:
        base = [
            r.day,
            r.date,
            r.month,
            r.day_total,
            r.hour,
            "" if r.mentions is None else r.mentions,
            "" if r.reposts is None else r.reposts,
            r.mentions_change,
            r.reposts_change,
            r.social_change,
        ]
        if r.channels:
            for ch in r.channels:
                writer.writerow(base + [ch.name, ch.mentions, ch.reposts])
        else:
            writer.writerow(base + ["", "", ""])

    if args.output:
        out_f.close()

if __name__ == '__main__':
    main()
