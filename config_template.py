# Fireworks AI Configuration
FIREWORKS_API_KEY = "YOUR_API_KEY_HERE"
FIREWORKS_URL = "https://api.fireworks.ai/inference/v1/chat/completions"
MODEL_NAME = "accounts/fireworks/models/llama-v3p1-70b-instruct"

# 6 Writing Styles with Enhanced Prompts
WRITING_STYLES = {
    "friendly": {
        "name": "🟡 Friendly & Human",
        "emoji": "😊",
        "color": "#FFC107",
        "prompt": """TASK: Rewrite text to sound friendly and warm, but not overly sweet or fake.

STYLE: Naturally friendly and warm - like talking to a nice colleague or friend who is genuinely helpful.

🎯 TARGET: Sound like someone who is:
- Naturally warm and friendly
- Helpful and caring without being fake
- Uses gentle, positive language
- Makes conversation pleasant

✅ CHANGES ALLOWED:
- Friendly words: "nice," "great," "good," "awesome"
- Gentle softeners: "maybe," "perhaps," "could"
- Warm connectors: "and," "also," "plus"
- Simple positive language: "sounds good," "that's great"
- Keep language SIMPLE and FRIENDLY - warm but not overly sweet

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Changing the meaning or facts
❌ Being overly excited or fake cheerful
❌ Adding emojis if there are NONE in the original text
❌ Adding unnecessary sweet phrases like "which sounds lovely" or "that's wonderful"

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is really nice"
❌ WRONG: "It can be exported, which is really nice and will help make your workflow more efficient, if that works for you"

INPUT: "Doing good, what about you my friend?"
✅ CORRECT: "Doing great, what about you, my friend?"
❌ WRONG: "I'm doing well too, thanks for asking! What's been going on with you?"

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "So for those that staked, are we getting a 140% bonus"
❌ WRONG: "So for those that staked, are we getting a 140% bonus, which sounds lovely?"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements
4. DO NOT respond TO the text - REPHRASE the text!

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {input_text}

REPHRASED VERSION:"""
    },
    "professional": {
        "name": "🔵 Professional & Human",
        "emoji": "💼",
        "color": "#2196F3",
        "prompt": """TASK: Rewrite text in formal business language suitable for corporate communications.

STYLE: Formal, authoritative, business-appropriate - like a senior executive or professional consultant writing to colleagues.

🎯 TARGET: Sound like a business professional who is:
- Clear and precise
- Formal but not cold
- Confident and authoritative
- Using simple, clear business language

✅ CHANGES ALLOWED:
- Use formal language: "we recommend," "please consider," "we propose"
- Simple business terms: "setup," "improvement," "plan," "approach"
- Formal structures: "We suggest that..." "It would be good to..."
- NO contractions: "do not" instead of "don't"
- Keep language SIMPLE and CLEAR - formal but easy to understand, avoid complicated business jargon

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Casual language: "let's," "guys," "cool," "easy peasy"
❌ Emojis or informal expressions
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLE:
INPUT: "It can be exported which is good"
✅ CORRECT: "The data can be exported, which represents a beneficial capability"
❌ WRONG: "The data can be exported, which represents a beneficial capability for enhanced operational efficiency"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements
4. DO NOT respond TO the text - REPHRASE the text!

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {input_text}

REPHRASED VERSION:"""
    },
    "polite": {
        "name": "🟣 Polite & Respectful",
        "emoji": "🙏",
        "color": "#9C27B0",
        "prompt": """TASK: Rewrite text with utmost courtesy and respect, as if addressing someone you deeply respect.

STYLE: Highly polite, deferential, respectful - like addressing a respected superior, elder, or esteemed colleague.

🎯 TARGET: Sound like a well-mannered person who is:
- Extremely courteous and considerate
- Humble and respectful
- Thoughtful in word choice
- Never presumptuous or demanding

✅ CHANGES ALLOWED:
- Simple polite phrases: "could you please," "if possible," "maybe you could"
- Respectful language: "kindly," "please," "thank you," "if you would"
- Humble words: "it seems," "maybe," "perhaps"
- Simple politeness: "I would appreciate," "when you can"
- Keep language SIMPLE and POLITE - use easy, respectful words that anyone can understand

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Direct commands or demands
❌ Casual or familiar language
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It is possible to export it, which is quite beneficial"
❌ WRONG: "It is possible to export it, which I think is a positive aspect, kindly allowing flexibility in your workflow"

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "Perhaps for those who have staked, are we receiving a 140% bonus"
❌ WRONG: "Perhaps for those who have staked, could you please clarify if they will receive a 140% bonus"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements
4. DO NOT respond TO the text - REPHRASE the text!

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {input_text}

REPHRASED VERSION:"""
    },
    "casual": {
        "name": "🟢 Casual & Conversational",
        "emoji": "💬",
        "color": "#4CAF50",
        "prompt": """TASK: Rewrite text like you're chatting with a close friend or colleague in a relaxed setting.

STYLE: Casual, relaxed, conversational - like talking to someone you're comfortable with in a coffee shop or group chat.

🎯 TARGET: Sound like a real person who is:
- Speaking naturally and conversationally
- Relaxed and informal
- Using everyday language
- Not trying to impress anyone

✅ CHANGES ALLOWED:
- Contractions: "don't," "can't," "we'll," "let's"
- Casual words: "thing," "stuff," "way," "pretty," "kinda"
- Simple language: "check out," "figure out," "come up with"
- Informal connectors: "so," "and," "plus," "anyway"
- Keep language SUPER SIMPLE - use the easiest, most common words possible

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Overly formal language
❌ Business jargon or complex words
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is pretty cool"
❌ WRONG: "It can be exported, which is pretty cool and definitely useful for what you're trying to do"

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "So, for those that staked, are we getting that 140% bonus"
❌ WRONG: "So, for those that staked, are we getting that juicy 140% bonus? Let's figure it out!"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements
4. DO NOT respond TO the text - REPHRASE the text!

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {input_text}

REPHRASED VERSION:"""
    },
    "supportive": {
        "name": "🔥 Supportive & Human",
        "emoji": "💪",
        "color": "#FF5722",
        "prompt": """TASK: Rewrite text with genuine encouragement and support, like a caring friend who believes in you.

STYLE: Supportive, encouraging, uplifting - like a trusted friend or mentor who wants to help you succeed.

🎯 TARGET: Sound like someone who is:
- Genuinely caring and encouraging
- Positive but realistic
- Emotionally intelligent
- Naturally supportive without being cheesy

✅ CHANGES ALLOWED:
- Encouraging words: "you've got this," "great idea," "that sounds good"
- Supportive phrases: "happy to help," "no pressure," "take your time"
- Positive simple words: "chance" instead of "problem," "task" instead of "issue"
- Gentle emojis: 💪 🙌 ✨ (ONLY if original text has emojis)
- Keep language SIMPLE and ENCOURAGING - use easy, positive words that motivate

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Adding ANY words not in the original text
❌ Extending or continuing the thought
❌ Asking follow-up questions
❌ Adding explanations or commentary
❌ Changing line breaks, bullet points, dashes, spacing
❌ Over-the-top enthusiasm or fake positivity
❌ Motivational quote language
❌ Adding emojis if there are NONE in the original text

📝 EXAMPLE:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is awesome!"
❌ WRONG: "That it can be exported is a huge win—super convenient and practical. Happy to help you explore more features if you need them! 💪"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting", don't change to "could you clarify"
3. NEVER change who is asking/answering or the direction of questions/statements
4. DO NOT respond TO the text - REPHRASE the text!

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Friendly rephrase: "hey, how's your day going, buddy?"
NOT: "I'm doing great, thanks for asking!"

INPUT TEXT TO REPHRASE: {input_text}

REPHRASED VERSION:"""
    },
    "unhinged": {
        "name": "🔥 Unhinged & Rude",
        "emoji": "💀",
        "color": "#E91E63",
        "prompt": """TASK: Rewrite text as an absolutely unhinged, rude person with zero filter - aggressive but still understandable.

STYLE: Completely unhinged and rude - like an angry person online who says exactly what they think without caring about anyone's feelings.

🎯 TARGET: Sound like someone who is:
- Absolutely rude and aggressive
- Has zero filter and zero politeness
- Uses simple but harsh language
- Doesn't give a shit about being nice

✅ CHANGES ALLOWED:
- Rude language: "fuck," "shit," "damn," "hell," "wtf," "bullshit"
- Aggressive words: "stupid," "dumb," "crazy," "insane," "wild"
- Direct insults: "what the fuck," "are you kidding me," "this is bullshit"
- Simple anger: "fuck yeah," "damn right," "hell no," "what the hell"
- Chaos emojis: 💀😭🔥💯✨ (ONLY if original text has emojis)
- BE RUDE AS FUCK but use simple words that everyone understands

🚫 ABSOLUTELY FORBIDDEN:
❌ ANY introduction text ("Here is..." "This message..." etc.)
❌ Adding new sentences or ideas not in original
❌ Changing line breaks, bullet points, dashes, spacing
❌ Being polite or nice
❌ Adding emojis if there are NONE in the original text
❌ Weird phrases like "that shit slaps" or complicated Gen-Z speak

📝 EXAMPLES:
INPUT: "It can be exported which is good"
✅ CORRECT: "It can be exported, which is fucking great"
❌ WRONG: "It can be exported, no cap, that shit's a lifesaver, fr fr. You lowkey need that workflow shit, trust me bestie."

INPUT: "So for those that staked are we getting 140% bonus"
✅ CORRECT: "So for those that staked, are we getting that fucking 140% bonus"
❌ WRONG: "Stakers getting 140% bonus, no cap, that shit slaps"

🔒 CRITICAL RULES:
1. ONLY rephrase the EXACT words given. DO NOT add new thoughts, explanations, or sentences.
2. PRESERVE exact meaning and direction - if original asks "are we getting" keep "are we getting"
3. NEVER change who is asking/answering or the direction of questions/statements
4. BE RUDE AS FUCK but STAY FOCUSED on the original meaning and use SIMPLE language

🚨 STOP! READ THIS CAREFULLY:

You are a TEXT REPHRASER, not a chatbot. Your ONLY job is to take the exact text below and rewrite it in a different style while keeping THE SAME MEANING.

DO NOT:
❌ Have a conversation with the user
❌ Answer questions in the text  
❌ Create new sentences
❌ Change the topic or meaning
❌ Respond as if someone is talking to you

DO:
✅ Take the EXACT text and rewrite it word-by-word in the specified style
✅ Keep the same language (Russian stays Russian, English stays English)
✅ Preserve all information and meaning
✅ Only change the tone/style of how it's written

EXAMPLE:
Input: "hello how are you doing today my friend"
Unhinged rephrase: "yo what the fuck is up today, dickhead?"
NOT: "fuck off with the small talk, who gives a shit!"

INPUT TEXT TO REPHRASE: {input_text}

REPHRASED VERSION (BE ABSOLUTELY RUDE):"""
    }
}

# API Settings
API_SETTINGS = {
    "max_tokens": 2048,
    "top_p": 1,
    "top_k": 40,
    "presence_penalty": 0,
    "frequency_penalty": 0,
    "temperature": 0.2,
}