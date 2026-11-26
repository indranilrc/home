# Moving the Site to indranilroychoudhury.com

Do this only after the new site is live and checked at
`https://indranilrc.github.io/home/`.

## 1. In This Repo (Builder)

Edit `content/site.yml`:

```yaml
url: https://indranilroychoudhury.com
base_path: ""
cname: indranilroychoudhury.com
```

Commit and push. The build now writes a `CNAME` file and all links drop the
`/home` prefix.

## 2. At the Domain Registrar (Indranil)

Log in wherever `indranilroychoudhury.com` is registered (probably Weebly or
Square). Open the DNS settings and:

1. Remove any existing `A`, `AAAA`, or `CNAME` records for `@` and `www` that
   point at Weebly.
2. Add four `A` records for `@`:
   `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
3. Add four `AAAA` records for `@`:
   `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
4. Add a `CNAME` record: `www` → `indranilrc.github.io`

DNS changes can take from a few minutes to a day to spread.

## 3. On GitHub (Indranil)

1. Account **Settings → Pages → Verified domains**: add and verify
   `indranilroychoudhury.com` (adds one `TXT` record at the registrar). This
   stops anyone else from claiming the domain on GitHub.
2. Repo **Settings → Pages**: set **Custom domain** to
   `indranilroychoudhury.com`. Wait for the DNS check to pass.
3. Tick **Enforce HTTPS** once the certificate is issued (can take up to an hour).

## 4. Check

- `https://indranilroychoudhury.com/` shows the new site with a valid lock icon.
- `https://www.indranilroychoudhury.com/` redirects to it.
- `https://indranilrc.github.io/home/` redirects to it.

## 5. Retire Weebly (Indranil)

Only after step 4 passes: unpublish or cancel the Weebly site, **keeping the
domain registration** (or transfer the domain to another registrar first).
