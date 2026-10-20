"""Build local profile SVGs from GitHub's public APIs. Python standard library only."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
USER = 'AkashDataLab'
BG, PANEL, EDGE = '#0a101f', '#0f1b2e', '#263650'
WHITE, MUTED, TEAL, BLUE = '#e3e8f4', '#8e9eb9', '#22d3ee', '#aa9bef'


def text(x, y, value, size=14, color=WHITE, weight=400):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}">{html.escape(str(value))}</text>'


def rect(x, y, w, h, color=PANEL, r=8):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{color}"/>'


def svg(title, height, body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img"><title>{html.escape(title)}</title>{rect(0,0,960,height,BG,16)}{body}</svg>\n'


def streaks(days):
    longest = run = 0
    for day in days:
        run = run + 1 if day['contributionCount'] else 0
        longest = max(longest, run)
    eligible = days[:-1] if days and not days[-1]['contributionCount'] else days
    current = 0
    for day in reversed(eligible):
        if not day['contributionCount']:
            break
        current += 1
    return current, longest, sum(d['contributionCount'] > 0 for d in days)


def stat_card(title, items, note):
    body = text(28, 34, title, 15, TEAL, 700)
    width = 904 / len(items)
    for i, (label, value) in enumerate(items):
        x = 28 + i * width
        body += rect(x, 54, width - 12, 94)
        body += text(x+16, 95, value, 30, WHITE, 700)
        body += text(x+16, 127, label, 13, MUTED)
    body += text(28, 177, note, 12, MUTED)
    return svg(title, 198, body)


def bars(title, values, labels, note, color):
    body = text(28, 34, title, 15, TEAL, 700)
    peak = max(max(values, default=0), 1)
    for level in range(4):
        y = 185 - level * 40
        body += f'<path d="M60 {y}H924" stroke="{EDGE}" stroke-width="1"/>'
        body += text(28, y+4, round(peak*level/3, 1), 10, MUTED)
    step = 864 / max(len(values), 1)
    for i, value in enumerate(values):
        h = value / peak * 120
        x = 60+i*step+4
        if h:
            body += f'<g><title>{html.escape(labels[i])}: {value}</title>{rect(x,185-h,step-8,h,color,3)}</g>'
        else:
            body += rect(x, 183, step-8, 2, EDGE, 1)
    for i in sorted({0, len(labels)//2, len(labels)-1}):
        body += text(60+i*step, 207, labels[i][5:], 11, MUTED)
    body += text(28, 241, note, 12, MUTED)
    return svg(title, 264, body)


def calendar(weeks):
    body = text(28, 34, 'A YEAR OF CONTRIBUTIONS', 15, TEAL, 700)
    colors = ['#1c2c40', '#155e63', '#148b85', '#2bbca9', TEAL]
    peak = max((d['contributionCount'] for w in weeks for d in w['contributionDays']), default=0)
    prev_month = ''
    for wi, week in enumerate(weeks):
        x = 55 + wi * 16
        ds = week['contributionDays']
        if ds:
            month = dt.date.fromisoformat(ds[0]['date']).strftime('%b')
            if month != prev_month and wi < len(weeks)-2:
                body += text(x, 61, month, 10, MUTED)
                prev_month = month
        for d in ds:
            count = d['contributionCount']
            level = 0 if count == 0 else min(4, 1 + int((count/max(peak,1))*3))
            body += f'<g><title>{d["date"]}: {count} contributions</title>{rect(x,74+d["weekday"]*16,12,12,colors[level],3)}</g>'
    body += text(18, 102, 'M', 10, MUTED)+text(18,134,'W',10,MUTED)+text(18,166,'F',10,MUTED)
    body += text(28, 215, 'GitHub contribution calendar · rolling year · UTC', 12, MUTED)
    return svg('Contribution calendar', 238, body)


def request(url, payload=None):
    token = os.environ.get('GH_TOKEN')
    headers = {'User-Agent':'AkashDataLab-profile', 'Accept':'application/vnd.github+json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = None if payload is None else json.dumps(payload).encode()
    if data:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)


def repositories():
    repos, page = [], 1
    while True:
        batch = request(f'https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def replace_section(readme, key, contents):
    pattern = rf'<!-- {key}:START -->.*?<!-- {key}:END -->'
    updated, n = re.subn(pattern, lambda _: f'<!-- {key}:START -->\n{contents}\n<!-- {key}:END -->', readme, flags=re.S)
    if n != 1:
        raise ValueError(f'Expected exactly one {key} section; no files written.')
    return updated


def language_card(totals):
    if not totals:
        body = text(28,34,'LANGUAGES / CODE MIX',15,TEAL,700)
        body += text(28,88,'Your language mix starts with your first code project.',20,WHITE,700)
        body += text(28,124,'Based on code bytes in public, original repositories. Not a skill rating.',13,MUTED)
        return svg('Language mix',156,body)
    total = sum(totals.values())
    top = sorted(totals.items(),key=lambda x:x[1],reverse=True)[:5]
    remaining = total-sum(v for _,v in top)
    if remaining: top.append(('Other',remaining))
    colors=[TEAL,BLUE,'#f5b95f','#fb8ca6','#84cc96','#8e9eb9']
    body=text(28,34,'LANGUAGES / CODE MIX',15,TEAL,700)
    x=28
    for i,(name,count) in enumerate(top):
        width=904*count/total
        body+=rect(round(x,2),55,round(width,2),12,colors[i],0)
        x+=width
        col=i%3; row=i//3
        body+=text(28+col*300,104+row*32,f'{name}  {100*count/total:.1f}%',14,colors[i],700)
    body+=text(28,178,'Code bytes in public, original repositories · Not a skill rating',12,MUTED)
    return svg('Language mix',200,body)


def light_variant(content):
    palette={BG:'#f4f6fc',PANEL:'#ffffff',EDGE:'#d8deec',WHITE:'#202d48',MUTED:'#63728c',TEAL:'#007e97',BLUE:'#7254bb',
      '#1c2c40':'#e7edf7','#155e63':'#c0e7ed','#148b85':'#7dcbd6','#2bbca9':'#35a8bc'}
    for old,new in palette.items(): content=content.replace(old,new)
    return content


def build(repos, user, today, languages=None):
    collection = user['year']
    weeks = collection['contributionCalendar']['weeks']
    days = [d for w in weeks for d in w['contributionDays'] if d['date'] <= today.isoformat()]
    current, longest, active = streaks(days)
    start = today-dt.timedelta(days=29)
    dates = [(start+dt.timedelta(days=i)).isoformat() for i in range(30)]
    activity = {d['date']:d['contributionCount'] for d in days}
    commits = dict.fromkeys(dates, 0)
    for repo in user['month']['commitContributionsByRepository']:
        connection = repo['contributions']
        if connection['pageInfo']['hasNextPage']:
            raise ValueError('Commit data needs pagination; preserving previous cards.')
        for d in connection['nodes']:
            date = d['occurredAt'][:10]
            if date in commits:
                commits[date] += d['commitCount']
    cards = {
      'overview.svg':stat_card('GITHUB / OVERVIEW', [
        ('Public repositories',len(repos)),('Stars received',sum(r['stargazers_count'] for r in repos)),
        ('Contributions · 1 year',collection['contributionCalendar']['totalContributions']),
        ('Qualifying commits · 1 year',collection['totalCommitContributions'])],
        f'Public owned repos, including forks · {user["followers"]["totalCount"]} followers · Updated {today.isoformat()} UTC'),
      'streak.svg':stat_card('CONSISTENCY / CONTRIBUTION STREAK', [
        ('Current streak · days',current),('Longest streak · last year',longest),('Active days · last year',active)],
        'UTC days · Today may still be in progress · Streaks limited to the calendar shown'),
      'activity.svg':bars('ACTIVITY / LAST 30 DAYS',[activity.get(d,0) for d in dates],dates,
        'Daily GitHub contributions · commits, pull requests, issues, and other qualifying activity', TEAL),
      'calendar.svg':calendar(weeks),
      'commits.svg':bars('COMMIT CONTRIBUTIONS / LAST 30 DAYS',list(commits.values()),dates,
        'GitHub-qualified commit contributions · up to 100 repositories · UTC',BLUE)
    }
    cards['languages.svg'] = language_card(languages or {})
    eligible = {r['full_name']:r for r in repos if not r['fork'] and not r['archived'] and r['name'].lower()!=USER.lower()}
    chosen = [eligible[p['nameWithOwner']] for p in user['pinnedItems']['nodes'] if p and p.get('nameWithOwner') in eligible][:3]
    if not chosen:
        chosen = sorted(eligible.values(), key=lambda r:r['pushed_at'] or '', reverse=True)[:3]
    projects = '*My published projects will appear here as this portfolio grows.*'
    if chosen:
        projects = '\n\n'.join(
            f'<b><a href="{html.escape(r["html_url"],quote=True)}">{html.escape(r["name"])}</a></b><br />\n'
            + html.escape((r.get('description') or 'Explore the repository, code, and project notes.')[:240]).replace('\n',' ')
            + f'<br /><sub>{html.escape(r.get("language") or "Project")} · {r["stargazers_count"]} stars</sub>' for r in chosen)
    readme = (ROOT/'README.md').read_text()
    readme = replace_section(readme,'PROJECTS',projects)
    readme = replace_section(readme,'UPDATED',f'<sub>Activity last refreshed {today.isoformat()} UTC. Updated daily through GitHub Actions.</sub>')
    # All API calls and validation finish before changing output files.
    for name, content in cards.items():
        (ROOT/'assets'/name.replace('.svg','-dark.svg')).write_text(content)
        (ROOT/'assets'/name.replace('.svg','-light.svg')).write_text(light_variant(content))
    (ROOT/'README.md').write_text(readme)


def main():
    if not os.environ.get('GH_TOKEN'):
        raise SystemExit('Run this through the included GitHub Actions workflow; GH_TOKEN is required.')
    today = dt.datetime.now(dt.timezone.utc).date()
    query = '''query($login:String!,$from:DateTime!,$to:DateTime!){
      user(login:$login){
        followers{totalCount}
        pinnedItems(first:6,types:[REPOSITORY]){nodes{... on Repository{nameWithOwner}}}
        year:contributionsCollection(to:$to){
          totalCommitContributions
          contributionCalendar{totalContributions weeks{contributionDays{date weekday contributionCount}}}
        }
        month:contributionsCollection(from:$from,to:$to){
          commitContributionsByRepository(maxRepositories:100){
            contributions(first:100){pageInfo{hasNextPage} nodes{occurredAt commitCount}}
          }
        }
      }
    }'''
    result = request('https://api.github.com/graphql',{'query':query,'variables':{
      'login':USER,'from':(today-dt.timedelta(days=29)).isoformat()+'T00:00:00Z',
      'to':dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}})
    if result.get('errors') or not result.get('data',{}).get('user'):
        raise RuntimeError('GitHub did not return complete profile data; previous cards are retained. '+str(result.get('errors','')))
    repos = repositories()
    languages = {}
    for repo in repos:
        if repo['fork'] or repo['name'].lower()==USER.lower():
            continue
        amounts = request(repo['languages_url'])
        for language,count in amounts.items():
            languages[language] = languages.get(language,0)+count
    build(repos, result['data']['user'],today,languages)
    print('Updated profile cards and featured projects.')


if __name__ == '__main__':
    main()
