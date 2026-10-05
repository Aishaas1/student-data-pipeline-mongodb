# Student Data Pipeline

## Project Overview

هذا المشروع عبارة عن Pipeline هندسي لدمج بيانات الطلاب من خمسة مصادر مختلفة:

1. CSV
2. REST API
3. SQLite Database
4. MongoDB
5. Web Scraping (HTML)

تم تصميم المشروع لتنفيذ المراحل التالية:

Extract → Validate → Clean → Integrate → Transform → Final Validation → Load

الهدف هو إنتاج Dataset نهائي منظم ونظيف وقابل للاستخدام في التحليل وذكاء الأعمال وتطبيقات تعلم الآلة.

## Architecture

```text
student_data_pipeline/
├── app/
│   ├── sources/
│   │   ├── csv_source.py
│   │   ├── api_source.py
│   │   ├── database_source.py
│   │   └── mongodb_source.py
│   ├── transformation/
│   │   ├── cleaner.py
│   │   ├── transformer.py
│   │   └── integration.py
│   ├── validation/
│   │   └── quality.py
│   ├── output/
│   │   └── csv_writer.py
│   └── utils/
│       └── logger.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── rejected/
├── database/
├── logs/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## Data Sources

### CSV

يحتوي على البيانات الأساسية للطالب:

- student_id
- student_name
- age
- major
- city

### REST API

يحتوي على البيانات الأكاديمية:

- student_id
- gpa
- attendance
- status

تم إنشاء Mock REST API محلي حتى يعمل المشروع بدون الاعتماد على الإنترنت.

### Web Scraping

يتم جلب بيانات إضافية من صفحة HTML من خلال Web Scraping باستخدام `requests` و`BeautifulSoup`.

البيانات الخام لهذا المصدر محفوظة كصفحة HTML وليست JSON، ويتم استخراج:

- student_id
- program
- enrollment_type

ويتم تشغيل صفحة HTML محليًا ثم جلبها عبر HTTP حتى يكون المشروع قابلًا للتشغيل والاختبار بدون الاعتماد على موقع خارجي.

### SQLite

تحتوي قاعدة البيانات على:

- courses
- enrollments

ويتم استخدام SQL JOIN لاستخراج:

- student_id
- course
- score
- semester

### MongoDB

تمت إضافة MongoDB كمصدر رابع قابل للتشغيل بطريقتين.

الوضع الافتراضي يستخدم بيانات Mock بنفس شكل وثائق MongoDB حتى يعمل المشروع مباشرة بدون الحاجة إلى تشغيل خادم MongoDB.

يمكن تشغيل MongoDB الحقيقي من خلال تغيير use_mock إلى False في main.py.

بيانات MongoDB تحتوي على:

- student_id
- advisor
- scholarship
- department

## ETL Pipeline

### Extract

يتم استخراج البيانات من CSV وREST API وSQLite وMongoDB وWeb Scraping في طبقات منفصلة.

### Validate

يتم فحص:

- student_id
- age
- GPA
- attendance
- score

### Clean

يتم:

- إزالة التكرارات
- إزالة المسافات الزائدة
- توحيد حالة النصوص
- تحويل الأنواع
- تجهيز القيم المفقودة

### Integrate

يتم دمج المصادر باستخدام student_id كمفتاح مشترك.

### Transform

تم تنفيذ التحويلات التالية:

- تعويض GPA المفقود بالوسيط
- تعويض attendance المفقود بالوسيط
- حساب average_score
- حساب course_count
- إنشاء performance_level
- إنشاء attendance_status
- إضافة source

### Final Validation

يتم فحص Dataset النهائي قبل حفظه.

### Load

يتم إنشاء:

```text
data/processed/final_dataset.csv
data/rejected/rejected_records.csv
logs/pipeline.log
```

## Data Quality

تم تطبيق القواعد التالية:

1. student_id لا يمكن أن يكون NULL.
2. student_id يجب أن يكون فريداً في المصدر الأساسي.
3. العمر يجب أن يكون بين 16 و80.
4. GPA يجب أن يكون بين 0 و4.
5. attendance يجب أن يكون بين 0 و100.
6. score يجب أن يكون بين 0 و100.
7. يجب أن يكون student_id متوافقاً بين المصادر.

## Missing Values

تم استخدام Median لتعويض GPA وattendance لأن الوسيط أقل تأثراً بالقيم المتطرفة، كما تم تعويض average_score بالوسيط بعد الدمج.

## Duplicate Records

تم اكتشاف التكرارات باستخدام student_id في مصدر CSV، ثم الاحتفاظ بأول سجل وحذف السجلات المكررة.

## Invalid Records

السجلات التي تفشل في قواعد الجودة يتم تسجيلها في:

```text
data/rejected/rejected_records.csv
```

ويتم حفظ سبب الرفض ومصدر السجل.

## Logging

يتم تسجيل مراحل التشغيل في:

```text
logs/pipeline.log
```

## Installation

```bash
py -m pip install -r requirements.txt
```

## Running

```bash
py main.py
```

## Testing

```bash
py -m pytest -q
```

## Output

### final_dataset.csv

الملف النهائي يحتوي على البيانات المدمجة والمنظفة والمتحقق منها.

### rejected_records.csv

يحتوي على السجلات التي لم تجتز قواعد الجودة مع سبب الرفض.

### pipeline.log

يحتوي على سجل مراحل تنفيذ Pipeline.

## MongoDB Real Connection

لتشغيل MongoDB الحقيقي:

1. تأكد من تشغيل MongoDB.
2. عدّل use_mock إلى False.
3. استخدم URI الخاص بخادم MongoDB.

مثال:

```python
extract_mongodb(
    uri="mongodb://localhost:27017",
    database_name="student_pipeline",
    collection_name="student_profiles",
    seed_path=MONGO_SEED_PATH,
    use_mock=False,
)
```

## Tests

تم اختبار:

- تحميل CSV
- الاتصال بالـ REST API
- استخراج SQLite
- استخراج MongoDB
- إزالة التكرارات
- معالجة القيم المفقودة
- رفض السجلات غير الصالحة
- دمج المصادر
- إنشاء الملفات النهائية

## Questions and Answers

### 1. لماذا نحتاج إلى Data Pipeline عند التعامل مع مصادر متعددة؟

لأن البيانات في الأنظمة الحقيقية تكون موزعة بين ملفات وقواعد بيانات وواجهات API وأنظمة أخرى، ويحتاج التحليل إلى بيانات موحدة ونظيفة.

### 2. ما الفرق بين Raw Data وProcessed Data؟

Raw Data هي البيانات كما وصلت من المصدر، بينما Processed Data هي البيانات بعد التنظيف والتحويل والتحقق والدمج.

### 3. ما الفرق بين Extract وTransform وLoad؟

Extract تعني استخراج البيانات، Transform تعني تنظيف وتحويل البيانات، وLoad تعني حفظ البيانات الناتجة في الوجهة النهائية.

### 4. ما المشاكل التي واجهتها أثناء دمج البيانات؟

أهم المشاكل كانت اختلاف جودة البيانات، التكرارات، القيم المفقودة، واختلاف شكل البيانات بين المصادر.

### 5. كيف تعاملت مع Missing Values؟

استخدمت Median لتعويض GPA وattendance والقيم الرقمية المناسبة بعد التأكد من نوع البيانات.

### 6. كيف تعاملت مع Duplicate Records؟

تم اكتشاف التكرارات باستخدام student_id والاحتفاظ بأول سجل.

### 7. كيف تعاملت مع Invalid Records؟

تم تطبيق قواعد Validation وتسجيل السجلات غير الصالحة في rejected_records.csv مع سبب الرفض.

### 8. لماذا يجب فصل Extraction عن Transformation؟

لفصل مسؤولية الحصول على البيانات عن مسؤولية تنظيفها وتحويلها، مما يجعل المشروع أسهل في الصيانة والتطوير.

### 9. لماذا يعتبر Data Validation جزءاً أساسياً من Data Engineering؟

لأن البيانات غير الصحيحة قد تؤدي إلى نتائج تحليلية أو نماذج تعلم آلة غير صحيحة.

### 10. كيف يمكن تطوير Pipeline ليعمل بشكل دوري وآلي؟

يمكن تشغيله باستخدام Scheduler أو نظام Workflow مثل Airflow أو خدمة جدولة النظام.

### 11. كيف يمكن جعل Pipeline يتعامل مع ملايين السجلات؟

يمكن استخدام المعالجة على دفعات، الفهارس، الاستعلامات الفعالة، التخزين الموزع، وتقنيات Parallel Processing عند الحاجة.

### 12. ما الفرق بين Batch Processing وStreaming Processing؟

Batch Processing يعالج مجموعة من البيانات في وقت محدد، بينما Streaming Processing يعالج البيانات أثناء وصولها بشكل مستمر.

## Data Lineage

تمت إضافة عمود source في Dataset النهائي لتوضيح أن البيانات النهائية تم دمجها من:

CSV + API + SQLite + MongoDB + Web Scraping

## Reusable Architecture

تم فصل كل مصدر في Module مستقل، لذلك يمكن إضافة مصدر جديد مثل Excel أو JSON أو MySQL أو PostgreSQL أو مصدر Web Scraping آخر بدون إعادة كتابة Pipeline بالكامل.
