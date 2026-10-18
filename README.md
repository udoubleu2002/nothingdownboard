# Nothing Down Board website

Every $0-Down Deal, Updated Daily. A static site that Netlify rebuilds from `data/offers.json` each time it changes.

## What's here

| Path | What it is |
|---|---|
| `site.json` | Site name, tagline, description and **your domain** |
| `data/offers.json` | The offers. The daily refresh replaces this file. |
| `build.py` | Builds every page into `public/` (Python standard library only) |
| `src/site.css`, `src/site.js` | Styles and the search/filter script, inlined into each page |
| `static/` | Favicon, app icons, social share image, web app manifest |
| `netlify.toml` | Tells Netlify to run `python3 build.py` and publish `public/` |

## What the build produces

- **Homepage** with the headline "Nothing-Down Deals for {weekday, date}", every offer pre-rendered in the HTML (readable by Google without JavaScript), and an FAQ.
- **Category pages:** `/car-leases/`, `/car-financing/`, `/home-loans/`, `/phones/`, `/home-improvement/`, each titled for the current month.
- **Brand pages** under `/deals/` for every brand with two or more offers (Toyota, Honda, T-Mobile, AT&T…).
- **About and affiliate disclosure** at `/about/`, plus a helpful 404 page.
- **SEO:** unique title and description per page, canonical links, Open Graph and X/Twitter share cards, structured data (offer lists, breadcrumbs, FAQ, site search box), `sitemap.xml` and `robots.txt`.
- **Phones:** sticky search bar, sideways-scrolling category chips, a bottom-sheet filter drawer, 44px tap targets, safe-area support for notched phones, light and dark mode, add-to-home-screen icons.
- Offers past their end date are left out automatically.

## Phone and visitor features

- **One-tap filters** above the list (Nothing at signing, No trade-in, No new line, Under $350/mo, New today, Saved). Every filter is kept in the page link, so a filtered view can be shared.
- **Total cost** on every lease (payment × months) and a "Lowest total cost" sort.
- **Save and share** on every offer. Saved offers are kept on the visitor's device; Share opens the phone's share menu (or copies the link on desktop).
- **"What can I get?"** — a 3-question match that sends visitors to the offers they qualify for. Open it from any page, or link to `/#match`.
- **Bottom bar on phones:** Deals, Match me, Saved, Guides.
- **A page for every offer** at `/offer/<id>/`, with key facts, what you need, similar offers and a link to the source.
- **New since your last visit:** returning visitors see a purple tag on offers added since they last came, plus a one-tap filter.
- **Deal alerts sign-up** using Netlify Forms (no extra code or server).

## Deal alerts: where sign-ups go

Netlify collects every sign-up automatically once the site is deployed. In Netlify open **Forms → deal-alerts** to see them. To get an email for each sign-up, go to **Forms → Form notifications → Add notification → Email notification**. To actually send the alerts, connect the form to an email service (for example Mailchimp, Buttondown or ConvertKit) through Zapier, or export the list as CSV. Netlify's free plan includes a monthly sign-up limit; check your plan.

## Setup

1. **Set your domain.** Edit `site.json` and is set to `https://nothingdown.com`. If you ever make www the primary domain in Netlify, change it to `https://www.nothingdown.com` to match.
2. **Push to GitHub.** Create an empty repository and upload this folder's contents (not `public/`, which Netlify builds).
3. **Connect Netlify.** Add new project → Import an existing project → GitHub → pick the repo. Netlify reads `netlify.toml`, so leave the build settings as they are and deploy.
4. **Add your domain in Netlify.** Domain management → Add a domain. Add `nothingdown.com` and set it as the **primary domain**; Netlify then redirects `www.nothingdown.com` to it.
5. **Point GoDaddy at Netlify.** In GoDaddy DNS: set the `A` record for `@` to `75.2.60.5` (delete other `@` A records, including "Parked"), and set the `CNAME` for `www` to your `yoursite.netlify.app` address. HTTPS turns on by itself once DNS updates.
6. **Tell Google.** Add the domain in Google Search Console, verify it, and submit `https://nothingdown.com/sitemap.xml`. Use the URL Inspection tool on the homepage to request indexing.

## Preview locally

```
python3 build.py
cd public && python3 -m http.server 8000
```

Then open http://localhost:8000.

## Daily updates

Each morning the refresh writes a new `data/offers.json` (with `meta.lastRefreshed` set to that day) and commits it. Netlify sees the commit, runs the build, and the headline date, "New today" tags, sitemap dates and month-based titles all update together.
