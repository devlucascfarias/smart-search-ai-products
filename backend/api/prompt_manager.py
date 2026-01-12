"""
Gerenciador de Prompts para o Smart Search AI
Carrega e gerencia prompts externos para melhor manutenibilidade
"""
import os
from pathlib import Path
from typing import Dict

class PromptManager:
    """Gerencia prompts externos para o sistema de busca inteligente"""
    
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            prompts_dir = os.path.join(os.path.dirname(__file__), "prompts")
        self.prompts_dir = Path(prompts_dir)
        self._cache: Dict[str, str] = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """
        Carrega um prompt do arquivo.
        
        Args:
            prompt_name: Nome do arquivo de prompt (sem extensão)
            
        Returns:
            Conteúdo do prompt
            
        Raises:
            FileNotFoundError: Se o arquivo de prompt não existir
        """
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}. "
                f"Available prompts: {self.list_available_prompts()}"
            )
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[prompt_name] = content
        
        return content
    
    def list_available_prompts(self) -> list:
        """Lista todos os prompts disponíveis"""
        if not self.prompts_dir.exists():
            return []
        return [f.stem for f in self.prompts_dir.glob("*.txt")]
    
    def reload_prompt(self, prompt_name: str) -> str:
        """Recarrega um prompt do arquivo, ignorando o cache"""
        if prompt_name in self._cache:
            del self._cache[prompt_name]
        return self.load_prompt(prompt_name)
    
    def clear_cache(self):
        """Limpa o cache de prompts"""
        self._cache.clear()


prompt_manager = PromptManager()
