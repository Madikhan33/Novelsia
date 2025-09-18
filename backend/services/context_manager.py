from typing import Dict, List, Optional, Any
from collections import deque
from datetime import datetime
import json
  
class ContextManager:
    def __init__(self, max_history_size: int = 10):
        self.max_history_size = max_history_size
        self.writing_history = deque(maxlen=max_history_size)
        self.characters: Dict[str, Dict[str, Any]] = {}
        self.world_info: Dict[str, Any] = {}
        self.style_preferences: Dict[str, Any] = {
            "tone": "neutral",
            "pov": "third_person",
            "tense": "past",
            "genre": "general"
        }
        self.chapter_summaries: Dict[int, str] = {}
        self.current_scene_context = ""
        
    def add_to_history(self, text: str, chapter_id: int):
        """Добавляет текст в историю написания."""
        self.writing_history.append({
            "text": text,
            "chapter_id": chapter_id,
            "timestamp": datetime.now().isoformat()
        })
        
    def add_character(self, name: str, description: str, traits: List[str] = None):
        """Добавляет информацию о персонаже."""
        self.characters[name] = {
            "description": description,
            "traits": traits or [],
            "mentions": []
        }
        
    def update_world_info(self, key: str, value: Any):
        """Обновляет информацию о мире истории."""
        self.world_info[key] = value
        
    def set_style_preference(self, key: str, value: str):
        """Устанавливает стилевые предпочтения."""
        if key in self.style_preferences:
            self.style_preferences[key] = value
            
    def add_chapter_summary(self, chapter_id: int, summary: str):
        """Добавляет краткое содержание главы."""
        self.chapter_summaries[chapter_id] = summary
        
    def set_current_scene(self, scene_description: str):
        """Устанавливает контекст текущей сцены."""
        self.current_scene_context = scene_description
        
    def get_full_context(self, current_text: str, chapter_id: int) -> Dict[str, Any]:
        """
        Возвращает полный контекст для генерации.
        """
        # Получаем последние записи из истории
        recent_history = list(self.writing_history)[-3:]  # Последние 3 фрагмента
        
        # Собираем упоминания персонажей в текущем тексте
        mentioned_characters = []
        for char_name in self.characters:
            if char_name.lower() in current_text.lower():
                mentioned_characters.append({
                    "name": char_name,
                    **self.characters[char_name]
                })
                
        return {
            "current_text": current_text,
            "recent_history": recent_history,
            "chapter_id": chapter_id,
            "chapter_summary": self.chapter_summaries.get(chapter_id, ""),
            "current_scene": self.current_scene_context,
            "mentioned_characters": mentioned_characters,
            "style": self.style_preferences,
            "world_info": self.world_info
        }
        
    def build_prompt_context(self, context_data: Dict[str, Any]) -> str:
        """
        Строит контекстную часть промпта для AI.
        """
        prompt_parts = []
        
        # Информация о стиле
        style = context_data.get("style", {})
        if style:
            style_desc = f"Стиль: {style.get('genre', 'general')}, "
            style_desc += f"время: {style.get('tense', 'past')}, "
            style_desc += f"тон: {style.get('tone', 'neutral')}"
            prompt_parts.append(style_desc)
            
        # Информация о мире
        world_info = context_data.get("world_info", {})
        if world_info:
            world_desc = "Мир истории: " + ", ".join([f"{k}: {v}" for k, v in world_info.items()])
            prompt_parts.append(world_desc)
            
        # Текущая сцена
        if context_data.get("current_scene"):
            prompt_parts.append(f"Текущая сцена: {context_data['current_scene']}")
            
        # Упомянутые персонажи
        characters = context_data.get("mentioned_characters", [])
        if characters:
            char_desc = "Персонажи в сцене:\n"
            for char in characters:
                char_desc += f"- {char['name']}: {char['description']}"
                if char.get('traits'):
                    char_desc += f" (черты: {', '.join(char['traits'])})"
                char_desc += "\n"
            prompt_parts.append(char_desc)
            
        # Краткое содержание главы
        if context_data.get("chapter_summary"):
            prompt_parts.append(f"Контекст главы: {context_data['chapter_summary']}")
            
        # Недавняя история
        history = context_data.get("recent_history", [])
        if history:
            history_text = "Недавно написанное:\n"
            for entry in history[-2:]:  # Последние 2 фрагмента
                text_preview = entry['text'][:200] + "..." if len(entry['text']) > 200 else entry['text']
                history_text += f"- {text_preview}\n"
            prompt_parts.append(history_text)
            
        return "\n\n".join(prompt_parts)
        
    def export_context(self) -> str:
        """Экспортирует весь контекст в JSON."""
        return json.dumps({
            "characters": self.characters,
            "world_info": self.world_info,
            "style_preferences": self.style_preferences,
            "chapter_summaries": self.chapter_summaries,
            "current_scene": self.current_scene_context
        }, ensure_ascii=False, indent=2)
        
    def import_context(self, json_data: str):
        """Импортирует контекст из JSON."""
        data = json.loads(json_data)
        self.characters = data.get("characters", {})
        self.world_info = data.get("world_info", {})
        self.style_preferences = data.get("style_preferences", self.style_preferences)
        self.chapter_summaries = data.get("chapter_summaries", {})
        self.current_scene_context = data.get("current_scene", "")


# Глобальный экземпляр менеджера контекста
context_manager = ContextManager()