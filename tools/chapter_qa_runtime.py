"""Run bounded final Chapter 1 QA only against an explicit isolated session."""

import argparse
import base64
import hashlib
import json
import struct
import subprocess
import time
import unicodedata
from pathlib import Path

import capture_framebuffer
from setup_qa import ROOT, request


RUNTIME = ROOT / "work/ui/stages_0.1.12/runtime"
GAME_ID = "NPJH50380"
ALLOWED_BUTTONS = {"circle", "cross", "up", "down", "left", "right", "start", "select"}


def memory(address, size):
    assert 0x08800000 <= address < address + size <= 0x0A000000
    return base64.b64decode(request("memory.read", address=address, size=size)["base64"])


def wide(address, limit):
    data = memory(address, (limit + 1) * 2)
    end = next(index for index in range(0, len(data), 2) if data[index:index + 2] == b"\0\0")
    assert end <= limit * 2
    return data[:end].decode("cp932")


def observe(report, check=False, context=0x08E31910):
    """Read the display VM without assuming it is currently in dialogue."""
    paused = request("cpu.status")["stepping"]
    if not paused:
        request("cpu.stepping")
    try:
        vm = struct.unpack("<15I", memory(0x08A3A9E4, 60))
        script_loaded = 0x08800000 <= vm[7] < vm[7] + report["decoded_size"] <= 0x0A000000
        live_script_sha256 = None
        if script_loaded:
            live_script_sha256 = hashlib.sha256(memory(vm[7], report["decoded_size"])).hexdigest()
        if check and script_loaded:
            assert live_script_sha256 == report["decoded_sha256"]
        state = memory(context, 0x3D4)
        count = struct.unpack_from("<I", state, 0x3CC)[0]
        if count > 6:
            return {
                "pc": vm[1], "native": hex(vm[12]), "script_base": hex(vm[7]), "lines": [],
                "choice": False, "names": {}, "dialogue_active": False,
                "display_record_count": count, "script_loaded": script_loaded,
                "live_script_sha256": live_script_sha256,
            }
        name_pointers = struct.unpack("<3I", memory(context + 0x4BE8, 12))
        tokens = {}
        for token, pointer, limit in zip("●▲■", name_pointers, (6, 8, 8)):
            if 0x08800000 <= pointer < 0x0A000000:
                tokens[token] = wide(pointer, limit)
        records = [row for row in report["changes"] if row["reference_instructions"]]
        records += [row for group in report["layout_groups"] for page in group["pages"] for row in page]
        by_offset = {row["new_offset"]: row for row in records}
        lines = []
        for index in range(count):
            base = 0x84 + index * 0x8C
            pointer, choice = struct.unpack_from("<2I", state, base)
            raw, kinds = b"", []
            for cell in range(32):
                character, kind = struct.unpack_from("<2H", state, base + 10 + cell * 4)
                if not character:
                    break
                raw += struct.pack("<H", character)
                kinds.append(kind)
            target = by_offset.get(pointer - vm[7])
            shown = raw.decode("cp932", errors="replace")
            if target:
                expected = target["display_text"]
                for token, text in tokens.items():
                    expected = expected.replace(token, text)
                assert raw == expected.encode("cp932"), (target["id"], shown, expected)
                assert len(kinds) <= 31
            lines.append({
                "id": target["id"] if target else None,
                "text": target["text"] if target else None,
                "rendered": unicodedata.normalize("NFKC", shown) if target else None,
                "pointer": hex(pointer),
                "units": len(kinds),
                "selectable": bool(state[base + 8]),
                "choice": choice,
                "kinds": kinds,
            })
        return {
            "pc": vm[1], "native": hex(vm[12]), "script_base": hex(vm[7]), "lines": lines,
            "choice": any(line["selectable"] for line in lines),
            "names": {token: unicodedata.normalize("NFKC", text) for token, text in tokens.items()},
            "dialogue_active": True,
            "script_loaded": script_loaded,
            "live_script_sha256": live_script_sha256,
        }
    finally:
        if not paused:
            request("cpu.resume")


def listener_pid(port):
    output = subprocess.check_output(["netstat", "-ano", "-p", "tcp"], text=True, encoding="utf-8")
    matches = []
    for line in output.splitlines():
        fields = line.split()
        if len(fields) >= 5 and fields[3].upper() == "LISTENING" and fields[1].rsplit(":", 1)[-1] == str(port):
            matches.append(int(fields[-1]))
    if len(matches) != 1:
        raise RuntimeError("Expected exactly one local debugger listener on port %d: %r" % (port, matches))
    return matches[0]


def validate_session(session_path, candidate):
    session = json.loads(session_path.read_text(encoding="utf-8-sig"))
    required = {"pid", "game", "port"}
    if not required <= set(session):
        raise ValueError("Session is missing required fields: " + str(required - set(session)))
    if session["port"] != 19381:
        raise ValueError("The final QA session must use port 19381")
    if Path(session["game"]).resolve() != candidate.resolve():
        raise ValueError("Session ISO is not the requested final candidate")
    process = subprocess.run(
        ["powershell", "-NoProfile", "-Command", "(Get-Process -Id %d).Path" % session["pid"]],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    expected_executable = session_path.parent / "PPSSPPWindows64.exe"
    if process.returncode or not process.stdout.strip() or Path(process.stdout.strip()).resolve() != expected_executable.resolve():
        raise RuntimeError("Recorded QA process is not running")
    if listener_pid(session["port"]) != session["pid"]:
        raise RuntimeError("Port 19381 is not owned by the recorded isolated QA process")
    game = request("game.status")
    if game["game"]["id"] != GAME_ID:
        raise RuntimeError("Unexpected game on the isolated debugger session")
    return session, game


def parse_native(value):
    if value.lower() == "none":
        return None
    return hex(int(value, 0))


def press(button, delay):
    if button not in ALLOWED_BUTTONS:
        raise ValueError("Unsupported QA button: " + button)
    if request("cpu.status")["stepping"]:
        request("cpu.resume")
    request("input.buttons.press", button=button, duration=10)
    time.sleep(delay)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session", type=Path, required=True,
                        help="Explicit isolated work/scratch/.../session.json path")
    parser.add_argument("--candidate", type=Path,
                        default=Path("work/output/0.1.12/Summon_Night_3_EN_0.1.12.iso"))
    parser.add_argument("--advance", type=int, default=0)
    parser.add_argument("--until", default="stages_641")
    parser.add_argument("--stop-native", default="0x31",
                        help="Stop before the expected post-opening setup native, or 'none'.")
    parser.add_argument("--press", help="Explicit comma-separated button presses.")
    parser.add_argument("--auto-opening", action="store_true")
    parser.add_argument("--boot", action="store_true")
    parser.add_argument("--capture", help="New PNG filename beneath the stages runtime folder.")
    parser.add_argument("--confirm-default-name", action="store_true")
    parser.add_argument("--reviewed-name-capture", type=Path,
                        help="Previously inspected isolated name-entry capture required for name confirmation.")
    parser.add_argument("--tag", default="final_inspect")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--delay", type=float, default=0.65)
    parser.add_argument("--context", type=lambda value: int(value, 0), default=0x08E31910)
    args = parser.parse_args()
    if not 0 <= args.advance <= 120 or not .2 <= args.delay <= 5:
        raise ValueError("Advance and delay are outside bounded QA limits")
    if args.confirm_default_name and not args.reviewed_name_capture:
        raise ValueError("Name confirmation requires --reviewed-name-capture")
    if args.confirm_default_name and args.press:
        raise ValueError("Use a separate command for the confirmed default-name action")
    candidate = (ROOT / args.candidate).resolve() if not args.candidate.is_absolute() else args.candidate.resolve()
    session_path = (ROOT / args.session).resolve() if not args.session.is_absolute() else args.session.resolve()
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    if not session_path.is_file():
        raise FileNotFoundError(session_path)
    manifest_path = candidate.with_name("manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = manifest["script_changes"][0]
    stop_native = parse_native(args.stop_native)
    preview = {
        "mode": "execute" if args.execute else "dry run",
        "session": str(session_path), "candidate": str(candidate), "expected_output_sha256": manifest["output_sha256"],
        "until": args.until, "stop_native": stop_native, "advance": args.advance,
        "auto_opening": args.auto_opening, "press": args.press,
        "name_confirmation": bool(args.confirm_default_name), "capture": args.capture,
        "policy": "The original native 0x31 is an expected post-opening setup transition. Capture and inspect the name-entry screen before the separate explicit default-name confirmation.",
    }
    print(json.dumps(preview, indent=2), flush=True)
    if not args.execute:
        return
    session, game = validate_session(session_path, candidate)
    state = {} if args.boot else observe(report, check=True, context=args.context)
    states, actions, stop_reason = ([] if args.boot else [state]), [], None
    if args.press:
        for button in args.press.split(","):
            press(button, 3 if args.boot else 1.5)
            actions.append(button)
        state = observe(report, context=args.context)
        states.append(state)
    if args.confirm_default_name:
        reviewed = (RUNTIME / args.reviewed_name_capture).resolve() if not args.reviewed_name_capture.is_absolute() else args.reviewed_name_capture.resolve()
        if not reviewed.is_file() or RUNTIME not in reviewed.parents:
            raise ValueError("Reviewed name-entry capture must be an existing isolated runtime PNG")
        press("start", 1.5)
        actions.append("confirm-default-name:start")
        state = observe(report, context=args.context)
        states.append(state)
    for step in range(args.advance):
        if stop_native and state.get("native") == stop_native:
            stop_reason = "expected_native_" + stop_native
            break
        if any(args.until in (line["id"] or "") for line in state.get("lines", [])):
            stop_reason = "target_reached"
            break
        if state.get("choice"):
            header = state["lines"][0]["id"]
            if args.auto_opening and header == "00:00065:text:0002691a":
                press("circle", 1.5); actions.append("recollection:first")
            elif args.auto_opening and header == "00:00065:text:0002884a":
                press("circle", 1.5); actions.append("girl:refined")
            else:
                stop_reason = "unapproved_choice"
                break
        else:
            press("circle", args.delay)
            actions.append("advance")
        state = observe(report, context=args.context)
        if not states or state != states[-1]:
            states.append(state)
            print(json.dumps({"step": step + 1, "native": state["native"],
                              "text": [line["text"] for line in state["lines"]], "choice": state["choice"]}), flush=True)
    if args.capture:
        filename = Path(args.capture)
        target = (RUNTIME / filename).resolve()
        if filename.name != str(filename) or target.suffix != ".png" or RUNTIME not in target.parents or target.exists():
            raise ValueError("Capture must be a new simple PNG filename in the isolated runtime folder")
        if request("cpu.status")["stepping"]:
            request("cpu.resume")
        time.sleep(3)
        capture_framebuffer.request = request
        png, metadata = capture_framebuffer.capture(hold=True)
        target.write_bytes(png)
        target.with_suffix(".json").write_text(json.dumps({"state": state, "capture": metadata}, indent=2) + "\n", encoding="utf-8")
    trace = RUNTIME / (args.tag + ".trace.json")
    if trace.exists():
        raise FileExistsError(trace)
    trace.write_text(json.dumps({
        "session": session, "game": game, "candidate_sha256": manifest["output_sha256"],
        "live_script_sha256": report["decoded_sha256"], "states": states, "actions": actions,
        "stop_reason": stop_reason,
    }, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"final": state, "stop_reason": stop_reason, "trace": str(trace)}), flush=True)


if __name__ == "__main__":
    main()
