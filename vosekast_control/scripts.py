import subprocess
import asyncio
from main import main
import os


def backend(emulate=False):
    asyncio.run(main(emulate=emulate))


def frontend():
    subprocess.call('cd frontend && yarn start', shell=True)


def build():
    print("Build frontend for app:")
    subprocess.call('cd frontend && yarn build', shell=True)


def start():
    print("Start vosekast in production mode:")
    backend()


def dev():
    print("Start vosekast in dev mode:")
    frontend()
    backend(emulate=True)


def dev_backend():
    print("Start the backend alone:")
    backend(emulate=True)


def dev_frontend():
    print("Start the frontend standalone:")
    frontend()
