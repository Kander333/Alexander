import re
from dataclasses import dataclass
from typing import List

@dataclass
class Record:
    day: str
    date: int
    month: str
    day_total: int
    hour: str
    mentions: int
    reposts: int
    social: int

weekday_pattern = re.compile(r'(Пн|Вт|Ср|Чт|Пт|Сб|Вс),\s*(\d{1,2})\s*(\w{3})\s*([+\-]?\d+)?')
hour_pattern = re.compile(r'(\d{2}:\d{2})(?:\s(\d+))?\s([+\-]?\d+)\s\|\s([+\-]?\d+)\s([+\-]?\d+)')

def parse_table(text: str) -> List[Record]:
    pos = 0
    current_day = None
    records: List[Record] = []
    while pos < len(text):
        wd_match = weekday_pattern.match(text, pos)
        if wd_match:
            day_name, date, month, day_total = wd_match.groups()
            current_day = (day_name, int(date), month, int(day_total or '0'))
            pos = wd_match.end()
            # skip whitespace
            while pos < len(text) and text[pos].isspace():
                pos += 1
            continue
        hr_match = hour_pattern.match(text, pos)
        if hr_match and current_day:
            hour, count, mchg, rchg, schg = hr_match.groups()
            record = Record(day=current_day[0], date=current_day[1], month=current_day[2],
                             day_total=current_day[3], hour=hour, mentions=int(mchg),
                             reposts=int(rchg), social=int(schg))
            records.append(record)
            pos = hr_match.end()
            while pos < len(text) and text[pos].isspace():
                pos += 1
            continue
        pos += 1
    return records

def main():
    import sys, json
    text = sys.stdin.read()
    records = parse_table(text)
    for rec in records:
        print(rec)

if __name__ == '__main__':
    main()
