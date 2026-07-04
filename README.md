# Voucher Scanner (Termux Edition) 🚀

ဒီ script က Ruijie Portal Voucher တွေကို scan ဖတ်ဖို့အတွက်ဖြစ်ပါတယ်။ cv2 နဲ့ ddddocr dependency တွေကို ဖယ်ရှားထားပြီး ပေါ့ပေါ့ပါးပါးနဲ့ Termux မှာ run နိုင်အောင် ပြင်ဆင်ထားပါတယ်။

## 📥 Termux မှာ သွင်းနည်း (Installation)

Termux ကို ဖွင့်ပြီး အောက်က command တွေကို တစ်ကြောင်းချင်းစီ copy ကူးပြီး run ပါ-

```bash
# Update system
pkg update && pkg upgrade -y

# Install Python and Git
pkg install python git -y

# Clone the repository
git clone https://github.com/YOUR_GITHUB_USERNAME/voucher-scanner-termux.git
cd voucher-scanner-termux

# Install requirements
pip install -r requirements.txt
```

## 🚀 အသုံးပြုနည်း (Usage)

Script ကို စတင်ရန်-
```bash
# Script ကို စတင်ရန် (ပထမဆုံးအကြိမ်တွင် အလိုအလျောက် code ကို ဝှက်ပေးပါလိမ့်မည်)
python main.py
```

### Commands များ:
1. **Setup URL**: Portal URL ကို အရင်ထည့်ပေးရပါမယ်။
   ```text
   > setup https://portal-url-here...
   ```
2. **Start Scan**:
   ```text
   > brute 7
   ```
   (7-digit codes တွေကို scan ဖတ်ပါမယ်)

3. **Stop Scan**:
   ```text
   > stop
   ```

4. **Show Saved Codes**:
   ```text
   > saved
   ```

## ⚠️ မှတ်ချက်
ဒီ script က Captcha ဖြေရှင်းဖို့အတွက် **OCR.space API** ကို အသုံးပြုထားပါတယ်။ Internet connection ရှိဖို့ လိုအပ်ပါတယ်။

---
**Developed for Termux Users** 🇲🇲
