# M03 backend foundation

Private development implementation: FastAPI, PostgreSQL/PostGIS, opaque cookie sessions and a persisted operational workflow. [Implementation report](../../docs/engineering/M03_BACKEND_IMPLEMENTATION_REPORT.md), [executed acceptance](../../docs/testing/M03_ACCEPTANCE_RESULTS.md), [all 117 operation statuses](../../data/schemas/m03-implementation-matrix.json). There are 58 implemented canonical operations; this is not a public deployment or a sensor validation.

Run commands from the repository root in PowerShell 7. Keep private configuration, mail, certificates, database files and evidence **outside the Git checkout**. Acceptance resets only a separately confirmed `hydro_disposable_*` database. Never point it at an operational database. No default user/password is shipped. Operator bootstrap prompts privately; choose your own email and password. Bootstrap creates a verified ADMIN only, with no inherited engineering or evaluator powers.

## Compose reproduction

Requires Docker Engine with Compose v2. This route is exercised by the M03 CI job; see the acceptance report for the observed result. PostGIS, Python and Caddy images are pinned by digest. Only HTTPS on loopback port 8443 is published. The database and internal probes have no published port. The root database secret is consumed by the database and initializer; the nonroot API cannot read operator credentials on the Linux container filesystem.

```powershell
$repo = (Get-Location).Path
$private = Join-Path (Split-Path $repo -Parent) 'hydro-m03-private-compose'
New-Item -ItemType Directory -Path $private -ErrorAction Stop | Out-Null
$env:HYDRO_PRIVATE_DIRECTORY = $private
$env:HYDRO_DATABASE_SECRET_FILE = Join-Path $private 'database-root.txt'
[IO.File]::WriteAllText($env:HYDRO_DATABASE_SECRET_FILE, [Convert]::ToBase64String([Security.Cryptography.RandomNumberGenerator]::GetBytes(40)))
$env:HYDRO_INIT_DATABASE = 'hydro_local_m03'
docker compose -f services/api/compose.yaml --profile tools config --quiet
docker compose -f services/api/compose.yaml --profile tools build
docker compose -f services/api/compose.yaml up -d api proxy
# Initializer applies Alembic migrations; bootstrap prompts for your private password.
docker compose -f services/api/compose.yaml exec --user 0 api python -c "import json,os; os.environ['HYDRO_MIGRATION_URL']=json.load(open('/private/operator/operator.json'))['migration_url']; from hydro.cli import main; main()" bootstrap --confirm-database hydro_local_m03 --slug local-utility --name 'Local Utility' --admin-email 'admin@example.invalid' --display-name 'Local Administrator' --enable-reporting
```

Copy Caddy's CA certificate explicitly; do not disable certificate verification or install an unreviewed system trust root:

```powershell
docker compose -f services/api/compose.yaml cp proxy:/data/caddy/pki/authorities/local/root.crt (Join-Path $private 'localhost-ca.crt')
# curl.exe uses explicit CA trust for this request only.
curl.exe --cacert (Join-Path $private 'localhost-ca.crt') https://localhost:8443/api/v1/auth/csrf
```

The CSRF response and cookie are session secrets: do not paste them into reports. Login then requires that cookie, its CSRF value and `Origin: https://localhost:8443`. All writes require CSRF and exact Origin, including public registration/recovery. Auth/global writes reject `Idempotency-Key`; tenant business writes require a UUID key, and versioned updates require `If-Match`. Account verification/invitation/recovery messages are private development files, not externally sent mail. There is no HTTP token-retrieval endpoint. ADMIN invites staff through the actual administration API; EVALUATOR cannot be invited here.

Use a **separate Compose project and new private directory** for destructive acceptance. Set new paths as above, then:

```powershell
# Stop the manual project before switching; localhost port/subnet are shared.
docker compose -f services/api/compose.yaml down
$env:COMPOSE_PROJECT_NAME = 'hydrooverity-m03-acceptance'
$env:HYDRO_INIT_DATABASE = 'hydro_disposable_m03'
docker compose -f services/api/compose.yaml up -d api proxy
docker compose -f services/api/compose.yaml --profile tools run --rm backend-check
docker compose -f services/api/compose.yaml --profile tools run --rm backend-check python services/api/tools/demo_backend.py --operator-config /private/operator/operator.json --runtime-config /private/runtime/runtime.json --confirm-disposable-database hydro_disposable_m03_demo --output-directory /private/https-demo
docker compose -f services/api/compose.yaml down
# No -v: existing database volumes are preserved. Stop the first project before
# starting the second: both deliberately use the same localhost port/subnet.
Remove-Item Env:COMPOSE_PROJECT_NAME
```

## Native Windows reproduction

Actually exercised with Python 3.12.14, official EDB PostgreSQL 17.11 and the official OSGeo PostGIS 3.6.2 bundle. Install/extract those tools separately into a private working directory; ensure PostGIS DLLs, extension control and SQL match the PostgreSQL installation. No machine policy change or copied Python environment is required. The operator needs an existing, privately configured local cluster and its privileged DSN, only during setup. Use a password-protected loopback listener. The examples below assume its `bin` path and port are known; adapt those paths to your installation.

```powershell
$repo = (Get-Location).Path
$private = Join-Path (Split-Path $repo -Parent) 'hydro-m03-private-native'
$venv = Join-Path (Split-Path $repo -Parent) 'hydro-m03-py312'
py -3.12 -m venv $venv
$py = Join-Path $venv 'Scripts/python.exe'
& $py -m pip install --only-binary=:all: -r services/api/requirements-lock.txt
# Only if Windows Application Control rejects SQLAlchemy's compiled extension:
$env:DISABLE_SQLALCHEMY_CEXT = '1'
& $py -m pip install --no-binary=SQLAlchemy --no-deps --force-reinstall SQLAlchemy==2.1.5
Remove-Item Env:DISABLE_SQLALCHEMY_CEXT
& $py -m pip check
$env:PYTHONPATH = Join-Path $repo 'services/api'
# Enter an existing privileged PostgreSQL DSN without shell history or console echo.
$secureDsn = Read-Host 'Private PostgreSQL operator DSN' -AsSecureString
$env:HYDRO_OPERATOR_DSN = [Net.NetworkCredential]::new('', $secureDsn).Password
& $py -m hydro.operator --database hydro_disposable_m03 --confirm-database hydro_disposable_m03 --private-directory $private
Remove-Item Env:HYDRO_OPERATOR_DSN
$operator = Get-Content (Join-Path $private 'operator.json') | ConvertFrom-Json
$env:HYDRO_MIGRATION_URL = $operator.migration_url
& $py -m alembic -c services/api/alembic.ini upgrade head
& $py -m hydro.cli bootstrap --confirm-database hydro_disposable_m03 --slug local-utility --name 'Local Utility' --admin-email 'admin@example.invalid' --display-name 'Local Administrator' --enable-reporting
Remove-Item Env:HYDRO_MIGRATION_URL
# This acceptance command resets the confirmed disposable database, including
# the synthetic bootstrap above. Never substitute your operational database.
& $py services/api/tools/verify_backend.py --operator-config (Join-Path $private 'operator.json') --runtime-config (Join-Path $private 'runtime.json') --confirm-disposable-database hydro_disposable_m03 --evidence-directory (Join-Path $private 'evidence')
# Actual HTTPS example starts its own API/proxy, verifies TLS, restarts the API,
# retains the synthetic database and stops only its own child processes.
& $py services/api/tools/demo_backend.py --operator-config (Join-Path $private 'operator.json') --runtime-config (Join-Path $private 'runtime.json') --confirm-disposable-database hydro_disposable_m03_demo --output-directory (Join-Path $private 'https-demo') --openssl 'C:\Program Files\Git\usr\bin\openssl.exe'
```

For a persistent manual session, create a two-day localhost certificate (OpenSSL required), then launch the API and proxy hidden. They have no privileged environment variables:

```powershell
$openssl = 'C:\Program Files\Git\usr\bin\openssl.exe'
$certificate = Join-Path $private 'localhost.crt'
$key = Join-Path $private 'localhost.key'
& $openssl req -x509 -newkey rsa:2048 -nodes -days 2 -keyout $key -out $certificate -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost,IP:127.0.0.1'
$apiArgs = '-m hydro.local api --runtime-config "' + (Join-Path $private 'runtime.json') + '"'
$proxyArgs = '-m hydro.local proxy --certificate "' + $certificate + '" --key "' + $key + '"'
$api = Start-Process -FilePath $py -ArgumentList $apiArgs -WindowStyle Hidden -PassThru
$proxy = Start-Process -FilePath $py -ArgumentList $proxyArgs -WindowStyle Hidden -PassThru
curl.exe --cacert $certificate https://localhost:8443/api/v1/public/project-status
# Private readiness is available only on the unexposed API listener.
Invoke-RestMethod http://127.0.0.1:8000/internal/health/ready
Stop-Process -Id $proxy.Id, $api.Id
```

Stop a native cluster only with its own `pg_ctl -D <dedicated-data-directory> stop -m fast`; do not stop unrelated PostgreSQL installations. Runtime configuration contains only the restricted application DSN and HMAC key. Native Windows processes share the current operator account; container user separation is stronger. Private ACLs restrict the development artifacts to that account and SYSTEM.

## Quality and regression checks

```powershell
& $py -m pip install --only-binary=:all: -r services/api/requirements-quality.txt
& $py -m ruff check services/api
& $py -m ruff format --check services/api
& $py services/api/tools/traceability.py --check
& $py services/api/tools/validate_runtime_openapi.py
& $py scripts/check_repository.py
& $py scripts/check_m02_design.py
& $py scripts/test_m02_design_checker.py -v
git diff --check
```

M05 and M08 retain their own isolated environments, requirements and reproduction commands. They must not be installed into this backend environment. Generated raw scientific truth and seeds stay outside ordinary APIs, dashboard artifacts and this acceptance evidence. Private development mail is bounded and post-commit; external delivery, shared multi-instance limits, upload handling, ingestion, live scientific verification and production operations require separately authorized work.
