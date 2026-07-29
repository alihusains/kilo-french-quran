# Quran Admin - GitHub Pages

Static single-file CRUD app for managing Quran surahs, verses, and tafsir.

**Connects to Supabase at**: https://supabase.com/dashboard/project/ayyfeobcubwoasrshhbg

## Deployment

1. Go to **Settings → Pages**
2. Set **Source** to **GitHub Actions**
3. Push to `main` branch

The site will be live at: https://alihusains.github.io/kilo-french-quran/

## Login

Default password: `admin123`

Change `ADMIN_PASSWORD` in the script before deploying.

## Features

- Dashboard with statistics
- Surah list with search
- Verse management (edit Arabic and French)
- Tafsir CRUD operations
- Responsive design for mobile/desktop

## Configuration

Edit in the script (line ~100):

```javascript
const CONFIG = {
  SUPABASE_URL: 'https://ayyfeobcubwoasrshhbg.supabase.co',
  SUPABASE_ANON_KEY: 'sb_publishable_CmQP2Ir7vqQu40j9WUHn-w_95NqUUKS',
  ADMIN_PASSWORD: 'admin123'
}
```

## Troubleshooting

- **Blank page**: Check browser console for errors
- **Cannot login**: Verify ADMIN_PASSWORD
- **No data**: Ensure database is populated in Supabase
