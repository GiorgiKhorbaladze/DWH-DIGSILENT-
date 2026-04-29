# DWH-DIGSILENT

თუ რთულია გაშვება, გამოიყენე **ერთი ფაილი**:

## ✅ ყველაზე მარტივი გზა

1. ორჯერ დააჭირე: **`START_HERE.bat`**
2. ჩასვი API key როცა მოგთხოვს
3. დაელოდე დასრულებას
4. შედეგი იქნება Desktop-ზე: `DIgSILENT_Table_YYYY_MM_DD.csv`

---

## Legacy Python 2.7 usage (pip-ის გარეშე)

ეს პროექტი მუშაობს `legacy_py27.py`-ით ისე, რომ არაფერი დასაყენებელი არ დაგჭირდეს (თუ Python უკვე დგას კომპიუტერზე).

გამოყენებული მოდულები მხოლოდ built-in-ებია:
- `urllib2`
- `csv`
- `os`
- `sys`
- `datetime`
- `codecs`

### ხელით გაშვება (თუ გინდა)

CMD:
```cmd
set DWH_API_KEY=აქ_ჩასვას_API_KEY
python legacy_py27.py
```

---

## როგორ მუშაობს

- ჯერ ცდილობს DWH API-დან წამოღებას.
- თუ API ვერ იმუშავებს (TLS/HTTPS/DNS/network), მოგთხოვს local CSV ფაილის path-ს.
- ამოწმებს სვეტებს: `name`, `P`, `Q`, `type`.
- `P/Q` გადააქვს `float`-ში, error-ის დროს ხდება `0.0`.
- ინახავს Desktop-ზე თარიღიანი სახელით.

---

## დამატებითი ფაილები

- `main.py` — Python 3 flow
- `run.bat` — main.py გაშვება
- `run_py27.bat` — legacy_py27.py გაშვება
- `START_HERE.bat` — ყველაზე მარტივი one-click launcher
