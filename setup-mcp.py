#!/usr/bin/env python3
"""
Setup MCP - Auto-configuração do OSP Marketing Tools para Claude Code
Detecta e configura automaticamente o servidor MCP em qualquer sistema operacional.
"""

import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple


class MCPSetup:
    """Configurador automático para MCP do Claude Code."""

    def __init__(self, silent: bool = False):
        self.silent = silent
        self.system = platform.system()
        self.config_path = self._find_config_path()
        self.backup_path = None

    def _find_config_path(self) -> Optional[Path]:
        """Encontra o arquivo de configuração do Claude Code baseado no OS."""
        home = Path.home()

        # Possíveis localizações por sistema operacional
        config_locations = {
            "Darwin": [  # macOS
                home
                / "Library"
                / "Application Support"
                / "Claude"
                / "claude_desktop_config.json",
                home / ".claude" / "claude_desktop_config.json",
                home
                / "Library"
                / "Application Support"
                / "com.anthropic.claude"
                / "config.json",
            ],
            "Windows": [
                Path(os.environ.get("APPDATA", ""))
                / "Claude"
                / "claude_desktop_config.json",
                Path(os.environ.get("LOCALAPPDATA", ""))
                / "Claude"
                / "claude_desktop_config.json",
                home / ".claude" / "claude_desktop_config.json",
            ],
            "Linux": [
                home / ".config" / "claude" / "claude_desktop_config.json",
                home / ".claude" / "claude_desktop_config.json",
                home / ".local" / "share" / "claude" / "config.json",
            ],
        }

        # Tentar cada localização possível
        for path in config_locations.get(self.system, []):
            if path.exists():
                return path

        # Tentar localização genérica
        generic_path = home / ".claude" / "claude_desktop_config.json"
        if generic_path.exists():
            return generic_path

        return None

    def _create_default_config(self) -> Path:
        """Cria um arquivo de configuração padrão se não existir."""
        home = Path.home()

        # Determinar onde criar o config
        if self.system == "Darwin":  # macOS
            config_dir = home / "Library" / "Application Support" / "Claude"
        elif self.system == "Windows":
            config_dir = Path(os.environ.get("APPDATA", home)) / "Claude"
        else:  # Linux
            config_dir = home / ".config" / "claude"

        config_dir.mkdir(parents=True, exist_ok=True)
        config_path = config_dir / "claude_desktop_config.json"

        # Criar configuração mínima
        default_config = {"mcpServers": {}}

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=2)

        return config_path

    def backup_config(self) -> bool:
        """Faz backup da configuração atual."""
        if not self.config_path or not self.config_path.exists():
            return False

        self.backup_path = self.config_path.with_suffix(".json.backup")
        counter = 1

        # Encontrar um nome de backup único
        while self.backup_path.exists():
            self.backup_path = self.config_path.with_suffix(f".json.backup{counter}")
            counter += 1

        try:
            shutil.copy2(self.config_path, self.backup_path)
            if not self.silent:
                print(f"✓ Backup criado: {self.backup_path}")
            return True
        except Exception as e:
            if not self.silent:
                print(f"✗ Erro ao criar backup: {e}")
            return False

    def load_config(self) -> Tuple[bool, Dict]:
        """Carrega a configuração atual."""
        if not self.config_path:
            return False, {}

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            return True, config
        except json.JSONDecodeError as e:
            if not self.silent:
                print(f"✗ Erro ao ler configuração JSON: {e}")
            return False, {}
        except Exception as e:
            if not self.silent:
                print(f"✗ Erro ao carregar configuração: {e}")
            return False, {}

    def add_osp_server(self, config: Dict) -> Dict:
        """Adiciona o servidor OSP Marketing Tools à configuração."""
        # Garantir que mcpServers existe
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Caminho do servidor Python
        server_path = (
            Path(__file__).parent / "src" / "osp_marketing_tools" / "server.py"
        )

        # Configuração do servidor OSP
        osp_server = {
            "command": sys.executable,  # Python executável atual
            "args": [str(server_path)],
            "env": {},
        }

        # Adicionar ou atualizar
        config["mcpServers"]["osp-marketing-tools"] = osp_server

        return config

    def save_config(self, config: Dict) -> bool:
        """Salva a configuração atualizada."""
        if not self.config_path:
            return False

        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            if not self.silent:
                print(f"✗ Erro ao salvar configuração: {e}")
            return False

    def validate_setup(self) -> bool:
        """Valida se a configuração foi aplicada corretamente."""
        success, config = self.load_config()
        if not success:
            return False

        # Verificar se nosso servidor está configurado
        if "mcpServers" in config and "osp-marketing-tools" in config["mcpServers"]:
            server_config = config["mcpServers"]["osp-marketing-tools"]
            if "command" in server_config and "args" in server_config:
                return True

        return False

    def rollback(self) -> bool:
        """Reverte para o backup se algo der errado."""
        if not self.backup_path or not self.backup_path.exists():
            return False

        try:
            shutil.copy2(self.backup_path, self.config_path)
            if not self.silent:
                print(f"✓ Configuração revertida do backup")
            return True
        except Exception as e:
            if not self.silent:
                print(f"✗ Erro ao reverter: {e}")
            return False

    def run(self) -> bool:
        """Executa o processo completo de configuração."""
        print("\n🔧 OSP Marketing Tools - Configurador MCP")
        print("=" * 50)

        # Passo 1: Detectar sistema
        print(f"\n1. Sistema detectado: {self.system}")

        # Passo 2: Encontrar ou criar config
        if not self.config_path:
            print("2. Arquivo de configuração não encontrado")
            print("   Criando configuração padrão...")
            self.config_path = self._create_default_config()
            print(f"   ✓ Criado: {self.config_path}")
        else:
            print(f"2. Configuração encontrada: {self.config_path}")

        # Passo 3: Backup
        print("\n3. Criando backup...")
        if not self.backup_config():
            print("   ⚠ Continuando sem backup")

        # Passo 4: Carregar config
        print("\n4. Carregando configuração...")
        success, config = self.load_config()
        if not success:
            print("   ✗ Falha ao carregar configuração")
            return False

        # Passo 5: Adicionar servidor OSP
        print("\n5. Adicionando servidor OSP Marketing Tools...")
        config = self.add_osp_server(config)

        # Passo 6: Salvar
        print("\n6. Salvando configuração...")
        if not self.save_config(config):
            print("   ✗ Falha ao salvar")
            if self.rollback():
                print("   ✓ Revertido para backup")
            return False

        # Passo 7: Validar
        print("\n7. Validando configuração...")
        if self.validate_setup():
            print("   ✓ Configuração válida!")
            print("\n✅ SUCESSO! OSP Marketing Tools configurado para Claude Code")
            print("\n📝 Próximos passos:")
            print("   1. Reinicie o Claude Code")
            print("   2. As ferramentas estarão disponíveis automaticamente")
            print("   3. Para testar sem MCP: npx ipcom-marketing-ai demo")
            return True
        else:
            print("   ✗ Validação falhou")
            if self.rollback():
                print("   ✓ Revertido para backup")
            return False


def main():
    """Função principal."""
    # Verificar argumentos
    silent = "--silent" in sys.argv or "-s" in sys.argv

    # Executar setup
    setup = MCPSetup(silent=silent)
    success = setup.run()

    # Código de saída
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
