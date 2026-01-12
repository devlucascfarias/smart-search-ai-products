# Prompts do Smart Search AI

Este diretório contém os prompts externos usados pelo sistema de busca inteligente.

## Estrutura

- `category_analysis.txt` - Prompt para análise e mapeamento de categorias
- `response_generation.txt` - Prompt para geração da resposta final ao usuário

## Vantagens desta Abordagem

### ✅ **Manutenibilidade**
- Prompts podem ser editados sem mexer no código Python
- Fácil de versionar e fazer rollback de mudanças
- Separação clara entre lógica e conteúdo

### ✅ **Colaboração**
- Product Managers podem editar prompts diretamente
- Não precisa conhecer Python para ajustar comportamento da IA
- Facilita A/B testing de diferentes versões de prompts

### ✅ **Performance**
- Prompts são carregados uma vez e mantidos em cache
- Reduz overhead de parsing de strings grandes
- Facilita implementação de prompt caching da API

### ✅ **Debugging**
- Fácil identificar qual prompt está causando problemas
- Logs podem referenciar arquivos específicos
- Facilita testes isolados de cada prompt

## Como Usar

```python
from prompt_manager import prompt_manager

# Carregar um prompt
template = prompt_manager.load_prompt("category_analysis")

# Listar prompts disponíveis
available = prompt_manager.list_available_prompts()

# Recarregar um prompt (útil em desenvolvimento)
template = prompt_manager.reload_prompt("category_analysis")

# Limpar cache (força reload de todos os prompts)
prompt_manager.clear_cache()
```

## Boas Práticas

1. **Versionamento**: Sempre commitar mudanças de prompts com mensagens descritivas
2. **Testes**: Testar mudanças de prompts antes de fazer deploy
3. **Documentação**: Documentar mudanças significativas neste README
4. **Backup**: Manter versões anteriores de prompts que funcionaram bem

## Histórico de Mudanças

### 2026-01-12
- ✅ Criação inicial dos prompts externos
- ✅ Migração de prompts inline para arquivos `.txt`
- ✅ Implementação do `PromptManager` com cache
