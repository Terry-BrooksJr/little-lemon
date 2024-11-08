from invoke import task, Collection
from invoke.watchers import FailingResponder, Responder
import os


@task()
def start(ctx, port, workers, threads, log_level="INFO"):
    ctx.run(f'doppler run -- gunicorn --workers {workers} --threads {threads} --log-level {log_level}  --env DJANGO_SETTINGS_MODULE=little_lemon.settings little_lemon.wsgi  -b :{port} ')

@task()
def update_schema_from_models(ctx):
    ctx.run("doppler run -- python manage.py makemigrations")

@task(pre=update_schema_from_models)
def update_db(ctx):
    ctx.run("doppler run -- python manage.py migrate")

@task(default=True)
def dev_run(ctx, port=8000):
    ctx.run(f'doppler run -- python manage.py runserver {port} ')

@task
def test(ctx):
    ctx.run("doppler run -- python manage.py test --keepdb")


@task
def sync(ctx, dry_run=False):
    if not dry_run:
        ctx.run("doppler run -- poetry install --sync")
    if dry_run:
      ctx.run("doppler run -- poetry install --sync --dry-run")
  
    ctx.run("pip freeze > ../requirements.txt")

@task
def uncache(ctx):
    ctx.run("doppler run -- python manage.py invalidate_cachalot")


@task(help={'file': "path to Dockerfile", "platform":"Set target platform for build"})
def build_docker_image(ctx, file,doppler_token=os.getenv('DOPPLER_TOKEN'), platform="linux/amd64"):
    ctx.run(f"docker buildx build --push -t little-lemon:latest  --file {file} --platform {platform} --build-arg=DOPPLER_TOKEN={doppler_token} .")

@task
def install_redis_cli(ctx):
    signMeIn = FailingResponder(
        pattern=r"Password:\s",
        response="M0rdS1th",
    )    
    ctx.sudo('npm install -g redis-cli', watchers=[signMeIn] )
    
    
@task(install_redis_cli)
def set_redis_users(ctx, username, password, host, identity):
    redis = Responder(
        pattern=r"dragonfly.yo-momma.net:6379>",
        response=f"ACL SETUSER {username} on >{password} allkeys +@all"
    )
    ctx.run("rdcli -h {host} -a {identity} -p 6379", pty=True, watchers=[redis]) 


@task
def  schema_check(ctx):
    ctx.run("doppler run -- python manage.py schema --check")
