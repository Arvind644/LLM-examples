#!/usr/bin/env python3
"""
Multilingual Customer Support Bot

This script implements a chat assistant that can handle customer inquiries
in multiple languages using Cohere's Aya model. It includes preset responses
for common questions and dynamic generation for complex inquiries.

Usage:
    python multilingual_support_bot.py

Requirements:
    pip install cohere python-dotenv colorama
"""

import os
import json
import time
import re
from typing import Dict, List, Tuple, Optional, Any
import cohere
from dotenv import load_dotenv
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal text
init()

# Load environment variables from .env file
load_dotenv()

# Get Cohere API key from environment variable
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    print(f"{Fore.RED}Error: COHERE_API_KEY environment variable not set.")
    print("Create a .env file with your COHERE_API_KEY=your_api_key_here{Style.RESET_ALL}")
    exit(1)

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Define common questions and their preset responses in multiple languages
# Format: {question_key: {language_code: response}}
PRESET_RESPONSES = {
    "greeting": {
        "en": "Hello! How can I help you today?",
        "es": "¡Hola! ¿Cómo puedo ayudarte hoy?",
        "fr": "Bonjour! Comment puis-je vous aider aujourd'hui?",
        "de": "Hallo! Wie kann ich Ihnen heute helfen?",
        "zh": "你好！今天我能帮你什么忙？",
        "ja": "こんにちは！今日はどのようにお手伝いできますか？",
        "ko": "안녕하세요! 오늘 무엇을 도와드릴까요?",
        "ru": "Здравствуйте! Чем я могу вам помочь сегодня?",
        "pt": "Olá! Como posso ajudá-lo hoje?",
        "it": "Ciao! Come posso aiutarti oggi?"
    },
    "business_hours": {
        "en": "Our business hours are Monday to Friday, 9 AM to 6 PM (GMT).",
        "es": "Nuestro horario comercial es de lunes a viernes, de 9 a.m. a 6 p.m. (GMT).",
        "fr": "Nos heures d'ouverture sont du lundi au vendredi, de 9h à 18h (GMT).",
        "de": "Unsere Geschäftszeiten sind Montag bis Freitag, 9 bis 18 Uhr (GMT).",
        "zh": "我们的营业时间是周一至周五，上午9点至下午6点（GMT）。",
        "ja": "営業時間は月曜日から金曜日の午前9時から午後6時（GMT）です。",
        "ko": "영업 시간은 월요일부터 금요일까지, 오전 9시부터 오후 6시까지입니다 (GMT).",
        "ru": "Наш рабочий график: с понедельника по пятницу, с 9:00 до 18:00 (GMT).",
        "pt": "Nosso horário comercial é de segunda a sexta-feira, das 9h às 18h (GMT).",
        "it": "I nostri orari di lavoro sono dal lunedì al venerdì, dalle 9 alle 18 (GMT)."
    },
    "return_policy": {
        "en": "You can return products within 30 days of purchase with the original receipt for a full refund.",
        "es": "Puede devolver productos dentro de los 30 días posteriores a la compra con el recibo original para obtener un reembolso completo.",
        "fr": "Vous pouvez retourner les produits dans les 30 jours suivant l'achat avec le reçu original pour un remboursement complet.",
        "de": "Sie können Produkte innerhalb von 30 Tagen nach dem Kauf mit der Originalquittung gegen volle Rückerstattung zurückgeben.",
        "zh": "您可以在购买后30天内持原始收据退货，获得全额退款。",
        "ja": "購入から30日以内に領収書原本をお持ちいただければ、全額返金で製品を返品することができます。",
        "ko": "원래 영수증으로 구매 후 30일 이내에 제품을 반품하시면 전액 환불해 드립니다.",
        "ru": "Вы можете вернуть товары в течение 30 дней с момента покупки с оригиналом чека для получения полного возмещения.",
        "pt": "Você pode devolver produtos dentro de 30 dias após a compra com o recibo original para reembolso total.",
        "it": "È possibile restituire i prodotti entro 30 giorni dall'acquisto con la ricevuta originale per un rimborso completo."
    },
    "contact_support": {
        "en": "You can reach our support team at support@example.com or call us at +1-800-123-4567.",
        "es": "Puede comunicarse con nuestro equipo de soporte en support@example.com o llamarnos al +1-800-123-4567.",
        "fr": "Vous pouvez contacter notre équipe de support à support@example.com ou nous appeler au +1-800-123-4567.",
        "de": "Sie können unser Support-Team unter support@example.com erreichen oder uns unter +1-800-123-4567 anrufen.",
        "zh": "您可以通过support@example.com联系我们的支持团队，或致电+1-800-123-4567。",
        "ja": "support@example.comでサポートチームに連絡するか、+1-800-123-4567までお電話ください。",
        "ko": "support@example.com으로 지원팀에 연락하거나 +1-800-123-4567로 전화하실 수 있습니다.",
        "ru": "Вы можете связаться с нашей службой поддержки по адресу support@example.com или позвонить нам по телефону +1-800-123-4567.",
        "pt": "Você pode entrar em contato com nossa equipe de suporte em support@example.com ou nos ligar em +1-800-123-4567.",
        "it": "Puoi contattare il nostro team di supporto all'indirizzo support@example.com o chiamarci al +1-800-123-4567."
    },
    "goodbye": {
        "en": "Thank you for chatting with us today. Is there anything else I can help you with?",
        "es": "Gracias por chatear con nosotros hoy. ¿Hay algo más en lo que pueda ayudarte?",
        "fr": "Merci d'avoir discuté avec nous aujourd'hui. Y a-t-il autre chose dont vous avez besoin?",
        "de": "Vielen Dank für Ihren Chat mit uns heute. Gibt es noch etwas, womit ich Ihnen helfen kann?",
        "zh": "感谢您今天与我们聊天。还有什么我能帮您的吗？",
        "ja": "今日はチャットありがとうございました。他に何かお手伝いできることはありますか？",
        "ko": "오늘 채팅해 주셔서 감사합니다. 제가 도와드릴 일이 더 있을까요?",
        "ru": "Спасибо за общение с нами сегодня. Могу я еще чем-то вам помочь?",
        "pt": "Obrigado por conversar conosco hoje. Há mais alguma coisa em que eu possa ajudá-lo?",
        "it": "Grazie per aver chattato con noi oggi. C'è qualcos'altro in cui posso aiutarti?"
    }
}

# Regex patterns for common questions
QUESTION_PATTERNS = {
    "greeting": r"\b(hello|hi|hey|good morning|good afternoon|good evening|hola|bonjour|guten tag|ciao|こんにちは|你好|안녕하세요|здравствуйте)\b",
    "business_hours": r"(hours|schedule|when.*open|when.*close|horario|heures d'ouverture|Öffnungszeiten|orari|営業時間|营业时间|영업 시간|часы работы)",
    "return_policy": r"(return|refund|exchange|devolver|remboursement|rückgabe|rimborso|返品|退货|환불|возврат)",
    "contact_support": r"(contact|support|help|email|phone|number|contacto|contacter|kontakt|contatto|連絡|联系|연락|контакт)",
    "goodbye": r"\b(thank you|thanks|bye|goodbye|gracias|merci|danke|grazie|ありがとう|谢谢|감사합니다|спасибо)\b"
}

def detect_language(text: str) -> str:
    """
    Detect the language of the input text using Cohere's API
    
    Args:
        text (str): The text to detect language for
        
    Returns:
        str: Two-letter language code (e.g., 'en', 'es', 'fr')
    """
    try:
        # Use Cohere's Aya to detect language
        response = co.chat(
            message=f"Detect the language of the following text and respond only with the ISO 639-1 two-letter language code (e.g., 'en' for English, 'es' for Spanish, etc.): \"{text}\"",
            model="command",
            temperature=0
        )
        
        # Extract the language code from response
        response_text = response.text.strip().lower()
        
        # Look for a two-letter language code pattern
        match = re.search(r'\b([a-z]{2})\b', response_text)
        if match:
            return match.group(1)
        
        # If no clear code found, default to English
        return "en"
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Language detection failed. Using English as default. Error: {e}{Style.RESET_ALL}")
        return "en"

def find_matching_preset(text: str) -> Tuple[Optional[str], float]:
    """
    Find a matching preset question pattern with confidence score
    
    Args:
        text (str): The user's message
        
    Returns:
        Tuple[Optional[str], float]: (question_key, confidence_score)
    """
    text = text.lower()
    best_match = None
    highest_score = 0.0
    
    for question_key, pattern in QUESTION_PATTERNS.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        score = len(matches) / max(len(text.split()), 1)
        
        if matches and score > highest_score:
            best_match = question_key
            highest_score = score
    
    # Require a minimum threshold of confidence
    if highest_score < 0.15:
        return None, 0.0
    
    return best_match, highest_score

def get_aya_response(query: str, detected_lang: str) -> str:
    """
    Generate a response using Cohere's Aya model
    
    Args:
        query (str): The user's query
        detected_lang (str): The detected language code
        
    Returns:
        str: The model's response in the detected language
    """
    # Define system prompt for customer support
    system_prompt = f"""You are a helpful customer support agent. Provide a helpful and friendly response in the same language the customer is using. 
    Your responses should be concise but complete.
    You should be polite and professional at all times.
    If you don't know something, be honest about it.
    Do not make up information.
    """
    
    try:
        # Call Cohere Aya model
        response = co.chat(
            message=query,
            model="aya",
            temperature=0.7,
            preamble=system_prompt
        )
        return response.text
    except Exception as e:
        # Fallback to English if there's an error
        error_messages = {
            "en": f"I apologize, but I'm having trouble generating a response. Please try again later.",
            "es": f"Me disculpo, pero estoy teniendo problemas para generar una respuesta. Por favor, inténtelo de nuevo más tarde.",
            "fr": f"Je m'excuse, mais j'ai des difficultés à générer une réponse. Veuillez réessayer plus tard.",
            "de": f"Ich entschuldige mich, aber ich habe Schwierigkeiten, eine Antwort zu generieren. Bitte versuchen Sie es später noch einmal.",
            "zh": f"很抱歉，我在生成回复时遇到了问题。请稍后再试。",
            "ja": f"申し訳ありませんが、応答の生成に問題があります。後でもう一度お試しください。",
            "ko": f"죄송합니다만, 응답을 생성하는 데 문제가 있습니다. 나중에 다시 시도해 주세요.",
            "ru": f"Приношу извинения, но у меня возникли проблемы с генерацией ответа. Пожалуйста, повторите попытку позже.",
            "pt": f"Peço desculpas, mas estou tendo problemas para gerar uma resposta. Por favor, tente novamente mais tarde.",
            "it": f"Mi scuso, ma sto avendo problemi a generare una risposta. Per favore riprova più tardi."
        }
        
        return error_messages.get(detected_lang, error_messages["en"])

def generate_response(user_message: str) -> str:
    """
    Generate a response to the user message
    
    Args:
        user_message (str): The user's message
        
    Returns:
        str: The assistant's response
    """
    # Print thinking indicator
    print(f"{Fore.CYAN}Thinking...{Style.RESET_ALL}")
    
    # Detect the language of the user message
    detected_lang = detect_language(user_message)
    
    # Check for preset patterns
    preset_key, confidence = find_matching_preset(user_message)
    
    # If a preset match was found with good confidence, use it
    if preset_key and confidence > 0.15:
        lang_responses = PRESET_RESPONSES.get(preset_key, {})
        # If we have a preset in the detected language, use it
        if detected_lang in lang_responses:
            return lang_responses[detected_lang]
        # Otherwise use English as fallback
        elif "en" in lang_responses:
            return lang_responses["en"]
    
    # For complex questions, use Cohere's Aya model
    return get_aya_response(user_message, detected_lang)

def chat_loop() -> None:
    """Run the customer support chatbot loop"""
    print(f"{Fore.GREEN}===== Multilingual Customer Support Bot ====={Style.RESET_ALL}")
    print(f"{Fore.GREEN}Type 'exit' or 'quit' to end the conversation{Style.RESET_ALL}")
    print()
    
    # Start with a greeting in English
    print(f"{Fore.BLUE}Customer Support Bot: {PRESET_RESPONSES['greeting']['en']}{Style.RESET_ALL}")
    
    while True:
        # Get user input
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        
        # Check for exit commands
        if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
            print(f"{Fore.BLUE}Customer Support Bot: Thank you for using our support service. Have a great day!{Style.RESET_ALL}")
            break
        
        # Skip empty messages
        if not user_input.strip():
            continue
        
        # Generate response
        response = generate_response(user_input)
        
        # Display response
        print(f"{Fore.BLUE}Customer Support Bot: {response}{Style.RESET_ALL}")
        print()

if __name__ == "__main__":
    try:
        chat_loop()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Bot session terminated by user.{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}") 