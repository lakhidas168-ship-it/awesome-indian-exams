# Growth plan: reaching aspirants in every kind of town, for free

For the JEVX planner and the owner (2026-09-27). The goal is for every aspirant in India to find the list and
pass it on, in villages, small towns and cities alike, with no ads, no paid promotion and no spam. The list only
grows because it is useful and easy to share.

## What the research says

| Finding | Source | What it means for us |
|---|---|---|
| India had 886 million active internet users in 2024: 488M rural (55%) and 397M urban. Rural users grow twice as fast | [Kantar–IAMAI via BusinessToday](https://www.businesstoday.in/technology/news/story/indias-internet-revolution-key-insights-from-kantar-and-iamai-report-461043-2025-01-16), [MediaNama](https://www.medianama.com/2025/01/223-rural-adoption-ai-india-internet-2024-kantar-iamai-report/) | Rural is the majority, so design for it first |
| 98% of internet users use content in Indic languages; 57% of urban users prefer them. Lack of local-language content is a top reason people stay offline | same | Hindi first, then other languages |
| About 536 million WhatsApp users in India, the largest market | [Backlinko](https://backlinko.com/whatsapp-users) | WhatsApp sharing is channel number one |
| Android is about 92% of phones; about 30% are low-end; 1 GB of data costs roughly ₹9–20 | [IMARC](https://www.imarcgroup.com/india-smartphone-market), [TelecomTalk](https://telecomtalk.info/imc2025-pm-1gb-costs-less-than-tea/1000563/) | Keep pages light and make them work offline |
| Self-study "reading rooms" and village digital libraries are booming across small-town UP, Bihar, Haryana and Rajasthan | [ThePrint](https://theprint.in/ground-reports/reading-room-libraries-small-town-india-exam-generation/2937980/), [ETV Bharat](https://www.etvbharat.com/en/!offbeat/this-digital-library-in-uttar-pradesh-village-becomes-hub-for-competitive-exam-preparation-enn25070602794) | These rooms are where aspirants gather offline: put a poster with a QR code there |
| Physics Wallah and Adda247 grew through free YouTube classes, low prices and vernacular content in tier-2 and tier-3 towns | [Storyboard18](https://www.storyboard18.com/brand-marketing/how-physicswallah-went-from-a-youtube-channel-to-a-rs-3040-crore-listed-edtech-company-99201.htm), [Adda247](https://www.adda247.com/) | Trust comes from free value first; language beats polish |
| Job-alert sites draw about a crore visits a month through Hindi search for notifications, admit cards and results | [FreeJobAlert](https://www.freejobalert.com/) | Search traffic follows official dates, so the official-dates calendar (`T-107`) matters |
| Wordle grew from 90 to over 2 million players in about two months: one puzzle a day, and a result you can share without spoiling the answer. It started in a family WhatsApp group | [Wikipedia](https://en.wikipedia.org/wiki/Wordle) | A daily question with a spoiler-free WhatsApp share |
| Kolibri reaches schools with no internet by copying content device to device from one "seeded" device | [Learning Equality](https://learningequality.org/kolibri/about-kolibri/) | The offline zip can travel phone to phone by Nearby Share or Bluetooth |

## The loops, and what is built

| Loop | How it spreads | Status |
|---|---|---|
| **Daily question share** | Answer → share ✅/❌ and your streak on WhatsApp (never the answer) → friends try it → they share | ✅ `tools/daily` |
| **Share any page** | WhatsApp, Telegram, copy and native share buttons under every page title | ✅ on every page |
| **Rich link previews** | Every shared link shows a title, a description and a preview image in WhatsApp and Telegram | ✅ `overrides/main.html`, `hooks/seo.py`, `assets/social-card.png` |
| **Install as an app** | "Add to Home screen"; pages already opened work offline | ✅ `manifest.webmanifest`, `sw.js` |
| **Phone-to-phone copy** | The offline zip (about 3 MB) is shared by Nearby Share or Bluetooth where data is scarce | ✅ zip, and how-to in `tools/` and `hi/` |
| **Hindi first page** | Hindi speakers land on a page in Hindi and share it in Hindi groups | ✅ `hi/index.md` · 🔜 `T-312` for more pages |
| **Reading-room posters** | A QR poster in Hindi and English on library and college notice boards | ✅ `tools/poster` |
| **Search** | Every page has a real description; official dates will bring notification searches | ✅ descriptions · 🔜 `T-107` calendar |
| **Community fixes** | Bilingual issue forms: "Report a mistake" and "Suggest a free resource". Fixes build trust | ✅ `.github/ISSUE_TEMPLATE/` |
| **Channel posts** | A Telegram channel with the daily question and new pages, posted from the Mac once a day | 🔜 `T-318` (owner step `H-007`) |
| **More daily questions** | Original questions per module keep the daily question fresh and useful across exams | 🔜 `T-319` |

## Rules that keep growth honest

- **No spam.** No unsolicited messages, no mass-adding to groups, no fake reviews or accounts. Sharing is always
  the student's own choice.
- **No tracking of students.** Measure only aggregates the platforms already give: GitHub traffic (views,
  clones, referrers), and Search Console once the owner adds it. No analytics scripts, no cookies.
- **No paid growth and no guarantees.** Word of mouth only. Never claim results, selections or ranks.
- **Never schedule the hive on GitHub** (see `docs/FREE-LLM-APIS.md`). The Telegram post runs from the Mac.

## Measuring (monthly, `T-322`)

JEVX writes one line a month to this file. It records GitHub page views, unique visitors and top referrers from
the repository's traffic page, Search Console clicks once available, and the number of issues opened by
students. No per-person data.
