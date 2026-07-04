PS D:\MisProyectos\exSoftOptic\backend> python -m pip install --upgrade pip
Requirement already satisfied: pip in C:\Users\Traba\AppData\Roaming\Python\Python314\site-packages (26.0.1)
Collecting pip
  Downloading pip-26.1.2-py3-none-any.whl.metadata (4.6 kB)
Downloading pip-26.1.2-py3-none-any.whl (1.8 MB)
   ---------------------------------------- 1.8/1.8 MB 5.2 MB/s  0:00:00
Installing collected packages: pip
  Attempting uninstall: pip
    Found existing installation: pip 26.0.1
    Uninstalling pip-26.0.1:
      Successfully uninstalled pip-26.0.1
Successfully installed pip-25.2
WARNING: There was an error checking the latest version of pip.
PS D:\MisProyectos\exSoftOptic\backend> python -m pip install -r .\requirements-dev.txt
Collecting fastapi==0.110.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 2))
  Downloading fastapi-0.110.0-py3-none-any.whl.metadata (25 kB)
Collecting uvicorn==0.27.1 (from uvicorn[standard]==0.27.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 3))
  Downloading uvicorn-0.27.1-py3-none-any.whl.metadata (6.3 kB)
Collecting python-multipart==0.0.9 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 4))
  Using cached python_multipart-0.0.9-py3-none-any.whl.metadata (2.5 kB)
Collecting sqlalchemy==2.0.27 (from sqlalchemy[asyncio]==2.0.27->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 7))
  Downloading SQLAlchemy-2.0.27-py3-none-any.whl.metadata (9.6 kB)
Collecting asyncpg==0.29.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 8))
  Using cached asyncpg-0.29.0.tar.gz (820 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting alembic==1.13.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 9))
  Downloading alembic-1.13.1-py3-none-any.whl.metadata (7.4 kB)
Collecting psycopg2-binary==2.9.9 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 10))
  Using cached psycopg2-binary-2.9.9.tar.gz (384 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting motor==3.3.2 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 13))
  Downloading motor-3.3.2-py3-none-any.whl.metadata (20 kB)
Collecting pymongo==4.6.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 14))
  Downloading pymongo-4.6.1.tar.gz (1.4 MB)
     ---------------------------------------- 1.4/1.4 MB 5.4 MB/s  0:00:00
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting redis==5.0.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 17))
  Using cached redis-5.0.1-py3-none-any.whl.metadata (8.9 kB)
Collecting aioredis==2.0.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 18))
  Downloading aioredis-2.0.1-py3-none-any.whl.metadata (15 kB)
Collecting python-jose==3.3.0 (from python-jose[cryptography]==3.3.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 21))
  Using cached python_jose-3.3.0-py2.py3-none-any.whl.metadata (5.4 kB)
Collecting passlib==1.7.4 (from passlib[bcrypt]==1.7.4->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 22))
  Using cached passlib-1.7.4-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting bcrypt==4.1.2 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 23))
  Downloading bcrypt-4.1.2-cp39-abi3-win_amd64.whl.metadata (9.8 kB)
Collecting pydantic==2.6.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 27))
  Downloading pydantic-2.6.1-py3-none-any.whl.metadata (83 kB)
Collecting pydantic-settings==2.1.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 28))
  Using cached pydantic_settings-2.1.0-py3-none-any.whl.metadata (2.9 kB)
Collecting email-validator==2.1.0.post1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 29))
  Downloading email_validator-2.1.0.post1-py3-none-any.whl.metadata (25 kB)
Collecting celery==5.3.6 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Downloading celery-5.3.6-py3-none-any.whl.metadata (21 kB)
Collecting httpx==0.27.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 35))
  Using cached httpx-0.27.0-py3-none-any.whl.metadata (7.2 kB)
Collecting python-dotenv==1.0.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 38))
  Downloading python_dotenv-1.0.1-py3-none-any.whl.metadata (23 kB)
Collecting structlog==24.1.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 39))
  Downloading structlog-24.1.0-py3-none-any.whl.metadata (6.9 kB)
Collecting loguru==0.7.2 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 40))
  Downloading loguru-0.7.2-py3-none-any.whl.metadata (23 kB)
Collecting python-dateutil==2.8.2 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 41))
  Downloading python_dateutil-2.8.2-py2.py3-none-any.whl.metadata (8.2 kB)
Collecting reportlab==4.1.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 44))
  Downloading reportlab-4.1.0-py3-none-any.whl.metadata (1.4 kB)
Collecting weasyprint==61.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading weasyprint-61.0-py3-none-any.whl.metadata (3.7 kB)
Collecting openpyxl==3.1.2 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 48))
  Using cached openpyxl-3.1.2-py2.py3-none-any.whl.metadata (2.5 kB)
Collecting pandas==2.2.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 49))
  Downloading pandas-2.2.0.tar.gz (4.4 MB)
     ---------------------------------------- 4.4/4.4 MB 8.5 MB/s  0:00:00
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Installing backend dependencies ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pytest>=7.4.4 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 52))
  Downloading pytest-9.1.1-py3-none-any.whl.metadata (7.6 kB)
Collecting pytest-asyncio==0.23.4 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 53))
  Downloading pytest_asyncio-0.23.4-py3-none-any.whl.metadata (3.9 kB)
Collecting pytest-cov==4.1.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 54))
  Downloading pytest_cov-4.1.0-py3-none-any.whl.metadata (26 kB)
Collecting factory-boy==3.3.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 55))
  Downloading factory_boy-3.3.0-py2.py3-none-any.whl.metadata (15 kB)
Collecting black==24.1.1 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 58))
  Downloading black-24.1.1-py3-none-any.whl.metadata (73 kB)
Collecting isort==5.13.2 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 59))
  Downloading isort-5.13.2-py3-none-any.whl.metadata (12 kB)
Collecting flake8==7.0.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 60))
  Downloading flake8-7.0.0-py2.py3-none-any.whl.metadata (3.8 kB)
Collecting mypy==1.8.0 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 61))
  Downloading mypy-1.8.0-py3-none-any.whl.metadata (1.8 kB)
Collecting ipython==8.21.0 (from -r .\requirements-dev.txt (line 5))
  Downloading ipython-8.21.0-py3-none-any.whl.metadata (5.9 kB)
Collecting ipdb==0.13.13 (from -r .\requirements-dev.txt (line 6))
  Downloading ipdb-0.13.13-py3-none-any.whl.metadata (14 kB)
Collecting pytest-watch==4.2.0 (from -r .\requirements-dev.txt (line 7))
  Downloading pytest-watch-4.2.0.tar.gz (16 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting pre-commit==3.6.0 (from -r .\requirements-dev.txt (line 8))
  Downloading pre_commit-3.6.0-py2.py3-none-any.whl.metadata (1.3 kB)
Collecting debugpy==1.8.1 (from -r .\requirements-dev.txt (line 11))
  Downloading debugpy-1.8.1-py2.py3-none-any.whl.metadata (1.1 kB)
Collecting starlette<0.37.0,>=0.36.3 (from fastapi==0.110.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 2))
  Downloading starlette-0.36.3-py3-none-any.whl.metadata (5.9 kB)
Requirement already satisfied: typing-extensions>=4.8.0 in C:\Python314\Lib\site-packages (from fastapi==0.110.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 2)) (4.15.0)
Requirement already satisfied: annotated-types>=0.4.0 in C:\Python314\Lib\site-packages (from pydantic==2.6.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 27)) (0.7.0)
Collecting pydantic-core==2.16.2 (from pydantic==2.6.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 27))
  Downloading pydantic_core-2.16.2.tar.gz (368 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Installing backend dependencies ... done
  Preparing metadata (pyproject.toml) ... done
Collecting click>=7.0 (from uvicorn==0.27.1->uvicorn[standard]==0.27.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 3))
  Downloading click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
Requirement already satisfied: h11>=0.8 in C:\Python314\Lib\site-packages (from uvicorn==0.27.1->uvicorn[standard]==0.27.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 3)) (0.16.0)
Collecting greenlet!=0.4.17 (from sqlalchemy==2.0.27->sqlalchemy[asyncio]==2.0.27->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 7))
  Downloading greenlet-3.5.3-cp314-cp314-win_amd64.whl.metadata (3.9 kB)
Collecting Mako (from alembic==1.13.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 9))
  Using cached mako-1.3.12-py3-none-any.whl.metadata (2.9 kB)
Requirement already satisfied: dnspython<3.0.0,>=1.16.0 in C:\Python314\Lib\site-packages (from pymongo==4.6.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 14)) (2.8.0)
Collecting async-timeout (from aioredis==2.0.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 18))
  Downloading async_timeout-5.0.1-py3-none-any.whl.metadata (5.1 kB)
Collecting ecdsa!=0.15 (from python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 21))
  Using cached ecdsa-0.19.2-py2.py3-none-any.whl.metadata (29 kB)
Collecting rsa (from python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 21))
  Using cached rsa-4.9.1-py3-none-any.whl.metadata (5.6 kB)
Collecting pyasn1 (from python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 21))
  Using cached pyasn1-0.6.3-py3-none-any.whl.metadata (8.4 kB)
Requirement already satisfied: idna>=2.0.0 in C:\Python314\Lib\site-packages (from email-validator==2.1.0.post1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 29)) (3.18)
Collecting billiard<5.0,>=4.2.0 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached billiard-4.2.4-py3-none-any.whl.metadata (4.8 kB)
Collecting click-didyoumean>=0.3.0 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached click_didyoumean-0.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting click-plugins>=1.1.1 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached click_plugins-1.1.1.2-py2.py3-none-any.whl.metadata (6.5 kB)
Collecting click-repl>=0.2.0 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached click_repl-0.3.0-py3-none-any.whl.metadata (3.6 kB)
Collecting kombu<6.0,>=5.3.4 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached kombu-5.6.2-py3-none-any.whl.metadata (3.5 kB)
Collecting tzdata>=2022.7 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached tzdata-2026.2-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting vine<6.0,>=5.1.0 (from celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached vine-5.1.0-py3-none-any.whl.metadata (2.7 kB)
Requirement already satisfied: anyio in C:\Python314\Lib\site-packages (from httpx==0.27.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 35)) (4.13.0)
Requirement already satisfied: certifi in C:\Python314\Lib\site-packages (from httpx==0.27.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 35)) (2026.5.20)
Requirement already satisfied: httpcore==1.* in C:\Python314\Lib\site-packages (from httpx==0.27.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 35)) (1.0.9)
Collecting sniffio (from httpx==0.27.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 35))
  Using cached sniffio-1.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting colorama>=0.3.4 (from loguru==0.7.2->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 40))
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Collecting win32-setctime>=1.0.0 (from loguru==0.7.2->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 40))
  Using cached win32_setctime-1.2.0-py3-none-any.whl.metadata (2.4 kB)
Collecting six>=1.5 (from python-dateutil==2.8.2->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 41))
  Using cached six-1.17.0-py2.py3-none-any.whl.metadata (1.7 kB)
Collecting pillow>=9.0.0 (from reportlab==4.1.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 44))
  Downloading pillow-12.3.0-cp314-cp314-win_amd64.whl.metadata (9.3 kB)
Collecting chardet (from reportlab==4.1.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 44))
  Using cached chardet-7.4.3-cp314-cp314-win_amd64.whl.metadata (9.4 kB)
Collecting pydyf>=0.8.0 (from weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading pydyf-0.12.1-py3-none-any.whl.metadata (2.5 kB)
Requirement already satisfied: cffi>=0.6 in C:\Python314\Lib\site-packages (from weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45)) (2.0.0)
Collecting html5lib>=1.1 (from weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading html5lib-1.1-py2.py3-none-any.whl.metadata (16 kB)
Collecting tinycss2>=1.0.0 (from weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading tinycss2-1.5.1-py3-none-any.whl.metadata (3.0 kB)
Collecting cssselect2>=0.1 (from weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading cssselect2-0.9.0-py3-none-any.whl.metadata (2.9 kB)
Collecting Pyphen>=0.9.1 (from weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading pyphen-0.17.2-py3-none-any.whl.metadata (3.2 kB)
Collecting fonttools>=4.0.0 (from fonttools[woff]>=4.0.0->weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading fonttools-4.63.0-cp314-cp314-win_amd64.whl.metadata (121 kB)
Collecting et-xmlfile (from openpyxl==3.1.2->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 48))
  Using cached et_xmlfile-2.0.0-py3-none-any.whl.metadata (2.7 kB)
Collecting numpy<2,>=1.26.0 (from pandas==2.2.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 49))
  Using cached numpy-1.26.4-cp314-cp314-win_amd64.whl
Collecting pytz>=2020.1 (from pandas==2.2.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 49))
  Downloading pytz-2026.2-py2.py3-none-any.whl.metadata (22 kB)
Collecting pytest>=7.4.4 (from -r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 52))
  Downloading pytest-7.4.4-py3-none-any.whl.metadata (7.9 kB)
Collecting coverage>=5.2.1 (from coverage[toml]>=5.2.1->pytest-cov==4.1.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 54))
  Downloading coverage-7.15.0-cp314-cp314-win_amd64.whl.metadata (8.8 kB)
Collecting Faker>=0.7.0 (from factory-boy==3.3.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 55))
  Downloading faker-40.28.1-py3-none-any.whl.metadata (16 kB)
Collecting mypy-extensions>=0.4.3 (from black==24.1.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 58))
  Downloading mypy_extensions-1.1.0-py3-none-any.whl.metadata (1.1 kB)
Collecting packaging>=22.0 (from black==24.1.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 58))
  Using cached packaging-26.2-py3-none-any.whl.metadata (3.5 kB)
Collecting pathspec>=0.9.0 (from black==24.1.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 58))
  Downloading pathspec-1.1.1-py3-none-any.whl.metadata (14 kB)
Collecting platformdirs>=2 (from black==24.1.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 58))
  Using cached platformdirs-4.10.0-py3-none-any.whl.metadata (5.5 kB)
Collecting mccabe<0.8.0,>=0.7.0 (from flake8==7.0.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 60))
  Using cached mccabe-0.7.0-py2.py3-none-any.whl.metadata (5.0 kB)
Collecting pycodestyle<2.12.0,>=2.11.0 (from flake8==7.0.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 60))
  Downloading pycodestyle-2.11.1-py2.py3-none-any.whl.metadata (4.5 kB)
Collecting pyflakes<3.3.0,>=3.2.0 (from flake8==7.0.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 60))
  Downloading pyflakes-3.2.0-py2.py3-none-any.whl.metadata (3.5 kB)
Collecting decorator (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading decorator-5.3.1-py3-none-any.whl.metadata (3.9 kB)
Collecting jedi>=0.16 (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading jedi-0.20.0-py2.py3-none-any.whl.metadata (23 kB)
Collecting matplotlib-inline (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading matplotlib_inline-0.2.2-py3-none-any.whl.metadata (2.4 kB)
Collecting prompt-toolkit<3.1.0,>=3.0.41 (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Using cached prompt_toolkit-3.0.52-py3-none-any.whl.metadata (6.4 kB)
Collecting pygments>=2.4.0 (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Using cached pygments-2.20.0-py3-none-any.whl.metadata (2.5 kB)
Collecting stack-data (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading stack_data-0.6.3-py3-none-any.whl.metadata (18 kB)
Collecting traitlets>=5 (from ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading traitlets-5.15.1-py3-none-any.whl.metadata (10 kB)
Collecting docopt>=0.4.0 (from pytest-watch==4.2.0->-r .\requirements-dev.txt (line 7))
  Downloading docopt-0.6.2.tar.gz (25 kB)
  Installing build dependencies ... done
  Getting requirements to build wheel ... done
  Preparing metadata (pyproject.toml) ... done
Collecting watchdog>=0.6.0 (from pytest-watch==4.2.0->-r .\requirements-dev.txt (line 7))
  Downloading watchdog-6.0.0-py3-none-win_amd64.whl.metadata (44 kB)
Collecting cfgv>=2.0.0 (from pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Downloading cfgv-3.5.0-py2.py3-none-any.whl.metadata (8.9 kB)
Collecting identify>=1.0.0 (from pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Downloading identify-2.6.19-py2.py3-none-any.whl.metadata (4.4 kB)
Collecting nodeenv>=0.11.1 (from pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Downloading nodeenv-1.10.0-py2.py3-none-any.whl.metadata (24 kB)
Collecting pyyaml>=5.1 (from pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Using cached pyyaml-6.0.3-cp314-cp314-win_amd64.whl.metadata (2.4 kB)
Collecting virtualenv>=20.10.0 (from pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Downloading virtualenv-21.5.1-py3-none-any.whl.metadata (3.4 kB)
Requirement already satisfied: cryptography>=3.4.0 in C:\Python314\Lib\site-packages (from python-jose[cryptography]==3.3.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 21)) (47.0.0)
Collecting httptools>=0.5.0 (from uvicorn[standard]==0.27.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 3))
  Downloading httptools-0.8.0-cp314-cp314-win_amd64.whl.metadata (3.7 kB)
Collecting watchfiles>=0.13 (from uvicorn[standard]==0.27.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 3))
  Downloading watchfiles-1.2.0-cp314-cp314-win_amd64.whl.metadata (5.0 kB)
Collecting websockets>=10.4 (from uvicorn[standard]==0.27.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 3))
  Using cached websockets-16.0-cp314-cp314-win_amd64.whl.metadata (7.0 kB)
Collecting iniconfig (from pytest>=7.4.4->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 52))
  Using cached iniconfig-2.3.0-py3-none-any.whl.metadata (2.5 kB)
Collecting pluggy<2.0,>=0.12 (from pytest>=7.4.4->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 52))
  Using cached pluggy-1.6.0-py3-none-any.whl.metadata (4.8 kB)
Collecting amqp<6.0.0,>=5.1.1 (from kombu<6.0,>=5.3.4->celery==5.3.6->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 32))
  Using cached amqp-5.3.1-py3-none-any.whl.metadata (8.9 kB)
Collecting wcwidth (from prompt-toolkit<3.1.0,>=3.0.41->ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading wcwidth-0.8.2-py3-none-any.whl.metadata (43 kB)
Requirement already satisfied: pycparser in C:\Python314\Lib\site-packages (from cffi>=0.6->weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45)) (3.0)
Collecting webencodings (from cssselect2>=0.1->weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading webencodings-0.5.1-py2.py3-none-any.whl.metadata (2.1 kB)
Collecting brotli>=1.0.1 (from fonttools[woff]>=4.0.0->weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading brotli-1.2.0-cp314-cp314-win_amd64.whl.metadata (6.3 kB)
Collecting zopfli>=0.1.4 (from fonttools[woff]>=4.0.0->weasyprint==61.0->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 45))
  Downloading zopfli-0.4.3-cp310-abi3-win_amd64.whl.metadata (3.6 kB)
Collecting parso<0.9.0,>=0.8.6 (from jedi>=0.16->ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading parso-0.8.7-py2.py3-none-any.whl.metadata (8.2 kB)
Collecting distlib<1,>=0.3.7 (from virtualenv>=20.10.0->pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Downloading distlib-0.4.3-py2.py3-none-any.whl.metadata (5.3 kB)
Collecting filelock<4,>=3.24.2 (from virtualenv>=20.10.0->pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Using cached filelock-3.29.5-py3-none-any.whl.metadata (2.0 kB)
Collecting python-discovery>=1.4.2 (from virtualenv>=20.10.0->pre-commit==3.6.0->-r .\requirements-dev.txt (line 8))
  Downloading python_discovery-1.4.3-py3-none-any.whl.metadata (5.6 kB)
Requirement already satisfied: MarkupSafe>=0.9.2 in C:\Python314\Lib\site-packages (from Mako->alembic==1.13.1->-r D:\MisProyectos\exSoftOptic\backend\requirements.txt (line 9)) (3.0.3)
Collecting executing>=1.2.0 (from stack-data->ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading executing-2.2.1-py2.py3-none-any.whl.metadata (8.9 kB)
Collecting asttokens>=2.1.0 (from stack-data->ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading asttokens-3.0.1-py3-none-any.whl.metadata (4.9 kB)
Collecting pure-eval (from stack-data->ipython==8.21.0->-r .\requirements-dev.txt (line 5))
  Downloading pure_eval-0.2.3-py3-none-any.whl.metadata (6.3 kB)
Downloading fastapi-0.110.0-py3-none-any.whl (92 kB)
Downloading pydantic-2.6.1-py3-none-any.whl (394 kB)
Downloading uvicorn-0.27.1-py3-none-any.whl (60 kB)
Using cached python_multipart-0.0.9-py3-none-any.whl (22 kB)
Downloading SQLAlchemy-2.0.27-py3-none-any.whl (1.9 MB)
   ---------------------------------------- 1.9/1.9 MB 7.9 MB/s  0:00:00
Downloading alembic-1.13.1-py3-none-any.whl (233 kB)
Downloading motor-3.3.2-py3-none-any.whl (70 kB)
Downloading redis-5.0.1-py3-none-any.whl (250 kB)
Downloading aioredis-2.0.1-py3-none-any.whl (71 kB)
Using cached python_jose-3.3.0-py2.py3-none-any.whl (33 kB)
Using cached passlib-1.7.4-py2.py3-none-any.whl (525 kB)
Downloading bcrypt-4.1.2-cp39-abi3-win_amd64.whl (158 kB)
Downloading pydantic_settings-2.1.0-py3-none-any.whl (11 kB)
Downloading email_validator-2.1.0.post1-py3-none-any.whl (32 kB)
Downloading celery-5.3.6-py3-none-any.whl (422 kB)
Using cached httpx-0.27.0-py3-none-any.whl (75 kB)
Downloading python_dotenv-1.0.1-py3-none-any.whl (19 kB)
Downloading structlog-24.1.0-py3-none-any.whl (65 kB)
Downloading loguru-0.7.2-py3-none-any.whl (62 kB)
Downloading python_dateutil-2.8.2-py2.py3-none-any.whl (247 kB)
Downloading reportlab-4.1.0-py3-none-any.whl (1.9 MB)
   ---------------------------------------- 1.9/1.9 MB 4.3 MB/s  0:00:00
Downloading weasyprint-61.0-py3-none-any.whl (271 kB)
Downloading openpyxl-3.1.2-py2.py3-none-any.whl (249 kB)
Downloading pytest_asyncio-0.23.4-py3-none-any.whl (17 kB)
Downloading pytest_cov-4.1.0-py3-none-any.whl (21 kB)
Downloading factory_boy-3.3.0-py2.py3-none-any.whl (36 kB)
Downloading black-24.1.1-py3-none-any.whl (195 kB)
Downloading isort-5.13.2-py3-none-any.whl (92 kB)
Downloading flake8-7.0.0-py2.py3-none-any.whl (57 kB)
Downloading mypy-1.8.0-py3-none-any.whl (2.6 MB)
   ---------------------------------------- 2.6/2.6 MB 4.6 MB/s  0:00:00
Downloading ipython-8.21.0-py3-none-any.whl (810 kB)
   ---------------------------------------- 810.0/810.0 kB 4.9 MB/s  0:00:00
Downloading ipdb-0.13.13-py3-none-any.whl (12 kB)
Downloading pre_commit-3.6.0-py2.py3-none-any.whl (204 kB)
Downloading debugpy-1.8.1-py2.py3-none-any.whl (4.8 MB)
   ---------------------------------------- 4.8/4.8 MB 5.1 MB/s  0:00:00
Downloading pytest-7.4.4-py3-none-any.whl (325 kB)
Using cached billiard-4.2.4-py3-none-any.whl (87 kB)
Downloading click-8.4.2-py3-none-any.whl (119 kB)
Using cached kombu-5.6.2-py3-none-any.whl (214 kB)
Using cached vine-5.1.0-py3-none-any.whl (9.6 kB)
Using cached amqp-5.3.1-py3-none-any.whl (50 kB)
Using cached mccabe-0.7.0-py2.py3-none-any.whl (7.3 kB)
Using cached pluggy-1.6.0-py3-none-any.whl (20 kB)
Using cached prompt_toolkit-3.0.52-py3-none-any.whl (391 kB)
Downloading pycodestyle-2.11.1-py2.py3-none-any.whl (31 kB)
Downloading pyflakes-3.2.0-py2.py3-none-any.whl (62 kB)
Downloading starlette-0.36.3-py3-none-any.whl (71 kB)
Downloading cfgv-3.5.0-py2.py3-none-any.whl (7.4 kB)
Using cached click_didyoumean-0.3.1-py3-none-any.whl (3.6 kB)
Using cached click_plugins-1.1.1.2-py2.py3-none-any.whl (11 kB)
Using cached click_repl-0.3.0-py3-none-any.whl (10 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Downloading coverage-7.15.0-cp314-cp314-win_amd64.whl (223 kB)
Downloading cssselect2-0.9.0-py3-none-any.whl (15 kB)
Using cached ecdsa-0.19.2-py2.py3-none-any.whl (150 kB)
Downloading faker-40.28.1-py3-none-any.whl (2.1 MB)
   ---------------------------------------- 2.1/2.1 MB 3.9 MB/s  0:00:00
Downloading fonttools-4.63.0-cp314-cp314-win_amd64.whl (2.3 MB)
   ---------------------------------------- 2.3/2.3 MB 4.1 MB/s  0:00:00
Downloading brotli-1.2.0-cp314-cp314-win_amd64.whl (375 kB)
Downloading greenlet-3.5.3-cp314-cp314-win_amd64.whl (240 kB)
Downloading html5lib-1.1-py2.py3-none-any.whl (112 kB)
Downloading httptools-0.8.0-cp314-cp314-win_amd64.whl (92 kB)
Downloading identify-2.6.19-py2.py3-none-any.whl (99 kB)
Downloading jedi-0.20.0-py2.py3-none-any.whl (4.9 MB)
   ---------------------------------------- 4.9/4.9 MB 4.4 MB/s  0:00:01
Downloading parso-0.8.7-py2.py3-none-any.whl (107 kB)
Downloading mypy_extensions-1.1.0-py3-none-any.whl (5.0 kB)
Downloading nodeenv-1.10.0-py2.py3-none-any.whl (23 kB)
Using cached packaging-26.2-py3-none-any.whl (100 kB)
Downloading pathspec-1.1.1-py3-none-any.whl (57 kB)
Downloading pillow-12.3.0-cp314-cp314-win_amd64.whl (7.2 MB)
   ---------------------------------------- 7.2/7.2 MB 4.8 MB/s  0:00:01
Using cached platformdirs-4.10.0-py3-none-any.whl (22 kB)
Downloading pydyf-0.12.1-py3-none-any.whl (8.0 kB)
Using cached pygments-2.20.0-py3-none-any.whl (1.2 MB)
Downloading pyphen-0.17.2-py3-none-any.whl (2.1 MB)
   ---------------------------------------- 2.1/2.1 MB 3.6 MB/s  0:00:00
Downloading pytz-2026.2-py2.py3-none-any.whl (510 kB)
Using cached pyyaml-6.0.3-cp314-cp314-win_amd64.whl (156 kB)
Using cached six-1.17.0-py2.py3-none-any.whl (11 kB)
Downloading tinycss2-1.5.1-py3-none-any.whl (28 kB)
Downloading traitlets-5.15.1-py3-none-any.whl (85 kB)
Using cached tzdata-2026.2-py2.py3-none-any.whl (349 kB)
Downloading virtualenv-21.5.1-py3-none-any.whl (4.6 MB)
   ---------------------------------------- 4.6/4.6 MB 2.4 MB/s  0:00:01
Downloading distlib-0.4.3-py2.py3-none-any.whl (470 kB)
Using cached filelock-3.29.5-py3-none-any.whl (45 kB)
Downloading python_discovery-1.4.3-py3-none-any.whl (33 kB)
Downloading watchdog-6.0.0-py3-none-win_amd64.whl (79 kB)
Downloading watchfiles-1.2.0-cp314-cp314-win_amd64.whl (288 kB)
Downloading webencodings-0.5.1-py2.py3-none-any.whl (11 kB)
Using cached websockets-16.0-cp314-cp314-win_amd64.whl (178 kB)
Using cached win32_setctime-1.2.0-py3-none-any.whl (4.1 kB)
Downloading zopfli-0.4.3-cp310-abi3-win_amd64.whl (288 kB)
Downloading async_timeout-5.0.1-py3-none-any.whl (6.2 kB)
Using cached chardet-7.4.3-cp314-cp314-win_amd64.whl (939 kB)
Downloading decorator-5.3.1-py3-none-any.whl (10 kB)
Using cached et_xmlfile-2.0.0-py3-none-any.whl (18 kB)
Using cached iniconfig-2.3.0-py3-none-any.whl (7.5 kB)
Using cached mako-1.3.12-py3-none-any.whl (78 kB)
Downloading matplotlib_inline-0.2.2-py3-none-any.whl (9.5 kB)
Using cached pyasn1-0.6.3-py3-none-any.whl (83 kB)
Using cached rsa-4.9.1-py3-none-any.whl (34 kB)
Using cached sniffio-1.3.1-py3-none-any.whl (10 kB)
Downloading stack_data-0.6.3-py3-none-any.whl (24 kB)
Downloading asttokens-3.0.1-py3-none-any.whl (27 kB)
Downloading executing-2.2.1-py2.py3-none-any.whl (28 kB)
Downloading pure_eval-0.2.3-py3-none-any.whl (11 kB)
Downloading wcwidth-0.8.2-py3-none-any.whl (323 kB)
Building wheels for collected packages: asyncpg, psycopg2-binary, pymongo, pandas, pytest-watch, pydantic-core, docopt
  Building wheel for asyncpg (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for asyncpg (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [283 lines of output]
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-7z_8fmhy\overlay\Lib\site-packages\setuptools\config\_apply_pyprojecttoml.py:82: SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
      !!

              ********************************************************************************
              Please use a simple string containing a SPDX expression for `project.license`. You can also use `project.license-files`. (Both options available on setuptools>=77.0.0).

              By 2027-Feb-18, you need to update your project and remove deprecated calls
              or your builds will no longer be supported.

              See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
              ********************************************************************************

      !!
        corresp(dist, value, root_dir)
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-7z_8fmhy\overlay\Lib\site-packages\setuptools\config\_apply_pyprojecttoml.py:61: SetuptoolsDeprecationWarning: License classifiers are deprecated.
      !!

              ********************************************************************************
              Please consider removing the following classifiers in favor of a SPDX license expression:

              License :: OSI Approved :: Apache Software License

              See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
              ********************************************************************************

      !!
        dist._finalize_license_expression()
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-7z_8fmhy\overlay\Lib\site-packages\setuptools\dist.py:765: SetuptoolsDeprecationWarning: License classifiers are deprecated.
      !!

              ********************************************************************************
              Please consider removing the following classifiers in favor of a SPDX license expression:

              License :: OSI Approved :: Apache Software License

              See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
              ********************************************************************************

      !!
        self._finalize_license_expression()
      running bdist_wheel
      running build
      running build_py
      creating build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\cluster.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\compat.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\connection.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\connect_utils.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\connresource.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\cursor.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\introspection.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\pool.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\prepared_stmt.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\serverversion.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\transaction.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\types.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\utils.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\_asyncio_compat.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\_version.py -> build\lib.win-amd64-cpython-314\asyncpg
      copying asyncpg\__init__.py -> build\lib.win-amd64-cpython-314\asyncpg
      creating build\lib.win-amd64-cpython-314\asyncpg\exceptions
      copying asyncpg\exceptions\_base.py -> build\lib.win-amd64-cpython-314\asyncpg\exceptions
      copying asyncpg\exceptions\__init__.py -> build\lib.win-amd64-cpython-314\asyncpg\exceptions
      creating build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\types.py -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\__init__.py -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      creating build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\__init__.py -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      creating build\lib.win-amd64-cpython-314\asyncpg\_testbase
      copying asyncpg\_testbase\fuzzer.py -> build\lib.win-amd64-cpython-314\asyncpg\_testbase
      copying asyncpg\_testbase\__init__.py -> build\lib.win-amd64-cpython-314\asyncpg\_testbase
      creating build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\__init__.py -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      running egg_info
      writing asyncpg.egg-info\PKG-INFO
      writing dependency_links to asyncpg.egg-info\dependency_links.txt
      writing requirements to asyncpg.egg-info\requires.txt
      writing top-level names to asyncpg.egg-info\top_level.txt
      reading manifest file 'asyncpg.egg-info\SOURCES.txt'
      reading manifest template 'MANIFEST.in'
      warning: no files found matching '*.py' under directory 'examples'
      adding license file 'LICENSE'
      adding license file 'AUTHORS'
      writing manifest file 'asyncpg.egg-info\SOURCES.txt'
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-7z_8fmhy\overlay\Lib\site-packages\setuptools\command\build_py.py:215: _Warning: Package 'asyncpg.pgproto' is absent from the `packages` configuration.
      !!

              ********************************************************************************
              ############################
              # Package would be ignored #
              ############################
              Python recognizes 'asyncpg.pgproto' as an importable package[^1],
              but it is absent from setuptools' `packages` configuration.

              This leads to an ambiguous overall configuration. If you want to distribute this
              package, please make sure that 'asyncpg.pgproto' is explicitly added
              to the `packages` configuration field.

              Alternatively, you can also rely on setuptools' discovery methods
              (for example by using `find_namespace_packages(...)`/`find_namespace:`
              instead of `find_packages(...)`/`find:`).

              You can read more about "package discovery" on setuptools documentation page:

              - https://setuptools.pypa.io/en/latest/userguide/package_discovery.html

              If you don't want 'asyncpg.pgproto' to be distributed and are
              already explicitly excluding 'asyncpg.pgproto' via
              `find_namespace_packages(...)/find_namespace` or `find_packages(...)/find`,
              you can try to use `exclude_package_data`, or `include-package-data=False` in
              combination with a more fine grained `package-data` configuration.

              You can read more about "package data files" on setuptools documentation page:

              - https://setuptools.pypa.io/en/latest/userguide/datafiles.html


              [^1]: For Python, any directory (with suitable naming) can be imported,
                    even if it does not contain any `.py` files.
                    On the other hand, currently there is no concept of package data
                    directory, all directories are treated like packages.
              ********************************************************************************

      !!
        check.warn(importable)
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-7z_8fmhy\overlay\Lib\site-packages\setuptools\command\build_py.py:215: _Warning: Package 'asyncpg.protocol' is absent from the `packages` configuration.
      !!

              ********************************************************************************
              ############################
              # Package would be ignored #
              ############################
              Python recognizes 'asyncpg.protocol' as an importable package[^1],
              but it is absent from setuptools' `packages` configuration.

              This leads to an ambiguous overall configuration. If you want to distribute this
              package, please make sure that 'asyncpg.protocol' is explicitly added
              to the `packages` configuration field.

              Alternatively, you can also rely on setuptools' discovery methods
              (for example by using `find_namespace_packages(...)`/`find_namespace:`
              instead of `find_packages(...)`/`find:`).

              You can read more about "package discovery" on setuptools documentation page:

              - https://setuptools.pypa.io/en/latest/userguide/package_discovery.html

              If you don't want 'asyncpg.protocol' to be distributed and are
              already explicitly excluding 'asyncpg.protocol' via
              `find_namespace_packages(...)/find_namespace` or `find_packages(...)/find`,
              you can try to use `exclude_package_data`, or `include-package-data=False` in
              combination with a more fine grained `package-data` configuration.

              You can read more about "package data files" on setuptools documentation page:

              - https://setuptools.pypa.io/en/latest/userguide/datafiles.html


              [^1]: For Python, any directory (with suitable naming) can be imported,
                    even if it does not contain any `.py` files.
                    On the other hand, currently there is no concept of package data
                    directory, all directories are treated like packages.
              ********************************************************************************

      !!
        check.warn(importable)
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-7z_8fmhy\overlay\Lib\site-packages\setuptools\command\build_py.py:215: _Warning: Package 'asyncpg.protocol.record' is absent from the `packages` configuration.
      !!

              ********************************************************************************
              ############################
              # Package would be ignored #
              ############################
              Python recognizes 'asyncpg.protocol.record' as an importable package[^1],
              but it is absent from setuptools' `packages` configuration.

              This leads to an ambiguous overall configuration. If you want to distribute this
              package, please make sure that 'asyncpg.protocol.record' is explicitly added
              to the `packages` configuration field.

              Alternatively, you can also rely on setuptools' discovery methods
              (for example by using `find_namespace_packages(...)`/`find_namespace:`
              instead of `find_packages(...)`/`find:`).

              You can read more about "package discovery" on setuptools documentation page:

              - https://setuptools.pypa.io/en/latest/userguide/package_discovery.html

              If you don't want 'asyncpg.protocol.record' to be distributed and are
              already explicitly excluding 'asyncpg.protocol.record' via
              `find_namespace_packages(...)/find_namespace` or `find_packages(...)/find`,
              you can try to use `exclude_package_data`, or `include-package-data=False` in
              combination with a more fine grained `package-data` configuration.

              You can read more about "package data files" on setuptools documentation page:

              - https://setuptools.pypa.io/en/latest/userguide/datafiles.html


              [^1]: For Python, any directory (with suitable naming) can be imported,
                    even if it does not contain any `.py` files.
                    On the other hand, currently there is no concept of package data
                    directory, all directories are treated like packages.
              ********************************************************************************

      !!
        check.warn(importable)
      copying asyncpg\pgproto\__init__.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\buffer.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\buffer.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\consts.pxi -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\cpythonx.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\debug.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\frb.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\frb.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\hton.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\pgproto.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\pgproto.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\tohex.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\pgproto\uuid.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto
      copying asyncpg\protocol\consts.pxi -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\coreproto.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\coreproto.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\cpythonx.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\encodings.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\pgtypes.pxi -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\prepared_stmt.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\prepared_stmt.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\protocol.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\protocol.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\scram.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\scram.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\settings.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      copying asyncpg\protocol\settings.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol
      creating build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\__init__.pxd -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\bits.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\bytea.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\context.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\datetime.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\float.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\geometry.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\hstore.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\int.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\json.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\jsonpath.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\misc.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\network.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\numeric.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\pg_snapshot.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\text.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\tid.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\pgproto\codecs\uuid.pyx -> build\lib.win-amd64-cpython-314\asyncpg\pgproto\codecs
      copying asyncpg\protocol\codecs\array.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\base.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\base.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\pgproto.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\range.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\record.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      copying asyncpg\protocol\codecs\textutils.pyx -> build\lib.win-amd64-cpython-314\asyncpg\protocol\codecs
      creating build\lib.win-amd64-cpython-314\asyncpg\protocol\record
      copying asyncpg\protocol\record\__init__.pxd -> build\lib.win-amd64-cpython-314\asyncpg\protocol\record
      running build_ext
      building 'asyncpg.pgproto.pgproto' extension
      creating build\temp.win-amd64-cpython-314\Release\asyncpg\pgproto
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD -IC:\Python314\include -IC:\Python314\Include "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcasyncpg/pgproto/pgproto.c /Fobuild\temp.win-amd64-cpython-314\Release\asyncpg\pgproto\pgproto.obj -O2
      pgproto.c
      asyncpg/pgproto/pgproto.c(864): warning C4996: 'Py_UNICODE': deprecated in 3.13
      asyncpg/pgproto/pgproto.c(865): warning C4996: 'Py_UNICODE': deprecated in 3.13
      asyncpg/pgproto/pgproto.c(1667): warning C4013: '_PyInterpreterState_GetConfig' sin definir; se supone que extern devuelve como resultado int
      asyncpg/pgproto/pgproto.c(1667): error C2223: el operando izquierdo de '->optimization_level' debe se¤alar a struct/union
      asyncpg/pgproto/pgproto.c(38932): warning C4013: '_PyUnicode_FastCopyCharacters' sin definir; se supone que extern devuelve como resultado int
      asyncpg/pgproto/pgproto.c(41809): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(42043): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(42239): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(42435): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(42745): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(43055): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(43289): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(43485): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(43719): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      asyncpg/pgproto/pgproto.c(43915): error C2198: '_PyLong_AsByteArray': no hay suficientes argumentos para la llamada
      error: command 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Tools\\MSVC\\14.29.30133\\bin\\HostX86\\x64\\cl.exe' failed with exit code 2
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for asyncpg
  Building wheel for psycopg2-binary (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for psycopg2-binary (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [115 lines of output]
      C:\Users\Traba\AppData\Local\Temp\pip-build-env-mbee0exw\overlay\Lib\site-packages\setuptools\dist.py:765: SetuptoolsDeprecationWarning: License classifiers are deprecated.
      !!

              ********************************************************************************
              Please consider removing the following classifiers in favor of a SPDX license expression:

              License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)

              See https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#license for details.
              ********************************************************************************

      !!
        self._finalize_license_expression()
      running bdist_wheel
      running build
      running build_py
      creating build\lib.win-amd64-cpython-314\psycopg2
      copying lib\errorcodes.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\errors.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\extensions.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\extras.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\pool.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\sql.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\tz.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\_ipaddress.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\_json.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\_range.py -> build\lib.win-amd64-cpython-314\psycopg2
      copying lib\__init__.py -> build\lib.win-amd64-cpython-314\psycopg2
      running build_ext
      building 'psycopg2._psycopg' extension
      creating build\temp.win-amd64-cpython-314\Release\psycopg
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_asis.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_asis.obj
      adapter_asis.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_binary.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_binary.obj
      adapter_binary.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_datetime.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_datetime.obj
      adapter_datetime.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_list.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_list.obj
      adapter_list.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_pboolean.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_pboolean.obj
      adapter_pboolean.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_pdecimal.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_pdecimal.obj
      adapter_pdecimal.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_pfloat.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_pfloat.obj
      adapter_pfloat.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_pint.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_pint.obj
      adapter_pint.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\adapter_qstring.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\adapter_qstring.obj
      adapter_qstring.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\aix_support.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\aix_support.obj
      aix_support.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\bytes_format.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\bytes_format.obj
      bytes_format.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\column_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\column_type.obj
      column_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\connection_int.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\connection_int.obj
      connection_int.c
      psycopg\connection_int.c(1050): warning C4996: 'PyWeakref_GetObject': deprecated in 3.13
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\connection_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\connection_type.obj
      connection_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\conninfo_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\conninfo_type.obj
      conninfo_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\cursor_int.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\cursor_int.obj
      cursor_int.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\cursor_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\cursor_type.obj
      cursor_type.c
      psycopg\cursor_type.c(782): warning C4996: 'PyWeakref_GetObject': deprecated in 3.13
      psycopg\cursor_type.c(829): warning C4996: 'PyWeakref_GetObject': deprecated in 3.13
      psycopg\cursor_type.c(914): warning C4996: 'PyWeakref_GetObject': deprecated in 3.13
      psycopg\cursor_type.c(983): warning C4996: 'PyWeakref_GetObject': deprecated in 3.13
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\diagnostics_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\diagnostics_type.obj
      diagnostics_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\error_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\error_type.obj
      error_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\green.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\green.obj
      green.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\libpq_support.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\libpq_support.obj
      libpq_support.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\lobject_int.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\lobject_int.obj
      lobject_int.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\lobject_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\lobject_type.obj
      lobject_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\microprotocols.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\microprotocols.obj
      microprotocols.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\microprotocols_proto.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\microprotocols_proto.obj
      microprotocols_proto.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\notify_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\notify_type.obj
      notify_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\pqpath.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\pqpath.obj
      pqpath.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\psycopgmodule.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\psycopgmodule.obj
      psycopgmodule.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\replication_connection_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\replication_connection_type.obj
      replication_connection_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\replication_cursor_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\replication_cursor_type.obj
      replication_cursor_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\replication_message_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\replication_message_type.obj
      replication_message_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\solaris_support.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\solaris_support.obj
      solaris_support.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\typecast.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\typecast.obj
      typecast.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\utils.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\utils.obj
      utils.c
      psycopg\utils.c(397): warning C4013: '_PyInterpreterState_Get' sin definir; se supone que extern devuelve como resultado int
      psycopg\utils.c(397): warning C4047: '==': 'int' es distinto en los niveles de direccionamiento indirecto de 'PyInterpreterState *'
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\win32_support.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\win32_support.obj
      win32_support.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\cl.exe" /c /nologo /O2 /W3 /GL /DNDEBUG /MD "-DPSYCOPG_VERSION=2.9.9 (dt dec pq3 ext lo64)" -DPSYCOPG_DEBUG=1 -DPG_VERSION_NUM=180001 -DHAVE_LO64=1 -DPSYCOPG_DEBUG=1 -IC:\Python314\include -IC:\Python314\Include -I. -IC:/PROGRA~1/POSTGR~1/18/include -IC:/PROGRA~1/POSTGR~1/18/include/server "-IC:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\include" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\ucrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\shared" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\um" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\winrt" "-IC:\Program Files (x86)\Windows Kits\10\include\10.0.26100.0\cppwinrt" /Tcpsycopg\xid_type.c /Fobuild\temp.win-amd64-cpython-314\Release\psycopg\xid_type.obj
      xid_type.c
      "C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\bin\HostX86\x64\link.exe" /nologo /INCREMENTAL:NO /LTCG /DLL /MANIFEST:EMBED,ID=2 /MANIFESTUAC:NO /LIBPATH:C:\Python314\libs /LIBPATH:C:\Python314 /LIBPATH:C:\Python314\PCbuild\amd64 /LIBPATH:C:/PROGRA~1/POSTGR~1/18/lib "/LIBPATH:C:\Program Files (x86)\Microsoft Visual Studio\2019\BuildTools\VC\Tools\MSVC\14.29.30133\lib\x64" "/LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.26100.0\ucrt\x64" "/LIBPATH:C:\Program Files (x86)\Windows Kits\10\lib\10.0.26100.0\um\x64" ws2_32.lib advapi32.lib secur32.lib libpq.lib shfolder.lib build\temp.win-amd64-cpython-314\Release\psycopg\adapter_asis.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_binary.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_datetime.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_list.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_pboolean.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_pdecimal.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_pfloat.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_pint.obj build\temp.win-amd64-cpython-314\Release\psycopg\adapter_qstring.obj build\temp.win-amd64-cpython-314\Release\psycopg\aix_support.obj build\temp.win-amd64-cpython-314\Release\psycopg\bytes_format.obj build\temp.win-amd64-cpython-314\Release\psycopg\column_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\connection_int.obj build\temp.win-amd64-cpython-314\Release\psycopg\connection_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\conninfo_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\cursor_int.obj build\temp.win-amd64-cpython-314\Release\psycopg\cursor_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\diagnostics_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\error_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\green.obj build\temp.win-amd64-cpython-314\Release\psycopg\libpq_support.obj build\temp.win-amd64-cpython-314\Release\psycopg\lobject_int.obj build\temp.win-amd64-cpython-314\Release\psycopg\lobject_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\microprotocols.obj build\temp.win-amd64-cpython-314\Release\psycopg\microprotocols_proto.obj build\temp.win-amd64-cpython-314\Release\psycopg\notify_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\pqpath.obj build\temp.win-amd64-cpython-314\Release\psycopg\psycopgmodule.obj build\temp.win-amd64-cpython-314\Release\psycopg\replication_connection_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\replication_cursor_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\replication_message_type.obj build\temp.win-amd64-cpython-314\Release\psycopg\solaris_support.obj build\temp.win-amd64-cpython-314\Release\psycopg\typecast.obj build\temp.win-amd64-cpython-314\Release\psycopg\utils.obj build\temp.win-amd64-cpython-314\Release\psycopg\win32_support.obj build\temp.win-amd64-cpython-314\Release\psycopg\xid_type.obj /OUT:build\lib.win-amd64-cpython-314\psycopg2\_psycopg.cp314-win_amd64.pyd /IMPLIB:build\temp.win-amd64-cpython-314\Release\psycopg\_psycopg.cp314-win_amd64.lib
         Creando biblioteca build\temp.win-amd64-cpython-314\Release\psycopg\_psycopg.cp314-win_amd64.lib y objeto build\temp.win-amd64-cpython-314\Release\psycopg\_psycopg.cp314-win_amd64.exp
      utils.obj : error LNK2001: s¡mbolo externo _PyInterpreterState_Get sin resolver
      build\lib.win-amd64-cpython-314\psycopg2\_psycopg.cp314-win_amd64.pyd : fatal error LNK1120: 1 externos sin resolver
      error: command 'C:\\Program Files (x86)\\Microsoft Visual Studio\\2019\\BuildTools\\VC\\Tools\\MSVC\\14.29.30133\\bin\\HostX86\\x64\\link.exe' failed with exit code 1120
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for psycopg2-binary
  Building wheel for pymongo (pyproject.toml) ... done
  Created wheel for pymongo: filename=pymongo-4.6.1-cp314-cp314-win_amd64.whl size=474499 sha256=e4414fc49a95731a2bea24ab07635c23d99167e4e41149e1d58645481b5e0479
  Stored in directory: c:\users\traba\appdata\local\pip\cache\wheels\4a\61\ed\114aad5f3fd4c7087ecbcbc1db81199d44aae45aa638a7e18f
  Building wheel for pandas (pyproject.toml) ... done
  Created wheel for pandas: filename=pandas-2.2.0-cp314-cp314-win_amd64.whl size=38999218 sha256=565e9039becdd60536117d2091628a60a1f62becc4ad0a1f9c3caa7a7297e5a0
  Stored in directory: c:\users\traba\appdata\local\pip\cache\wheels\ea\00\8a\2aa41c84691b7f391a4327869fa59d4267244da2f52a841f9d
  Building wheel for pytest-watch (pyproject.toml) ... done
  Created wheel for pytest-watch: filename=pytest_watch-4.2.0-py3-none-any.whl size=13367 sha256=be4896363f2a0f1007eaac808e9342904695f85a612c875385a611e6a337e73a
  Stored in directory: c:\users\traba\appdata\local\pip\cache\wheels\bb\b5\4e\e922d72c72d63ac09c68f8430449bdaa63477f979f2dc6b8e9
  Building wheel for pydantic-core (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for pydantic-core (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [137 lines of output]
      Python reports SOABI: cp314-win_amd64
      Computed rustc target triple: x86_64-pc-windows-msvc
      Installation directory: C:\Users\Traba\AppData\Local\puccinialin\puccinialin\Cache
      Rustup already downloaded
      Installing rust to C:\Users\Traba\AppData\Local\puccinialin\puccinialin\Cache\rustup
      warn: It looks like you have an existing rustup settings file at:
      warn: C:\Users\Traba\AppData\Local\puccinialin\puccinialin\Cache\rustup\settings.toml
      warn: Rustup will install the default toolchain as specified in the settings file,
      warn: instead of the one inferred from the default host triple.
      info: profile set to minimal
      info: setting default host triple to x86_64-pc-windows-msvc
      warn: Updating existing toolchain, profile choice will be ignored
      info: syncing channel updates for stable-x86_64-pc-windows-msvc
      info: default toolchain set to stable-x86_64-pc-windows-msvc
      Checking if cargo is installed
      cargo 1.96.1 (356927216 2026-06-26)
      Rust not found, installing into a temporary directory
      Running `maturin pep517 build-wheel -i C:\Python314\python.exe --compatibility off`
      ðŸ“¦ Including license file `LICENSE`
      ðŸ\x8d¹ Building a mixed python/rust project
      ðŸ\x90\x8d Found CPython 3.14 at C:\Python314\python.exe
      ðŸ”— Found pyo3 bindings
      ðŸ“¡ Using build options features, bindings from pyproject.toml
         Compiling autocfg v1.1.0
         Compiling proc-macro2 v1.0.76
         Compiling target-lexicon v0.12.9
         Compiling unicode-ident v1.0.10
         Compiling cc v1.0.79
         Compiling once_cell v1.18.0
         Compiling cfg-if v1.0.0
         Compiling version_check v0.9.4
         Compiling quote v1.0.35
         Compiling python3-dll-a v0.2.9
         Compiling syn v2.0.48
         Compiling static_assertions v1.1.0
         Compiling windows_x86_64_msvc v0.48.0
         Compiling heck v0.4.1
         Compiling pyo3-build-config v0.20.2
         Compiling lexical-util v0.8.5
         Compiling ahash v0.8.7
         Compiling num-traits v0.2.16
         Compiling getrandom v0.2.10
         Compiling lock_api v0.4.10
         Compiling num-integer v0.1.45
         Compiling pyo3-ffi v0.20.2
         Compiling parking_lot_core v0.9.8
         Compiling rustversion v1.0.13
         Compiling libc v0.2.147
         Compiling zerocopy v0.7.32
         Compiling windows-targets v0.48.1
         Compiling memoffset v0.9.0
         Compiling num-bigint v0.4.4
         Compiling smallvec v1.11.2
         Compiling scopeguard v1.1.0
         Compiling tinyvec_macros v0.1.1
         Compiling allocator-api2 v0.2.16
         Compiling tinyvec v1.6.0
         Compiling hashbrown v0.14.3
         Compiling pyo3-macros-backend v0.20.2
         Compiling pyo3 v0.20.2
         Compiling lexical-parse-integer v0.8.6
         Compiling lexical-write-integer v0.8.5
         Compiling serde v1.0.195
         Compiling memchr v2.6.3
         Compiling lexical-write-float v0.8.5
         Compiling strum_macros v0.25.3
         Compiling aho-corasick v1.0.2
         Compiling lexical-parse-float v0.8.5
         Compiling pyo3-macros v0.20.2
         Compiling unicode-normalization v0.1.22
         Compiling parking_lot v0.12.1
         Compiling serde_derive v1.0.195
         Compiling unicode-bidi v0.3.13
         Compiling indoc v2.0.4
         Compiling serde_json v1.0.109
         Compiling unindent v0.2.3
         Compiling equivalent v1.0.1
         Compiling regex-syntax v0.8.2
         Compiling percent-encoding v2.3.1
         Compiling indexmap v2.0.0
         Compiling form_urlencoded v1.2.1
         Compiling idna v0.5.0
         Compiling regex-automata v0.4.3
         Compiling strum v0.25.0
         Compiling lexical-core v0.8.5
         Compiling pydantic-core v2.16.2 (C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5)
         Compiling itoa v1.0.8
         Compiling ryu v1.0.14
      error: failed to run custom build command for `pydantic-core v2.16.2 (C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5)`

      Caused by:
        process didn't exit successfully: `C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\target\release\build\pydantic-core-e76f326e8a45bade\build-script-build` (exit code: 101)
        --- stdout
        cargo:rustc-cfg=Py_3_6
        cargo:rustc-cfg=Py_3_7
        cargo:rustc-cfg=Py_3_8
        cargo:rustc-cfg=Py_3_9
        cargo:rustc-cfg=Py_3_10
        cargo:rustc-cfg=Py_3_11
        cargo:rustc-cfg=Py_3_12
        cargo:rustc-cfg=Py_3_13
        cargo:rustc-cfg=Py_3_14
        cargo:rerun-if-changed=python/pydantic_core/core_schema.py
        cargo:rerun-if-changed=generate_self_schema.py

        --- stderr
        Traceback (most recent call last):
          File "C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\generate_self_schema.py", line 192, in eval_forward_ref
            return type_._evaluate(core_schema.__dict__, None, set())
                   ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'

        During handling of the above exception, another exception occurred:

        Traceback (most recent call last):
          File "C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\generate_self_schema.py", line 240, in <module>
            main()
            ~~~~^^
          File "C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\generate_self_schema.py", line 210, in main
            value = get_schema(s, definitions)
          File "C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\generate_self_schema.py", line 54, in get_schema
            return type_dict_schema(obj, definitions)
          File "C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\generate_self_schema.py", line 152, in type_dict_schema
            field_type = eval_forward_ref(field_type)
          File "C:\Users\Traba\AppData\Local\Temp\pip-install-pzwfz2ku\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\generate_self_schema.py", line 195, in eval_forward_ref
            return type_._evaluate(core_schema.__dict__, None)
                   ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'

        thread 'main' (20068) panicked at build.rs:29:9:
        generate_self_schema.py failed with exit code: 1
        note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
      warning: build failed, waiting for other jobs to finish...
      ðŸ’¥ maturin failed
        Caused by: Failed to build a native library through cargo
        Caused by: Cargo build finished with "exit code: 101": `"cargo" "rustc" "--profile" "release" "--features" "pyo3/extension-module" "--message-format" "json-render-diagnostics" "--manifest-path" "C:\\Users\\Traba\\AppData\\Local\\Temp\\pip-install-pzwfz2ku\\pydantic-core_f4b3e98e6cd54ad49e80f8d61dc197d5\\Cargo.toml" "--lib" "--crate-type" "cdylib"`
      Error: command ['maturin', 'pep517', 'build-wheel', '-i', 'C:\\Python314\\python.exe', '--compatibility', 'off'] returned non-zero exit status 1
      [end of output]

  note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for pydantic-core
  Building wheel for docopt (pyproject.toml) ... done
  Created wheel for docopt: filename=docopt-0.6.2-py2.py3-none-any.whl size=13887 sha256=338748776eb0216efbea23067b5402f6c5a9d933fd1aca7a3b48f0b871600643
  Stored in directory: c:\users\traba\appdata\local\pip\cache\wheels\79\6f\5f\26c3d1a144117ef52122d67c32b9f3c297c3dec4fea00a31ac
Successfully built pymongo pandas pytest-watch docopt
Failed to build asyncpg psycopg2-binary pydantic-core

[notice] A new release of pip is available: 25.2 -> 26.1.2
[notice] To update, run: python.exe -m pip install --upgrade pip
error: failed-wheel-build-for-install

× Failed to build installable wheels for some pyproject.toml based projects
╰─> asyncpg, psycopg2-binary, pydantic-core