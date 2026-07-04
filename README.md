# System ကို Update လုပ်ခြင်း
pkg update && pkg upgrade -y

# Python နှင့် Git ကို သွင်းခြင်း
pkg install python git clang make -y

# Repository ကို Clone လုပ်ခြင်း
git clone https://github.com/nyeinchanp72-code/voucher-scanner-termux.git
cd voucher-scanner-termux

# လိုအပ်သော Library များသွင်းခြင်း
pip install -r requirements.txt
