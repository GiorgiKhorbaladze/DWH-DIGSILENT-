# DWH-DIGSILENT

პროექტში არის ორი რეჟიმი:

1. **main.py** — Python 3 ვერსია (არსებული მოდულებით)
2. **legacy_py27.py** — Python 2.7 legacy ვერსია, მხოლოდ built-in ბიბლიოთეკებით

---

## Legacy Python 2.7 usage (pip-ის გარეშე)

თუ კომპიუტერზე გაქვთ მხოლოდ Python 2.7 და არაფრის დაყენება არ შეიძლება, გამოიყენეთ `legacy_py27.py`.

### რა იყენებს legacy ვერსია

მხოლოდ Python 2.7 built-in modules:
- `urllib2`
- `csv`
- `os`
- `sys`
- `datetime`
- `codecs`

`pandas`, `requests` და სხვა გარე პაკეტები **არ გამოიყენება**.

### 1) API key დაყენება (აუცილებელია)

CMD-ში:
```cmd
set DWH_API_KEY=აქ_ჩასვას_API_KEY
```

PowerShell-ში:
```powershell
$env:DWH_API_KEY="აქ_ჩასვას_API_KEY"
```

### 2) გაშვება

```cmd
python legacy_py27.py
```

ან ორჯერ დაკლიკებით:
- გაუშვით `run_py27.bat`

### 3) როგორ მუშაობს

1. ცდილობს API-დან CSV-ის წამოღებას (`urllib2`-ით).
2. API თუ ჩავარდა (TLS/HTTPS/DNS/network), ავტომატურად გადადის fallback რეჟიმში და გთხოვთ local CSV path-ს.
3. ამოწმებს სვეტებს: `name`, `P`, `Q`, `type`.
4. `P` და `Q` გადაყავს `float`-ში; არავალიდური მნიშვნელობები ხდება `0.0`.
5. ინახავს შედეგს Desktop-ზე სახელით:
   `DIgSILENT_Table_YYYY_MM_DD.csv`

---

## Python 3 main.py (დატოვებულია)

`main.py` დარჩენილია Python 3 flow-სთვის (როგორც ითხოვეთ).
თუ Python 2.7 გაქვთ, გამოიყენეთ მხოლოდ `legacy_py27.py`.
