# JWT Mini-API

## Kirjeldus

Väike Flaski API, mis demonstreerib JWT (JSON Web Token) autentimist.
Kasutaja logib sisse kasutajanime ja parooliga, saab tokeni ning kasutab seda
kaitstud endpointide poole pöördumiseks. Üks endpoint on lubatud ainult
kasutajatele, kelle roll on `admin`.

## Kasutatud tehnoloogiad

- Python 3
- Flask
- PyJWT
- python-dotenv

## Paigaldamine

1. Loo ja aktiveeri virtuaalkeskkond.

   macOS / Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   Windows PowerShell:

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

2. Paigalda vajalikud teegid:

   ```bash
   pip install -r requirements.txt
   ```

3. Loo projekti kausta fail `.env` salajase võtmega:

   ```
   JWT_SECRET=super_secret_key_123
   ```

   Fail `.env` on lisatud `.gitignore` faili ega satu Giti.

## Käivitamine

```bash
python app.py
```

Server käivitub aadressil `http://127.0.0.1:5001`.

## Kasutajad

| kasutajanimi | parool     | roll    |
|--------------|------------|---------|
| student      | student123 | student |
| admin        | admin123   | admin   |

## Näide: /login

Päring:

```bash
curl -X POST http://127.0.0.1:5001/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student","password":"student123"}'
```

Vastus (HTTP 200):

```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...."
}
```

Token on allkirjastatud algoritmiga HS256, kehtib 5 minutit ja sisaldab välju:
`sub` (kasutajanimi), `role` (roll), `iat` (väljastamise aeg) ja `exp` (aegumise aeg).

## Näide: JWT kasutamine

Saada token päises `Authorization`:

```bash
curl http://127.0.0.1:5001/profiil \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Vastus (HTTP 200):

```json
{
  "role": "student",
  "username": "student"
}
```

## Endpointid

| Meetod | Tee       | Ligipääs         | Vastused                                                                      |
|--------|-----------|------------------|-------------------------------------------------------------------------------|
| POST   | /login    | avalik           | 200 + token õigete andmete korral, 401 vale kasutajanime või parooli korral   |
| GET    | /profiil  | kehtiv JWT       | 200 + kasutaja info, 401 kui token puudub, on vigane, muudetud või aegunud    |
| GET    | /admin    | JWT, roll admin  | 200 adminile, 403 studentile, 401 kui token puudub või on vigane              |

## Testimine

API-d testiti käsitsi käsuga `curl`. Kõik 7 testi läbiti edukalt.

| #  | Test                                   | Endpoint        | Oodatud | Tegelik | Tulemus |
|----|----------------------------------------|-----------------|---------|---------|---------|
| 1  | Edukas sisselogimine                   | POST /login     | 200     | 200     | Läbitud |
| 2  | Vale parool                            | POST /login     | 401     | 401     | Läbitud |
| 3  | Profiil kehtiva tokeniga               | GET /profiil    | 200     | 200     | Läbitud |
| 4  | Profiil ilma tokenita                  | GET /profiil    | 401     | 401     | Läbitud |
| 5  | Muudetud token                         | GET /profiil    | 401     | 401     | Läbitud |
| 6  | Aegunud token                          | GET /profiil    | 401     | 401     | Läbitud |
| 7  | Student kasutab admin endpointi        | GET /admin      | 403     | 403     | Läbitud |

## Turvamärkused

- Salajane võti on failis `.env`, mitte lähtekoodis, ja `.env` ei ole Gitis.
- Tokenid on allkirjastatud algoritmiga HS256 ja aeguvad 5 minuti pärast.
- Server aktsepteerib tokeni kontrollimisel ainult algoritmi HS256.
- Muudetud token ei läbi allkirja kontrolli ja aegunud token (`exp`) lükatakse tagasi; mõlemal juhul on vastus 401.
- Kasutajad ja paroolid on koodis lihttekstina. See sobib ainult õppeprojektiks. Päris rakenduses kasutataks andmebaasi ja räsitud paroole.
- Server töötab debug-režiimis ja tavalise HTTP kaudu. Päris rakenduses tuleb kasutada HTTPS-i ja debug-režiim välja lülitada.
- Igaüks saab JWT sisu lugeda, seega ära pane tokenisse paroole ega muid saladusi.
