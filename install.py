"""Portable public installer. Uses only local game files and bundled patch data."""
import base64
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import lz4.frame

HOME = Path(__file__).resolve().parent
GAME = HOME.parent


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def payload(home):
    return json.loads(gzip.decompress((home / 'patches.json.gz').read_bytes()))


def game_idle():
    p = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq GoWR.exe', '/FO', 'CSV', '/NH'],
                       capture_output=True, text=True, check=True, creationflags=0x08000000)
    require('"gowr.exe"' not in p.stdout.lower(), 'Close the game before installing or uninstalling.')


def target(game, name, spec):
    path = (game / spec['directory'] / name).resolve()
    require(path.is_relative_to(game.resolve()), 'Invalid path in the package.')
    return path


def executable_version(path):
    # Read the fixed numeric file version, not the localized FileVersion text
    # (GoWR's text is "0,0,0,0"). Windows PowerShell is available on supported
    # systems and avoids adding ctypes/native DLLs to our portable Python.
    # Pass the path as data, never interpolate it into PowerShell source.
    env = os.environ.copy()
    env['KRATOS_ONLY_VERSION_EXE'] = str(path.resolve())
    powershell = Path(env.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    script = (
        "$ErrorActionPreference = 'Stop'; "
        "$v = [System.Diagnostics.FileVersionInfo]::GetVersionInfo($env:KRATOS_ONLY_VERSION_EXE); "
        "'{0}.{1}.{2}.{3}' -f $v.FileMajorPart, $v.FileMinorPart, $v.FileBuildPart, $v.FilePrivatePart"
    )
    message = ('Could not read GoWR.exe version information. Windows PowerShell and valid '
               'executable version metadata are required. No files were changed.')
    try:
        result = subprocess.run([str(powershell), '-NoLogo', '-NoProfile', '-NonInteractive',
                                 '-Command', script], env=env, capture_output=True, text=True,
                                timeout=20, creationflags=0x08000000)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise RuntimeError(message) from error
    parts = result.stdout.strip().split('.')
    require(result.returncode == 0 and len(parts) == 4 and
            all(p.isascii() and p.isdecimal() and 0 <= int(p) <= 65535 for p in parts), message)
    version = tuple(map(int, parts))
    require(any(version), 'GoWR.exe has no usable numeric file version. No files were changed.')
    return version


def check_game(game, pack):
    require((game / 'GoWR.exe').is_file(),
            'Extract the KratosOnly folder into the game folder, next to GoWR.exe.')
    detected = executable_version(game / 'GoWR.exe')
    supported = [tuple(v) for v in pack['exe_file_versions']]
    label = '.'.join(map(str, detected))
    require(detected in supported,
            'Unsupported game build: detected ' + label + '; supported: ' +
            ', '.join('.'.join(map(str, v)) for v in supported) + '. No files were changed.')
    print('Game executable version: ' + label, flush=True)
    require(file_hash(game / 'exec/dc/pc_le/quests_main.dcb') == pack['quests_sha256'],
            'Incompatible quest database: quests_main.dcb. The executable version matches, '
            'but this game data is not supported. No files were changed.')


def make_patched(raw, spec):
    require(lz4.frame.get_frame_info(raw)['content_size'] == spec['decoded_size'],
            'Incompatible file size.')
    decoded, used = lz4.frame.decompress(raw, return_bytes_read=True)
    require(used == len(raw) and digest(decoded) in spec['input_decoded_sha256'],
            'File modified by another mod, or incompatible game version.')
    data = bytearray(decoded)
    last = 0
    for offset, encoded in spec['patches']:
        change = base64.b64decode(encoded, validate=True)
        require(last <= offset <= len(data) - len(change), 'Invalid patch range.')
        data[offset:offset + len(change)] = change
        last = offset + len(change)
    require(digest(data) == spec['output_decoded_sha256'], 'Patch validation failed.')
    packed = lz4.frame.compress(bytes(data), compression_level=0, store_size=True, **spec['frame'])
    require(digest(packed) == spec['output_sha256'], 'Output does not match the validated version.')
    return packed


def install(game=GAME, home=HOME):
    game_idle()
    pack = payload(home)
    check_game(game, pack)
    state_path = home / 'installation.json'
    state = json.loads(state_path.read_text(encoding='utf-8')) if state_path.exists() else None
    if state:
        require(state['version'] in [pack['version'], *pack.get('compatible_installed_versions', [])]
                and state['game'] == str(game.resolve()),
                'Backup belongs to another installation. Use the original mod folder.')
        require(set(state['assets']) == set(pack['assets']), 'Incomplete backup record.')
    originals = {}
    with tempfile.TemporaryDirectory(prefix='stage-', dir=home) as staging:
        stage = Path(staging)
        require(stage.resolve().is_relative_to(home.resolve()), 'Temporary folder is outside the package.')
        # Prepare and verify every result before replacing any game file.
        for name, spec in pack['assets'].items():
            live = target(game, name, spec)
            raw = live.read_bytes()
            current_hash = digest(raw)
            backup = home / 'backups' / name
            if state:
                original_hash = state['assets'][name]
                require(backup.is_file() and file_hash(backup) == original_hash,
                        'Missing or modified backup: ' + name)
                require(current_hash in (original_hash, spec['output_sha256'], *spec.get('previous_output_sha256', [])),
                        'Conflict with another mod: ' + name)
                original = backup.read_bytes()
            else:
                require(current_hash != spec['output_sha256'] or
                        spec['output_decoded_sha256'] in spec['input_decoded_sha256'],
                        'The mod is already installed, but this package has no backup. Uninstall the previous copy first.')
                original = raw
                original_hash = current_hash
                require(not backup.exists() or file_hash(backup) == original_hash,
                        'Existing backup does not match the game: ' + name)
            try:
                built = make_patched(original, spec)
            except Exception as error:
                raise RuntimeError(name + ': ' + str(error)) from error
            atomic(stage / name, built)
            originals[name] = original_hash
            print('Validated: ' + name, flush=True)
        # Preserve each recipient's exact compressed originals, never ours.
        for name, spec in pack['assets'].items():
            backup = home / 'backups' / name
            if not backup.exists():
                atomic(backup, target(game, name, spec).read_bytes())
            require(file_hash(backup) == originals[name], 'Backup verification failed: ' + name)
        previous_state = state_path.read_bytes() if state_path.exists() else None
        atomic(state_path, json.dumps({'version': pack['version'], 'game': str(game.resolve()),
                                      'assets': originals}, indent=2).encode('utf-8'))
        # Also retain the exact entry state for rollback of a reinstall.
        changed = []
        try:
            for name, spec in pack['assets'].items():
                live = target(game, name, spec)
                if file_hash(live) == spec['output_sha256']:
                    continue
                atomic(stage / (name + '.rollback'), live.read_bytes())
                changed.append(name)
                atomic(live, (stage / name).read_bytes())
                require(file_hash(live) == spec['output_sha256'], 'Installation failed: ' + name)
        except Exception:
            for name in reversed(changed):
                atomic(target(game, name, pack['assets'][name]), (stage / (name + '.rollback')).read_bytes())
            if previous_state is not None:
                atomic(state_path, previous_state)
            raise
    print('\nKratos Only installed successfully. All seven story skips are included.')


def uninstall(game=GAME, home=HOME):
    game_idle()
    pack = payload(home)
    state_path = home / 'installation.json'
    require(state_path.exists(), 'No installation is registered in this folder.')
    state = json.loads(state_path.read_text(encoding='utf-8'))
    require(state['version'] in [pack['version'], *pack.get('compatible_installed_versions', [])]
            and state['game'] == str(game.resolve()),
            'The record belongs to another installation.')
    require(set(state['assets']) == set(pack['assets']), 'Incomplete backup record.')
    for name, spec in pack['assets'].items():
        backup = home / 'backups' / name
        require(backup.is_file() and file_hash(backup) == state['assets'][name], 'Invalid backup: ' + name)
        require(file_hash(target(game, name, spec)) in
                (state['assets'][name], spec['output_sha256'], *spec.get('previous_output_sha256', [])),
                'Conflict: ' + name + '. Remove the subsequent modification before uninstalling.')
    for name, spec in pack['assets'].items():
        live = target(game, name, spec)
        if file_hash(live) != state['assets'][name]:
            atomic(live, (home / 'backups' / name).read_bytes())
        require(file_hash(live) == state['assets'][name], 'Restoration failed: ' + name)
    print('\nOriginal files restored. Save files were not changed.')


if __name__ == '__main__':
    try:
        require(len(sys.argv) == 2 and sys.argv[1] in ('install', 'uninstall'), 'Invalid command.')
        (install if sys.argv[1] == 'install' else uninstall)()
    except Exception as error:
        print('\nERROR: ' + str(error))
        sys.exit(1)
