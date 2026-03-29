
```
pip install requests python-dotenv
```

```
cp .env.example .env
```

```
python create_test_user.py
```

Result:
```
────────────────────────────────────────────────
  🛠   Remnawave — Create Test User
────────────────────────────────────────────────
  Username: shahrokh_test

  Creating user …

────────────────────────────────────────────────
  ✅  User created successfully
────────────────────────────────────────────────
  Username   : shahrokh_test
  UUID       : abc123...
  Status     : ACTIVE
  Tag        : TEST
  Traffic    : 1.00 GB
  Expires    : 2026-04-02T...
────────────────────────────────────────────────
  📎 Subscription URL:
  https://your-panel.com/api/sub/xxxxx
────────────────────────────────────────────────
```