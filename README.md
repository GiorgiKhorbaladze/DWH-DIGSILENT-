# DWH-DIGSILENT (Windows + Python 2.7)

ეს პროექტი არის **Windows local** გაშვებისთვის და გათვალისწინებულია **Python 2.7** გარემოზე.

## შენიშვნა Colab-ზე

თქვენი მოთხოვნის მიხედვით, Colab საერთოდ არ გამოიყენება. პროექტი სრულად local Windows flow-ზეა.

## ფაილები

- `main.py` — მთავარი runner (API + fallback)
- `src/dwh_client.py` — DWH API კლიენტი და local CSV reader
- `src/transform.py` — `transform_dataframe(df)` ტრანსფორმაცია
- `src/export.py` — Desktop-ზე შედეგის შენახვა
- `requirements.txt` — Python 2.7 თავსებადი პაკეტები
- `run.bat` — ორჯერ დაკლიკებით გაშვება
- `1.rar` — reference არქივი

## Python 2.7 setup

1. გახსენით CMD/PowerShell პროექტის ფოლდერში.
2. დააყენეთ პაკეტები:
   ```bash
   pip install -r requirements.txt
   ```

## API key (hardcode-ის გარეშე)

`DWH_API_KEY` უნდა იყოს environment variable.

### CMD (მიმდინარე ფანჯარა)
```cmd
set DWH_API_KEY=your_real_key
```

### PowerShell (მიმდინარე სესია)
```powershell
$env:DWH_API_KEY="your_real_key"
```

### PowerShell (მუდმივად)
```powershell
setx DWH_API_KEY "your_real_key"
```

## გაშვება

### ტერმინალიდან
```bash
python main.py
```

### Double-click
- გაუშვით `run.bat`.

## fallback რეჟიმი

- პროგრამა ჯერ ცდილობს API-დან CSV-ს წამოღებას.
- თუ API არ იმუშავებს (DNS/network/401/403/timeout/სხვა), პროგრამა გთხოვთ local CSV ფაილის path-ს.
- ამ ფაილზე გაგრძელდება ტრანსფორმაცია.

## ტრანსფორმაციის წესები

საჭირო სვეტები:
- `name`
- `P`
- `Q`
- `type`

ქცევა:
- თუ სვეტები აკლია → მკაფიო შეცდომა.
- `P/Q` გადაიყვანება numeric-ზე.
- არავალიდური `P/Q` მნიშვნელობები ხდება `0`.
- ნაჩვენებია რამდენი არავალიდური `P/Q` გასწორდა.

## შედეგი

საბოლოო ფაილი ინახება Desktop-ზე:

`DIgSILENT_Table_YYYY_MM_DD.csv`

Encoding: `utf-8-sig`
