"""Spoken story policy only; identifiers, captions and hashtags keep their names."""
import re,unicodedata
STORY_DIRECTION='''احكِ فرضية ماذا لو كحكاية مصرية طبيعية بصيغة المخاطب: تخيّل إنك… ثم الأفعال والنتائج والمفاجأة. البطل بلا اسم منطوق. لا تنطق ستيك مان أو ستيكي مان أو استيكي مان أو Stickman أو آرنولد، ولا تشرح نوع الرسمة للمشاهد. لا تبدأ كل جملة بصاحبنا أو بطلنا أو قام وفعل؛ استخدم فاعلًا مستترًا وروابط سببية طبيعية. ابدأ بالموقف الغريب نفسه، وصعّد العواقب مع كوميديا بصرية ونهاية مرتبطة بالفرضية. هذه قاعدة للسرد المنطوق؛ لا تمنع استعمال اسم نوع الرسوم في الهاشتاجات أو بيانات القناة.'''
def validate_unnamed_story(story):
 spoken=' '.join(scene.get('narration','') for scene in story.get('scenes',[]))
 spoken=''.join(c for c in unicodedata.normalize('NFKC',spoken) if unicodedata.category(c)!='Mn').replace('ـ','')
 patterns=(r'(?<![\u0621-\u064a])(?:ال)?[اأإ]?ست[يى]ك[يى]?\s*مان(?![\u0621-\u064a])',r'\bstick\s*man\b',r'(?:آرنولد|ارنولد|\barnold\b)')
 if any(re.search(pattern,spoken,re.I) for pattern in patterns):raise ValueError('Spoken protagonist must stay unnamed; retain this draft for correction before any voice request')
