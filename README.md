# ALTAMIMI Report

**ALTAMIMI Report** is an open-source desktop assistant for organizing legitimate social-media reports. It keeps a local history, opens the target in the user's normal browser, and links to official platform help centers. The final report is intentionally completed by the user through the platform's own interface.

## المميزات

- واجهة عربية حديثة مبنية بـ PySide6.
- يدعم Facebook وInstagram وX/Twitter وTikTok وروابط أخرى.
- حفظ السجل محليًا باستخدام SQLite.
- فتح الحساب/الصفحة/المنشور في المتصفح الافتراضي.
- فتح مركز المساعدة الرسمي للمنصة.
- تصدير السجل بصيغة CSV.
- لا يخزن البريد الإلكتروني أو كلمات المرور.
- لا يرسل أي بيانات إلى خادم تابع للمشروع.
- لا يحتوي على بلاغات جماعية أو anti-detection أو proxy rotation.

## المتطلبات

- Python 3.11 أو أحدث
- Windows 10/11 أو Linux


## تشغيل سريع على Windows

نزّل المشروع ثم شغّل:

```bat
run_windows.bat
```

أو يدويًا:

```bat
py -3.14 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

## تشغيل سريع على Kali / Linux

```bash
chmod +x run_linux.sh
./run_linux.sh
```

أو يدويًا:

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

## بناء ملف EXE

على Windows:

```bat
build_windows.bat
```

سيكون الناتج داخل مجلد `dist`.

## نشره على GitHub

```bash
git init
git add .
git commit -m "Initial release: ALTAMIMI Report v1.0.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ALTAMIMI-Report.git
git push -u origin main
```

بعدها أنشئ Tag مثل `v1.0.0`. Workflow الموجود في `.github/workflows/release-windows.yml` يبني Windows artifact تلقائيًا.

## الخصوصية

قاعدة البيانات تُحفظ في مجلد المستخدم:

- Linux/macOS: `~/.altamimi_report/reports.db`
- Windows: داخل مجلد Home للمستخدم تحت `.altamimi_report`

لا تضع كلمات مرور أو Cookies أو Tokens داخل GitHub.

## الاستخدام المسؤول

المشروع مصمم لتنظيم البلاغات المشروعة ومساعدة المستخدم على الوصول إلى أدوات الإبلاغ الرسمية. لا تستخدمه للمضايقة، البلاغات الكاذبة، تعطيل حسابات الآخرين، أو تجاوز وسائل الحماية الخاصة بالمنصات.

## License

MIT — راجع ملف [LICENSE](LICENSE).
