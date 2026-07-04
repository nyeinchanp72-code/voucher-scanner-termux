# Voucher Scanner (Termux Edition) 🚀

ဒီ Script က Ruijie Portal Voucher တွေကို အလိုအလျောက် Scan ဖတ်ပေးမယ့် Tool ဖြစ်ပါတယ်။ အခု Version မှာ ကုဒ်တွေကို လုံခြုံအောင် ပြုလုပ်ထားပြီး ပေါ့ပါးမြန်ဆန်အောင် ဖန်တီးထားပါတယ်။

## 📥 Termux မှာ သွင်းနည်း (Installation)

Termux ကို ဖွင့်ပြီး အောက်ပါ Command များကို တစ်ကြောင်းချင်းစီ Copy ကူးပြီး Run ပါ-

```bash
# System ကို Update လုပ်ခြင်း
pkg update && pkg upgrade -y

# Python နှင့် Git ကို သွင်းခြင်း
pkg install python git clang make -y

# Repository ကို Clone လုပ်ခြင်း
git clone https://github.com/nyeinchanp72-code/voucher-scanner-termux.git
cd voucher-scanner-termux

# လိုအပ်သော Library များသွင်းခြင်း
pip install -r requirements.txt
```

## 🚀 အသုံးပြုနည်း (Usage)

Script ကို စတင်ရန် အောက်ပါ Command ကို ရိုက်ပါ-
```bash
python main.py
```

> **မှတ်ချက်:** ပထမဆုံးအကြိမ် Run သည့်အခါ ကုဒ်များကို လုံခြုံအောင် အလိုအလျောက် ပြုပြင်ပေးမည် ဖြစ်သောကြောင့် ခဏစောင့်ပေးပါ။ နောက်ပိုင်းတွင် ပုံမှန်အတိုင်း တိုက်ရိုက် Run နိုင်မည် ဖြစ်သည်။

## 🛠 အသုံးပြုနိုင်သော Command များ

Script ပွင့်လာပါက အောက်ပါ Command များကို အသုံးပြုနိုင်ပါသည်-

- **Portal URL သတ်မှတ်ရန်:**
  `setup <portal_url>`
  *(ဥပမာ: `setup https://10.10.10.1/portal/`)*

- **Scan စတင်ရန်:**
  `brute <digit_number>`
  *(ဥပမာ: ဂဏန်း ၇ လုံးကို scan ဖတ်လိုပါက `brute 7` ဟု ရိုက်ပါ)*

- **Scan ရပ်တန့်ရန်:**
  `stop`

- **သိမ်းဆည်းထားသော Code များကြည့်ရန်:**
  `saved`

- **Bot ၏ အခြေအနေကို စစ်ဆေးရန်:**
  `status`

- **Program မှ ထွက်ရန်:**
  `exit`

---

**Developed for Termux Users** 🇲🇲
