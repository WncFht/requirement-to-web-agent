"""Separate first-run platform scaffolds from trusted compiler output."""

from contextlib import contextmanager
from pathlib import Path
import shutil
import sys
from tempfile import mkdtemp

LOCK = ".arc-generation.lock"
MANAGED = (
    ".arc/pipeline_state.json",
    ".arc/agent",
    ".arc/project/report.json",
    ".arc/requirements.json",
    ".arc/db_schema.json",
    ".arc/backend_tdd.json",
    ".arc/ui_design.json",
)


def publish(application, output, backup):
    """Replace an initial scaffold without deleting its files; roll back a failed move.

    The output directory itself stays in place (it can be a platform mount).
    A platform Git directory stays in place too. Other previous entries move to
    the external backup so a successful seal describes exactly the new app.
    """
    previous, installed = [], []
    try:
        for path in sorted(output.iterdir()):
            if path.name in {LOCK, ".git"}:
                continue
            shutil.move(str(path), str(backup / path.name))
            previous.append(path.name)
        for path in sorted(application.iterdir()):
            shutil.move(str(path), str(output / path.name))
            installed.append(path.name)
    except BaseException:
        for name in reversed(installed):
            shutil.move(str(output / name), str(application / name))
        for name in reversed(previous):
            shutil.move(str(backup / name), str(output / name))
        raise


@contextmanager
def application_output(output, *, inputs, source, resume=False):
    """Yield a clean first-run workspace, or the unchanged managed resume target.

    An unmanaged, populated platform destination is not an old checkpoint.
    Generate separately and publish only on success. Keep both failure evidence
    and the untouched initial scaffold if generation fails. Existing compiler
    state is never adopted as a new run or deleted to make it pass.
    """
    output, inputs, source = (
        Path(output),
        Path(inputs).resolve(),
        Path(source).resolve(),
    )
    if output.is_symlink():
        raise ValueError("Output directory cannot be a symlink")
    output = output.resolve()
    if (
        output == inputs
        or output.is_relative_to(inputs)
        or inputs.is_relative_to(output)
        or output == source
        or source.is_relative_to(output)
    ):
        raise ValueError(
            "Output directory must not overlap inputs or contain the agent source"
        )
    if output.exists() and not output.is_dir():
        raise ValueError("Output must be a directory")
    if (output / ".arc").is_symlink():
        raise ValueError("Compiler metadata directory cannot be a symlink")
    if (output / LOCK).exists():
        raise ValueError(
            "Output generation lock exists; check for an active or interrupted writer"
        )
    if resume:
        yield output
        return
    if any(
        (output / name).exists() or (output / name).is_symlink() for name in MANAGED
    ):
        raise ValueError(
            "Existing compiler output is preserved; use --resume for identical legacy work or choose a new output"
        )
    if not output.exists() or not any(
        path.name != "node_modules" for path in output.iterdir()
    ):
        yield output
        return

    # The workspace lives outside the target, including on generation failure.
    # shutil.move also supports /tmp and the target being on different mounts.
    lock = output / LOCK
    with lock.open("x"):
        pass
    workspace = None
    try:
        workspace = Path(mkdtemp(prefix="arc-generation-"))
        application, backup = workspace / "application", workspace / "previous-output"
        application.mkdir()
        backup.mkdir()
        dependencies = output / "node_modules"
        if dependencies.is_symlink():
            raise ValueError("Initial node_modules cannot be a symlink")
        if dependencies.exists():
            # Copy, not link: npm must not mutate the initial destination on failure.
            shutil.copytree(dependencies, application / "node_modules", symlinks=True)
        print(
            f"Initial platform output detected; generating in {application}", flush=True
        )
        yield application
        if not all(
            (application / name).is_file() for name in ("package.json", "deploy.sh")
        ) or not all((application / name).is_dir() for name in ("frontend", "backend")):
            raise ValueError(
                "Generated application lacks package.json, deploy.sh, frontend or backend"
            )
        publish(application, output, backup)
        print(
            f"Application published at {output}; initial files retained at {backup}",
            flush=True,
        )
        application.rmdir()
    except BaseException:
        if workspace is not None:
            print(
                f"Generation/publication failed; work and original-file backup retained at {workspace}",
                file=sys.stderr,
                flush=True,
            )
        raise
    finally:
        lock.unlink(missing_ok=True)
