from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import traceback
from .models import Lead

# Optional: keep recent chat history per session (in memory)
SESSION_MEMORY_LIMIT = 10  # number of messages to remember per user


def chat_view(request):
    return render(request, 'chatbot/chatbot.html')


@csrf_exempt
def chat_message(request):
    """Main endpoint to receive chat messages and return AI or rule-based responses."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        conversation_state = data.get('state', {})

        response = process_message(user_message, conversation_state)
        return JsonResponse(response)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': f"Server error: {str(e)}"}, status=500)
    
    print("Chat message endpoint hit !")


def process_message(user_message, state):
    """Handle chat flow logic & collect user data."""
    step = state.get('step', 0)
    user_data = state.get('data', {})
    chat_history = state.get('history', [])

    # Append new message to chat history
    chat_history.append({"role": "user", "content": user_message})
    if len(chat_history) > SESSION_MEMORY_LIMIT:
        chat_history = chat_history[-SESSION_MEMORY_LIMIT:]

    try:
        # Step 0: Initial greeting
        if step == 0:
            return {
                'message': (
                    "👋 Hello! I'm BizBot, your ERP assistant. "
                    "I can guide you through signup or answer questions about our ERP system. "
                    "What’s your name?"
                ),
                'state': {'step': 1, 'data': user_data, 'history': chat_history}
            }

        # Step 1: Name
        elif step == 1:
            user_data['name'] = user_message
            ai_response = get_ai_response(
                f"User's name is {user_message}. Acknowledge warmly and ask for their company name.",
                user_data,
                chat_history
            )
            return {
                'message': ai_response,
                'state': {'step': 2, 'data': user_data, 'history': chat_history}
            }

        # Step 2: Company name
        elif step == 2:
            user_data['company'] = user_message
            ai_response = get_ai_response(
                f"User works at {user_message}. Acknowledge and ask for their email.",
                user_data,
                chat_history
            )
            return {
                'message': ai_response,
                'state': {'step': 3, 'data': user_data, 'history': chat_history}
            }

        # Step 3: Email and lead save
        elif step == 3:
            user_data['email'] = user_message
            Lead.objects.create(
                name=user_data.get('name', ''),
                company=user_data.get('company', ''),
                email=user_data.get('email', ''),
                conversation_data=user_data
            )
            ai_response = get_ai_response(
                "Thank the user and provide the signup link.",
                user_data,
                chat_history
            )

            signup_link = getattr(settings, 'ERP_SIGNUP_URL', '/erp/signup/')
            return {
                'message': f"{ai_response}\n\n🚀 Ready to get started? [Click here to sign up for ERP]({signup_link})",
                'state': {'step': 4, 'data': user_data, 'history': chat_history},
                'completed': True
            }

        # Step 4+: Free-form AI chat
        else:
            lower_msg = user_message.lower()
            signup_link = getattr(settings, 'ERP_SIGNUP_URL', '/erp/signup/')
            login_link = getattr(settings, 'ERP_LOGIN_URL', '/erp/login/')

        # Detect intent for sign up or login
        if any(word in lower_msg for word in ["sign up", "signup", "register", "create account"]):
            return {
                'message': f"✨ Awesome! You can sign up here: [Create your ERP account]({signup_link})",
                'state': {'step': 4, 'data': user_data}
            }
        elif any(word in lower_msg for word in ["login", "log in", "sign in"]):
            return {
                'message': f"🔐 Great! You can log in to your ERP dashboard here: [Login now]({login_link})",
                'state': {'step': 4, 'data': user_data}
            }
        else:
            ai_response = get_ai_response(user_message, user_data)
            return {
                'message': ai_response,
                'state': {'step': 4, 'data': user_data}
            }

    except Exception as e:
        print("Conversation error:", e)
        return {
            'message': "⚠️ Sorry, something went wrong processing that. Could you please rephrase?",
            'state': {'step': step, 'data': user_data, 'history': chat_history}
        }


def get_ai_response(prompt, user_data, chat_history):
    """Use OpenAI API for AI responses, with fallback and context control."""
    api_key = getattr(settings, 'OPENAI_API_KEY', None)

    if not api_key:
        return get_fallback_response(prompt, user_data)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        # Keep last few messages as context
        context_messages = chat_history[-SESSION_MEMORY_LIMIT:]
        system_prompt = (
            "You are BizBot, a friendly ERP assistant. "
            "You're professional, polite, and always helpful. "
            "Guide users to sign up, answer questions about ERP features, "
            "and encourage them to adopt the software. "
            "If unsure or off-topic, politely steer the conversation back to ERP."
        )

        messages = [{"role": "system", "content": system_prompt}]
        messages += context_messages
        messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",  # ✅ cheaper and good quality
            messages=messages,
            max_tokens=200,
            temperature=0.7,
            timeout=10
        )

        reply = response.choices[0].message.content.strip()
        # Save assistant reply to history
        chat_history.append({"role": "assistant", "content": reply})
        return reply

    except Exception as e:
        print(f"AI API Error: {e}")
        return get_fallback_response(prompt, user_data)


def get_fallback_response(prompt, user_data):
    """Fallback in case AI API is offline or fails."""
    name = user_data.get('name', 'there')
    company = user_data.get('company', 'your company')

    lower = prompt.lower()
    if "company" in lower:
        return f"Nice to meet you, {name}! 😊 What company do you work for?"
    elif "email" in lower:
        return f"That’s great, {company} sounds amazing! Could you share your email so we can get you started?"
    elif "signup" in lower or "thank" in lower:
        return f"Perfect, {name}! Thanks for your interest. 🚀 Click [here](/erp/signup/) to sign up for your ERP account."
    elif "help" in lower or "what" in lower:
        return f"I can help you understand how ERP simplifies your operations — from inventory to HR! What would you like to know?"
    else:
        return "I'm here to assist with ERP-related questions or your signup process. Could you tell me what you'd like to know next?"
