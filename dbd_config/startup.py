import os
from pathlib import Path


_MIGRATIONS_APPLIED = False


def _env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _should_apply_startup_migrations():
    if _env_bool("DISABLE_STARTUP_MIGRATIONS", default=False):
        return False
    return _env_bool("AUTO_APPLY_MIGRATIONS", default=_env_bool("RENDER", default=False))


def _acquire_lock(lock_file):
    if os.name == "nt":
        import msvcrt

        lock_file.seek(0)
        lock_file.write("1")
        lock_file.flush()
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_LOCK, 1)
        return

    import fcntl

    fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)


def _release_lock(lock_file):
    if os.name == "nt":
        import msvcrt

        lock_file.seek(0)
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_UNLCK, 1)
        return

    import fcntl

    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def apply_startup_migrations():
    global _MIGRATIONS_APPLIED

    if _MIGRATIONS_APPLIED or not _should_apply_startup_migrations():
        return

    lock_path = Path(os.getenv("STARTUP_MIGRATION_LOCKFILE", "/tmp/dbd-startup-migrate.lock"))
    lock_path.parent.mkdir(parents=True, exist_ok=True)

    with lock_path.open("a+", encoding="utf-8") as lock_file:
        _acquire_lock(lock_file)
        try:
            if _MIGRATIONS_APPLIED:
                return

            from django.core.management import call_command

            call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
            _MIGRATIONS_APPLIED = True
        finally:
            _release_lock(lock_file)
