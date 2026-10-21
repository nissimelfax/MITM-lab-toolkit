[English](README.md) | [עברית](README.he.md)

# MITM Lab Toolkit

אוסף קטן של סקריפטים ב־Python ו־Scapy שבונים עמדת man-in-the-middle ברשת מקומית, ומדגימים שלוש התקפות LAN קלאסיות ברמת הפקטות: הרעלת ARP, זיוף DNS, והזרקת חבילות TCP RST. הפרויקט נכתב במעבדה לצורך למידה עצמית, מתוך רצון להבין איך ההתקפות האלה באמת עובדות ולא רק להפעיל כלי מוכן.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Scapy](https://img.shields.io/badge/built%20with-Scapy-green)
![Purpose](https://img.shields.io/badge/purpose-educational-orange)

> **לשימוש מורשה בלבד.** הסקריפטים נועדו ללמידה ולבדיקות על רשתות ומכשירים שבבעלותך או שקיבלת עליהם אישור מפורש בכתב. שימוש בהם מול מערכות שאינן שלך אינו חוקי ברוב המקומות. האחריות על השימוש היא עליך.

## תוכן

- [איך זה מתחבר יחד](#איך-זה-מתחבר-יחד)
- [דרישות](#דרישות)
- [איך מוצאים את מספר ה־interface](#איך-מוצאים-את-מספר-ה-interface)
- [הסקריפטים](#הסקריפטים)
  - [arp_spoofer.py](#arp_spooferpy-1)
  - [DNS_POISION.py](#dns_poisionpy-1)
  - [RST_PKTS.py](#rst_pktspy-1)
  - [mac_fixer.py](#mac_fixerpy-1)
- [הבהרה](#הבהרה)

## איך זה מתחבר יחד

הסקריפטים מתוכננים לרוץ ביחד. קודם שמים את המחשב שלנו באמצע בעזרת הרעלת ARP, ואז מריצים את ה־DNS וה־RST מעל העמדה הזו.

```mermaid
flowchart LR
    VIC["Victim device"] <-->|traffic| ATT["My PC<br/>(attacker / MITM 
 set DNS spoof on it)"]
    ATT <-->|traffic| GW["Router / Internet"]
```

סדר הרצה טיפוסי:

1. `arp_spoofer.py` כדי שהתעבורה תתחיל לעבור דרך המחשב שלך.
2. `DNS_POISION.py` ו/או `RST_PKTS.py` מעל העמדה הזו.

## דרישות

- Python 3.10 ומעלה
- [Scapy](https://scapy.net/)
- בווינדוס: התקנה של [Npcap](https://npcap.com/)
- הרשאות מנהל / root (הסקריפטים שולחים ומאזינים לפקטות גולמיות)

```bash
pip install scapy
```

## איך מוצאים את מספר ה־interface

כל סקריפט מקבל `--iface` כ**מספר** של interface ב־Scapy. כדי לראות את הרשימה ואת המספרים:

```bash
python -c "from scapy.all import show_interfaces; show_interfaces()"
```

קח את המספר מעמודת ה־index של ה־interface שאתה רוצה להשתמש בו.

## הסקריפטים

### arp_spoofer.py

שם את המחשב שלך בין הקורבן לבין הראוטר. הסקריפט שולח תשובות ARP מזויפות שאומרות לקורבן "הראוטר נמצא ב־MAC שלי", ולראוטר "הקורבן נמצא ב־MAC שלי", כך שהתעבורה בשני הכיוונים עוברת דרכך. ה־MAC שלך נשלף אוטומטית מה־interface שבחרת.

<details>
<summary>ארגומנטים ודוגמה</summary>

```
--victim-ip    כתובת ה־IP של הקורבן
--victim-mac   כתובת ה־MAC של הקורבן
--router-ip    כתובת ה־IP של הראוטר
--router-mac   כתובת ה־MAC של הראוטר
--iface        מספר ה־interface (ראה למעלה)
```

```bash
python arp_spoofer.py \
  --victim-ip 192.168.1.50 \
  --victim-mac AA:BB:CC:DD:EE:FF \
  --router-ip 192.168.1.1 \
  --router-mac 11:22:33:44:55:66 \
  --iface 15
```

רץ בלולאה ומרענן את הרשומות המורעלות עד שעוצרים עם Ctrl+C.
</details>

### DNS_POISION.py

דורש עמדת MITM פעילה (הרץ קודם את `arp_spoofer.py`). הסקריפט מאזין לשאילתות ה־DNS של הקורבן, וכשהוא רואה שאילתה לדומיין שבחרת שיוצאת לאחד משרתי ה־DNS הלגיטימיים, הוא מחזיר רשומת A מזויפת שמפנה את הדומיין ל־IP שבשליטתך.

<details>
<summary>ארגומנטים ודוגמה</summary>

```
--victim-ip     כתובת ה־IP של הקורבן
--iface         מספר ה־interface
--conf-domain   הדומיין שרוצים לחטוף (למשל `example.com.`)
--dns-ip        כתובת או כתובות IP של שרתי DNS לגיטימיים להאזנה
--fake-server   ה־IP שהתשובה המזויפת מחזירה (השרת שמתחזה לשרת האמיתי)
```

```bash
python DNS_POISION.py \
  --victim-ip 192.168.1.50 \
  --iface 15 \
  --conf-domain example.com. \
  --dns-ip 192.168.1.1 8.8.8.8 \
  --fake-server 192.168.1.80
```

`--dns-ip` מקבל כמה ערכים מופרדים ברווח.
</details>

### RST_PKTS.py

מאזין לתעבורת TCP מהקורבן אל רשימת כתובות IP, ומזריק חבילות TCP RST כדי לנתק את החיבורים האלה. שימושי ב־lab כדי להכריח את הקורבן לנתק חיבורים קיימים, כך שייווצר חיבור חדש (ושאילתת DNS חדשה).

<details>
<summary>ארגומנטים ודוגמה</summary>

```
--victim-ip    כתובת ה־IP של הקורבן
--iface        מספר ה־interface
--target-ips   כתובת או כתובות IP שרוצים לאפס להן את החיבורים
```

```bash
python RST_PKTS.py \
  --victim-ip 192.168.1.50 \
  --iface 15 \
  --target-ips 93.184.216.34 1.2.3.4
```

`--target-ips` מקבל כמה ערכים מופרדים ברווח.
</details>

### mac_fixer.py

כלי עזר קטן. מקבל כתובת MAC כמעט בכל פורמט (מקפים, נקודות, בלי מפרידים, אותיות גדולות או קטנות), ומחזיר אותה בפורמט הנקודתיים התקני ש־Scapy מצפה לו.

<details>
<summary>שימוש</summary>

```bash
python mac_fixer.py AA-BB-CC-DD-EE-FF
# -> aa:bb:cc:dd:ee:ff
```

אם מריצים בלי ארגומנט, הסקריפט יבקש להקליד את הכתובת.
</details>

## הבהרה

הפרויקט נועד ללמידה ולבדיקות מורשות בלבד. הרץ אותו ב־lab שבשליטתך, או מול מערכות שקיבלת עליהן אישור מפורש בכתב. תקיפת רשתות או מכשירים ללא הרשאה אינה חוקית ברוב המדינות. הכותב אינו אחראי לשימוש לרעה או לנזק שייגרם מהקוד הזה.
