# FindNet

**有伴才有劲 · Better together**

FindNet helps people in the Bay Area Chinese community find each other to get
outside and move: group walks, tai chi and square dancing, and meetups for dog
owners. People post an activity at a place and time, others join, and on the day
they tap *I'm here* so friends know they've arrived.

> **Status: prototype.** The app runs inside a claude.ai Artifact, which provides
> sign-in and the shared database. Opening `app/index.html` anywhere else shows
> the screens but cannot sign in or save. See
> [docs/architecture.md](docs/architecture.md) for what to replace to run it
> standalone.

## Features

- **Two sides, one app**: 长辈走走 (group walks) and 狗狗玩伴 (dog meetups), switchable at any time
- **Activities**: create, join, *I'm here* check-in, quick picks for common activities, times and durations
- **Dog profiles**: breed, size, temperament, vaccination; size rules on dog meetups with a warning when your dog may not fit
- **Progress**: active days per week and month, calendar, minutes, estimated calories, monthly consistency draw
- **Friends**: follow, mutual follow = friends, block, nickname search
- **Privacy**: visibility set to Everyone / Friends only / Only me; *Friends only* and chat are end-to-end encrypted
- **Three languages**: 简体中文, 繁體中文 (Taiwan/Hong Kong usage) and English, with activity types and breeds translated for each reader
- **Accessibility**: large type, big tap targets, high contrast, light and dark themes

## Repository layout

```
app/index.html                   the whole app (HTML, CSS, JS, translations)
app/artifact-capabilities.json   database access rules used when publishing
tests/run_tests.py               logic tests run against app/index.html
docs/architecture.md             data model, privacy design, how to go standalone
marketing/                       20 s Chinese ad, poster, music bed
marketing/render/                scripts that regenerate the ad
```

## Tests

```bash
python3 tests/run_tests.py      # needs Node 20+
```

Covers encryption between friends, weekly and monthly day counting, dog profile
validation and size matching, and the three translations.

## Roadmap

1. Pilot with Chinese-speaking seniors and dog owners in the Bay Area
2. Standalone backend and phone-number sign-in
3. WeChat Mini Program with WeChat sign-in

## License

Licensed under the [Apache License 2.0](LICENSE). Copyright 2026 Weijie Zhang.
The FindNet name and logo are not covered by the license; see [NOTICE](NOTICE).

---

## 中文简介

FindNet 帮助湾区华人社区的朋友们找到彼此，一起出门动起来：长辈一起散步、打太极、跳广场舞，养狗的朋友约狗狗一起玩。有人发起一个时间地点，大家报名，当天到了点一下「我到了」，朋友就知道你到了。

**当前状态：原型。** 应用运行在 claude.ai Artifact 里，由它提供登录和共享数据库。在其他地方直接打开 `app/index.html` 只能看到界面，不能登录或保存。改成独立应用需要替换的部分见 [docs/architecture.md](docs/architecture.md)。

主要功能：长辈走走和狗狗玩伴两个入口；发起、报名、「我到了」签到；狗狗资料与大小匹配；每周、每月运动天数和日历；关注、好友、屏蔽；「仅好友可见」和私聊端到端加密；简体、繁體、English 三种语言。

本项目采用 Apache 2.0 许可证。FindNet 名称和标志不在许可范围内，详见 NOTICE。
