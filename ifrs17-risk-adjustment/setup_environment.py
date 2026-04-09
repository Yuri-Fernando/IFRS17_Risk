#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico e setup do ambiente para IFRS 17 Risk Adjustment Engine
Executa verificações e instala dependências automaticamente
"""

import sys
import subprocess
import os
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"


def print_header(msg):
    print(f"\n{'='*70}")
    print(f"  {msg}")
    print(f"{'='*70}\n")


def check_python_version():
    """Verifica versao do Python"""
    print("[1/6] Verificando versao do Python...")
    version = sys.version_info
    print(f"  Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("  [ERRO] Python 3.8+ requerido")
        return False
    print("  [OK] Versao OK\n")
    return True


def check_pip():
    """Verifica se pip esta disponivel"""
    print("[2/6] Verificando pip...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True
        )
        print(f"  {result.stdout.strip()}")
        print("  [OK] pip OK\n")
        return True
    except Exception as e:
        print(f"  [ERRO] {e}\n")
        return False


def check_project_structure():
    """Verifica estrutura do projeto"""
    print("[3/6] Verificando estrutura do projeto...")
    project_root = Path(__file__).parent
    required_dirs = ['src', 'data', 'notebooks', 'config', 'reports']
    required_files = ['requirements.txt', 'run_pipeline.py', 'notebooks/main.ipynb']

    all_ok = True
    for dir_name in required_dirs:
        dir_path = project_root / dir_name
        status = "[OK]" if dir_path.exists() else "[FALTA]"
        print(f"  {status} {dir_name}/")
        if not dir_path.exists():
            all_ok = False

    for file_name in required_files:
        file_path = project_root / file_name
        status = "[OK]" if file_path.exists() else "[FALTA]"
        print(f"  {status} {file_name}")
        if not file_path.exists():
            all_ok = False

    if all_ok:
        print("  [OK] Estrutura OK\n")
    else:
        print("  [AVISO] Alguns arquivos estao faltando\n")

    return all_ok


def check_dataset():
    """Verifica se o dataset existe"""
    print("[4/6] Verificando dataset...")
    dataset_path = Path(__file__).parent / 'data' / 'raw' / 'Insurance claims data.csv'

    if dataset_path.exists():
        size_mb = dataset_path.stat().st_size / (1024 * 1024)
        print(f"  [OK] Dataset encontrado: {size_mb:.1f} MB")
        print(f"       {dataset_path}\n")
        return True
    else:
        print(f"  [ERRO] Dataset nao encontrado em:")
        print(f"         {dataset_path}\n")
        return False


def install_dependencies():
    """Instala dependencias do requirements.txt"""
    print("[5/6] Instalando dependencias...")
    project_root = Path(__file__).parent
    requirements_file = project_root / 'requirements.txt'

    if not requirements_file.exists():
        print("  [ERRO] requirements.txt nao encontrado\n")
        return False

    try:
        print("  Instalando pacotes (isso pode levar alguns minutos)...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            capture_output=False,
            text=True
        )

        if result.returncode == 0:
            print("  [OK] Dependencias instaladas com sucesso\n")
            return True
        else:
            print("  [ERRO] Erro ao instalar dependencias\n")
            return False
    except Exception as e:
        print(f"  [ERRO] {e}\n")
        return False


def verify_imports():
    """Verifica se os imports principais funcionam"""
    print("[6/6] Verificando imports...")
    required_imports = [
        ('numpy', 'np'),
        ('pandas', 'pd'),
        ('scipy', 'scipy'),
        ('sklearn', 'sklearn'),
        ('statsmodels', 'statsmodels'),
        ('matplotlib', 'matplotlib'),
        ('seaborn', 'seaborn'),
    ]

    all_ok = True
    for module_name, alias in required_imports:
        try:
            __import__(module_name)
            print(f"  [OK] {module_name}")
        except ImportError:
            print(f"  [FALTA] {module_name} - NAO INSTALADO")
            all_ok = False

    # Verifica se src pode ser importado
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from src.data.load_data import load_data
        print(f"  [OK] src.data.load_data")
    except ImportError as e:
        print(f"  [ERRO] src.data.load_data - {e}")
        all_ok = False

    if all_ok:
        print("  [OK] Todos os imports OK\n")
    else:
        print("  [AVISO] Alguns pacotes ainda nao estao disponíveis\n")

    return all_ok


def main():
    print_header("IFRS 17 Risk Adjustment Engine - Setup do Ambiente")

    checks = [
        ("Versao do Python", check_python_version()),
        ("pip", check_pip()),
        ("Estrutura do projeto", check_project_structure()),
        ("Dataset", check_dataset()),
    ]

    print("\nResumo das verificacoes:")
    print("-" * 70)
    for name, result in checks:
        status = "[OK]" if result else "[ERRO]"
        print(f"  {status} {name}")

    all_checks_ok = all(result for _, result in checks)

    if not all_checks_ok:
        print("\n[AVISO] Alguns problemas foram detectados. Tentando corrigir...\n")

    # Tenta instalar dependencias
    install_success = install_dependencies()

    # Verifica imports finais
    imports_ok = verify_imports()

    print_header("Resultado Final")

    if install_success and imports_ok:
        print("[OK] AMBIENTE PRONTO!")
        print("\nProximos passos:")
        print("  1. Abra o notebook:")
        print("     jupyter notebook notebooks/main.ipynb")
        print("  2. Execute todas as celulas na ordem (Shift+Enter)")
        print("  3. Os resultados serao salvos em reports/result_final.json")
        return 0
    else:
        print("[ERRO] Ainda ha problemas no ambiente.")
        print("\nTroubleshoot:")
        print("  1. Verifique se Python 3.8+ esta instalado")
        print("  2. Execute este script novamente")
        print("  3. Se o problema persistir, veja requirements.txt")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
