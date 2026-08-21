# Blender Add-ons Pack (All-in-One)

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Blender](https://img.shields.io/badge/Blender-3.6%20LTS%20%7C%204.2%20LTS%20%7C%205.0-orange?logo=blender)](https://www.blender.org)
[![Version](https://img.shields.io/badge/Version-v3.0.0-brightgreen)]()

O **Blender Add-ons Pack** unifica todas as ferramentas essenciais de animação, rigging e produtividade em um único add-on consolidado para o **Blender 3.6 LTS, 4.0, 4.1, 4.2 LTS e 5.0+**.

---

## 🎯 Módulos Integrados

Tudo fica organizado em uma única aba limpa na Sidebar do Blender (**`N-Panel > Add-ons Pack`**):

### 1. 🚀 Dynamic Parent
- Criação e toggle instantâneo de constraints animados **Child Of**
- Permite segurar e soltar objetos dinamicamente durante animações
- Operadores: **Criar Parent**, **Desativar Parent**, **Limpar Parent**

### 2. 🦴 Rig Constraints Manager (R6 & Custom)
- **Copy Transforms em Lote:** transfere movimento entre armatures compatíveis com 1 clique
- **Gerador de Foot Bones (R6):** cria automaticamente ossos auxiliares para os pés em rigs de Roblox
- **Limpador em Lote:** remove todas as constraints de um rig com segurança

### 3. 🛠️ Ferramentas de Rig & Viewport
- Alternar visualização **In Front** da Armature
- Exibir/ocultar **Nomes dos Bones** e **Eixos Locais (XYZ)** na Viewport
- **Resetar Rest Pose:** volta o rig para a pose de repouso padrão instantaneamente

### 4. 🎬 Utilitários de Animação
- **Ajustar Frame Range:** calcula e define o início e fim da timeline a partir dos keyframes do objeto selecionado
- **Bake de Animação:** executa bake com visual keying para exportação limpa em FBX/GLTF

---

## 📦 Como Instalar no Blender (1 Clique)

1. Baixe o arquivo **`blender_addons_pack_v3.0.0.zip`** da aba [Releases](../../releases)
2. No Blender: **Edit → Preferences → Add-ons** (ou **Get Extensions** no Blender 4.2+)
3. Clique em **Install from Disk...** (ícone de engrenagem no canto superior direito)
4. Selecione o arquivo `.zip` e ative o checkbox **Blender Add-ons Pack (All-in-One)**
5. Pressione `N` na 3D Viewport para abrir a barra lateral e clique na aba **`Add-ons Pack`**!

---

## 🏗️ Estrutura do Repositório

```
blender-addons-pack/
├── __init__.py                  ← Entrypoint unificado (bl_info v3.0.0)
├── blender_manifest.toml        ← Manifesto para Blender 4.2+ Extensions
├── dynamic_parent.py            ← Módulo Dynamic Parent
├── rig_constraints_manager.py   ← Módulo Rig Constraints & R6
├── rig_tools.py                 ← Módulo de viewport e armature tools
├── anim_utils.py                ← Módulo de utilitários de animação
├── ui_panels.py                 ← Painel unificado da Sidebar (N-Panel)
├── blender_addons_pack_v3.0.0.zip ← Pacote instalável
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

---

## 📄 Licença

Distribuído sob a licença **GNU General Public License v3.0** — veja [LICENSE](LICENSE) para detalhes.
