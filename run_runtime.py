import sys
import os
import platform
import subprocess

def run_local(args):
    python_cmd = "python"
    if platform.system() == "Windows":
        python_cmd = "python"
    cmd = [python_cmd, "app/realtime.py"] + args
    subprocess.run(cmd)

def run_docker(args):
    base_cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath('app')}:/app/app",
        "ocr-v", "python", "/app/app/realtime.py"
    ]
    if not args:
        # Webcam: só funciona no Linux normalmente
        base_cmd.insert(3, "--device")
        base_cmd.insert(4, "/dev/video0")
    cmd = base_cmd + [f"/app/app/{a}" if a and not a.startswith('/') else a for a in args]
    subprocess.run(cmd)

if __name__ == "__main__":
    print("Escolha o modo de execução:")
    print("1 - Local (recomendado para webcam)")
    print("2 - Docker (recomendado para imagens)")
    mode = input("Modo [1/2]: ").strip()
    args = sys.argv[1:]
    if mode == "1":
        run_local(args)
    else:
        run_docker(args)
