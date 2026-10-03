#!/usr/bin/env python
"""
Script para gerar o instalador do Nex-Júris.
Passos:
1. Build do frontend
2. PyInstaller do backend
3. Geração do .exe final com NSIS
"""
import os
import sys
import subprocess
import shutil

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIST_DIR = os.path.join(ROOT_DIR, "dist")


def build_frontend():
    print("[1/3] Compilando frontend...")
    subprocess.run(
        ["npx", "vite", "build"],
        cwd=os.path.join(ROOT_DIR, "frontend"),
        check=True,
    )
    print("  Frontend compilado em dist/")


def build_backend():
    print("[2/3] Gerando executável do backend...")
    backend_dir = os.path.join(ROOT_DIR, "backend")
    spec_path = os.path.join(DIST_DIR, "nexjuris-backend.spec")

    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--name", "nexjuris-backend",
            "--onefile",
            "--distpath", DIST_DIR,
            "--workpath", os.path.join(DIST_DIR, "build"),
            "--add-data", f"{os.path.join(backend_dir, 'app')}{os.pathsep}app",
            "--hidden-import", "uvicorn",
            "--hidden-import", "sqlalchemy",
            "--hidden-import", "pytesseract",
            "--hidden-import", "pdf2image",
            "--hidden-import", "docx",
            "--hidden-import", "PIL",
            "--hidden-import", "requests",
            "run.py",
        ],
        cwd=backend_dir,
        check=True,
    )
    print("  Backend compilado como .exe")


def create_installer():
    print("[3/3] Gerando instalador NSIS...")
    nsi_path = os.path.join(os.path.dirname(__file__), "installer.nsi")

    if not shutil.which("makensis"):
        print("  NSIS não encontrado. Instale NSIS: https://nsis.sourceforge.io/")
        print("  Após instalar, execute manualmente:")
        print(f"    makensis {nsi_path}")
        return

    subprocess.run(["makensis", nsi_path], cwd=os.path.dirname(__file__), check=True)
    print("  Instalador gerado!")


def main():
    os.makedirs(DIST_DIR, exist_ok=True)
    build_frontend()
    build_backend()
    create_installer()
    print("\n✅ Instalador gerado em:", DIST_DIR)


if __name__ == "__main__":
    main()
