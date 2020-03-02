import subprocess
import asyncio
from vosekast_control.main import main


def backend():
    asyncio.run(main())


def frontend():
    subprocess.call('cd frontend && yarn start', shell=True)


def dev():
    print("Start vosekast in dev mode:")

    frontend()
    backend()


def dev_backend():
    print("Start the backend alone:")

    backend()


def dev_frontend():
    print("Start the frontend standalone:")
    frontend()
