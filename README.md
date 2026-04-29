# DWH-DIGSILENT პროექტი

ეს პროექტი იღებს CSV მონაცემს DWH/Unistream BI API-დან, ამუშავებს DataFrame-ს ტრანსფორმაციით და ინახავს შედეგს DIgSILENT ფორმატში.

## პროექტის სტრუქტურა

- `colab_ready.py` — Google Colab flow (secret/input + download)
- `main.py` — Windows/Desktop runner
- `src/dwh_client.py` — API-დან CSV წამოღება
- `src/transform.py` — ტრანსფორმაციის ლოგიკა (`transform_dataframe(df)`)
- `src/export.py` — CSV export (`/content/output` და Desktop)
- `requirements.txt`

## მოთხოვნები

- Python 3.10+
- `pip install -r requirements.txt`

## Google Colab გაშვება

1. ატვირთეთ პროექტი Colab გარემოში.
2. დააყენეთ ბიბლიოთეკები:
   ```python
   !pip install -r requirements.txt
   ```
3. API key მიწოდების უსაფრთხო გზა:
   - რეკომენდებული: Colab Secrets-ში შექმენით `DWH_API_KEY`.
   - ალტერნატივა: runtime env var (`os.environ["DWH_API_KEY"] = "..."`).
   - fallback: `getpass()`-ით ინტერაქტიური შეყვანა (ეკრანზე არ გამოჩნდება).
4. გაუშვით:
   ```python
   !python colab_ready.py
   ```
5. სკრიპტი:
   - ჩამოტვირთავს CSV-ს API-დან;
   - დაბეჭდავს პირველ 5 row-ს;
   - გაუშვებს ტრანსფორმაციას;
   - შეინახავს `/content/output/DIgSILENT_Table_YYYY_MM_DD.csv`;
   - გამოიძახებს `google.colab.files.download()` ავტომატური ჩამოტვირთვისთვის.

> შენიშვნა: Colab ვერ წერს თქვენს Windows Desktop-ზე პირდაპირ.

## Windows ლოკალურად გაშვება

1. გახსენით Command Prompt / PowerShell პროექტის ფოლდერში.
2. დააყენეთ დამოკიდებულებები:
   ```bash
   pip install -r requirements.txt
   ```
3. ჩასვით API key გარემოს ცვლადში:
   - PowerShell:
     ```powershell
     setx DWH_API_KEY "your_real_api_key"
     ```
   - ან მიმდინარე სესიაში:
     ```powershell
     $env:DWH_API_KEY="your_real_api_key"
     ```
4. გაუშვით:
   ```bash
   python main.py
   ```
5. შედეგი შეინახება Desktop-ზე:
   `DIgSILENT_Table_YYYY_MM_DD.csv`

## უსაფრთხოება

- API key **არ არის hardcoded** კოდში.
- API key **არ იბეჭდება** ლოგებში.
- გამოიყენება `requests` timeout + status check + მკაფიო error handling.

## CSV სქემა და ვალიდაცია

მოსალოდნელი სვეტები:
- `name`
- `P`
- `Q`
- `type`

თუ სვეტი აკლია, ტრანსფორმაცია აბრუნებს მკაფიო შეცდომას.
`P` და `Q` გადადის numeric ტიპში, არავალიდური მნიშვნელობები ხდება `0`.
