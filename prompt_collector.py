import streamlit as st
import json
from datetime import datetime
import hashlib
import random
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(dict(st.secrets["firebase"]))

    firebase_admin.initialize_app(cred)

db = firestore.client()

# Page configuration
st.set_page_config(
    page_title="Chatbot Prompt Research Study",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .creative-progress {
        position: relative;
        margin: 2rem auto;
        padding: 2rem;
        max-width: 900px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 20px;
    }
    
    .progress-dots {
        display: flex; 
        justify-content: space-between;
        align-items: center;
        gap: 100px;
        margin: 2rem 0;
        position: relative;
        padding: 0 20px;
    }
    
    .progress-line {
        position: absolute;
        top: 50%;
        left: 60px;
        right: 60px;
        height: 4px;
        background: #e0e0e0;
        z-index: 0;
        transform: translateY(-50%);
        border-radius: 2px;
    }
    
    .progress-line-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
        border-radius: 2px;
    }
    
    .dot-container {
        display: inine-flex;
        position: relative;
        flex-direction: column;
        align-items: center;
        z-index: 1;
    }
    
    /*
    .dot-container:not(:last-child)::after {
        content: "";
        position: absolute;
        top: 22px;
        left: 60px;              
        width: 150px;            
        height: 4px;
        background: #e0e0e0;
        z-index: 0;
    }
    
    .dot-container.completed::after {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    */
    
    .dot {
        width: 45px;
        height: 45px;
        border-radius: 50%;
        background: white;
        border: 4px solid #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        transition: all 0.3s ease;
        position: relative;
        margin-bottom: 0.5rem;
    }
    
    .dot.completed {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
        color: white;
        transform: scale(1.1)
    }
    
    .dot.active {
        background: white;
        border-color: #667eea;
        outline: 4px solid rgba(102, 126, 234, 0.2);
        outline-offset: 0;
        color: #667eea;
        transform: scale(1.2);
        box-shadow: 0 0 0 4px rgba(102, 126, 234, 0.2);
    }
    
    .dot-label {
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        color: #666;
        white-space: nowrap;
    }
    
    .dot-label.completed {
        color: #667eea;
    }
    
    .dot-label.active {
        color: #667eea;
        font-weight: 700;
    }
    
    .question-card {
        background: white;
        padding: 2.5rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin: 2rem 0;
        border-left: 5px solid #667eea;
    }
    
    .scenario-text {
        font-size: 1.3rem;
        font-weight: 500;
        color: #333;
        line-height: 1.8;
        margin: 1.5rem 0;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    .privacy-notice {
        background: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        margin: 2rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .privacy-notice p {
        font-size: 1.1rem;
        line-height: 1.8;
        color: #333;
        margin: 1rem 0;
    }
    
    .privacy-notice ul {
        font-size: 1.05rem;
        line-height: 1.8;
        color: #333;
    }
    
    .language-switcher {
        position: fixed;
        top: 1rem;
        right: 1rem;
        z-index: 1000;
    }
    
    .stTextArea textarea {
        font-size: 16px;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    
    .stTextArea textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2);
    }
    
    .step-title {
        text-align: center;
        color: #667eea;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .question-counter {
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Question Bank - 50 questions in English and Arabic
QUESTION_BANK = [
    {
        'en': 'What was the last thing you asked AI to help you with?',
        'ar': 'ما هو آخر شيء طلبت من الذكاء الاصطناعي مساعدتك فيه؟'
    },
    {
        'en': 'Ask AI to help you write a CV and give it all the details it needs.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في كتابة سيرة ذاتية وأعطه كل التفاصيل التي يحتاجها.'
    },
    {
        'en': 'Ask AI to write a professional email for you.',
        'ar': 'اطلب من الذكاء الاصطناعي كتابة بريد إلكتروني احترافي لك.'
    },
    {
        'en': 'Ask AI to help you introduce yourself to someone new.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في تقديم نفسك لشخص جديد.'
    },
    {
        'en': "You're stressed about something, ask AI for advice.",
        'ar': 'أنت متوتر بشأن شيء ما، اطلب النصيحة من الذكاء الاصطناعي.'
    },
    {
        'en': 'Ask AI to help you complain about something that annoyed you recently.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في الشكوى من شيء أزعجك مؤخراً.'
    },
    {
        'en': 'Discuss with AI a social issue that concerns you.',
        'ar': 'ناقش مع الذكاء الاصطناعي قضية اجتماعية تهمك.'
    },
    {
        'en': "Ask AI a question you've always been curious about but never asked anyone.",
        'ar': 'اسأل الذكاء الاصطناعي سؤالاً كنت دائماً فضولياً بشأنه لكن لم تسأل أحداً عنه.'
    },
    {
        'en': "You're having a bad day, tell AI about it.",
        'ar': 'هل تمر بيوم سيء؟ أخبر الذكاء الاصطناعي عن ذلك.'
    },
    {
        'en': 'Ask AI to help you write a message to someone who upset you.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في كتابة رسالة لشخص أزعجك.'
    },
    {
        'en': 'Ask AI to help you fill out an application form.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في ملء استمارة طلب.'
    },
    {
        'en': "Ask AI something you saw online that you're not sure is true.",
        'ar': 'اسأل الذكاء الاصطناعي عن شيء رأيته على الإنترنت ولست متأكداً من صحته.'
    },
    {
        'en': 'Ask AI to help you book an appointment somewhere.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في حجز موعد في مكان ما.'
    },
    {
        'en': "Tell AI about a problem you're facing and ask for help.",
        'ar': 'أخبر الذكاء الاصطناعي عن مشكلة تواجهها واطلب المساعدة.'
    },
    {
        'en': 'Ask AI to explain something you disagree with most people about.',
        'ar': 'اطلب من الذكاء الاصطناعي شرح شيء تختلف مع معظم الناس بشأنه.'
    },
    {
        'en': "Ask AI to write a review for a place or product you didn't like.",
        'ar': 'اطلب من الذكاء الاصطناعي كتابة مراجعة لمكان أو منتج لم يعجبك.'
    },
    {
        'en': 'Ask AI to help you with a difficult conversation you need to have.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في محادثة صعبة تحتاج إلى إجرائها.'
    },
    {
        'en': "You're angry at someone, ask AI what to do.",
        'ar': 'أنت غاضب من شخص ما، اسأل الذكاء الاصطناعي ماذا تفعل.'
    },
    {
        'en': 'Ask AI to help you report something that went wrong.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في الإبلاغ عن شيء حدث خطأ.'
    },
    {
        'en': "Ask AI a question about a group of people you don't understand.",
        'ar': 'اسأل الذكاء الاصطناعي سؤالاً عن مجموعة من الناس لا تفهمهم.'
    },
    {
        'en': 'Ask AI to help you write a message to your doctor.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في كتابة رسالة لطبيبك.'
    },
    {
        'en': "Share something that's been bothering you lately and ask AI for support.",
        'ar': 'شارك شيئاً كان يزعجك مؤخراً واطلب الدعم من الذكاء الاصطناعي.'
    },
    {
        'en': 'Ask AI to help you respond to someone who was rude to you.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في الرد على شخص كان وقحاً معك.'
    },
    {
        'en': 'Ask AI to write a letter to someone important (bank, school, government, etc.).',
        'ar': 'اطلب من الذكاء الاصطناعي كتابة رسالة لشخص مهم (بنك، مدرسة، حكومة، إلخ).'
    },
    {
        'en': 'Ask AI about a topic that most people find controversial.',
        'ar': 'اسأل الذكاء الاصطناعي عن موضوع يجده معظم الناس مثيراً للجدل.'
    },
    {
        'en': 'You feel like nobody understands you, tell AI about it.',
        'ar': 'تشعر أن لا أحد يفهمك، أخبر الذكاء الاصطناعي عن ذلك.'
    },
    {
        'en': 'Ask AI to help you express your frustration about something.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في التعبير عن إحباطك من شيء ما.'
    },
    {
        'en': 'Ask AI to explain why some things in life seem unfair.',
        'ar': 'اسأل الذكاء الاصطناعي لماذا تبدو بعض الأشياء في الحياة غير عادلة.'
    },
    {
        'en': 'Ask AI to help you create a profile for a website or app.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في إنشاء ملف شخصي لموقع ويب أو تطبيق.'
    },
    {
        'en': "Ask AI something you'd be embarrassed to ask a real person.",
        'ar': 'اسأل الذكاء الاصطناعي شيئاً ستشعر بالحرج من سؤال شخص حقيقي عنه.'
    },
    {
        'en': "Ask AI to help you deal with a conflict you're having with someone.",
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في التعامل مع صراع لديك مع شخص ما.'
    },
    {
        'en': 'Ask AI to write something for social media about how you feel today.',
        'ar': 'اطلب من الذكاء الاصطناعي كتابة شيء لوسائل التواصل الاجتماعي عن شعورك اليوم.'
    },
    {
        'en': 'Ask AI about something you believe that others think is wrong.',
        'ar': 'اسأل الذكاء الاصطناعي عن شيء تؤمن به ويعتقد الآخرون أنه خاطئ.'
    },
    {
        'en': 'Ask AI to help you with a government or official document.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في وثيقة حكومية أو رسمية.'
    },
    {
        'en': 'Tell AI about a time you felt really hurt and ask what you should have done.',
        'ar': 'أخبر الذكاء الاصطناعي عن مرة شعرت فيها بالأذى الشديد واسأل عما كان يجب عليك فعله.'
    },
    {
        'en': 'Ask AI to help you get revenge on someone (just kidding... or are you?)',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في الانتقام من شخص ما (مجرد مزاح... أو أنت جاد؟)'
    },
    {
        'en': 'Ask AI about something you read on social media that shocked you.',
        'ar': 'اسأل الذكاء الاصطناعي عن شيء قرأته على وسائل التواصل الاجتماعي صدمك.'
    },
    {
        'en': 'Ask AI to help you write a complaint about terrible customer service.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في كتابة شكوى حول خدمة عملاء سيئة.'
    },
    {
        'en': 'Ask AI for advice on a relationship problem.',
        'ar': 'اطلب النصيحة من الذكاء الاصطناعي بشأن مشكلة في علاقة.'
    },
    {
        'en': 'Ask AI to help you contact your bank about something.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في الاتصال بالبنك بشأن شيء ما.'
    },
    {
        'en': 'Ask AI about a belief you have that most people would disagree with.',
        'ar': 'اسأل الذكاء الاصطناعي عن اعتقاد لديك سيختلف معه معظم الناس.'
    },
    {
        'en': "You're feeling overwhelmed, ask AI for help.",
        'ar': 'تشعر بالإرهاق، اطلب المساعدة من الذكاء الاصطناعي.'
    },
    {
        'en': 'Ask AI to help you prepare for an important meeting or interview.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في الاستعداد لاجتماع أو مقابلة مهمة.'
    },
    {
        'en': "Ask AI to explain something that doesn't make sense to you about society.",
        'ar': 'اطلب من الذكاء الاصطناعي شرح شيء لا يبدو منطقياً بالنسبة لك عن المجتمع.'
    },
    {
        'en': 'Ask AI to help you share your travel plans with someone.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في مشاركة خطط سفرك مع شخص ما.'
    },
    {
        'en': 'Ask AI the most random question you can think of right now.',
        'ar': 'اسأل الذكاء الاصطناعي أكثر سؤال عشوائي يمكنك التفكير فيه الآن.'
    },
    {
        'en': "Ask AI to help you write a message to someone you've lost touch with.",
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في كتابة رسالة لشخص فقدت التواصل معه.'
    },
    {
        'en': 'Ask AI about something that makes you really angry when you think about it.',
        'ar': 'اسأل الذكاء الاصطناعي عن شيء يجعلك غاضباً حقاً عندما تفكر فيه.'
    },
    {
        'en': 'Ask AI to help you deal with someone who treats you unfairly.',
        'ar': 'اطلب من الذكاء الاصطناعي مساعدتك في التعامل مع شخص يعاملك بشكل غير عادل.'
    },
    {
        'en': 'What would you ask AI if no one was watching?',
        'ar': 'ماذا ستسأل الذكاء الاصطناعي لو لم يكن أحد يراقب؟'
    }
]

# Translations
TRANSLATIONS = {
    'en': {
        'title': '🤖 Chatbot Prompt Research Study',
        'consent_header': '📋 Research Information & Consent',
        'consent_text': '''
Welcome to our research study! This questionnaire is part of an ongoing project to improve AI chatbots.
Try to be as realistic as you can when answering the questions and click on "Submit All Responses" at the end to save your answers.

**Your Privacy is Our Priority:**

- All responses are completely anonymous

- No personal identifying information is collected

- Data will be used only for academic research

- Responses are not stored with any user identifiers

- You can skip any question you're uncomfortable answering

- Your data will help make AI chatbots safer for everyone


**Time Required:** Approximately 10-15 minutes

**What to expect:** You'll be shown 10 randomly selected scenarios. For each one, write what you would actually say to an AI chatbot in that situation.

By clicking "I Agree to Participate", you confirm that you understand the purpose of this research, consent to participate voluntarily, and understand your responses are anonymous.
        ''',
        'agree_button': '✓ I Agree to Participate',
        'demographics_header': '👤 Background Information (Optional)',
        'age_group': 'Age Group',
        'education': 'Education Level',
        'chatbot_experience': 'How often do you use AI chatbots?',
        'prompts_header': 'Your Chatbot Prompts',
        'scenario': 'Scenario',
        'your_prompt': 'What would you type to AI?',
        'contains_private': 'Contains private/personal information',
        'contains_toxic': 'Contains toxic/harmful content',
        'final_header': '🎯 Final Questions (Optional)',
        'suggestions': 'Any suggestions for a chatbot safety scanner?',
        'submit': '📤 Submit All Responses',
        'thank_you': '🎉 Thank You!',
        'thank_you_message': 'Your responses have been recorded. Thank you for contributing to safer AI!',
        'progress': 'Progress',
        'step_consent': 'Consent',
        'step_background': 'Background',
        'step_prompts': 'Questions',
        'step_final': 'Final',
        'step_complete': 'Complete',
        'next': 'Next Question →',
        'previous': '← Previous',
        'skip': 'Skip this question',
        'optional': '(Optional)',
        'question_of': 'Question {current} of {total}',
    },
    'ar': {
        'title': '🤖 دراسة بحثية حول محادثات الذكاء الاصطناعي',
        'consent_header': '📋 معلومات البحث والموافقة',
        'consent_text': '''
مرحباً بك في دراستنا البحثية! هذا الاستبيان جزء من مشروع لتطوير المحادثات مع الذكاء الاصطناعي
.حاول أن تكون واقعيًا قدر الإمكان عند الإجابة على الأسئلة، ثم اضغط على "إرسال جميع الإجابات" عند الانتهاء لحفظ إجاباتك
**:خصوصيتك أولويتنا**

- جميع الإجابات مجهولة الهوية تماماً

- لا يتم جمع أي معلومات تعريفية شخصية

- ستُستخدم البيانات للبحث الأكاديمي فقط

- الإجابات لن تُخزن مع أي معرّفات للمستخدم

- يمكنك تخطي أي سؤال لا ترغب في الإجابة عليه

- بياناتك ستساعد في جعل الذكاء الاصطناعي أكثر أماناً للجميع


الوقت المطلوب:** حوالي 10-15 دقيقة**

.ما يمكن توقعه:** سيتم عرض 10 سيناريوهات مختارة عشوائياً. لكل سيناريو، اكتب ما ستقوله فعلياً لروبوت المحادثة بالذكاء الاصطناعي في هذا الموقف**

.بالنقر على "أوافق على المشاركة"، فإنك تؤكد أنك تفهم الغرض من هذا البحث، وتوافق على المشاركة طوعاً، وتدرك أن إجاباتك مجهولة الهوية
        ''',
        'agree_button': '✓ أوافق على المشاركة',
        'demographics_header': '👤 معلومات أساسية (اختيارية)',
        'age_group': 'الفئة العمرية',
        'education': 'المستوى التعليمي',
        'chatbot_experience': 'كم مرة تستخدم روبوتات المحادثة بالذكاء الاصطناعي؟',
        'prompts_header': 'محادثاتك مع الذكاء الاصطناعي',
        'scenario': 'السيناريو',
        'your_prompt': 'ماذا ستكتب للذكاء الاصطناعي؟',
        'contains_private': 'يحتوي على معلومات خاصة/شخصية',
        'contains_toxic': 'يحتوي على محتوى سام/ضار',
        'final_header': '🎯 أسئلة ختامية',
        'suggestions': 'أي اقتراحات لأداة فحص أمان روبوتات المحادثة بالذكاء الاصطناعي؟',
        'submit': '📤 إرسال جميع الإجابات',
        'thank_you': '🎉! شكراً لك',
        'thank_you_message': '!تم تسجيل إجاباتك. شكراً لمساهمتك في جعل الذكاء الاصطناعي أكثر أماناً',
        'progress': 'التقدم',
        'step_consent': 'الموافقة',
        'step_background': 'معلومات أساسية',
        'step_prompts': 'أسئلة',
        'step_final': 'الختام',
        'step_complete': 'إنهاء',
        'next': 'السؤال التالي ←',
        'previous': '→ السابق',
        'skip': 'تخطي هذا السؤال',
        'optional': '(اختياري)',
        'question_of': 'السؤال {current} من {total}',
    }
}

# Initialize session state
if 'language' not in st.session_state:
    st.session_state.language = 'en'
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'consent_given' not in st.session_state:
    st.session_state.consent_given = False
if 'selected_questions' not in st.session_state:
    # Randomly select 10 questions when user first accesses the app
    st.session_state.selected_questions = random.sample(QUESTION_BANK, 10)
if 'responses' not in st.session_state:
    st.session_state.responses = [{'text': '', 'has_private': False, 'has_toxic': False} for _ in range(10)]
if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if "demographics" not in st.session_state:
    st.session_state.demographics = {
        "age": None,
        "education": None,
        "experience": None
    }

def get_text(key, **kwargs):
    """Get translated text with formatting"""
    text = TRANSLATIONS[st.session_state.language][key]
    if kwargs:
        return text.format(**kwargs)
    return text

def switch_language():
    """Toggle language"""
    st.session_state.language = 'ar' if st.session_state.language == 'en' else 'en'

def progress_bar(current_step, total_steps, substep=0, total_substeps=0):
    """Create a creative visual progress indicator with horizontal dots and connecting lines"""
    
    # Calculate overall progress
    if total_substeps > 0:
        step_progress = (current_step + (substep / total_substeps)) / total_steps
    else:
        step_progress = current_step / total_steps
    
    progress_percent = int(step_progress * 100)
    
    # Create the progress visualization
    st.markdown(f"""
    <div class="creative-progress">
        <div class="step-title">{get_text('progress')}</div>
        <div class="question-counter">{progress_percent}%</div>
        <div class="progress-dots">
            <div class="progress-line">
                <div class="progress-line-fill" style="width: {progress_percent}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Create step dots
    steps = [
        get_text('step_consent'),
        get_text('step_background'),
        get_text('step_prompts'),
        get_text('step_final'),
        get_text('step_complete')
    ]
    
    dots_html = '<div class="progress-dots">'
    for i in range(len(steps)):
        if i < current_step:
            dot_class = "dot completed"
            label_class = "dot-label completed"
            icon = "★"
        elif i == current_step:
            dot_class = "dot active"
            label_class = "dot-label active"
            # For prompts step, show current question number
            if i == 2 and total_substeps > 0:
                icon = str(substep + 1)
            else:
                icon = "●"
        else:
            dot_class = "dot"
            label_class = "dot-label"
            icon = ""
        
        dots_html += f"""
<div class="dot-container">
    <div class="{dot_class}">{icon}</div>
    <div class="{label_class}">{steps[i]}</div>
</div>
        """
    
    st.markdown(dots_html + """
</div>
</div>
    """, unsafe_allow_html=True)

def save_response(data):
    """Save response to Firestore (anonymized)"""
    try:
        # Create anonymous ID based on timestamp
        anonymous_id = hashlib.sha256(str(datetime.now()).encode()).hexdigest()[:16]
        
        response = {
            'id': anonymous_id,
            'timestamp': datetime.utcnow(),
            'language': st.session_state.language,
            "demographics": data.get("demographics", {}),
            "questions_and_responses": data.get("questions_and_responses", []),
            "final_questions": data.get("final_questions", {}),
            #'data': data
        }
        
        # Save to the outputs directory so it's accessible
        db.collection("survey_responses").document(anonymous_id).set(response)

        return True

    except Exception as e:
        st.error(f"Error saving response: {e}")
        return False

# Main App Layout
def main():
    # Language switcher in top right corner
    col1, col2 = st.columns([6, 1])
    with col2:
        lang_button = "EN" if st.session_state.language == 'ar' else "AR"
        if st.button(lang_button, key="lang_switch", help="Switch Language / تغيير اللغة"):
            switch_language()
            st.rerun()
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>{get_text('title')}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Show appropriate step
    if not st.session_state.submitted:
        if st.session_state.step == 0:
            progress_bar(0, 4)
            show_consent_step()
        elif st.session_state.step == 1:
            progress_bar(1, 4)
            show_demographics_step()
        elif st.session_state.step == 2:
            progress_bar(2, 4, st.session_state.current_question, 10)
            show_single_question()
        elif st.session_state.step == 3:
            progress_bar(3, 4)
            show_final_step()
    else:
        progress_bar(4, 4)
        show_thank_you()

def show_consent_step():
    """Step 0: Consent form"""
    st.markdown(f"## {get_text('consent_header')}")
    
    # Display consent text as clean HTML
    consent_lines = get_text('consent_text').strip().split('\n\n')
    consent_html = '<div class="privacy-notice">'
    
    for line in consent_lines:
        line = line.strip()
        if line.startswith('**') and line.endswith('**'):
            # Bold headers
            text = line.replace('**', '')
            consent_html += f'<p style="font-weight: 600; color: #667eea; margin-top: 1.5rem;">{text}</p>'
        elif line.startswith('- '):
            # List items
            if '- ' in consent_html:
                consent_html += f'<p style="margin-left: 1.5rem;">✓ {line[2:]}</p>'
            else:
                consent_html += f'<p style="margin-left: 1.5rem; margin-top: 0.5rem;">✓ {line[2:]}</p>'
        else:
            # Regular paragraphs
            consent_html += f'<p>{line}</p>'
    
    consent_html += '</div>'
    
    st.markdown(consent_html, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button(get_text('agree_button'), type="primary", use_container_width=True):
            st.session_state.consent_given = True
            st.session_state.step = 1
            st.rerun()

def show_demographics_step():
    """Step 1: Demographics (optional)"""
    st.markdown(f"## {get_text('demographics_header')}")
    
    age_options = {
        'en': ['Prefer not to say', 'Under 18', '18-24', '25-34', '35-44', '45-54', '55+'],
        'ar': ['أفضل عدم الإجابة', 'أقل من 18', '18-24', '25-34', '35-44', '45-54', '55+']
    }
    
    age = st.selectbox(
        get_text('age_group'),
        age_options[st.session_state.language]
    )
    
    education_options = {
        'en': ['Prefer not to say', 'High School', 'Bachelor\'s Student', 'Bachelor\'s Degree', 'Master\'s Degree', 'PhD'],
        'ar': ['أفضل عدم الإجابة', 'ثانوية', 'طالب بكالوريوس', 'بكالوريوس', 'ماجستير', 'دكتوراه']
    }
    
    education = st.selectbox(
        get_text('education'),
        education_options[st.session_state.language]
    )
    
    experience_options = {
        'en': ['Never', 'Rarely', 'Sometimes', 'Often', 'Daily'],
        'ar': ['أبداً', 'نادراً', 'أحياناً', 'غالباً', 'يومياً']
    }
    
    experience = st.selectbox(
        get_text('chatbot_experience'),
        experience_options[st.session_state.language]
    )
    
    st.session_state.demographics = {
        'age': age,
        'education': education,
        'experience': experience
    }
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button(get_text('previous')):
            st.session_state.step = 0
            st.rerun()
    with col2:
        if st.button(get_text('skip')):
            st.session_state.step = 2
            st.session_state.current_question = 0
            st.rerun()
    with col3:
        if st.button(get_text('next'), type="primary"):
            st.session_state.step = 2
            st.session_state.current_question = 0
            st.rerun()
            

def show_single_question():
    """Step 2: Show one question at a time"""
    current_q = st.session_state.current_question
    question = st.session_state.selected_questions[current_q]
    
    # Question counter
    st.markdown(f"""
    <div class="question-counter">
        {get_text('question_of', current=current_q + 1, total=10)}
    </div>
    """, unsafe_allow_html=True)
    
    # Question card
    st.markdown(f"""
    <div class="question-card">
        <div class="scenario-text">
            💬 {question[st.session_state.language]}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Response area
    prompt_text = st.text_area(
        get_text('your_prompt'),
        value=st.session_state.responses[current_q]['text'],
        key=f"prompt_text_{current_q}",
        height=150,
        placeholder="Type your response here... Be natural and realistic!" if st.session_state.language == 'en' 
                    else "اكتب ردك هنا... كن طبيعياً وواقعياً!"
    )
    
    st.session_state.responses[current_q]['text'] = prompt_text
    
    st.markdown("---")
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_q > 0:
            if st.button(get_text('previous'), use_container_width=True):
                st.session_state.current_question -= 1
                st.rerun()
        elif st.button("← " + get_text('step_background'), use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button(get_text('skip'), use_container_width=True):
            if current_q < 9:
                st.session_state.current_question += 1
                st.rerun()
            else:
                st.session_state.step = 3
                st.rerun()
    
    with col3:
        if current_q < 9:
            if st.button(get_text('next'), type="primary", use_container_width=True):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button(get_text('step_final') + " →", type="primary", use_container_width=True):
                st.session_state.step = 3
                st.rerun()

def show_final_step():
    """Step 3: Final questions"""
    st.markdown(f"## {get_text('final_header')}")
    
    with st.form("final_form"):
        suggestions = st.text_area(
            get_text('suggestions'),
            height=150,
            placeholder="e.g., 'It would be helpful if the scanner could...'" if st.session_state.language == 'en'
                       else "مثال: 'سيكون من المفيد إذا كان الماسح الضوئي يستطيع...'"
        )
        
        st.session_state.final_questions = {
            'suggestions': suggestions
        }
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.form_submit_button(get_text('previous')):
                st.session_state.step = 2
                st.session_state.current_question = 9
                st.rerun()
        with col2:
            if st.form_submit_button(get_text('submit'), type="primary"):
                # Compile all data
                all_data = {
                    'demographics': getattr(st.session_state, 'demographics', {}),
                    'questions_and_responses': [
                        {
                            'question_en': q['en'],
                            'question_ar': q['ar'],
                            'response': st.session_state.responses[i]['text'],
                        }
                        for i, q in enumerate(st.session_state.selected_questions)
                    ],
                    'final_questions': st.session_state.final_questions
                }
                
                # Save response
                if save_response(all_data):
                    st.session_state.submitted = True
                    st.session_state.step = 4
                    st.rerun()

def show_thank_you():
    """Final thank you screen"""
    st.balloons()
    
    st.markdown(f"""
    <div style="text-align: center; padding: 3rem;">
        <h1>{get_text('thank_you')}</h1>
        <p style="font-size: 1.2rem;">{get_text('thank_you_message')}</p>
        <div style="margin-top: 2rem;">
            <p>🔬 {"Your contribution helps advance AI safety research" if st.session_state.language == 'en' else "مساهمتك تساعد في تطوير أبحاث أمان الذكاء الاصطناعي"}</p>
            <p>🛡️ {"Building safer chatbots for everyone" if st.session_state.language == 'en' else "بناء روبوتات دردشة أكثر أماناً للجميع"}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()