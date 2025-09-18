from openai import AsyncOpenAI
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import re
import asyncio
from config import settings
from models_init import AISuggestion, Chapter, Novel
from schemas.ai_suggestion import AISuggestionCreate, AISuggestionRequest
from .context_manager import context_manager

class SmartAIService:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
            try:
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to initialize OpenAI client: {str(e)}")
    
    async def generate_suggestion_continuation(
        self, 
        context: str, 
        novel_context: Optional[str] = None,
        style: str = "neutral",
        max_length: int = 150,
        chapter_id: Optional[int] = None,
        chapter_full_content: Optional[str] = None,
        use_full_context: bool = True
    ) -> str:
        """
        Генерирует обычную подсказку для продолжения текста (для панели подсказок).
        """
        if self.client is None:
            raise HTTPException(
                status_code=500,
                detail="OpenAI client not initialized. Please configure OPENAI_API_KEY."
            )
        
        context = context.strip()

        try:
            # Анализируем стиль текста
            detected_style = await self._analyze_writing_style(context)
            
            # Получаем полный контекст если нужно
            enhanced_prompt = None
            if use_full_context and chapter_id and chapter_full_content:
                full_context_for_manager = f"{chapter_full_content}\n{context}".strip()
                full_context_info = context_manager.get_full_context(full_context_for_manager, chapter_id)
                enhanced_prompt = context_manager.build_prompt_context(full_context_info)
            
            # Создаем промпт для генерации
            prompt = await self._create_continuation_prompt(
                context, novel_context, detected_style, style, enhanced_prompt
            )
            
            # Генерируем подсказку для панели
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_suggestion_system_prompt()
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(max_length, 120),
                temperature=0.5,
                presence_penalty=0.4,
                frequency_penalty=0.25,
                top_p=0.92
            )
            
            continuation = response.choices[0].message.content.strip()
            continuation = await self._clean_suggestion_continuation(continuation, context)

            return continuation
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating suggestion continuation: {str(e)}"
            )

    async def generate_inline_continuation(
        self, 
        context: str, 
        novel_context: Optional[str] = None,
        style: str = "neutral",
        chapter_id: Optional[int] = None,
        chapter_full_content: Optional[str] = None,
        use_full_context: bool = True
    ) -> str:
        """
        Генерирует инлайн-подсказку (короткое продолжение прямо в тексте).
        """
        if self.client is None:
            raise HTTPException(
                status_code=500,
                detail="OpenAI client not initialized. Please configure OPENAI_API_KEY."
            )
        
        context = context.strip()

        try:
            # Анализируем стиль текста
            detected_style = await self._analyze_writing_style(context)
            
            # Получаем полный контекст если нужно
            enhanced_prompt = None
            if use_full_context and chapter_id and chapter_full_content:
                full_context_for_manager = f"{chapter_full_content}\n{context}".strip()
                full_context_info = context_manager.get_full_context(full_context_for_manager, chapter_id)
                enhanced_prompt = context_manager.build_prompt_context(full_context_info)
            
            # Создаем промпт для генерации
            prompt = await self._create_continuation_prompt(
                context, novel_context, detected_style, style, enhanced_prompt
            )
            
            # Генерируем инлайн-подсказку
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_inline_system_prompt()
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=32,
                temperature=0.45,
                presence_penalty=0.5,
                frequency_penalty=0.3,
                top_p=0.9
            )
            
            continuation = response.choices[0].message.content.strip()
            continuation = await self._clean_inline_continuation(continuation, context)

            # Ensure at least 2 words; if too short, retry once with slightly higher temperature
            try:
                if len(re.findall(r"\S+", continuation)) < 2:
                    retry_resp = await self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": self._get_inline_system_prompt()},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=32,
                        temperature=0.65,
                        presence_penalty=0.4,
                        frequency_penalty=0.2,
                        top_p=0.95
                    )
                    retry_text = retry_resp.choices[0].message.content.strip()
                    retry_text = await self._clean_inline_continuation(retry_text, context)
                    if len(re.findall(r"\S+", retry_text)) >= 2:
                        continuation = retry_text
            except Exception:
                pass

            return continuation
            
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error generating inline continuation: {str(e)}"
            )
    
    def _get_suggestion_system_prompt(self) -> str:
        """Returns the system prompt for standard suggestions (longer continuations)."""
        return (
            "You are a world-class long-form fiction writing assistant embedded in a text editor. "
            "Extend the user's draft with a continuation that reads as if the same author wrote it.\n\n"
            "QUALITY & STYLE:\n"
            "- Be vivid and concrete; prefer showing over telling\n"
            "- Maintain the established point of view and narrative tense\n"
            "- Match the author's voice: vocabulary, syntax, pacing, and tone\n"
            "- Respect genre, mood, continuity, and previously established facts\n\n"
            "CONTINUATION RULES:\n"
            "- Length: aim for about 12–30 words (compact but meaningful)\n"
            "- Advance the scene or dialogue with clear intent; avoid filler\n"
            "- Do not introduce new proper nouns unless plainly implied by context\n"
            "- Avoid repeating phrases already present in the input\n"
            "- Dialogue (if any): keep speaker identity clear; use natural punctuation\n\n"
            "OUTPUT POLICY:\n"
            "- Output the continuation text only (no quotes, no labels, no commentary)\n"
            "- Write in the same language as the input\n"
            "- If the input ends a sentence, begin with a capital letter; otherwise, continue in lower-case\n"
            "- Use natural punctuation only when necessary"
        )

    def _get_inline_system_prompt(self) -> str:
        """Returns the system prompt for inline (very short) suggestions."""
        return (
            "You are a world-class inline autocompletion assistant for creative writing. "
            "Provide a tiny, high-quality continuation that completes the current phrase naturally.\n\n"
            "INLINE GUIDELINES:\n"
            "- Length: strictly 2–6 words\n"
            "- Preserve voice, tense, and point of view\n"
            "- Do not repeat words already present at the end of the input\n"
            "- Output text only (no quotes, no labels, no commentary)\n"
            "- Write in the same language as the input\n"
            "- If the input ends a sentence, begin with a capital letter; otherwise, continue in lower-case\n"
            "- Use minimal punctuation; only when truly necessary"
        )

    async def generate_smart_suggestions(
        self,
        db: Session,
        request: AISuggestionRequest,
        user_id: int
    ) -> List[str]:
        """
        Генерирует несколько вариантов продолжения (как в курсоре).
        """
        try:
            # Получаем контекст главы и новеллы
            chapter_context = ""
            novel_context = ""
            
            if request.chapter_id:
                chapter = db.query(Chapter).filter(Chapter.id == request.chapter_id).first()
                if chapter:
                    chapter_context = chapter.content[-1000:]  # Последние 1000 символов
                    novel = db.query(Novel).filter(Novel.id == chapter.novel_id).first()
                    if novel:
                        novel_context = f"Жанр: {novel.genre}. Описание: {novel.description}"
            
            # Генерируем несколько вариантов (3 запроса с небольшой задержкой)
            suggestions = []
            for i in range(3):
                try:
                    suggestion = await self.generate_suggestion_continuation(
                        request.context.strip(),
                        novel_context,
                        "neutral",
                        min(request.max_length or 100, 100),
                        chapter_id=request.chapter_id,
                        chapter_full_content=chapter_context,
                        use_full_context=True
                    )
                    if suggestion and len(suggestion.strip()) > 0:
                        suggestions.append(suggestion)
                    if i < 2:
                        await asyncio.sleep(0.3)
                except Exception:
                    continue
            
            # Если не удалось сгенерировать варианты, делаем один базовый запрос
            if not suggestions:
                suggestion = await self.generate_suggestion_continuation(
                    request.context.strip(),
                    novel_context,
                    "neutral",
                    100,
                    chapter_id=request.chapter_id,
                    chapter_full_content=chapter_context,
                    use_full_context=True
                )
                if suggestion:
                    suggestions.append(suggestion)
            
            return suggestions[:3]  # Возвращаем максимум 3 варианта
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating suggestions: {str(e)}"
            )
    
    async def _analyze_writing_style(self, text: str) -> Dict[str, Any]:
        """Анализирует стиль написания текста (simple heuristic used only as hints)."""
        style_info = {
            "sentence_length": "medium",
            "complexity": "medium", 
            "tone": "neutral",
            "tense": "past"
        }
        
        if not text:
            return style_info
        
        # Анализ длины предложений
        sentences = re.split(r'[.!?]+', text)
        avg_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len(sentences), 1)
        
        if avg_length < 8:
            style_info["sentence_length"] = "short"
        elif avg_length > 15:
            style_info["sentence_length"] = "long"
        
        # Анализ времени (простой)
        if " был " in text or " была " in text or " были " in text:
            style_info["tense"] = "past"
        elif " есть " in text or " является " in text:
            style_info["tense"] = "present"
        
        # Анализ эмоциональности
        emotional_words = ["восклицал", "кричал", "шептал", "волновался", "радовался", "плакал"]
        if any(word in text.lower() for word in emotional_words):
            style_info["tone"] = "emotional"
        
        return style_info
    
    async def _create_continuation_prompt(
        self, 
        context: str, 
        novel_context: Optional[str], 
        detected_style: Dict[str, Any],
        requested_style: str,
        enhanced_context: Optional[str] = None
    ) -> str:
        """Builds a single prompt with context for text continuation (English)."""
        prompt_lines = []

        if enhanced_context:
            prompt_lines.append("Story context (optional):")
            prompt_lines.append(str(enhanced_context).strip())
            prompt_lines.append("")

        if novel_context:
            prompt_lines.append("Work context (optional):")
            prompt_lines.append(str(novel_context).strip())
            prompt_lines.append("")

        # Style hints derived from heuristic analysis and caller's preference
        if detected_style or requested_style:
            prompt_lines.append("Authorial style hints (not strict, use as guidance):")
            if detected_style:
                tone = detected_style.get("tone", "neutral")
                sent_len = detected_style.get("sentence_length", "medium")
                tense = detected_style.get("tense", "past")
                prompt_lines.append(
                    f"- Typical sentence length: {sent_len}; narrative tense: {tense}; tone: {tone}"
                )
            if requested_style:
                prompt_lines.append(f"- Requested style emphasis: {requested_style}")
            prompt_lines.append("")

        prompt_lines.append("Text to continue:")
        prompt_lines.append(context.strip())
        prompt_lines.append("")
        prompt_lines.append(
            "Task: Continue the text naturally in the same voice while preserving continuity and facts. "
            "Output only the continuation."
        )

        return "\n".join(prompt_lines).strip()
    
    async def _clean_suggestion_continuation(self, continuation: str, original_context: str) -> str:
        """Очищает и форматирует сгенерированную подсказку (для панели подсказок)."""
        clean_continuation = continuation.strip()
        
        # Убираем кавычки, если текст начинается и заканчивается ими
        if clean_continuation.startswith('"') and clean_continuation.endswith('"'):
            clean_continuation = clean_continuation[1:-1].strip()
        
        # Убираем лишние переносы строк
        clean_continuation = re.sub(r'\n{3,}', '\n\n', clean_continuation)

        # Удаляем возможное дублирование начала продолжения с уже введённым текстом
        try:
            context_tail = (original_context or "").strip()[-100:]
            start = clean_continuation
            max_overlap = min(50, len(start), len(context_tail))
            overlap = 0
            lt = context_tail.lower()
            ls = start.lower()
            for k in range(max_overlap, 0, -1):
                if lt.endswith(ls[:k]):
                    overlap = k
                    break
            if overlap:
                clean_continuation = start[overlap:].lstrip()
        except Exception:
            pass
        
        # Ограничиваем длину продолжения для подсказок (10-20 слов)
        try:
            words = re.findall(r"\S+", clean_continuation)
            if len(words) > 20:
                clean_continuation = " ".join(words[:20])
        except Exception:
            pass
        
        # Капитализация первой буквы если нужно
        try:
            tail = (original_context or "").rstrip()
            ends_sentence = len(tail) > 0 and tail[-1] in ".!?"
            if ends_sentence and clean_continuation:
                # Гарантируем пробел и заглавную первую букву
                clean_continuation = clean_continuation.lstrip()
                if clean_continuation and not tail.endswith(' '):
                    clean_continuation = ' ' + clean_continuation
                if clean_continuation.strip():
                    first_char = clean_continuation.lstrip()[0]
                    idx = clean_continuation.find(first_char)
                    clean_continuation = (
                        clean_continuation[:idx] + first_char.upper() + clean_continuation[idx+1:]
                    )
        except Exception:
            pass

        return clean_continuation.strip()

    async def _clean_inline_continuation(self, continuation: str, original_context: str) -> str:
        """Очищает и форматирует инлайн-подсказку (короткую подсказку прямо в тексте)."""
        clean_continuation = continuation.strip()
        
        # Убираем кавычки, если текст начинается и заканчивается ими
        if clean_continuation.startswith('"') and clean_continuation.endswith('"'):
            clean_continuation = clean_continuation[1:-1].strip()
        
        # Убираем лишние переносы строк (для инлайн не нужны)
        clean_continuation = re.sub(r'\n+', ' ', clean_continuation)

        # Удаляем возможное дублирование начала продолжения с уже введённым текстом
        try:
            context_tail = (original_context or "").strip()[-50:]
            start = clean_continuation
            max_overlap = min(25, len(start), len(context_tail))
            overlap = 0
            lt = context_tail.lower()
            ls = start.lower()
            for k in range(max_overlap, 0, -1):
                if lt.endswith(ls[:k]):
                    overlap = k
                    break
            if overlap:
                clean_continuation = start[overlap:].lstrip()
        except Exception:
            pass
        
        # Strictly limit inline suggestion length to 2–6 words
        try:
            words = re.findall(r"\S+", clean_continuation)
            if len(words) > 6:
                clean_continuation = " ".join(words[:6])
        except Exception:
            pass
        
        # Капитализация первой буквы если нужно
        try:
            tail = (original_context or "").rstrip()
            ends_sentence = len(tail) > 0 and tail[-1] in ".!?"
            if ends_sentence and clean_continuation:
                # Гарантируем пробел и заглавную первую букву
                clean_continuation = clean_continuation.lstrip()
                if clean_continuation and not tail.endswith(' '):
                    clean_continuation = ' ' + clean_continuation
                if clean_continuation.strip():
                    first_char = clean_continuation.lstrip()[0]
                    idx = clean_continuation.find(first_char)
                    clean_continuation = (
                        clean_continuation[:idx] + first_char.upper() + clean_continuation[idx+1:]
                    )
        except Exception:
            pass

        return clean_continuation.strip()
    
    async def save_suggestion(
        self,
        db: Session,
        suggestion_text: str,
        request: AISuggestionRequest,
        user_id: int,
        tokens_used: int = 0
    ) -> AISuggestion:
        """Сохраняет сгенерированную подсказку в базу данных."""
        suggestion_data = AISuggestionCreate(
            suggestion_type=request.suggestion_type,
            content=suggestion_text,
            context=request.context,
            chapter_id=request.chapter_id,
            novel_id=request.novel_id,
            user_id=user_id
        )
        
        db_suggestion = AISuggestion(
            suggestion_type=suggestion_data.suggestion_type,
            content=suggestion_data.content,
            context=suggestion_data.context,
            chapter_id=suggestion_data.chapter_id,
            novel_id=suggestion_data.novel_id,
            user_id=suggestion_data.user_id,
            model_used="gpt-4o-mini",
            tokens_used=tokens_used
        )
        
        db.add(db_suggestion)
        db.commit()
        db.refresh(db_suggestion)
        
        return db_suggestion

    async def generate_inline_suggestion(
        self,
        db: Session,
        request: AISuggestionRequest,
        user_id: int
    ) -> str:
        """
        Генерирует одну инлайн-подсказку для отображения прямо в тексте.
        """
        try:
            # Получаем контекст главы и новеллы
            chapter_context = ""
            novel_context = ""
            
            if request.chapter_id:
                chapter = db.query(Chapter).filter(Chapter.id == request.chapter_id).first()
                if chapter:
                    chapter_context = chapter.content[-1000:]  # Последние 1000 символов
                    novel = db.query(Novel).filter(Novel.id == chapter.novel_id).first()
                    if novel:
                        novel_context = f"Жанр: {novel.genre}. Описание: {novel.description}"
            
            # Генерируем инлайн-подсказку
            inline_suggestion = await self.generate_inline_continuation(
                request.context.strip(),
                novel_context,
                "neutral",
                chapter_id=request.chapter_id,
                chapter_full_content=chapter_context,
                use_full_context=True
            )
            
            return inline_suggestion
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating inline suggestion: {str(e)}"
            )

# Глобальный экземпляр сервиса
ai_service = SmartAIService()