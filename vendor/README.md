# vendor/ — local copies of CDN scripts

This package is fully **portable**: unzip anywhere, no install.
For complete offline operation, drop these 3 files into this folder:

| filename | source URL | size |
|---|---|---|
| react.js | https://unpkg.com/react@18.3.1/umd/react.development.js | ~1.0 MB |
| react-dom.js | https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js | ~1.2 MB |
| babel.js | https://unpkg.com/@babel/standalone@7.29.0/babel.min.js | ~2.7 MB |

## One-line download (online PC, then copy folder via USB)

**PowerShell (Windows):**
```powershell
cd vendor
iwr https://unpkg.com/react@18.3.1/umd/react.development.js -o react.js
iwr https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js -o react-dom.js
iwr https://unpkg.com/@babel/standalone@7.29.0/babel.min.js -o babel.js
```

**bash (mac/linux):**
```bash
cd vendor
curl -L -o react.js     https://unpkg.com/react@18.3.1/umd/react.development.js
curl -L -o react-dom.js https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js
curl -L -o babel.js     https://unpkg.com/@babel/standalone@7.29.0/babel.min.js
```

After this the entire package works **offline** — no internet needed.
Total vendor size: ~5 MB.
